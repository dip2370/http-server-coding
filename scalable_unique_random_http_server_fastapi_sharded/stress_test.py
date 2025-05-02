"""
Stress test script for FastAPI server.
Simulates high traffic by sending concurrent requests and logs outcomes.
"""

import requests
import concurrent.futures
import time
import argparse
from datetime import datetime

# FastAPI endpoint to test
URL = "http://127.0.0.1:8585/random"

# Default concurrency (adjust to CPU cores or system capability)
DEFAULT_CONCURRENCY = 4

def fetch(request_id):
    try:
        response = requests.get(URL, timeout=100)
        if response.status_code == 200:
            data = response.json()
            return (
                f"[{request_id}] ✅ SUCCESS | "
                f"Shard: {data.get('shard')} | "
                f"Value: {data.get('number')} | "
                f"Refill: {data.get('refill_status', 'N/A')}"
            )
        else:
            detail = response.json().get("detail", response.text)
            return f"[{request_id}] ❌ FAIL | Status: {response.status_code} | Detail: {detail}"
    except requests.exceptions.Timeout:
        return f"[{request_id}] ⚠️ TIMEOUT"
    except Exception as e:
        return f"[{request_id}] 🚨 EXCEPTION | {str(e)}"

def main(num_requests, concurrency):
    print(f"🚀 Starting load test with {num_requests} requests using {concurrency} threads...\n")
    start_time = time.time()

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {executor.submit(fetch, i): i for i in range(num_requests)}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            print(result)
            results.append(result)

    duration = time.time() - start_time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"stress_log_{timestamp}.txt"

    with open(log_filename, "w") as log_file:
        log_file.write("\n".join(results))

    print(f"\n✅ Load test completed in {duration:.2f} seconds.")
    print(f"📝 Results saved to {log_filename}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Stress test the FastAPI server.")
    parser.add_argument("--num_requests", type=int, default=1600, help="Total number of requests to send (default: 1600)")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY, help="Number of concurrent threads (default: 4)")
    args = parser.parse_args()

    main(args.num_requests, args.concurrency)
