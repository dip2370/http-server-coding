

import asyncio
import pytest
from fastapi.testclient import TestClient

# Import the FastAPI app and its global db_handler and rng instances.
from main_http_server import app, db_handler, rng

# Define async helper stubs that simulate insert_number outcomes.
async def always_true(_):
    return True

async def always_false(_):
    return False

def test_get_random_number_int(monkeypatch):
    """
    Test that a GET request to /random with type=int returns an integer.
    Here we patch the random number generator to return a fixed integer,
    and patch the DB insertion to always succeed.
    """
    # Monkeypatch the random number generator to return a fixed int value.
    monkeypatch.setattr(
        rng,
        "generate_random_number",
        lambda is_float: 123456789 if not is_float else 123.456789
    )
    # Patch the database insertion to always succeed (simulate a unique number insertion).
    monkeypatch.setattr(db_handler, "insert_number", always_true)
    
    client = TestClient(app)
    response = client.get("/random?type=int")
    assert response.status_code == 200
    data = response.json()
    assert "number" in data
    # Verify that the number is an integer and matches our mock value.
    assert isinstance(data["number"], int)
    assert data["number"] == 123456789

def test_get_random_number_float(monkeypatch):
    """
    Test that a GET request to /random with type=float returns a float.
    We patch the random number generator to return a predictable float,
    and patch the insert_number to always succeed.
    """
    # Return a fixed number: integer for default and float when is_float is True.
    monkeypatch.setattr(
        rng,
        "generate_random_number",
        lambda is_float: 123456789 if not is_float else 123.456789
    )
    monkeypatch.setattr(db_handler, "insert_number", always_true)
    
    client = TestClient(app)
    response = client.get("/random?type=float")
    assert response.status_code == 200
    data = response.json()
    assert "number" in data
    # Verify that the returned value is a float and matches our expected value.
    assert isinstance(data["number"], float)
    assert data["number"] == 123.456789

def test_get_random_number_failure(monkeypatch):
    """
    Test that if the insertion of the generated number always fails,
    after MAX_ATTEMPTS the API returns a 503 error.
    """
    # Patch insert_number so that it always returns False (simulate duplicate failure).
    monkeypatch.setattr(db_handler, "insert_number", always_false)
    
    client = TestClient(app)
    response = client.get("/random?type=int")
    # Since no number is inserted after MAX_ATTEMPTS, we expect a 503 Service Unavailable.
    assert response.status_code == 503
    data = response.json()
    assert data["detail"] == "Could not generate unique random number after retries."