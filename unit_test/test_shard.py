import os
import asyncio
import pytest
from pathlib import Path

import sys
from pathlib import Path
# Add the parent directory to the sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import the functions and constants from your shard population module.

from scalable_unique_random_http_server_fastapi_sharded.initialize_shards import (
    ensure_directories,
    populate_shard,
    main,
    NUM_SHARDS,
    SHARD_DIR,
    META_DIR,
    INT_META_DB,
    FLOAT_META_DB,
)

from utils.pooled_db_utils import DatabaseUtils

# Define a Fake RNG for predictable behavior.
class FakeRNG:
    def __init__(self):
        self.counter = 0

    def generate_random_number(self, is_float: bool):
        self.counter += 1
        # Return a float (with a decimal) if is_float is True; otherwise an integer.
        if is_float:
            return float(self.counter) + 0.1
        else:
            return self.counter

def test_ensure_directories(tmp_path, monkeypatch):
    """
    Test that ensure_directories() creates the expected directories.
    """
    # Create temporary directories for shards and metadata.
    fake_shard_dir = tmp_path / "test_shards"
    fake_meta_dir = tmp_path / "test_meta"
    # Override the global paths in the module.
    monkeypatch.setattr(shard_population, "SHARD_DIR", str(fake_shard_dir))
    monkeypatch.setattr(shard_population, "META_DIR", str(fake_meta_dir))
    
    # Call ensure_directories.
    ensure_directories()
    
    # Assert that the directories exist.
    assert fake_shard_dir.exists() and fake_shard_dir.is_dir()
    assert fake_meta_dir.exists() and fake_meta_dir.is_dir()


@pytest.mark.asyncio
async def test_populate_shard(tmp_path, monkeypatch):
    """
    Test the populate_shard() function with a small batch size and a fake RNG.
    """
    # Create a temporary directory for shard databases.
    fake_shard_dir = tmp_path / "shards"
    fake_shard_dir.mkdir()
    # Use a temporary file for the meta database.
    meta_db_path = str(tmp_path / "meta_int.db")
    
    # Override the global SHARD_DIR in the module.
    monkeypatch.setattr(shard_population, "SHARD_DIR", str(fake_shard_dir))
    
    # Pre-create the meta table (using is_metadata=True).
    meta_db = DatabaseUtils(meta_db_path, table_name="used_numbers")
    await meta_db.create_table(is_metadata=True)
    
    # Instantiate our FakeRNG.
    fake_rng = FakeRNG() 
    used_set = set()
    
    # Call populate_shard() for shard 0 with a batch size of 3.
    await populate_shard(shard_idx=0, batch_size=3, meta_db_path=meta_db_path, used_set=used_set, rng=fake_rng)
    
    # Check that the shard database was created with 3 entries.
    shard_path = os.path.join(str(fake_shard_dir), "shard_0.db")
    shard_db = DatabaseUtils(shard_path)
    count_shard = await shard_db.count_rows()
    assert count_shard == 3, f"Expected 3 rows in shard db, got {count_shard}"
    
    # Check that the meta database now contains 3 entries.
    count_meta = await meta_db.count_rows()
    assert count_meta == 3, f"Expected 3 rows in meta db, got {count_meta}"
    
    # Also, our local used_set should have 3 unique numbers.
    assert len(used_set) == 3


@pytest.mark.asyncio
async def test_main(monkeypatch, tmp_path):
    """
    Test the main() function. We override the global directory paths and
    the RandomNumberGenerator so that the shard and meta databases are
    created in a temporary location and use predictable random numbers.
    """
    # Create temporary directories.
    fake_shard_dir = tmp_path / "shards"
    fake_meta_dir = tmp_path / "meta"
    fake_shard_dir.mkdir()
    fake_meta_dir.mkdir()
    
    # Define new meta database file paths.
    int_meta_db = os.path.join(str(fake_meta_dir), "used_numbers_int.db")
    float_meta_db = os.path.join(str(fake_meta_dir), "used_numbers_float.db")
    
    # Override the global directory and database file paths.
    monkeypatch.setattr(shard_population, "SHARD_DIR", str(fake_shard_dir))
    monkeypatch.setattr(shard_population, "META_DIR", str(fake_meta_dir))
    monkeypatch.setattr(shard_population, "INT_META_DB", int_meta_db)
    monkeypatch.setattr(shard_population, "FLOAT_META_DB", float_meta_db)
    
    # Override RandomNumberGenerator to use our FakeRNG.
    fake_rng = FakeRNG()
    monkeypatch.setattr(shard_population, "RandomNumberGenerator", lambda: fake_rng)
    
    # Run the main() function with a small batch size, e.g., 3.
    await main(batch_size=3)
    
    # Verify that each shard database has 3 entries.
    for shard_idx in range(NUM_SHARDS):
        shard_db_path = os.path.join(str(fake_shard_dir), f"shard_{shard_idx}.db")
        db_utils = DatabaseUtils(shard_db_path)
        count = await db_utils.count_rows()
        assert count == 3, f"Shard {shard_idx} should have 3 entries, got {count}"
        
    # Check the metadata databases.
    # For shards with indices 0 and 1, their values go into INT_META_DB.
    int_meta_utils = DatabaseUtils(int_meta_db, table_name="used_numbers")
    # For shards with indices 2 and 3, their values go into FLOAT_META_DB.
    float_meta_utils = DatabaseUtils(float_meta_db, table_name="used_numbers")
    int_meta_count = await int_meta_utils.count_rows()
    float_meta_count = await float_meta_utils.count_rows()
    
    # Since we have 2 shards for each meta DB and each shard adds 3 unique values,
    # the expected count is 6.
    assert int_meta_count == 6, f"INT meta should have 6 entries, got {int_meta_count}"
    assert float_meta_count == 6, f"FLOAT meta should have 6 entries, got {float_meta_count}"