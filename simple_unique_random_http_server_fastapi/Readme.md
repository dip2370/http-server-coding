*********** Project: Unique Random Number Generator HTTP SERVER using FASTAPI **************

This project provides a simple HTTP server that generates unique random numbers within a specified range. Each number is guaranteed to be unique and will not be repeated, even if the server is restarted. The numbers are persisted across restarts in a JSON file.

## Logic

The server uses a set to efficiently check if a number has already been used, ensuring that each number is unique. If a number is generated that has already been used, the server will continue generating new numbers until a unique one is found. This approach ensures that the server can handle a large number of requests without repeating any numbers.

## unique_random_number_generator.py
This module provides a UniqueRandomNumberGenerator class that generates unique random numbers within a specified range. The class uses a file to store previously used numbers, which allows it to ensure uniqueness even if the script is restarted.

## unique_random_number_generator_fastapi.py
This script sets up a FastAPI server that exposes a /random endpoint.
When a GET request is made to this endpoint, the server generates a unique random number using the UniqueRandomNumberGenerator class and returns it as a JSON response.

## Requirements:

pip install fastapi uvicorn


******** Run the Script and Check the HTTP Server *******

1. Run the script using the command uvicorn unique_random_number_generator_fastapi:app --reload --port 5000 
       This will start the HTTP server, which by default listens on port 5000.

2. Check the Http Server:

Open a web browser --> Navigate to http://127.0.0.1:5000/random --> You should see a JSON response with a unique random number.

