import pytest
import random
from cache_performance_model import (
    DirectMappedCache,
)


def sequential_access_pattern(cache, num_accesses):
    for i in range(num_accesses):
        address = (
            i * 4
            if i * 4 < 2**cache.ADDR_WIDTH
            else random.randint(0, 2**cache.ADDR_WIDTH)
        )
        transaction_type = random.choice(["read", "write"])
        if transaction_type == "read":
            cache.read(address)
        else:
            cache.write(address)


@pytest.mark.parametrize("cache_config", [DirectMappedCache(cache_line_bytes=64)])
@pytest.mark.parametrize("pattern_func", [sequential_access_pattern])
@pytest.mark.parametrize("addr_width", [8, 16, 32, 64])
def test_cache_behavior(cache_config, pattern_func, addr_width):
    cache_config.ADDR_WIDTH = addr_width
    num_accesses = 100
    seed = 42
    cache_config.clear()
    random.seed(seed)
    pattern_func(cache_config, num_accesses)
    random.seed(seed)
    pattern_func(cache_config, num_accesses)
    cache_config.stats()
