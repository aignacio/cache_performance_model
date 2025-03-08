import pytest
import os
import random
from cache_performance_model import (
    DirectMappedCache,
    SetAssociativeCache,
    FullyAssociativeCache,
    ReplacementPolicy,
)

def test_benchmark():
    file_path = 'instruction_trace.txt'
    if not os.path.exists(file_path):
        print(f"File '{file_path}' does not exist.")
        return
    cache = SetAssociativeCache(n_way=4, replacement_policy=ReplacementPolicy.LRU)
    cache.ADDR_WIDTH = 64
    cache.clear()
    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split(",")

            if parts[0] == "read":
                address = parts[1]
                cache.read(int(address, 16))
            elif parts[0] == "write":
                address = parts[1]
                cache.write(int(address, 16))
    cache.stats()
