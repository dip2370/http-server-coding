# This code test the Utility Files #

import asyncio
import random
import aiosqlite
import pytest
import sys
from pathlib import Path
# Add the parent directory to the sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Importing our utility classes.
from utils.db_utils import DatabaseHandler            # From your first utils file
from utils.pooled_db_utils import DatabaseUtils     # From pooled_db_utils.py
from utils.random_number import RandomNumberGenerator  # From random_numbers.py


# Fixture to provide a temporary database file path.
@pytest.fixture
def db_file(tmp_path):
    return str(tmp_path / "test_database.db")


###############################
# Tests for DatabaseHandler
###############################
class TestDatabaseHandler:
    @pytest.mark.asyncio
    async def test_init_db_and_table_creation(self, db_file):
        db_handler = DatabaseHandler(db_file)
        await db_handler.init_db()

        # Verify that the 'random_numbers' table is created.
        async with aiosqlite.connect(db_file) as conn:
            cursor = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='random_numbers';"
            )
            table = await cursor.fetchone()
            assert table is not None, "random_numbers table should exist after init_db()"

    @pytest.mark.asyncio
    async def test_insert_number_and_duplicate(self, db_file):
        db_handler = DatabaseHandler(db_file)
        await db_handler.init_db()

        test_number = 42  # Using a fixed number for testing
        # First insertion should succeed.
        result_first = await db_handler.insert_number(test_number)
        assert result_first is True, "First insertion should succeed"

        # Second insertion (duplicate) should fail because of UNIQUE constraint.
        result_duplicate = await db_handler.insert_number(test_number)
        assert result_duplicate is False, "Duplicate insertion should return False"


###############################
# Tests for DatabaseUtils
###############################
class TestDatabaseUtils:
    @pytest.mark.asyncio
    async def test_table_creation_and_existence(self, db_file):
        db_utils = DatabaseUtils(db_file)
        exists_before = await db_utils.table_exists()
        assert not exists_before, "Table should not exist initially"

        await db_utils.create_table()
        exists_after = await db_utils.table_exists()
        assert exists_after, "Table should exist after create_table()"

    @pytest.mark.asyncio
    async def test_insert_and_fetch_values(self, db_file):
        db_utils = DatabaseUtils(db_file)
        await db_utils.create_table()

        values_to_insert = [1.1, 2.2, 3.3]
        await db_utils.insert_values(values_to_insert)

        fetched_values = await db_utils.fetch_all_values()
        assert fetched_values == set(values_to_insert), "Fetched values should match inserted values"

        row_count = await db_utils.count_rows()
        assert row_count == len(values_to_insert), f"There should be {len(values_to_insert)} rows in the table"

    @pytest.mark.asyncio
    async def test_pop_random_number(self, db_file):
        db_utils = DatabaseUtils(db_file)
        await db_utils.create_table()

        # Insert a few numbers into the pool.
        numbers = [10.0, 20.0, 30.0]
        await db_utils.insert_values(numbers)

        popped_values = set()
        # Repeatedly pop until no number is available.
        for _ in range(len(numbers)):
            num = await db_utils.pop_random_number()
            assert num in numbers, "Popped number should be one of the inserted values"
            popped_values.add(num)

        # Once all numbers are used, the pop should return None.
        no_more = await db_utils.pop_random_number()
        assert no_more is None, "pop_random_number should return None when no values remain"

        # Verify that all inserted numbers were popped.
        assert popped_values == set(numbers), "All inserted numbers should have been popped"


###############################
# Tests for RandomNumberGenerator
###############################
class TestRandomNumberGenerator:
    def test_generate_integer(self):
        rng = RandomNumberGenerator()
        number = rng.generate_random_number(is_float=False)
        assert isinstance(number, int), "When is_float=False, the generated number should be an integer"

    def test_generate_float(self):
        rng = RandomNumberGenerator()
        number = rng.generate_random_number(is_float=True)
        assert isinstance(number, float), "When is_float=True, the generated number should be a float"
        # Verify rounding: the function rounds to 6 decimal places.
        assert round(number, 6) == number, "Float should be rounded to 6 decimal places"