from fastapi import FastAPI, HTTPException
import asyncio
import os
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from utils.pooled_db_utils import DatabaseUtils
from utils.random_number import RandomNumberGenerator
from initialize_shards import populate_shard

app = FastAPI()

NUM_SHARDS = 4
REFILL_THRESHOLD = 100
REFILL_BATCH_SIZE = 100

SHARD_DIR = str(PROJECT_ROOT / "shards")
META_DIR = str(PROJECT_ROOT / "meta")
INT_META_DB = os.path.join(META_DIR, "used_numbers_int.db")
FLOAT_META_DB = os.path.join(META_DIR, "used_numbers_float.db")

ACTIVE_INT_SHARDS = [0, 1]
ACTIVE_FLOAT_SHARDS = [2, 3]
REQUEST_COUNTER = 0
REFILL_LOCK = asyncio.Lock()
REFILL_INDEX = 0

@app.on_event("startup")
async def on_startup():
    for shard_idx in range(NUM_SHARDS):
        shard_path = os.path.join(SHARD_DIR, f"shard_{shard_idx}.db")
        if not os.path.exists(shard_path):
            raise RuntimeError(f"Missing shard: {shard_path}")

@app.get("/random")
async def get_random():
    global REQUEST_COUNTER, REFILL_INDEX
    active_shards = ACTIVE_INT_SHARDS + ACTIVE_FLOAT_SHARDS
    if not active_shards:
        raise HTTPException(status_code=503, detail="All shards are being refilled")

    shard_idx = random.choice(active_shards)
    shard_path = os.path.join(SHARD_DIR, f"shard_{shard_idx}.db")
    db = DatabaseUtils(shard_path)
    number = await db.pop_random_number()
    
    if number is None:
        raise HTTPException(status_code=503, detail=f"Shard {shard_idx} is empty.")

    REQUEST_COUNTER += 1

    # Trigger refill logic
    if REQUEST_COUNTER >= REFILL_THRESHOLD:
        async with REFILL_LOCK:
            if REQUEST_COUNTER >= REFILL_THRESHOLD:  # Double-check inside lock
                await refill_one_shard()
                REQUEST_COUNTER = 0

    return {"shard": shard_idx, "number": number}

async def refill_one_shard():
    global REFILL_INDEX
    shard_idx = REFILL_INDEX % NUM_SHARDS
    REFILL_INDEX += 1

    print(f"Refilling shard {shard_idx}...")

    if shard_idx < 2:
        ACTIVE_INT_SHARDS.remove(shard_idx)
        meta = INT_META_DB
    else:
        ACTIVE_FLOAT_SHARDS.remove(shard_idx)
        meta = FLOAT_META_DB

    rng = RandomNumberGenerator()
    await populate_shard(shard_idx, REFILL_BATCH_SIZE, meta, rng)

    # Reactivate shard
    if shard_idx < 2:
        ACTIVE_INT_SHARDS.append(shard_idx)
    else:
        ACTIVE_FLOAT_SHARDS.append(shard_idx)

    print(f"Shard {shard_idx} refilled and reactivated.")
