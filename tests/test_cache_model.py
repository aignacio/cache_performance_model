import pytest
import random
from cache_performance_model import (
    DirectMappedCache,
    SetAssociativeCache,
    FullyAssociativeCache,
    ReplacementPolicy,
)


def sequential_access_pattern(cache, num_accesses):
    for i in range(num_accesses):
        address = i * 4
        transaction_type = random.choice(["read", "write"])
        if transaction_type == "read":
            cache.read(address)
        else:
            cache.write(address)


def spatial_locality_pattern(cache, num_accesses, stride=4):
    base_address = 0
    for i in range(num_accesses):
        address = base_address + random.randint(0, stride - 1)
        transaction_type = random.choice(["read", "write"])
        if transaction_type == "read":
            cache.read(address)
        else:
            cache.write(address)
        base_address += stride


def temporal_locality_pattern(cache, num_accesses, repeat_factor=2, seed=42):
    random.seed(seed)
    accessed_addresses = set()
    random_values = [random.random() for _ in range(num_accesses)]
    address_choices = [random.randint(0, 4 * 1024) * 4 for _ in range(num_accesses)]
    transactions = [random.choice(["read", "write"]) for _ in range(num_accesses)]
    reuse_choices = [random.randint(0, num_accesses - 1) for _ in range(num_accesses)]
    for i in range(num_accesses):
        address = (
            address_choices[i]
            if random_values[i] >= 0.5 or not accessed_addresses
            else list(accessed_addresses)[reuse_choices[i] % len(accessed_addresses)]
        )
        accessed_addresses.add(address)
        if transactions[i] == "read":
            cache.read(address)
        else:
            cache.write(address)


def random_access_pattern(cache, num_accesses):
    for i in range(num_accesses):
        address = random.randint(0, 255) * 4
        transaction_type = random.choice(["read", "write"])
        if transaction_type == "read":
            cache.read(address)
        else:
            cache.write(address)


def strided_access_pattern(cache, num_accesses, stride=64):
    base_address = 0
    for i in range(num_accesses):
        address = base_address
        if random.choice(["read", "write"]) == "read":
            cache.read(address)
        else:
            cache.write(address)
        base_address += stride


def conflict_access_pattern(cache, num_accesses, stride=64):
    for i in range(num_accesses):
        address = i * (4 * 1024)
        if random.choice(["read", "write"]) == "read":
            cache.read(address)
        else:
            cache.write(address)


@pytest.mark.parametrize(
    "cache_config",
    [
        DirectMappedCache(cache_line_bytes=64),
        *[
            SetAssociativeCache(n_way=4, replacement_policy=rp)
            for rp in ReplacementPolicy
            if rp != ReplacementPolicy.NONE
        ],
        *[
            FullyAssociativeCache(replacement_policy=rp)
            for rp in ReplacementPolicy
            if rp != ReplacementPolicy.NONE
        ],
    ],
)
@pytest.mark.parametrize(
    "pattern_func",
    [
        sequential_access_pattern,
        spatial_locality_pattern,
        temporal_locality_pattern,
        random_access_pattern,
        strided_access_pattern,
        conflict_access_pattern,
    ],
)
def test_cache_behavior(cache_config, pattern_func):
    num_accesses = 100
    seed = 42
    cache_config.clear()
    random.seed(seed)
    pattern_func(cache_config, num_accesses)
    random.seed(seed)
    pattern_func(cache_config, num_accesses)
    cache_config.stats()
