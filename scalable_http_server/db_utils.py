import aiosqlite
import os
from typing import List, Optional


class DatabaseUtils:
    def __init__(self, db_file: str, table_name: str = "number_pool"):
        self.db_file = db_file
        self.table_name = table_name

    async def table_exists(self) -> bool:
        async with aiosqlite.connect(self.db_file) as conn:
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
            cursor = await conn.execute(query, (self.table_name,))
            return await cursor.fetchone() is not None

    async def create_table(self, is_metadata: bool = False):
        async with aiosqlite.connect(self.db_file) as conn:
            await conn.execute("PRAGMA journal_mode=WAL;")
            if is_metadata:
                await conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        value REAL UNIQUE
                    );
                """)
            else:
                await conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        value REAL UNIQUE,
                        used INTEGER DEFAULT 0
                    );
                """)
            await conn.commit()

    async def insert_values(self, values: List[float]):
        async with aiosqlite.connect(self.db_file) as conn:
            await conn.executemany(
                f"INSERT OR IGNORE INTO {self.table_name} (value) VALUES (?)",
                [(v,) for v in values]
            )
            await conn.commit()

    async def fetch_all_values(self) -> set:
        async with aiosqlite.connect(self.db_file) as conn:
            cursor = await conn.execute(f"SELECT value FROM {self.table_name}")
            rows = await cursor.fetchall()
            return {row[0] for row in rows}

    async def count_rows(self) -> int:
        async with aiosqlite.connect(self.db_file) as conn:
            cursor = await conn.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            return (await cursor.fetchone())[0]

    '''async def pop_random_number(self) -> Optional[float]:
        async with aiosqlite.connect(self.db_file) as conn:
            cursor = await conn.execute(
                f"SELECT value FROM {self.table_name} WHERE used = 0 LIMIT 1"
            )
            row = await cursor.fetchone()
            if row:
                value = row[0]
                await conn.execute(f"DELETE FROM {self.table_name} WHERE value = ?", (value,))
                await conn.commit()
                return value
            return None'''

    async def pop_random_number(self):
        """
        Fetch a random number from the shard, ensuring that it is removed
        from the available pool once selected.
        """
        async with aiosqlite.connect(self.db_file) as conn:
            cursor = await conn.execute(
                f"SELECT value FROM {self.table_name} WHERE used = 0 ORDER BY RANDOM() LIMIT 1"
            )
            row = await cursor.fetchone()

            if row:
                number = row[0]
                # Mark the number as used
                await conn.execute(
                    f"UPDATE {self.table_name} SET used = 1 WHERE value = ?", (number,)
                )
                await conn.commit()
                return number
            else:
                return None

