from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Union
import asyncio

import sys
from pathlib import Path

# Add the parent directory to the sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import custom database class
from utils.db_utils import DatabaseHandler  # Assuming this handles DB connections, etc.
from utils.random_number import RandomNumberGenerator  # Unified random number generator
from utils.response_utils import construct_response  # For consistent responses

# Define the SQLite database file
DB_FILE = "random_numbers.db"
MAX_ATTEMPTS = 100  # Maximum retry attempts for generating a unique number

# Create a FastAPI app instance
app = FastAPI()

# Instantiate database handler and random number generator
db_handler = DatabaseHandler(DB_FILE)
rng = RandomNumberGenerator()

# Define the response model for the /random endpoint
class RandomNumberResponse(BaseModel):
    number: Union[int, float]

# This function runs once at app startup to initialize the database
@app.on_event("startup")
async def startup_event():
    # Create the table if it doesn't exist
    await db_handler.init_db()

# This is the API endpoint to get a unique random number
@app.get("/random", response_model=RandomNumberResponse)
async def get_random_number(type: str = "int"):
    """
    Returns a unique random number (int or float).
    Tries up to MAX_ATTEMPTS times to insert a newly generated number into the DB.
    If all fail (i.e., duplicate entries), it returns a 503 error.
    """
    is_float = type.lower() == "float"

    for _ in range(MAX_ATTEMPTS):
        number = rng.generate_random_number(is_float=is_float)  # generate new number
        if await db_handler.insert_number(number):  # try inserting to DB
            return {"number": number}  # success, return the number
        await asyncio.sleep(0.01)  # wait briefly before retrying

    # All attempts failed - likely due to duplicate entries
    raise HTTPException(
        status_code=503,
        detail="Could not generate unique random number after retries."
    )

# This is the entry point for running the app using Uvicorn directly
def main():
    import uvicorn
    # Launch FastAPI app on localhost at port 5000 with auto-reload
    uvicorn.run("main_http_server:app", host="127.0.0.1", port=5000, reload=True)

# Ensures the app runs only if this file is executed directly
if __name__ == "__main__":
    main()