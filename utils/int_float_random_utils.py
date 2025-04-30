import random

class RandomNumberGenerator:
    def generate_number(self, is_float: bool = False) -> float:
        """
        Generate a random number.
        
         If is_float is False, return a 32-bit integer.
         If is_float is True, return a float rounded to 6 decimal places.
        """
        if is_float:
            return round(random.uniform(0, 1e4), 4)
        else:
            return random.getrandbits(8)

def main():
    print("Testing RandomNumberGenerator.generate_number:")
    rng = RandomNumberGenerator()
    print("Random Integer:", rng.generate_number(is_float=False))
    print("Random Float:", rng.generate_number(is_float=True))

if __name__ == "__main__":
    main()