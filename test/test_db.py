import sqlite3
import time
import argparse

def get_all_values(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    return cursor.fetchall()

def insert_values(conn, target_table, data):
    if not data:
        return 0.0

    cursor = conn.cursor()
    placeholders = ",".join(["?"] * len(data[0]))
    insert_query = f"INSERT INTO {target_table} VALUES ({placeholders})"

    start_time = time.time()
    cursor.executemany(insert_query, data)
    conn.commit()
    elapsed = time.time() - start_time

    return elapsed

def create_target_table(conn, source_table, target_table):
    cursor = conn.cursor()
    # Creates an empty copy of the source table schema
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {target_table} AS SELECT * FROM {source_table} WHERE 0")
    conn.commit()

def main():
    parser = argparse.ArgumentParser(description="Extract all values from a SQLite table and time their insertion into another table.")
    parser.add_argument("--db", type=str, required=True, help="Path to the SQLite database")
    parser.add_argument("--table", type=str, required=True, help="Source table name")
    args = parser.parse_args()

    db_path = args.db
    source_table = args.table
    #target_table = f"{source_table}_copy"

    with sqlite3.connect(db_path) as conn:
        data = get_all_values(conn, source_table)
        for row in data:
            print(row)
        
        print(f"Fetched {len(data)} rows from '{source_table}'.")

if __name__ == "__main__":
    main()
