#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : test_cache_fully_associative.py
# License           : MIT license <Check LICENSE>
# Author            : Anderson I. da Silva (aignacio) <anderson@aignacio.com>
# Date              : 08.02.2025
# Last Modified Date: 24.02.2025
import logging
import random

from cache_performance_model import FullyAssociativeCache 
from cache_performance_model import ReplacementPolicy


# Test function 1: **Sequential Access Pattern (Low Spatial Locality)**
def sequential_access_pattern(cache, num_accesses):
    print("\nSequential Access Pattern:")
    for i in range(num_accesses):
        address = i * 4  # Simple pattern, accessing 4-byte blocks
        transaction_type = random.choice(["read", "write"])
        if transaction_type == "read":
            cache.read(address)
        else:
            cache.write(address)


# Test function 2: **Spatial Locality Access Pattern**
def spatial_locality_pattern(cache, num_accesses, stride=4):
    print("\nSpatial Locality Access Pattern:")
    base_address = 0
    for i in range(num_accesses):
        address = base_address + random.randint(0, stride - 1)  # Random nearby address
        transaction_type = random.choice(["read", "write"])
        if transaction_type == "read":
            cache.read(address)
        else:
            cache.write(address)
        base_address += stride  # Move base address forward by stride


def test_cache_comparison():
    caches = []

    num_accesses = 100
    seed = 42

    caches.append(
        FullyAssociativeCache(
            cache_size_kib=4, replacement_policy=ReplacementPolicy.LRU
        )
    )
    caches.append(
        FullyAssociativeCache(
            cache_size_kib=4, replacement_policy=ReplacementPolicy.FIFO
        )
    )

    access_patterns = [
        ("Sequential", sequential_access_pattern),
        ("Spatial Locality", spatial_locality_pattern),
    ]

    for cfg in caches:
        cfg.clear()
        for _ in range(2):
            for i in range(10):
                cfg.read(64*i)
        cfg.stats()

    # for pattern_name, pattern_func in access_patterns:
        # print(f"\n-------------------------------------------")
        # print(f"-------- {pattern_name.upper()} ---------")
        # print(f"-------------------------------------------")
        # for cfg in caches:
            # cfg.clear()
            # # Reset the random state before each test
            # random.seed(seed)
            # pattern_func(cfg, num_accesses)
            # random.seed(seed)
            # pattern_func(cfg, num_accesses)
            # cfg.stats()
