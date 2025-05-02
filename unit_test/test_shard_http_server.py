import os
import pytest
import asyncio
import random
from fastapi.testclient import TestClient
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from main_http_server import app, ACTIVE_INT_SHARDS, ACTIVE_FLOAT_SHARDS, NUM_SHARDS, SHARD_DIR, DatabaseUtils

# ----------------------------------------------------------------------
# Fixtures to control the environment for testing
# ----------------------------------------------------------------------

@pytest.fixture(autouse=True)
def fake_os_path_exists(monkeypatch):
    """
    Override os.path.exists to always return True so that the startup event
    (which checks for shard file existence) passes unless we explicitly want to fail.
    """
    monkeypatch.setattr(os.path, "exists", lambda path: True)

@pytest.fixture(autouse=True)
def reset_active_shards():
    """
    Reset the global active shards before each test.
    """
    ACTIVE_INT_SHARDS.clear()
    ACTIVE_INT_SHARDS.extend([0, 1])
    ACTIVE_FLOAT_SHARDS.clear()
    ACTIVE_FLOAT_SHARDS.extend([2, 3])
    yield
    # (Post-test cleanup, if needed, can be done here.)

# ----------------------------------------------------------------------
# Tests for the /random endpoint behavior
# ----------------------------------------------------------------------

def test_random_endpoint_success(monkeypatch):
    """
    Test that when the DB returns a valid number (pop_random_number returns 42)
    the endpoint returns a 200 response with the expected shard and number.
    """
    async def fake_pop_success(self):
        return 42

    # Patch the pop_random_number method to always return a valid number.
    monkeypatch.setattr(DatabaseUtils, "pop_random_number", fake_pop_success)
    # Force random.choice to always select shard 0.
    monkeypatch.setattr(random, "choice", lambda seq: 0)

    client = TestClient(app)
    response = client.get("/random")
    assert response.status_code == 200
    data = response.json()
    expected_shard = os.path.join(SHARD_DIR, "shard_0.db")
    assert data == {"shard": expected_shard, "number": 42}

def test_random_endpoint_empty_shard(monkeypatch):
    """
    Test that when a shard’s pop_random_number method returns None (empty shard)
    the endpoint returns a 503 error.
    """
    async def fake_pop_none(self):
        return None

    # Patch to simulate an empty shard.
    monkeypatch.setattr(DatabaseUtils, "pop_random_number", fake_pop_none)
    # Force random.choice to always select shard 0.
    monkeypatch.setattr(random, "choice", lambda seq: 0)

    client = TestClient(app)
    response = client.get("/random")
    # Since the shard returns no number, the endpoint must raise a 503.
    assert response.status_code == 503
    data = response.json()
    # Expected error message should indicate that shard 0 is empty.
    assert "Shard 0 is empty." in data["detail"]

def test_random_endpoint_no_active_shards(monkeypatch):
    """
    Test that if no active shards are available the endpoint immediately
    returns a 503 error with an appropriate detail message.
    """
    # Clear both integer and float active shard lists.
    ACTIVE_INT_SHARDS.clear()
    ACTIVE_FLOAT_SHARDS.clear()

    client = TestClient(app)
    response = client.get("/random")
    assert response.status_code == 503
    data = response.json()
    assert data["detail"] == "All shards are being refilled."

# ----------------------------------------------------------------------
# Tests for application startup and shutdown events
# ----------------------------------------------------------------------

def test_startup_event_failure(monkeypatch):
    """
    Test that the startup event fails if a shard file is missing.
    We simulate a missing shard by overriding os.path.exists.
    """
    def fake_exists(path):
        # Simulate that shard_0.db is missing.
        if "shard_0.db" in path:
            return False
        return True

    monkeypatch.setattr(os.path, "exists", fake_exists)

    with pytest.raises(RuntimeError) as excinfo:
        asyncio.run(app.state.on_startup())
    assert "Missing shard" in str(excinfo.value)
    assert "shard_0.db" in str(excinfo.value)

def test_shutdown_event(capsys):
    """
    Test that the shutdown event prints the expected shutdown message.
    """
    asyncio.run(app.state.on_shutdown())
    captured = capsys.readouterr().out
    assert "Server is shutting down..." in captured