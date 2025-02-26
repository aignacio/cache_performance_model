[![Lint > Tests > Publish](https://github.com/aignacio/cache_performance_model/actions/workflows/run.yaml/badge.svg)](https://github.com/aignacio/cache_performance_model/actions/workflows/run.yaml) [![codecov](https://codecov.io/gh/aignacio/cache_performance_model/branch/master/graph/badge.svg?token=4THWKTDMYH)](https://codecov.io/gh/aignacio/cache_performance_model) [![Documentation](https://github.com/aignacio/cache_performance_model/actions/workflows/sphinx.yaml/badge.svg)](https://aignacio.com/cache_performance_model/)

# Cache Performance Model

This project provides a model for simulating cache performance, including different cache configurations and replacement policies.

```bash
pip install cache-performance-model
```

## Classes

### Cache

`Cache` is an abstract base class for different cache models. It provides common functionality and properties for cache simulation.

### DirectMappedCache

`DirectMappedCache` is a class for simulating a direct-mapped cache. It inherits from `Cache` and implements the read and write methods.

### SetAssociativeCache

`SetAssociativeCache` is a class for simulating a set-associative cache. It inherits from `Cache` and implements the read and write methods. It supports different replacement policies such as RANDOM, FIFO, LRU, NMRU, and PLRU.

### FullyAssociativeCache

`FullyAssociativeCache` is a class for simulating a fully associative cache. It inherits from `Cache` and implements the read and write methods. It supports different replacement policies such as RANDOM, FIFO, LRU, NMRU, and PLRU.

## Examples

### Direct Mapped Cache

```python
from cache_performance_model.cache_model import DirectMappedCache

# Create a direct-mapped cache instance
cache = DirectMappedCache(cache_line_bytes=64, cache_size_kib=4)

# Perform read and write operations
cache.read(0x1A2B3C4D)
cache.write(0x1A2B3C4D)

# Print cache statistics
cache.stats()
```

### Set Associative Cache

```python
from cache_performance_model.cache_model import SetAssociativeCache
from cache_performance_model.types import ReplacementPolicy

# Create a set-associative cache instance with LRU replacement policy
cache = SetAssociativeCache(cache_line_bytes=64, cache_size_kib=4, n_way=4, replacement_policy=ReplacementPolicy.LRU)

# Perform read and write operations
cache.read(0x1A2B3C4D)
cache.write(0x1A2B3C4D)

# Print cache statistics
cache.stats()
```

### Fully Associative Cache

```python
from cache_performance_model.cache_model import FullyAssociativeCache
from cache_performance_model.types import ReplacementPolicy

# Create a fully associative cache instance with RANDOM replacement policy
cache = FullyAssociativeCache(cache_line_bytes=64, cache_size_kib=4, replacement_policy=ReplacementPolicy.RANDOM)

# Perform read and write operations
cache.read(0x1A2B3C4D)
cache.write(0x1A2B3C4D)

# Print cache statistics
cache.stats()
```

## Installation

To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

## Documentation

To build the documentation, run:

```bash
nox -s docs
```

The HTML pages will be in `docs/_build/html`.
