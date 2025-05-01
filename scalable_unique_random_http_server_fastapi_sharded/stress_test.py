"""
This script is designed to stress-test the FastAPI server.
It simulates heavy client traffic by sending a large number of concurrent requests and logs the results.
"""

import requests
import concurrent.futures  # Used for creating a thread pool to simulate concurrent users
import time
import argparse  # Import the argparse module

# API endpoint to be tested
URL = "http://127.0.0.1:8080/random"

# Number of concurrent threads to use
CONCURRENCY = 4  # Typically set to the number of CPU cores for maximum parallelism

def fetch(request_id):
    try:
        response = requests.get(URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return f"{request_id}: SUCCESS | Shard: {data['shard']} | Value: {data['number']}"
        else:
            # Log the error status and body (if JSON or text)
            try:
                error_detail = response.json().get("detail", response.text)
            except Exception:
                error_detail = response.text
            return f"{request_id}: FAIL | Status: {response.status_code} | Detail: {error_detail}"
    except Exception as e:
        return f"{request_id}: EXCEPTION | {str(e)}"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Stress test the FastAPI server.")
    parser.add_argument("--num_requests", type=int, default=16000, help="Total number of requests to send (default: 16000)")
    args = parser.parse_args()

    start_time = time.time()
    print(f"Starting load test with {args.num_requests} requests across {CONCURRENCY} threads...")

    # Use a ThreadPoolExecutor to simulate concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        # Map each request to a worker thread
        results = list(executor.map(fetch, range(args.num_requests)))

    # Write the results to a log file for post-test analysis
    with open("stress_log.txt", "w") as log_file:
        log_file.write("\n".join(results))

    total_time = time.time() - start_time
    print(f"Finished load test in {total_time:.2f} seconds.")
    print("Results saved to stress_log.txt")