# agent.py
import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Sequence
from dataclasses import dataclass
from pymongo import MongoClient
# LangChain imports
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_mongodb import MongoDBAtlasVectorSearch
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.mongodb import MongoDBSaver

# MongoDB imports
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
import ssl
import certifi

# Pydantic for data validation
from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Annotated

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type definitions for better code organization
class ItemLookupInput(BaseModel):
    query: str = Field(description="The search query")
    n: int = Field(default=10, description="Number of results to return")

class SearchResult(BaseModel):
    results: Optional[List[Any]] = None
    searchType: Optional[str] = None
    query: str
    count: int
    error: Optional[str] = None
    message: Optional[str] = None
    details: Optional[str] = None

# Define the state structure for the agent workflow
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# Utility function to handle API rate limits with exponential backoff
async def retry_with_backoff(func, max_retries: int = 3):
    """
    Retry function with exponential backoff for handling rate limits
    
    Args:
        func: The async function to retry
        max_retries: Maximum number of retry attempts (default 3)
    
    Returns:
        Result of the function call
    """
    # Loop through retry attempts
    for attempt in range(1, max_retries + 1):
        try:
            return await func()  # Try to execute the function
        except Exception as error:
            # Check if it's a rate limit error (HTTP 429) and we have retries left
            if hasattr(error, 'status_code') and error.status_code == 429 and attempt < max_retries:
                # Calculate exponential backoff delay: 2^attempt seconds, max 30 seconds
                delay = min(2 ** attempt, 30)
                logger.info(f"Rate limit hit. Retrying in {delay} seconds...")
                # Wait for the calculated delay before retrying
                await asyncio.sleep(delay)
                continue  # Go to next iteration (retry)
            raise error  # If not rate limit or out of retries, throw the error
    
    raise Exception("Max retries exceeded")  # This should never be reached

