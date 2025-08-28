# seed_database.py

import os
import json
import asyncio
from typing import List, Dict, Any
from datetime import datetime

# Import Google's Gemini chat model and embeddings for AI text generation and vector creation
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
# Import structured output parser to ensure AI returns data in specific format
from langchain_core.output_parsers import PydanticOutputParser
# Import MongoDB async client for database connection
from motor.motor_asyncio import AsyncIOMotorClient
import ssl
import certifi
# Import MongoDB Atlas vector search for storing and searching embeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
# Import Pydantic for data schema validation and type safety
from pydantic import BaseModel, Field
from typing import List as TypingList, Optional
# Load environment variables from .env file (API keys, connection strings)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define Pydantic models for furniture item structure with validation
class ManufacturerAddress(BaseModel):
    street: str = Field(description="Street address")
    city: str = Field(description="City name")
    state: str = Field(description="State/province")
    postal_code: str = Field(description="ZIP/postal code")
    country: str = Field(description="Country name")

class Prices(BaseModel):
    full_price: float = Field(description="Regular price")
    sale_price: float = Field(description="Discounted price")

class UserReview(BaseModel):
    review_date: str = Field(description="Date of review")
    rating: int = Field(description="Numerical rating (1-5)", ge=1, le=5)
    comment: str = Field(description="Review text comment")

class Item(BaseModel):
    item_id: str = Field(description="Unique identifier for the item")
    item_name: str = Field(description="Name of the furniture item")
    item_description: str = Field(description="Detailed description of the item")
    brand: str = Field(description="Brand/manufacturer name")
    manufacturer_address: ManufacturerAddress = Field(description="Manufacturer location")
    prices: Prices = Field(description="Pricing information")
    categories: TypingList[str] = Field(description="Array of category tags")
    user_reviews: TypingList[UserReview] = Field(description="Array of customer reviews")
    notes: str = Field(description="Additional notes about the item")

class ItemList(BaseModel):
    items: TypingList[Item] = Field(description="List of furniture items")

# Create MongoDB client instance using connection string from environment variables
# SSL configuration for macOS certificate issues
import ssl
import certifi

client = AsyncIOMotorClient(
    os.getenv("MONGODB_ATLAS_URI"),
    tlsCAFile=certifi.where(),

)

# Initialize Google Gemini chat model for generating synthetic furniture data
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",                    # Use Gemini 1.5 Flash model
    temperature=0.7,                             # Set creativity level (0.7 = moderately creative)
    google_api_key=os.getenv("GOOGLE_API_KEY"),  # Google API key from environment variables
)

# Create parser that ensures AI output matches our item schema
parser = PydanticOutputParser(pydantic_object=ItemList)

async def setup_database_and_collection() -> None:
    """Function to create database and collection before seeding"""
    print("Setting up database and collection...")
    
    # Get reference to the inventory_database database
    db = client["inventory_database"]
    
    # Create the items collection if it doesn't exist
    collections = await db.list_collection_names()
    
    if "items" not in collections:
        await db.create_collection("items")
        print("Created 'items' collection in 'inventory_database' database")
    else:
        print("'items' collection already exists in 'inventory_database' database")

async def create_vector_search_index() -> None:
    """Function to create vector search index"""
    try:
        db = client["inventory_database"]
        collection = db["items"]
        
        # Drop existing indexes
        await collection.drop_indexes()
        
        vector_search_idx = {
            "name": "vector_index",
            "type": "vectorSearch",
            "definition": {
                "fields": [
                    {
                        "type": "vector",
                        "path": "embedding",
                        "numDimensions": 768,
                        "similarity": "cosine"
                    }
                ]
            }
        }
        
        print("Creating vector search index...")
        # Note: In Python, we use create_search_index differently
        # This might need to be adjusted based on your MongoDB setup
        try:
            await collection.create_search_index(vector_search_idx)
            print("Successfully created vector search index")
        except Exception as e:
            print(f"Note: Vector search index creation may require MongoDB Atlas setup: {e}")
            
    except Exception as e:
        print(f'Failed to create vector search index: {e}')

