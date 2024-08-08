import math
import mmh3
import pickle

from bitarray import bitarray
from multiprocessing import Array, Lock


class BloomFilter:
    def __init__(self, size: int, num_hashes: int):
        self.size = size
        self.num_hashes = num_hashes
        self.lock = Lock()
        self.shared_array = Array("b", size)
        self.bit_array = bitarray(size)
        self.bit_array.setall(0)
        self.bit_array.frombytes(self.shared_array.get_obj())

    def add(self, item: str):
        with self.lock:
            for i in range(self.num_hashes):
                digest = mmh3.hash(item, i) % self.size
                self.bit_array[digest] = True

    def __contains__(self, item: str) -> bool:
        with self.lock:
            for i in range(self.num_hashes):
                digest = mmh3.hash(item, i) % self.size
                if not self.bit_array[digest]:
                    return False
            return True

    def save(self, filename: str):
        with self.lock:
            with open(filename, "wb") as f:
                pickle.dump((self.size, self.num_hashes, self.bit_array), f)

    @classmethod
    def load(cls, filename: str):
        with open(filename, "rb") as f:
            size, num_hashes, bit_array = pickle.load(f)
            bloom_filter = cls(size, num_hashes)
            bloom_filter.bit_array = bit_array
            return bloom_filter

    @classmethod
    def new(cls, num_elements: int, false_pos: float) -> "BloomFilter":
        size, num_hashes = optimal_size(num_elements, false_pos)
        return cls(size, num_hashes)


def optimal_size(n: int, p: float) -> tuple[int, int]:
    """
    Calculate the optimal size and number of hash functions for the Bloom filter.

    Args:
        n (int): Expected number of elements.
        p (float): Desired false positive probability.

    Returns:
        tuple[int, int]: The optimal size and number of hash functions.
    """
    size = -(n * math.log(p)) / (math.log(2) ** 2)
    num_hashes = (size / n) * math.log(2)
    return int(size), int(num_hashes)
