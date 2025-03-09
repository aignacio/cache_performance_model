import pytest
import os
import random
from cache_performance_model import (
    Cache,
    DirectMappedCache,
    SetAssociativeCache,
    FullyAssociativeCache,
    ReplacementPolicy,
)

Cache.ADDR_WIDTH = 64


@pytest.mark.parametrize(
    "cache",
    [
        DirectMappedCache(),
        *[
            SetAssociativeCache(n_way=2, replacement_policy=ReplacementPolicy.LRU),
            SetAssociativeCache(n_way=4, replacement_policy=ReplacementPolicy.LRU),
            SetAssociativeCache(n_way=8, replacement_policy=ReplacementPolicy.LRU),
            SetAssociativeCache(n_way=16, replacement_policy=ReplacementPolicy.LRU),
        ],
    ],
)
def test_benchmark(cache):
    # bench_type = "memory"
    bench_type = "instruction"
    file_path = bench_type + "_trace.txt"

    results_file = "cache_stats_results_" + bench_type + ".txt"

    if not os.path.exists(file_path):
        print(f"File '{file_path}' does not exist.")
        return

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

    # Get stats and print them as before
    stats = cache.stats()

    # Append results to file
    with open(results_file, "a") as f:
        cache_type = type(cache).__name__
        if cache_type == "SetAssociativeCache":
            cache_desc = f"{cache_type}(n_way={cache.n_way}, policy={cache.replacement_policy.name})"
        else:
            cache_desc = cache_type

        f.write(f"Cache: {cache_desc}\n")
        f.write(f"Stats: {stats}\n")
        f.write("-" * 50 + "\n")
