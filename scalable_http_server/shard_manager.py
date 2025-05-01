import asyncio
from random_number_generator import RandomNumberGenerator
from db_utils import DatabaseUtils
import aiosqlite


class ShardManager:
    """
    Responsible for managing shards and ensuring global randomness.
    """

    def __init__(self, shard_ids: list[int], meta_db_file: str):
        self.shard_ids = shard_ids  # IDs of shards to manage
        self.meta_db_file = meta_db_file  # Metadata DB to ensure global uniqueness

    async def refill_shard(self, shard_idx: int, batch_size: int):
        """
        Refill a shard with unique random numbers.

        Args:
            shard_idx (int): ID of the shard to refill.
            batch_size (int): Number of random numbers to generate.
        """
        shard_db = f"shards/shard_{shard_idx}.db"
        db_handler = DatabaseUtils(shard_db)
        rng = RandomNumberGenerator()

        # Generate batch of unique numbers
        fresh_numbers = []
        while len(fresh_numbers) < batch_size:
            print("refilling=====>",shard_db)
            number = rng.generate_unique_integer() if shard_idx < 2 else rng.generate_unique_float()
            if not await self.is_unique(number):
                continue
            fresh_numbers.append(number)

        await db_handler.insert_numbers(fresh_numbers)

    async def is_unique(self, number: float) -> bool:
        """
        Verify whether a random number is globally unique using metadata.

        Args:
            number (float): Random number to verify.

        Returns:
            bool: True if it's unique, False otherwise.
        """
        async with aiosqlite.connect(self.meta_db_file) as conn:
            cursor = await conn.execute(
                "SELECT 1 FROM used_numbers WHERE value = ?", (number,)
            )
            if await cursor.fetchone():  # Found, not unique
                return False
            await conn.execute("INSERT INTO used_numbers (value) VALUES (?)", (number,))
            await conn.commit()
            return True