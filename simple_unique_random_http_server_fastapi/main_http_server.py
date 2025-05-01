from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Union
import uvicorn
import sys
from pathlib import Path

# Add the parent directory to the sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.random_number import RandomNumberGenerator
from utils.error_handler import handle_exception
from utils.persistence_json_utils import load_used_numbers, save_used_numbers, define_persistence_file_path

# Constants and initialization
PERSISTENCE_FILE = define_persistence_file_path("used_numbers.json")
used_numbers = load_used_numbers(PERSISTENCE_FILE)
generator = RandomNumberGenerator()

# Define response model
class RandomNumberResponse(BaseModel):
    number: Union[int, float]

# Create FastAPI app
app = FastAPI(title="Unique Random Number Server With FastAPI")

# Endpoint for random number
@app.get("/random", response_model=RandomNumberResponse)
def get_random_number(type: str = "int"):
    try:
        is_float = type.lower() == "float"

        max_attempts = 100
        for _ in range(max_attempts):
            number = generator.generate_random_number(is_float=is_float)
            if number not in used_numbers:
                used_numbers.add(number)
                save_used_numbers(PERSISTENCE_FILE, used_numbers)
                break
        else:
            raise HTTPException(status_code=503, detail="Could not generate a unique number after multiple attempts.")

        return {"number": number}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

# Handle 404 errors for other paths
@app.get("/{path:path}")
def not_found(path: str):
    raise HTTPException(status_code=404, detail="Not found")

# Run the server
if __name__ == "__main__":
    uvicorn.run("main_http_server:app", host="127.0.0.1", port=8000, reload=True)