import random
import time
from functools import lru_cache
import sys

MAX_SIGNED_INT64 = 2 ** 63 - 1


class RNG:
    def __init__(self, seed: int = None):
        main_module = sys.modules['__main__']
        tick: int = getattr(main_module, 'tick', 0)
        if seed is None:
            seed = int(time.time() * 1000000) + tick
        else:
            seed = int(seed) + tick
        (self.seed, self.r) = self.generate_random_number(seed)

    @staticmethod
    @lru_cache(maxsize=4)
    def generate_random_number(seed: int) -> tuple[int, int]:
        random.seed(seed)
        random_number = random.randint(a=-MAX_SIGNED_INT64, b=MAX_SIGNED_INT64)
        return seed, random_number