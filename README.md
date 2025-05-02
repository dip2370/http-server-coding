*************** Unique Random Number HTTP API Server ***********************


This project provides a set of Python server implementations to generate unique random numbers (both integers and floats) via an HTTP API endpoint, always returning a JSON response. There are four progressive implementations included, each demonstrating a different architectural approach to the problem.

------------------------------------------------------------------------------------------------------
To Run these projects please install the python packages mentioned in requirements.txt

pip install -r ./requirements.txt



## 1. Simple HTTP Server
A synchronous HTTP server that serves unique random numbers at the /random endpoint. It uses a local JSON file (used_numbers.json) to persist previously served numbers, ensuring uniqueness across sessions. Supports an optional type=float query parameter to return floats.

===> How to Run:


    python simple_unique_random_http_server/main_http_server.py
    Starts the server on http://localhost:5000.

===> Check HTTP Server:

    http://localhost:5000/random

    http://localhost:5000/random?type=float

### Logic:
Each request checks whether the client wants an integer or float. It tries up to 100 times to generate a number not found in the JSON-based store. If successful, the number is added to the store and returned. If not, a 503 error is returned. Unrecognized paths return a 404.



## 2. Unique Random Number HTTP Server Using FastAPI (Synchronous, File-Based Persistence)

## Description:
A FastAPI-based version of the above server with the same logic and file-based persistence, but improved structure, validation, and maintainability. Responses and API behaviors are defined using FastAPI's features.

==> How to Run:

    cd simple_unique_random_http_server_fastapi
    uvicorn main_http_server:app --port 8000 --reload

===> Check HTTP Server:

    http://127.0.0.1:8000/random

    http://127.0.0.1:8000/random?type=float

## Logic:
Same as version 1: generates a number, checks for uniqueness in a JSON file, and returns it. The use of FastAPI allows for cleaner code and better scalability options.



### 3. Async Unique Random Number HTTP Server Using FastAPI and SQLite

This implementation builds a high-performance, production-ready HTTP API server using FastAPI in combination with SQLite and asynchronous I/O via aiosqlite. The server exposes a /random endpoint that returns a globally unique random number, either an integer or a float based on the type query parameter. Internally, it persists all generated numbers in a SQLite database with a unique constraint, ensuring no duplication across requests or restarts. As it leverages non-blocking asynchronous database operations, this version is well-suited for handling concurrent requests efficiently while preserving global uniqueness guarantees.

===>How to run:
    
    cd async_unique_random_http_server_fastapi_sqlite directory
    uvicorn main_http_server:app --port 5000 --reload

    Alternatively, if you're executing the script directly, it includes a main() function, so you can also run it like this:

    python main_http_server.py

    This will start the FastAPI app on http://127.0.0.1:5000.

===> How to check the HTTP server:
    open your browser and visit:

    http://127.0.0.1:5000/random
    To get a float instead of an integer, append the query parameter like this:

    http://127.0.0.1:5000/random?type=float
    You’ll receive a JSON response such as {"number": 928374} or {"number": 3482.712345}. 


*** ===> Concurrency Test ***

python test/test_concurrent.py

This Python script tests the concurrency performance of a FastAPI-based random number server by sending 100 simultaneous HTTP GET requests to the /random endpoint using 8 threads. Each request randomly chooses between requesting an integer or a float (?type=int or ?type=float) and sends it to the server at http://127.0.0.1:8000. The responses are parsed as JSON and printed, while any errors (like timeouts or connection issues) are caught and logged. The use of ThreadPoolExecutor ensures that multiple requests are made concurrently, effectively simulating client load to evaluate how well the server handles parallel traffic.


### Logic behind it:
Upon startup, the FastAPI app initializes the SQLite database with a random_numbers table if it doesn't already exist. The database uses WAL (Write-Ahead Logging) mode to enable better concurrency. When a request hits the /random endpoint, the app determines the required number type (int or float) and attempts up to MAX_ATTEMPTS (100) to generate a number that can be inserted into the database. The insertion is handled by the DatabaseHandler class, which uses aiosqlite for async DB operations. If a generated number violates the UNIQUE constraint or the DB is momentarily locked, it retries with a short delay using asyncio. Only if all attempts fail does the API return a 503 error. Successfully inserted numbers are stored persistently, guaranteeing global uniqueness across time and concurrent requests.

### Benefits over previous code:
This implementation offers significant improvements over both the basic synchronous HTTP server and the synchronous FastAPI variant. Firstly, the use of SQLite as a backing store for persistence is more robust and scalable than a flat JSON file, especially as the dataset grows. Secondly, this enables the server to handle many simultaneous requests without blocking on file or database locks. This means better performance with improved concurrency handling.

