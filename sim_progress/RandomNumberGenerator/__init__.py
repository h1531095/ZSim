import random
import time
from functools import lru_cache
import sys
import numpy as np


MAX_SIGNED_INT64: int = 2 ** 63 - 1


class RNG:
    def __init__(self, seed: int | None = None):
        self.seed: int | None = None
        self.r: int | None = None
        self.reseed(seed)

    def get_seed(self) -> int:
        assert self.seed is not None
        return self.seed

    def reseed(self, new_seed: int | None = None):
        main_module = sys.modules['__main__']
        tick: int = getattr(main_module, 'tick', 0)
        if new_seed is None:
            new_seed = int(time.time() * 1000000) + tick
        else:
            new_seed = int(new_seed) + tick
        (self.seed, self.r) = self.generate_random_number(new_seed)

    def random_float(self) -> float:
        random.seed(self.seed)
        return random.uniform(0.0, 1.0)

    @staticmethod
    @lru_cache(maxsize=4)
    def generate_random_number(seed: int) -> tuple[int, int]:
        random.seed(seed)
        random_number = random.randint(a=-MAX_SIGNED_INT64, b=MAX_SIGNED_INT64)
        return seed, random_number
    
    def generate_and_judge(self, possibility: float) -> bool:
        self.seed, self.r = self.generate_random_number(self.seed)
        return np.abs(self.r) < possibility * MAX_SIGNED_INT64


class SingletonRNG:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SingletonRNG, cls).__new__(cls)
        return cls._instance

    def __init__(self, expected_probability: float, *, max_iteration: int = 100):
        if not hasattr(self, 'initialized'):
            self.initialized: bool = True
            assert 0 <= expected_probability <= 1, 'Expected probability必须在0和1之间'
            self.expected_probability: float = expected_probability
            self.max_iteration: int = max_iteration
            self.true_count: int = int(expected_probability * max_iteration)
            self.false_count: int = max_iteration - self.true_count
            self.current_probability: float = self.true_count / max_iteration

    def get_random(self) -> bool:
        if self.true_count == 0:
            return False
        if self.false_count == 0:
            return True

        if random.random() < self.current_probability:
            self.true_count -= 1
            self.current_probability = self.true_count / (self.true_count + self.false_count)
            return True
        else:
            self.false_count -= 1
            self.current_probability = self.true_count / (self.true_count + self.false_count)
            return False


if __name__ == '__main__':
    # 使用示例
    rng = SingletonRNG(0.5)
    total = 10000
    true_count = 0
    for _ in range(total):
        true_count += rng.get_random()
    print(true_count / total)