async def generate_synthetic_data() -> List[Item]:
    """Generate synthetic furniture data using AI"""
    # Create detailed prompt instructing AI to generate furniture store data
    prompt = f"""You are a helpful assistant that generates furniture store item data. Generate 10 furniture store items. Each record should include the following fields: item_id, item_name, item_description, brand, manufacturer_address, prices, categories, user_reviews, notes. Ensure variety in the data and realistic values.

    {parser.get_format_instructions()}"""

    # Log progress to console
    print("Generating synthetic data...")

    # Send prompt to AI and get response
    response = await llm.ainvoke(prompt)

    # Parse AI response into structured list of Item objects
    try:
        parsed_data = parser.parse(response.content)
        return parsed_data.items
    except Exception as e:
        print(f"Error parsing AI response: {e}")
        # If parsing fails, return empty list or handle gracefully
        return []

async def create_item_summary(item: Item) -> str:
    """Function to create a searchable text summary from furniture item data"""
    # Extract manufacturer country information
    manufacturer_details = f"Made in {item.manufacturer_address.country}"
    
    # Join all categories into comma-separated string
    categories = ", ".join(item.categories)
    
    # Convert user reviews list into readable text format
    user_reviews = " ".join([
        f"Rated {review.rating} on {review.review_date}: {review.comment}"
        for review in item.user_reviews
    ])
    
    # Create basic item information string
    basic_info = f"{item.item_name} {item.item_description} from the brand {item.brand}"
    
    # Format pricing information
    price = f"At full price it costs: {item.prices.full_price} USD, On sale it costs: {item.prices.sale_price} USD"
    
    # Get additional notes
    notes = item.notes

    # Combine all information into comprehensive summary for vector search
    summary = f"{basic_info}. Manufacturer: {manufacturer_details}. Categories: {categories}. Reviews: {user_reviews}. Price: {price}. Notes: {notes}"

    return summary

async def seed_database() -> None:
    """Main function to populate database with AI-generated furniture data"""
    try:
        # Test connection to MongoDB Atlas
        await client.admin.command("ping")
        print("You successfully connected to MongoDB!")

        # Setup database and collection
        await setup_database_and_collection()
        
        # Create vector search index
        await create_vector_search_index()

        # Get reference to specific database
        db = client["inventory_database"]
        collection = db["items"]

        # Clear existing data from collection (fresh start)
        delete_result = await collection.delete_many({})
        print(f"Cleared {delete_result.deleted_count} existing documents from items collection")
        
        # Generate new synthetic furniture data using AI
        synthetic_data = await generate_synthetic_data()
        
        if not synthetic_data:
            print("No synthetic data generated. Exiting.")
            return

        print(f"Generated {len(synthetic_data)} synthetic items")

        # Process each item: create summary and prepare for vector storage
        records_with_summaries = []
        for record in synthetic_data:
            summary = await create_item_summary(record)
            records_with_summaries.append({
                "page_content": summary,
                "metadata": record.dict()
            })
        
        # Store each record with vector embeddings in MongoDB
        for i, record in enumerate(records_with_summaries):
            try:
                print(f"Processing record {i+1}/{len(records_with_summaries)}")
                
                # Convert the record to the format expected by MongoDBAtlasVectorSearch
                from langchain_core.documents import Document
                doc = Document(
                    page_content=record["page_content"],
                    metadata=record["metadata"]
                )
                
                # Create vector embeddings and store in MongoDB Atlas using Gemini
                vector_store = MongoDBAtlasVectorSearch.from_documents(
                    documents=[doc],                                    # Array containing single record
                    embedding=GoogleGenerativeAIEmbeddings(             # Google embedding model
                        google_api_key=os.getenv("GOOGLE_API_KEY"),     # Google API key
                        model="text-embedding-004",                     # Google's standard embedding model (768 dimensions)
                    ),
                    collection=collection,                              # MongoDB collection reference
                    index_name="vector_index",                         # Name of vector search index
                    text_key="embedding_text",                         # Field name for searchable text
                    embedding_key="embedding",                         # Field name for vector embeddings
                )

                # Log progress for each successfully processed item
                print(f"Successfully processed & saved record: {record['metadata']['item_id']}")
                
            except Exception as record_error:
                print(f"Error processing record {record['metadata'].get('item_id', 'unknown')}: {record_error}")
                continue

        # Log completion of entire seeding process
        print("Database seeding completed")

    except Exception as error:
        # Log any errors that occur during database seeding
        print(f"Error seeding database: {error}")
    finally:
        # Always close database connection when finished (cleanup)
        client.close()

# Execute the database seeding function and handle any errors
if __name__ == "__main__":
    asyncio.run(seed_database())