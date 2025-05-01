# utils/response_utils.py

import json

def construct_response(data=None, error=None):
    """
    Construct a JSON response.

    Parameters:
    - data: The data to include in the response (e.g., the generated number).
    - error: The error message to include in the response.

    Returns:
    - A JSON-encoded string.
    """
    if error:
        response = {"error": error}
    else:
        response = {"number": data}
    return json.dumps(response)