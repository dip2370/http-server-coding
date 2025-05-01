import asyncio
import os
from random_number_generator import RandomNumberGenerator
from db_utils import DatabaseUtils

# Configuration
NUM_SHARDS = 4
BATCH_SIZE = 1000
SHARD_DIR = "shards"
META_DIR = "meta"
INT_META_DB = os.path.join(META_DIR, "used_numbers_int.db")
FLOAT_META_DB = os.path.join(META_DIR, "used_numbers_float.db")


def ensure_directories():
    os.makedirs(SHARD_DIR, exist_ok=True)
    os.makedirs(META_DIR, exist_ok=True)


async def populate_shard(shard_idx: int, batch_size: int, meta_db_path: str, used_set: set):
    is_integer = shard_idx < 2
    shard_path = os.path.join(SHARD_DIR, f"shard_{shard_idx}.db")

    shard_db = DatabaseUtils(shard_path)
    meta_db = DatabaseUtils(meta_db_path, table_name="used_numbers")
    rng = RandomNumberGenerator()
    fresh_numbers = []

    if not await shard_db.table_exists():
        await shard_db.create_table()

    existing_count = await shard_db.count_rows()
    print(f"Shard {shard_idx} contains {existing_count} records. Appending {batch_size} new values.")

    while len(fresh_numbers) < batch_size:
        num = rng.generate_unique_integer() if is_integer else rng.generate_unique_float()
        if num not in used_set:
            used_set.add(num)
            fresh_numbers.append(num)

    await shard_db.insert_values(fresh_numbers)
    await meta_db.insert_values(fresh_numbers)

    print(f"Populated shard {shard_idx} with {len(fresh_numbers)} values.")


async def main():
    ensure_directories()

    int_meta = DatabaseUtils(INT_META_DB, "used_numbers")
    float_meta = DatabaseUtils(FLOAT_META_DB, "used_numbers")

    await int_meta.create_table(is_metadata=True)
    await float_meta.create_table(is_metadata=True)

    used_ints = await int_meta.fetch_all_values()
    used_floats = await float_meta.fetch_all_values()

    for shard_idx in range(NUM_SHARDS):
        if shard_idx < 2:
            await populate_shard(shard_idx, BATCH_SIZE, INT_META_DB, used_ints)
        else:
            await populate_shard(shard_idx, BATCH_SIZE, FLOAT_META_DB, used_floats)

    for shard_idx in range(NUM_SHARDS):
        shard_db = DatabaseUtils(os.path.join(SHARD_DIR, f"shard_{shard_idx}.db"))
        print(f"Shard {shard_idx} now has {await shard_db.count_rows()} entries.")

    print(f"Integer metadata count: {await int_meta.count_rows()}")
    print(f"Float metadata count: {await float_meta.count_rows()}")


if __name__ == "__main__":
    asyncio.run(main())
