#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : test_cache_model.py
# License           : MIT license <Check LICENSE>
# Author            : Anderson I. da Silva (aignacio) <anderson@aignacio.com>
# Date              : 08.02.2025
# Last Modified Date: 18.02.2025
import logging
import random

from cache_performance_model import DirectMappedCache, SetAssociativeCache
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


# Test function 3: **Temporal Locality Access Pattern**
def temporal_locality_pattern(cache, num_accesses, repeat_factor=2, seed=42):
    print("\nTemporal Locality Access Pattern:")
    accessed_addresses = set()
    # Pre-generate all random values
    random.seed(seed)  # Set a fixed seed to ensure reproducibility
    random_values = [random.random() for _ in range(num_accesses)]
    address_choices = [random.randint(0, 4 * 1024) * 4 for _ in range(num_accesses)]
    transactions = [random.choice(["read", "write"]) for _ in range(num_accesses)]
    reuse_choices = [
        random.randint(0, num_accesses - 1) for _ in range(num_accesses)
    ]  # Precompute reuse indices

    for i in range(num_accesses):
        if random_values[i] < 0.5 and accessed_addresses:
            address_list = list(accessed_addresses)
            address = address_list[
                reuse_choices[i] % len(address_list)
            ]  # Select from precomputed reuse index
        else:
            address = address_choices[i]
            accessed_addresses.add(address)

        if transactions[i] == "read":
            cache.read(address)
        else:
            cache.write(address)


# Test function 4: **Random Access Pattern**
def random_access_pattern(cache, num_accesses):
    print("\nRandom Access Pattern:")
    for i in range(num_accesses):
        address = random.randint(0, 255) * 4  # Random address in range
        transaction_type = random.choice(["read", "write"])
        if transaction_type == "read":
            cache.read(address)
        else:
            cache.write(address)


# Test function 5: **Strided Access Pattern**
def strided_access_pattern(cache, num_accesses, stride=64):
    print("\nStrided Access Pattern:")
    base_address = 0
    transaction_type = [random.choice(["read", "write"]) for _ in range(num_accesses)]
    for i in range(num_accesses):
        address = base_address
        # transaction_type = random.choice(['read', 'write'])
        if transaction_type[i] == "read":
            cache.read(address)
        else:
            cache.write(address)
        base_address += stride  # Move by stride each time


# Test function 5: **Strided Access Pattern**
def conflict_access_pattern(cache, num_accesses, stride=64):
    print("\nConflict Access Pattern:")
    base_address = 0
    transaction_type = [random.choice(["read", "write"]) for _ in range(num_accesses)]
    for i in range(num_accesses):
        address = base_address + i * (4 * 1024)
        # transaction_type = random.choice(['read', 'write'])
        if transaction_type[i] == "read":
            cache.read(address)
        else:
            cache.write(address)


def test_cache_comparison():
    caches = []

    num_accesses = 200
    seed = 42

    caches.append(DirectMappedCache(cache_line_bytes=64))
    caches.append(
        SetAssociativeCache(
            n_way=4, cache_size_kib=4, replacement_policy=ReplacementPolicy.RANDOM
        )
    )
    caches.append(
        SetAssociativeCache(
            n_way=4, cache_size_kib=4, replacement_policy=ReplacementPolicy.LRU
        )
    )
    caches.append(
        SetAssociativeCache(
            n_way=4, cache_size_kib=4, replacement_policy=ReplacementPolicy.NMRU
        )
    )
    caches.append(
        SetAssociativeCache(
            n_way=4, cache_size_kib=4, replacement_policy=ReplacementPolicy.FIFO
        )
    )
    caches.append(
        SetAssociativeCache(
            n_way=4, cache_size_kib=4, replacement_policy=ReplacementPolicy.PLRU
        )
    )


    access_patterns = [
        ("Sequential", sequential_access_pattern),
        ("Spatial Locality", spatial_locality_pattern),
        ("Temporal Locality", temporal_locality_pattern),
        ("Random", random_access_pattern),
        ("Strided", strided_access_pattern),
        ("Conflict", conflict_access_pattern),
    ]

    for pattern_name, pattern_func in access_patterns:
        print(f"\n-------------------------------------------")
        print(f"-------- {pattern_name.upper()} ---------")
        print(f"-------------------------------------------")
        for cfg in caches:
            cfg.clear()
            # Reset the random state before each test
            random.seed(seed)
            pattern_func(cfg, num_accesses)
            random.seed(seed)
            pattern_func(cfg, num_accesses)
            cfg.stats()
