import json
from pathlib import Path

def define_persistence_file_path(file_name: str) -> Path:
    """Define and return the persistence file path."""
    return Path(__file__).resolve().parent.parent / file_name

def load_used_numbers(file_path: Path) -> set:
    """Load used numbers from the persistence file."""
    if file_path.exists():
        try:
            with open(file_path, "r") as f:
                return set(json.load(f))
        except (FileNotFoundError, json.JSONDecodeError):
            return set()
    return set()

def save_used_numbers(file_path: Path, used_numbers: set):
    """Save used numbers to the persistence file."""
    try:
        with open(file_path, "w") as f:
            json.dump(list(used_numbers), f)
    except Exception as e:
        print(f"Error saving used numbers: {e}")