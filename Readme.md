*********** Project: Project: Concurrent Unique Random Number Generator HTTP Server using FastAPI & SQLite **************

This project provides a FastAPI server that generates unique random numbers (integers or floats) with support for concurrent requests. Each number is guaranteed to be unique and will not be repeated, even if the server is restarted. The numbers are persisted across restarts in an SQLite database with optimizations for concurrent access.

## Logic

The server uses an asynchronous SQLite database with Write-Ahead Logging (WAL) to efficiently store already-generated numbers, ensuring that each number is unique. When a request comes in, the server generates a random number and attempts to insert it into the database. If the insertion fails due to a duplicate, the server will retry with new numbers up to a maximum number of attempts (10 in our case). This approach ensures that the server can handle a large number of concurrent requests without repeating any numbers.

### main_http_server.py
This script sets up a FastAPI server that exposes a `/random` endpoint. When a GET request is made to this endpoint with an optional `type` parameter (either "int" or "float"), the server generates a unique random number using the RandomNumberGenerator class and ensures uniqueness by storing it in the database.

### utils/db_utils.py
This module provides a DatabaseHandler class that manages the SQLite database operations asynchronously. It includes:
  ** Database initialization with WAL journaling mode for concurrent access
  ** Insert operations with retry logic to handle database locks during high concurrency
  ** Utility functions for debugging and testing

### utils/int_float_random_utils.py
This module provides a RandomNumberGenerator class that generates either random integers (8-bit) or floating point numbers (0 to 10,000 with 4 decimal precision) based on the request type.

### test/test_concurrency.py
A testing utility that sends multiple concurrent requests to the server to verify its ability to handle high concurrency.

## Requirements:

pip install fastapi uvicorn aiosqlite


## Run the Server and Check the API

1. Run the script using the following command:

python main_http_server.py

Or alternatively:

uvicorn main_http_server:app --reload --port 5000

2. Check the HTTP Server:

   1. Basic Test: Open a web browser and navigate to http://127.0.0.1:5000/random. You should see a JSON response with a unique random integer.
   
   2. Request a Float: Navigate to http://127.0.0.1:5000/random?type=float to get a unique random float value.

   3. Test Concurrency: Run the concurrency test script to send multiple requests simultaneously:

       python test/test_concurrency.py