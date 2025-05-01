import asyncio
import os
import sys
from pathlib import Path
import argparse  # Import the argparse module

# Adjust path to import utils modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from utils.pooled_db_utils import DatabaseUtils
from utils.random_number import RandomNumberGenerator

# Configuration
NUM_SHARDS = 4
SHARD_DIR = str(PROJECT_ROOT / "shards")
META_DIR = str(PROJECT_ROOT / "meta")
INT_META_DB = os.path.join(META_DIR, "used_numbers_int.db")
FLOAT_META_DB = os.path.join(META_DIR, "used_numbers_float.db")

def ensure_directories():
    os.makedirs(SHARD_DIR, exist_ok=True)
    os.makedirs(META_DIR, exist_ok=True)

async def populate_shard(shard_idx: int, batch_size: int, meta_db_path: str, used_set: set, rng: RandomNumberGenerator):
    """Populate a shard with random numbers."""
    is_integer = shard_idx < 2
    shard_path = os.path.join(SHARD_DIR, f"shard_{shard_idx}.db")

    shard_db = DatabaseUtils(shard_path)
    meta_db = DatabaseUtils(meta_db_path, table_name="used_numbers")
    fresh_numbers = []

    if not await shard_db.table_exists():
        await shard_db.create_table()

    existing_count = await shard_db.count_rows()
    print(f"Shard {shard_idx} contains {existing_count} records. Appending {batch_size} new values.")

    attempt = 0
    while len(fresh_numbers) < batch_size and attempt < batch_size * 2: # Limit attempts
        num = rng.generate_random_number(is_float=is_integer)
        # Check against metadata db instead of local used_set
        if num not in await meta_db.fetch_all_values():
            used_set.add(num)  # Keep track locally for this batch
            fresh_numbers.append(num)
        else:
            print(f"Duplicate found in metadata for shard {shard_idx}: {num}")

        attempt += 1

    try:
        await shard_db.insert_values(fresh_numbers)
        await meta_db.insert_values(fresh_numbers)
        print(f"Populated shard {shard_idx} with {len(fresh_numbers)} values.")


    except Exception as e:
        print(f"Error populating shard {shard_idx}: {e}")

async def main(batch_size: int):  # Accept batch_size as an argument
    ensure_directories()
    rng = RandomNumberGenerator()

    int_meta = DatabaseUtils(INT_META_DB, "used_numbers")
    float_meta = DatabaseUtils(FLOAT_META_DB, "used_numbers")

    await int_meta.create_table(is_metadata=True)
    await float_meta.create_table(is_metadata=True)

    used_ints = await int_meta.fetch_all_values()
    used_floats = await float_meta.fetch_all_values()
    print(f"Initial Integer Metadata Count: {len(used_ints)}")
    print(f"Initial Float Metadata Count: {len(used_floats)}")


    # Refactor Shard population
    for shard_idx in range(NUM_SHARDS):
        if shard_idx < 2:
            await populate_shard(shard_idx, batch_size, INT_META_DB, used_ints, rng)
        else:
            await populate_shard(shard_idx, batch_size, FLOAT_META_DB, used_floats, rng)

    for shard_idx in range(NUM_SHARDS):
        shard_db_path = os.path.join(SHARD_DIR, f"shard_{shard_idx}.db")
        try:
            shard_db = DatabaseUtils(shard_db_path)
            count = await shard_db.count_rows()
            print(f"Shard {shard_idx} now has {count} entries.")
        except asyncio.TimeoutError:
            print(f"TimeoutError: Shard {shard_idx} took too long to count rows.")
        except Exception as e:
             print(f"Error counting rows in Shard {shard_idx}: {e}")


    print(f"Integer metadata count: {await int_meta.count_rows()}")
    print(f"Float metadata count: {await float_meta.count_rows()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize shards with random numbers.")
    parser.add_argument("--batch_size", type=int, default=1000, help="Number of random numbers per shard (default: 1000)")
    args = parser.parse_args()

    asyncio.run(main(args.batch_size))  # Pass the batch_size to main()