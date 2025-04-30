import aiosqlite  # Asynchronous SQLite client for non-blocking DB operations
import asyncio     # Required for async sleep when retrying DB operations

class DatabaseHandler:
    """
    This class handles database operations for the random number generator app.
    It uses SQLite with async I/O for concurrent-friendly operations.
    """

    def __init__(self, db_file: str):
        # Initialize the handler with the path to the SQLite database file.
        
        self.db_file = db_file

    async def init_db(self):
        """
        Initializes the SQLite database:
        Sets Write-Ahead Logging (WAL) for better concurrency.
        Creates a table `random_numbers` to store unique numbers.
        """
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("PRAGMA journal_mode=WAL;")  # Enable WAL for concurrent read/write
            await db.execute("""
                CREATE TABLE IF NOT EXISTS random_numbers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    number REAL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await db.commit()

    async def insert_number(self, number, retries=3, delay=0.05) -> bool:
        """
        Tries to insert a number into the database with retry logic.
        
        Parameters:
        number: The random number (int or float) to insert.
        retries: Number of times to retry in case of a database lock.
        delay: Delay (in seconds) between retries.
        
        Returns:
        True if insertion was successful.
        False if it failed due to a duplicate (IntegrityError) or DB lock (OperationalError).
        """
        for attempt in range(retries):
            try:
                # Connect to the DB with a timeout to wait for locks to clear
                async with aiosqlite.connect(self.db_file, timeout=5.0) as db:
                    await db.execute("PRAGMA journal_mode=WAL;")
                    await db.execute("INSERT INTO random_numbers (number) VALUES (?);", (number,))
                    await db.commit()
                return True  # Successfully inserted
            except aiosqlite.IntegrityError:
                # Duplicate number — violates UNIQUE constraint
                return False
            except aiosqlite.OperationalError as e:
                # DB might be locked due to concurrency
                if "locked" in str(e).lower() and attempt < retries - 1:
                    await asyncio.sleep(delay)  # Wait before retrying
                    continue
                return False  # Failed after retries

    async def show_numbers(self):
        """
        Prints all rows from the `random_numbers` table.
        Useful for debugging or inspection during testing.
        """
        async with aiosqlite.connect(self.db_file) as db:
            cursor = await db.execute("SELECT * FROM random_numbers")
            rows = await cursor.fetchall()
            for row in rows:
                print(row)

# Standalone test functionality for this module
if __name__ == "__main__":
    import asyncio
    from int_float_random_utils import RandomNumberGenerator

    async def test():
        # Instantiate the database handler
        db_handler = DatabaseHandler("random_numbers.db")
        print("Initializing database...")
        await db_handler.init_db()

        # Generate a test number
        rng = RandomNumberGenerator()
        test_number = rng.generate_number(is_float=False)
        print("Inserting a test random number:", test_number)

        # Try to insert it into the DB
        if await db_handler.insert_number(test_number):
            print("Insertion successful!")
        else:
            print("Insertion failed (possible duplicate value).")

        # Show all stored numbers
        print("\nCurrent records in the database:")
        await db_handler.show_numbers()

    # Run the test function asynchronously
    asyncio.run(test())