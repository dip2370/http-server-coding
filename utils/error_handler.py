# utils/error_handler.py

from fastapi import HTTPException

def handle_exception(e):
    """
    Handle exceptions and return an HTTPException with status code 503.

    Parameters:
    - e: The exception to handle.

    Returns:
    - An HTTPException instance.
    """
    return HTTPException(status_code=503, detail=str(e))