Unique Random Number HTTP API Server
This project provides a set of Python server implementations to generate globally unique random numbers (both integers and floats) via an HTTP API endpoint, always returning a JSON response. There are four progressive implementations included, each demonstrating a different architectural approach to the problem.

1. Simple HTTP Server
A synchronous HTTP server that serves unique random numbers at the /random endpoint. It uses a local JSON file (used_numbers.json) to persist previously served numbers, ensuring uniqueness across sessions. Supports an optional type=float query parameter to return floats.

How to Run:


python simple_unique_random_http_server/main_http_server.py
Starts the server on http://localhost:5000.

Check HTTP Server:

http://localhost:5000/random

http://localhost:5000/random?type=float

Logic:
Each request checks whether the client wants an integer or float. It tries up to 100 times to generate a number not found in the JSON-based store. If successful, the number is added to the store and returned. If not, a 503 error is returned. Unrecognized paths return a 404.



2. Unique Random Number HTTP Server Using FastAPI (Synchronous, File-Based Persistence)

Description:
A FastAPI-based version of the above server with the same logic and file-based persistence, but improved structure, validation, and maintainability. Responses and API behaviors are defined using FastAPI's features.

How to Run:


cd simple_unique_random_http_server_fastapi
uvicorn main_http_server:app --port 8000 --reload
Check HTTP Server:

http://127.0.0.1:8000/random

http://127.0.0.1:8000/random?type=float

Logic:
Same as version 1: generates a number, checks for uniqueness in a JSON file, and returns it. The use of FastAPI allows for cleaner code and better scalability options.

Benefits over previous code:
Cleaner structure, easier extensibility, and built-in support for validation and documentation.



3. Async Unique Random Number HTTP Server Using FastAPI and SQLite
What it does:
This implementation builds a high-performance, production-ready HTTP API server using FastAPI in combination with SQLite and asynchronous I/O via aiosqlite. The server exposes a /random endpoint that returns a globally unique random number, either an integer or a float based on the type query parameter. Internally, it persists all generated numbers in a SQLite database with a unique constraint, ensuring no duplication across requests or restarts. As it leverages non-blocking asynchronous database operations, this version is well-suited for handling concurrent requests efficiently while preserving global uniqueness guarantees.

How to run:
Navigate to the async_unique_random_http_server_fastapi_sqlite directory and start the server with:


uvicorn main_http_server:app --port 5000 --reload
Alternatively, if you're executing the script directly, it includes a main() function, so you can also run it like this:


python main_http_server.py
This will start the FastAPI app on http://127.0.0.1:5000.

How to check the HTTP server:
To check the server’s response, simply open your browser or use a tool like curl and visit:

arduino
Copy
Edit
http://127.0.0.1:5000/random
To get a float instead of an integer, append the query parameter like this:


http://127.0.0.1:5000/random?type=float
You’ll receive a JSON response such as {"number": 928374} or {"number": 3482.712345}. If the server cannot generate a unique number after several retries, it responds with a 503 error. Unknown routes like /hello will return a 404 by default via FastAPI’s routing system.

Logic behind it:
Upon startup, the FastAPI app initializes the SQLite database with a random_numbers table if it doesn't already exist. The database uses WAL (Write-Ahead Logging) mode to enable better concurrency. When a request hits the /random endpoint, the app determines the required number type (int or float) and attempts up to MAX_ATTEMPTS (100) to generate a number that can be inserted into the database. The insertion is handled by the DatabaseHandler class, which uses aiosqlite for async DB operations. If a generated number violates the UNIQUE constraint or the DB is momentarily locked, it retries with a short delay using asyncio. Only if all attempts fail does the API return a 503 error. Successfully inserted numbers are stored persistently, guaranteeing global uniqueness across time and concurrent requests.

Benefits over previous code:
This implementation offers significant improvements over both the basic synchronous HTTP server and the synchronous FastAPI variant. Firstly, the use of SQLite as a backing store for persistence is more robust and scalable than a flat JSON file, especially as the dataset grows. Secondly, the use of asynchronous I/O with FastAPI and aiosqlite enables the server to handle many simultaneous requests without blocking on file or database locks. This means better performance under load, fewer race conditions, and improved concurrency handling. The retry logic for inserts and use of WAL mode further enhance database responsiveness. Overall, this version is the most production-ready, scalable, and concurrent-friendly of the three.


4. Scalable Unique Random Number Server with Sharded SQLite and Persistent Metadata

What it does:
This implementation builds a fully asynchronous, scalable HTTP API server using FastAPI and SQLite to serve globally unique random numbers, leveraging a sharded architecture and persistent metadata tracking. The /random endpoint returns either a unique integer or a float, depending on the optional type query parameter (int by default). The backend comprises four shard databases (int_shard_0.db, int_shard_1.db, float_shard_0.db, float_shard_1.db) and two persistent metadata databases (used_numbers_int.db, used_numbers_float.db). The metadata DBs track all numbers ever served, ensuring global uniqueness across time and restarts. When a shard is depleted, the system triggers an async refill task that fetches globally unique numbers from the metadata check, refills the shard, and makes it available again. This ensures continuous, non-redundant service even under high demand or restarts.

How to run:

Initialize the shards and metadata databases using:


python initialize_shards.py
This script fills each shard with a set of random numbers (integers or floats) while ensuring that none have been served before, as checked against the metadata databases.

Start the HTTP server with:


uvicorn main_http_server:app --port 8000 --reload
Alternatively, the server script includes a main() method, so you can also run:


python main_http_server.py
The FastAPI app will start on http://127.0.0.1:8000.

How to check the HTTP server:
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

Logic behind it:
Each request randomly selects one of two shards for the requested data type (int or float). It attempts to fetch and mark one unused number (used = 0) from the shard. If successful, the number is returned and also inserted into the corresponding metadata DB to record it as globally used. If the shard has no available numbers, an async task is launched to refill it. The refill logic generates new random numbers in batches, checks each against the metadata DB (to enforce global uniqueness), and inserts only novel values into the shard database with used = 0. This decouples request servicing from refill logic, avoiding latency spikes during heavy loads. The use of aiosqlite ensures all database I/O is non-blocking, allowing high concurrency. Each shard database is independent, and each metadata DB is a persistent global ledger of all numbers ever served.

Benefits over previous code:
This architecture is the most complete, scalable, and restart-safe version so far. Earlier implementations either used single files or relied on per-shard uniqueness without persistence. This version introduces persistent global tracking via metadata databases, solving the problem of duplication across reboots or concurrent deployments. Unlike the earlier in-memory or shard-local-only solutions, this ensures every number served is globally unique, regardless of server restarts, crashes, or distributed operation. Furthermore, the decoupled async refill mechanism allows the server to handle requests gracefully even under resource exhaustion, queuing up fresh numbers in the background without blocking ongoing API traffic. In essence, it combines the robustness of persistent storage, the scalability of sharding, and the performance of asynchronous I/O, making it a production-grade system for serving unique random numbers at scale.