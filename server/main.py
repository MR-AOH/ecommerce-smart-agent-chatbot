# main.py
import os
import asyncio
import time
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import ssl
import certifi
from dotenv import load_dotenv

# Import our custom AI agent function
from agent import call_agent

# Load environment variables from .env file (must be first)
load_dotenv()

# Create FastAPI application instance
app = FastAPI(title="LangGraph Agent Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for now (for local dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response validation
class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    threadId: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str

# Global MongoDB client variable
mongo_client: Optional[AsyncIOMotorClient] = None

@app.on_event("startup")
async def startup_event():
    """Initialize MongoDB connection when server starts"""
    global mongo_client
    try:
        # Create MongoDB client using connection string from environment variables
        # SSL configuration for macOS certificate issues
        mongo_client = AsyncIOMotorClient(
            os.getenv("MONGODB_ATLAS_URI"),
            tlsCAFile=certifi.where()
        )
        
        # Ping MongoDB to verify connection is working
        await mongo_client.admin.command("ping")
        
        # Log successful connection
        print("You successfully connected to MongoDB!")
        
    except Exception as error:
        # Handle any errors during MongoDB connection
        print(f"Error connecting to MongoDB: {error}")
        # Exit the process with error code 1 (indicates failure)
        exit(1)

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection when server shuts down"""
    global mongo_client
    if mongo_client:
        mongo_client.close()
        print("MongoDB connection closed")

@app.get("/")
async def root():
    """Root endpoint - simple health check"""
    # Send simple response to confirm server is running
    return {"message": "LangGraph Agent Server"}

@app.post("/chat", response_model=ChatResponse)
async def start_chat(chat_message: ChatMessage):
    """Define endpoint for starting new conversations (POST /chat)"""
    global mongo_client
    
    if not mongo_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection not available"
        )
    
    # Extract user message from request body
    initial_message = chat_message.message
    
    # Generate unique thread ID using current timestamp
    thread_id = str(int(time.time() * 1000))  # Convert to milliseconds like Date.now()
    
    # Log the incoming message for debugging
    print(f"Initial message: {initial_message}")
    
    try:
        # Call our AI agent with the message and new thread ID
        response = await call_agent(mongo_client, initial_message, thread_id)
        
        # Send successful response with thread ID and AI response
        return ChatResponse(threadId=thread_id, response=response)
    
    except Exception as error:
        # Log any errors that occur during agent execution
        print(f"Error starting conversation: {error}")
        # Send error response with 500 status code
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/chat/{thread_id}", response_model=ChatResponse)
async def continue_chat(thread_id: str, chat_message: ChatMessage):
    """Define endpoint for continuing existing conversations (POST /chat/:threadId)"""
    global mongo_client
    
    if not mongo_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection not available"
        )
    
    # Extract user message from request body
    message = chat_message.message
    
    try:
        # Call AI agent with message and existing thread ID (continues conversation)
        response = await call_agent(mongo_client, message, thread_id)
        
        # Send AI response (no need to send threadId again since it's continuing)
        return ChatResponse(response=response)
        
    except Exception as error:
        # Log any errors that occur during agent execution
        print(f"Error in chat: {error}")
        # Send error response with 500 status code
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    # Start the FastAPI server on specified port
    print(f"Server running on port {port}")
    uvicorn.run(app, host="localhost", port=port)