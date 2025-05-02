import asyncio
import os
import sys
from pathlib import Path

# Adjust path for local imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from utils.pooled_db_utils import DatabaseUtils
from utils.random_number import RandomNumberGenerator

NUM_SHARDS = 4
SHARD_DIR = str(PROJECT_ROOT / "shards")
META_DIR = str(PROJECT_ROOT / "meta")
INT_META_DB = os.path.join(META_DIR, "used_numbers_int.db")
FLOAT_META_DB = os.path.join(META_DIR, "used_numbers_float.db")
INITIAL_FILL_SIZE = 5000

def ensure_directories():
    os.makedirs(SHARD_DIR, exist_ok=True)
    os.makedirs(META_DIR, exist_ok=True)

async def populate_shard(shard_idx: int, count: int, meta_db_path: str, rng: RandomNumberGenerator):
    is_integer = shard_idx < 2
    shard_path = os.path.join(SHARD_DIR, f"shard_{shard_idx}.db")

    shard_db = DatabaseUtils(shard_path)
    meta_db = DatabaseUtils(meta_db_path, "used_numbers")
    await shard_db.create_table()
    await meta_db.create_table(is_metadata=True)

    fresh_numbers = set()
    existing = set(await meta_db.fetch_all_values())

    while len(fresh_numbers) < count:
        num = rng.generate_random_number(is_float=not is_integer)
        if num not in existing and num not in fresh_numbers:
            fresh_numbers.add(num)

    await shard_db.insert_values(list(fresh_numbers))
    await meta_db.insert_values(list(fresh_numbers))
    print(f"Shard {shard_idx} populated with {len(fresh_numbers)} values.")

async def main():
    ensure_directories()
    rng = RandomNumberGenerator()

    for shard_idx in range(NUM_SHARDS):
        if shard_idx < 2:
            await populate_shard(shard_idx, INITIAL_FILL_SIZE, INT_META_DB, rng)
        else:
            await populate_shard(shard_idx, INITIAL_FILL_SIZE, FLOAT_META_DB, rng)

if __name__ == "__main__":
    asyncio.run(main())
