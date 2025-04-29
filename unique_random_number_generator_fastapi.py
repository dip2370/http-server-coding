from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import uvicorn
from unique_random_number_generator import UniqueRandomNumberGenerator

# Configuration Constants
MIN_NUM = 100
MAX_NUM = 100000
PERSISTENCE_FILE = Path("used_numbers.json")

# Instantiate the generator
generator = UniqueRandomNumberGenerator(MIN_NUM, MAX_NUM, PERSISTENCE_FILE)

# Define response model
class RandomNumberResponse(BaseModel):
    number: int

# Create FastAPI app
app = FastAPI(title="Unique Random Number Server With FastAPI")

# Endpoint for random number
@app.get("/random", response_model=RandomNumberResponse)
def get_random_number():
    try:
        number = generator.generate()
        return {"number": number}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

# Handle 404 errors for other paths
@app.get("/{path:path}")
def not_found(path: str):
    raise HTTPException(status_code=404, detail="Not found")

# Run the server
if __name__ == "__main__":
    uvicorn.run("unique_random_number_generator_fastapi:app", host="172.0.0.0", port=8000, reload=True)
