import asyncio
import os
from pathlib import Path
import sys

# Adjust path to import utils modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from utils.random_number import RandomNumberGenerator  # Updated import
from utils.pooled_db_utils import DatabaseUtils
import aiosqlite

class ShardManager:
    """
    Responsible for managing shards and ensuring global randomness.
    """

    def __init__(self, shard_ids: list[int], meta_db_file: str, shard_dir: str):
        self.shard_ids = shard_ids  # IDs of shards to manage
        self.meta_db_file = meta_db_file  # Metadata DB to ensure global uniqueness
        self.shard_dir = shard_dir # Shard directory path

    async def refill_shard(self, shard_idx: int, batch_size: int):
        """
        Refill a shard with unique random numbers.
        """
        shard_db_path = os.path.join(self.shard_dir, f"shard_{shard_idx}.db")
        db_handler = DatabaseUtils(shard_db_path)
        rng = RandomNumberGenerator()

        fresh_numbers = []
        attempts = 0
        while len(fresh_numbers) < batch_size and attempts < batch_size * 10:  # Limit attempts
            number = rng.generate_random_number(is_float=shard_idx < 2)
            is_unique_val = await self.is_unique(number)
            if is_unique_val:
                fresh_numbers.append(number)
            else:
                print(f"Number {number} is not unique. Attempt {attempts + 1}")
            attempts += 1

        if fresh_numbers:
            try:
                await db_handler.insert_values(fresh_numbers)
                print(f"Successfully refilled shard {shard_idx} with {len(fresh_numbers)} numbers.")
            except Exception as e:
                print(f"Error inserting numbers into shard {shard_idx}: {e}")
        else:
            print(f"Could not generate enough unique numbers for shard {shard_idx} after {attempts} attempts.")


    async def is_unique(self, number: float) -> bool:
        """
        Verify whether a random number is globally unique using metadata.
        """
        try:
            async with aiosqlite.connect(self.meta_db_file) as conn:
                async with conn.execute("SELECT 1 FROM used_numbers WHERE value = ?", (number,)) as cursor:
                    if await cursor.fetchone():  # Found, not unique
                        return False
                    await conn.execute("INSERT INTO used_numbers (value) VALUES (?)", (number,))
                    await conn.commit()
                    return True
        except Exception as e:
            print(f"Database error in is_unique: {e}")
            return False  # Treat DB errors as not unique to prevent crashes