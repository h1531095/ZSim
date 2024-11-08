import random
import time

MAX_SIGNED_INT64 = 2 ** 63 - 1


class RNG:
    def __init__(self, seed: int = int(time.time())):
        self.seed, self.r = self.generate_random_number(seed)

    @staticmethod
    def generate_random_number(seed: int) -> tuple[int, int]:
        random.seed(seed)
        random_number = random.randint(a=-MAX_SIGNED_INT64, b=MAX_SIGNED_INT64)
        return seed, random_number