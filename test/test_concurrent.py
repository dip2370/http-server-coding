import urllib.request       # For making HTTP requests
import urllib.parse         # For URL encoding query parameters
import concurrent.futures   # To run requests concurrently using threads
import random               # For randomly choosing between "int" and "float"
import json                 # To parse JSON response from the server

# Base URL of the FastAPI random number generator service
BASE_URL = "http://127.0.0.1:5000/random"

def make_request(req_type):
    """
    Makes a GET request to the /random endpoint with the specified type ('int' or 'float').

    Args:
        req_type (str): The type of number to request ("int" or "float").
    """
    try:
        # Encode the type as a query string (e.g., ?type=int)
        query_string = urllib.parse.urlencode({"type": req_type})
        url = f"{BASE_URL}?{query_string}"

        # Send the request and read the response
        with urllib.request.urlopen(url, timeout=5) as response:
            data = response.read()
            result = json.loads(data)  # Parse JSON response
            print(f"{req_type.upper()} -> {result}")  # Log the result
    except Exception as e:
        # Handle any errors (timeout, connection, parse failure, etc.)
        print(f"{req_type.upper()} -> Request failed: {e}")

def run_concurrent_requests(n_requests=100):
    """
    Executes multiple random number requests concurrently.

    Args:
        n_requests (int): Total number of requests to send.
    """
    # Generate a list of random types ("int" or "float") for each request
    types = [random.choice(["int", "float"]) for _ in range(n_requests)]

    # Use a thread pool to send requests concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        # Map each type in the list to a thread running make_request
        executor.map(make_request, types)

if __name__ == "__main__":
    # Run the test with default 100 requests
    run_concurrent_requests()
