import asyncio
from db_utils import DatabaseUtils

async def count_rows_in_database(db_file: str, table_name: str = "number_pool") -> int:
#async def count_rows_in_database(db_file: str, table_name: str = "used_numbers") -> int:
    db = DatabaseUtils(db_file, table_name)
    return await db.count_rows()

# Example usage
if __name__ == "__main__":
    async def main():
        db_file ="shards/shard_0.db"
        #db_file ="meta/used_numbers_int.db"  #"shards/shard_0.db"
        count = await count_rows_in_database(db_file)
        print(f"Number of rows in {db_file}: {count}")

    asyncio.run(main())
