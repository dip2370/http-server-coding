import random
import json
from pathlib import Path

class UniqueRandomNumberGenerator:
    def __init__(self, min_num: int, max_num: int, used_numbers_file: Path):

        '''Initializes the UniqueRandomNumberGenerator instance with the range for random numbers
        and the file path where the used numbers will be stored.
        used_numbers_file (Path): The file where used numbers are saved.
        '''

        self.min_num = min_num
        self.max_num = max_num
        self.used_numbers_file = used_numbers_file
        self.used_numbers_list = [] # List to store used numbers in order of generation
        self.used_numbers_set = set() # Set for quick lookup of used numbers


        # If the file already exists, load previously used numbers from it

        if self.used_numbers_file.exists():
            with self.used_numbers_file.open("r") as f:
                try:
                    # Load the used numbers from the file
                    data = json.load(f)
                    self.used_numbers_list = data.get("used_numbers", [])
                    self.used_numbers_set = set(self.used_numbers_list)
                except json.JSONDecodeError:
                    # If the file is empty or corrupted, initialize empty list and set
                    self.used_numbers_list = []
                    self.used_numbers_set = set()

    def _save_used_numbers(self):
        '''Saves the current list of used numbers to the file. '''
        with self.used_numbers_file.open("w") as f:
            json.dump({"used_numbers": self.used_numbers_list}, f, indent=2)

    def generate(self) -> int:

        '''Generates a unique random number that has not been generated before. 
        If all possible numbers have been used, raises an exception.'''

        # If all numbers in the given range have been used, raise an exception
        if len(self.used_numbers_set) >= (self.max_num - self.min_num + 1):
            raise Exception("All possible numbers have been used.")

 
        # Keep trying to generate a number that hasn't been used
        while True:
            new_number = random.randint(self.min_num, self.max_num)
            print(new_number,"generated")
            if new_number not in self.used_numbers_set:
                self.used_numbers_set.add(new_number)
                self.used_numbers_list.append(new_number)
                self._save_used_numbers()
                return new_number # return the generated new number
            else:
                print("Newly generated number ",new_number, "is already geneated")