# Main function that creates and runs the AI agent
async def call_agent(client: AsyncIOMotorClient, query: str, thread_id: str) -> str:
    """
    Main agent function that processes user queries using LangGraph workflow
    
    Args:
        client: MongoDB client instance
        query: User's query/message
        thread_id: Unique conversation thread identifier
        
    Returns:
        AI agent's response as string
    """
    try:
        # Database configuration
        db_name = "inventory_database"        # Name of the MongoDB database
        db = client[db_name]                  # Get database instance
        collection = db["items"]              # Get the 'items' collection

        # Create a custom tool for searching furniture inventory
        @tool("item_lookup", args_schema=ItemLookupInput)
        async def item_lookup_tool(query: str, n: int = 10) -> str:
            """
            Gathers furniture item details from the Inventory database
            
            Args:
                query: The search query
                n: Number of results to return (default 10)
                
            Returns:
                JSON string containing search results or error information
            """
            try:
                logger.info(f"Item lookup tool called with query: {query}")

                # Check if database has any data at all
                total_count = await collection.count_documents({})
                logger.info(f"Total documents in collection: {total_count}")

                # Early return if database is empty
                if total_count == 0:
                    logger.info("Collection is empty")
                    return json.dumps({
                        "error": "No items found in inventory",
                        "message": "The inventory database appears to be empty",
                        "count": 0,
                        "query": query
                    })

                # Get sample documents for debugging purposes
                sample_docs = []
                async for doc in collection.find({}).limit(3):
                    # Convert ObjectId to string for JSON serialization
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
                    sample_docs.append(doc)
                logger.info(f"Sample documents: {sample_docs}")

                # Configuration for MongoDB Atlas Vector Search
                db_config = {
                    "collection": collection,           # MongoDB collection to search
                    "index_name": "vector_index",       # Name of the vector search index
                    "text_key": "embedding_text",       # Field containing the text used for embeddings
                    "embedding_key": "embedding",       # Field containing the vector embeddings
                }

                # Create vector store instance for semantic search using Google Gemini embeddings
                vector_store = MongoDBAtlasVectorSearch(
                    embedding=GoogleGenerativeAIEmbeddings(
                        google_api_key=os.getenv("GOOGLE_API_KEY"),  # Google API key from environment
                        model="text-embedding-004",                   # Gemini embedding model
                    ),
                    **db_config
                )

                logger.info("Performing vector search...")
                # Perform semantic search using vector embeddings
                try:
                    result = await vector_store.asimilarity_search_with_score(query, k=n)
                    logger.info(f"Vector search returned {len(result)} results")
                except Exception as vector_error:
                    logger.warning(f"Vector search failed: {vector_error}")
                    result = []
                
                # If vector search returns no results, fall back to text search
                if len(result) == 0:
                    logger.info("Vector search returned no results, trying text search...")
                    # MongoDB text search using regular expressions
                    text_results = []
                    async for doc in collection.find({
                        "$or": [  # OR condition - match any of these fields
                            {"item_name": {"$regex": query, "$options": "i"}},        # Case-insensitive search in item name
                            {"item_description": {"$regex": query, "$options": "i"}}, # Case-insensitive search in description
                            {"categories": {"$regex": query, "$options": "i"}},       # Case-insensitive search in categories
                            {"embedding_text": {"$regex": query, "$options": "i"}}    # Case-insensitive search in embedding text
                        ]
                    }).limit(n):
                        # Convert ObjectId to string for JSON serialization
                        if '_id' in doc:
                            doc['_id'] = str(doc['_id'])
                        text_results.append(doc)
                    
                    logger.info(f"Text search returned {len(text_results)} results")
                    # Return text search results as JSON string
                    return json.dumps({
                        "results": text_results,
                        "searchType": "text",    # Indicate this was a text search
                        "query": query,
                        "count": len(text_results)
                    })

                # Process vector search results
                processed_results = []
                for doc, score in result:
                    doc_dict = doc.dict() if hasattr(doc, 'dict') else {"page_content": str(doc)}
                    doc_dict['similarity_score'] = float(score)
                    processed_results.append(doc_dict)

                # Return vector search results as JSON string
                return json.dumps({
                    "results": processed_results,
                    "searchType": "vector",   # Indicate this was a vector search
                    "query": query,
                    "count": len(processed_results)
                })
                
            except Exception as error:
                # Log detailed error information for debugging
                logger.error(f"Error in item lookup: {error}")
                logger.error(f"Error details: {type(error).__name__}: {str(error)}")
                
                # Return error information as JSON string
                return json.dumps({
                    "error": "Failed to search inventory",
                    "details": str(error),
                    "query": query,
                    "count": 0
                })

        # Array of all available tools (just one in this case)
        tools = [item_lookup_tool]
        # Create a tool execution node for the workflow
        tool_node = ToolNode(tools)

        # Initialize the AI model (Google's Gemini)
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",           # Use Gemini 1.5 Flash model
            temperature=0,                      # Deterministic responses (no randomness)
            max_retries=0,                      # Disable built-in retries (we handle our own)
            google_api_key=os.getenv("GOOGLE_API_KEY"),  # Google API key from environment
        ).bind_tools(tools)                     # Bind our custom tools to the model

        # Decision function: determines next step in the workflow
        def should_continue(state: AgentState) -> str:
            """
            Routing function that determines the next step in the workflow
            
            Args:
                state: Current state containing conversation messages
                
            Returns:
                Next node name ("tools" or "__end__")
            """
            messages = state["messages"]                               # Get all messages
            last_message = messages[-1]                               # Get the most recent message

            # If the AI wants to use tools, go to tools node; otherwise end
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"  # Route to tool execution
            return "__end__"    # End the workflow

        # Function that calls the AI model with retry logic
        async def call_model(state: AgentState) -> Dict[str, List[BaseMessage]]:
            """
            Call the AI model with conversation state and retry logic
            
            Args:
                state: Current agent state with conversation history
                
            Returns:
                Updated state with AI model's response
            """
            async def _call_model():
                # Create a structured prompt template
                prompt = ChatPromptTemplate.from_messages([
                    (
                        "system",  # System message defines the AI's role and behavior
                        f"""You are a helpful E-commerce Chatbot Agent for a furniture store.

    IMPORTANT: You have access to an item_lookup tool that searches the furniture inventory database. ALWAYS use this tool when customers ask about furniture items, even if the tool returns errors or empty results.

    When using the item_lookup tool:
    - If it returns results, provide helpful details about the furniture items
    - If it returns an error or no results, acknowledge this and offer to help in other ways
    - If the database appears to be empty, let the customer know that inventory might be being updated

    Current time: {datetime.now().isoformat()}""",
                    ),
                    MessagesPlaceholder("messages"),  # Placeholder for conversation history
                ])

                # Fill in the prompt template with actual values
                formatted_prompt = await prompt.aformat_messages(
                    messages=state["messages"]        # All previous messages
                )

                # Call the AI model with the formatted prompt
                result = await model.ainvoke(formatted_prompt)
                # Return new state with the AI's response added
                return {"messages": [result]}

            return await retry_with_backoff(_call_model)  # Wrap in retry logic

        # Build the workflow graph
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", call_model)                      # Add AI model node
        workflow.add_node("tools", tool_node)                       # Add tool execution node
        workflow.set_entry_point("agent")                           # Start workflow at agent
        workflow.add_conditional_edges("agent", should_continue)    # Agent decides: tools or end
        workflow.add_edge("tools", "agent")                         # After tools, go back to agent

        # create a sync client for LangGraph checkpoints
        sync_client = MongoClient(os.getenv("MONGODB_ATLAS_URI"), tlsCAFile=certifi.where())

        checkpointer = MongoDBSaver(
            client=sync_client,
            db_name=db_name
        )
        
        # Compile the workflow with state saving
        app = workflow.compile(checkpointer=checkpointer)

        # Execute the workflow
        final_state = await app.ainvoke(
            {
                "messages": [HumanMessage(content=query)],  # Start with user's question
            },
            config={
                "recursion_limit": 15,                      # Prevent infinite loops
                "configurable": {"thread_id": thread_id}    # Conversation thread identifier
            }
        )

        # Extract the final response from the conversation
        response = final_state["messages"][-1].content
        logger.info(f"Agent response: {response}")

        return response  # Return the AI's final response

    except Exception as error:
        # Handle different types of errors with user-friendly messages
        logger.error(f"Error in call_agent: {error}")
        
        if hasattr(error, 'status_code') and error.status_code == 429:  # Rate limit error
            raise Exception("Service temporarily unavailable due to rate limits. Please try again in a minute.")
        elif hasattr(error, 'status_code') and error.status_code == 401:  # Authentication error
            raise Exception("Authentication failed. Please check your API configuration.")
        else:  # Generic error
            raise Exception(f"Agent failed: {str(error)}")