import random

class RandomGenerator:
    def __init__(self, min_num: int, max_num: int):
        self.min_num = min_num
        self.max_num = max_num

    def generate(self) -> int:
        """
        Generate a unique random number between min_num and max_num.        
        """
        new_number = random.randint(self.min_num, self.max_num)
        return new_number

def main():
    generator = RandomGenerator(100, 100000)    
    
    for _ in range(5):
        num = generator.generate()
        print("Generated unique number:", num)

if __name__ == "__main__":
    main()