### 4. Scalable Unique Random Number Server with Sharded SQLite and Persistent Metadata

This implementation builds a fully asynchronous, scalable HTTP API server using FastAPI and SQLite to serve globally unique random numbers, leveraging a sharded architecture and persistent metadata tracking. The /random endpoint returns either a unique integer or a float, depending on the optional type query parameter (int by default). The backend comprises four shard databases (int_shard_0.db, int_shard_1.db, float_shard_0.db, float_shard_1.db) and two persistent metadata databases (used_numbers_int.db, used_numbers_float.db). The metadata DBs track all numbers ever served, ensuring global uniqueness across time and restarts. When a shard is depleted, the system triggers an async refill task that fetches globally unique numbers from the metadata check, refills the shard, and makes it available again. This ensures continuous, non-redundant service even under high demand or restarts.

****===> How to run: ***

    cd scalable_unique_random_http_server_fastapi_sharded

    ===> Initialize the shards and metadata databases using:

        python initialize_shards.py

        This script fills each shard with a set of random numbers (integers or floats) while ensuring that none have been served before, as checked against the metadata databases.

    ===> Start the HTTP server with:


    uvicorn main_http_server:app --port 8000 --reload

    It will start on http://127.0.0.1:8000.

*** ===> How to check the HTTP server: ***
    
    To request a unique number, open your browser or use curl to access:

    http://127.0.0.1:8000/random
    To explicitly request a float instead of an integer:

    http://127.0.0.1:8000/random?type=float
    You will receive a response like:

    {"number": 4837201, "shard": "int_shard_1.db"}
    or

    {"number": 839.347209, "shard": "float_shard_0.db"}

    If the shard is temporarily empty (all values used), the server returns:

    {"error": "No available numbers. Shard is being refilled. Please retry shortly."}
    and begins refilling that shard asynchronously in the background. Invalid routes like /hello return a 404, as per FastAPI defaults.


*** ===> Stress Test ***

python scalable_unique_random_http_server_fastapi_sharded/stress_test.py

This Python script performs a stress test on a FastAPI server by sending a specified number of concurrent HTTP GET requests to the /random endpoint (defaulting to 1600 requests using 4 threads), using a thread pool for parallel execution. Each request fetches a random number and expects a JSON response containing the shard, number, which are logged along with the request ID. The script handles timeouts and exceptions gracefully, prints each request outcome to the console in real time, and saves a complete log of all responses to a timestamped file. It’s designed to evaluate how the server performs under load, capturing both success and failure scenarios.


### Logic behind it:
Each shard stores a large precomputed pool of globally unique random numbers. When a request arrives, the server randomly selects one active shard for the requested type and pops a number from it by marking the used = 1 flag in the shard database. This avoids expensive real-time generation or duplicate checking during request time, enabling fast and scalable responses.
This design helps in minimizing request latency, supporting high throughput, and decoupling random number generation from request handling.
When a shard becomes empty (i.e., no more used = 0 numbers left), the system removes it from the active pool and asynchronously refills it. The refill logic generates a batch of random numbers, filters them against the persistent metadata DB to ensure global uniqueness, and populates the shard with fresh values (used = 0). The metadata DB acts as a global ledger, ensuring that no number is reused across time, reboots, or distributed instances.
The use of aiosqlite allows all database I/O to remain non-blocking and concurrent, supporting high scalability. Each shard operates independently, allowing the server to continue serving requests even while one or more shards are being refilled in the background.

### Benefits over previous code:
This system is designed to handle millions of requests efficiently. It does so by preloading a large number of globally unique random numbers—such as 10 million values distributed across multiple shards. The number of shards can be configured dynamically, for example, based on the number of CPU cores available. Half the shards can serve integers, and the other half can serve floats, ensuring balanced load and data type coverage.

When millions of requests hit the server concurrently, the architecture can handle them gracefully by simply popping preloaded numbers from the shards and marking them as used. This approach ensures constant-time access and minimal locking contention, which makes it ideal for high-concurrency environments.

If, during this process, it’s found that all numbers in a shard are used, the system automatically refills that shard in the background. Otherwise, shards can be periodically refilled to maintain the 10-million pool size, ensuring there's always a buffer of fresh values available for serving. This proactive refill mechanism prevents runtime exhaustion and prepares the system for sustained throughput.

By storing a preloaded pool of unique numbers and using simple atomic operations like pop-and-mark, the system achieves excellent concurrency handling and request throughput. It avoids on-the-fly computation, enabling low-latency responses even under extreme load. Persistent metadata tracking further guarantees that no number is ever reused, maintaining integrity across sessions and deployments.


