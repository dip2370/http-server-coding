import random


class RandomNumberGenerator:

    @staticmethod
    def generate_unique_integer(bit_size: int = 32) -> int:
        return random.getrandbits(bit_size)

    @staticmethod
    def generate_unique_float(decimal_places: int = 4) -> float:
        return round(random.uniform(0, 1e4), decimal_places)