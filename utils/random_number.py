# utils/random_number.py

import random

class RandomNumberGenerator:
    def generate_random_number(self, is_float: bool = False) -> float:
        """
        Generate a random number.
        
        If is_float is False, return an 8-bit integer.
        If is_float is True, return a float rounded to 4 decimal places.
        """
        if is_float:
            return round(random.uniform(0, 10^8), 6)
        else:
            return random.getrandbits(32)