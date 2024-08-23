import math
import mmh3
import pickle

from bitarray import bitarray
from multiprocessing import Array, Lock
from postit.files import FileClient

# TODO: Update class to save and load from a different file format


class BloomFilter:
    """
    A probabilistic data structure to check set membership.
    Utilizes multiple hash functions to map elements to an array of bits.
    Each bit represents the presence or absence of an element.
    Due to the probabilistic nature of bloom filters, there is a small chance of false positives.

    Implemented to be thread-safe.
    """

    def __init__(self, size: int, num_hashes: int):
        self.size = size
        self.num_hashes = num_hashes
        self.lock = Lock()
        self.shared_array = Array("b", size)
        self.bit_array = bitarray(size)
        self.bit_array.setall(0)
        self.bit_array.frombytes(self.shared_array.get_obj())

    def add(self, item: str):
        """
        Hashes the item multiple times and sets the corresponding bits to True.
        """
        with self.lock:
            for i in range(self.num_hashes):
                digest = mmh3.hash(item, i) % self.size
                self.bit_array[digest] = True

    def __contains__(self, item: str) -> bool:
        """
        Check for membership by hashing the item multiple times and checking the corresponding bits.
        """
        with self.lock:
            for i in range(self.num_hashes):
                digest = mmh3.hash(item, i) % self.size
                if not self.bit_array[digest]:
                    return False
            return True

    def save(self, filename: str):
        """
        Save the bloom filter to a pickle file.
        """
        with self.lock:
            file_client = FileClient.get_for_target(filename)
            with file_client.open(filename, "wb") as f:
                pickle.dump((self.size, self.num_hashes, self.bit_array), f)

    @classmethod
    def load(cls, filename: str):
        """
        Load a bloom filter from a pickle file.
        """
        file_client = FileClient.get_for_target(filename)
        with file_client.open(filename, "rb") as f:
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
    Utility to calculate BloomFilter parameters.
    Used to use memory efficiently while minimizing false positives.

    Args:
        n (int): # of elements.
        p (float): False positive rate.

    Returns:
        tuple[int, int]: Size of the bloom filter and number of hashes.
    """
    size = -(n * math.log(p)) / (math.log(2) ** 2)
    num_hashes = (size / n) * math.log(2)
    return int(size), int(num_hashes)
