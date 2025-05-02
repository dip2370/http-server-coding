"""
Main HTTP server to expose the `/random` API endpoint.
This server handles requests for globally unique random numbers,
manages shard selection dynamically, and ensures scalability through
asynchronous shard refilling and number serving.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
import random
import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from utils.pooled_db_utils import DatabaseUtils  # Updated import
from shard_manager import ShardManager

# Initialize FastAPI app
app = FastAPI()

# Configuration
NUM_SHARDS = 4  # Total number of shards
BATCH_SIZE = 1000  # Number of random numbers to populate during refill
SHARD_DIR = str(PROJECT_ROOT / "shards")  # Shard directory at the parent level
META_DIR = str(PROJECT_ROOT / "meta")  # Meta directory at the parent level
INT_META_DB = os.path.join(META_DIR, "used_numbers_int.db")
FLOAT_META_DB = os.path.join(META_DIR, "used_numbers_float.db")

# Separate shard lists for integers and floats
ACTIVE_INT_SHARDS = [0, 1]
ACTIVE_FLOAT_SHARDS = [2, 3]

# Shard Managers for integers and floats
int_shard_manager = ShardManager(ACTIVE_INT_SHARDS, INT_META_DB, SHARD_DIR)
float_shard_manager = ShardManager(ACTIVE_FLOAT_SHARDS, FLOAT_META_DB, SHARD_DIR)

@app.get("/random")
async def random_number_endpoint(background_tasks: BackgroundTasks):
    active_shards = ACTIVE_INT_SHARDS + ACTIVE_FLOAT_SHARDS
    if not active_shards:
        raise HTTPException(
            status_code=503,
            detail="No shards are available. System refill is in progress."
        )

    selected_shard = random.choice(active_shards)
    shard_db = os.path.join(SHARD_DIR, f"shard_{selected_shard}.db")  # Use SHARD_DIR
    db_handler = DatabaseUtils(shard_db)

    number = await db_handler.pop_random_number()
    if number is not None:
        return {"shard": shard_db, "number": number}

    # --- Shard is empty ---
    print(f"503: Shard {selected_shard} is empty. Refilling now...")

    if selected_shard in ACTIVE_INT_SHARDS:
        ACTIVE_INT_SHARDS.remove(selected_shard)
        background_tasks.add_task(int_shard_manager.refill_shard, selected_shard, BATCH_SIZE)
    elif selected_shard in ACTIVE_FLOAT_SHARDS:
        ACTIVE_FLOAT_SHARDS.remove(selected_shard)
        background_tasks.add_task(float_shard_manager.refill_shard, selected_shard, BATCH_SIZE)

    raise HTTPException(
        status_code=503,
        detail=f"Shard {selected_shard} is empty. Refilling, try again later."
    )

@app.on_event("startup")
async def startup_event():
    """
    Validate shard databases and prepare for runtime use.
    Do not prepopulate here as it is handled by `initialize_shards.py`.
    """
    for shard_idx in range(NUM_SHARDS):
        shard_db = os.path.join(SHARD_DIR, f"shard_{shard_idx}.db")  # Use SHARD_DIR
        if not os.path.exists(shard_db):
            raise RuntimeError(f"Shard {shard_db} is missing. Run `initialize_shards.py` first.")

    print("Server startup complete. Shard databases validated.")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Handle any cleanup tasks on shutdown. Currently, no specific logic is needed.
    """
    print("Server is shutting down...")