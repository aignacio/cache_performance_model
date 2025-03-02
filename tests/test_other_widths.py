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


@pytest.mark.parametrize("addr_width", [2**i for i in range(3,7)])
def test_other_widths(addr_width):
    num_accesses = 100
    seed = 42
    DirectMappedCache.ADDR_WIDTH = addr_width
    cache_config = DirectMappedCache(cache_line_bytes=64)
    cache_config.clear()
    random.seed(seed)
    sequential_access_pattern(cache_config, num_accesses)
    random.seed(seed)
    sequential_access_pattern(cache_config, num_accesses)
    cache_config.stats()
