Design of cache-performance-model
=================================

The `cache-performance-model` package is designed to model and analyze the performance of different cache architectures. The package includes the following main components:

1. **Types**: Enumerations and exceptions used throughout the package.
2. **Cache Models**: Abstract base class and specific implementations for different cache architectures.

Types
-----

The `types` module defines enumerations for cache access types and replacement policies, as well as custom exceptions.

- `AccessType`: Enumeration for cache access types (HIT, MISS).
  
  Example:
  .. code-block:: python

      from cache_performance_model.types import AccessType

      access = AccessType.HIT
      print(access)  # Output: AccessType.HIT

- `ReplacementPolicy`: Enumeration for cache replacement policies (NONE, RANDOM, FIFO, LRU, NMRU, PLRU).
  
  Example:
  .. code-block:: python

      from cache_performance_model.types import ReplacementPolicy

      policy = ReplacementPolicy.LRU
      print(policy)  # Output: ReplacementPolicy.LRU

- `CacheUnexpectedCaller`: Exception raised when hit/miss is not coming from read/write methods.
  
  Example:
  .. code-block:: python

      from cache_performance_model.types import CacheUnexpectedCaller

      try:
          raise CacheUnexpectedCaller()
      except CacheUnexpectedCaller as e:
          print(e)  # Output: Hit/Miss needs to be called from read or write methods

- `CacheIllegalParameter`: Exception raised when an illegal parameter is set.
  
  Example:
  .. code-block:: python

      from cache_performance_model.types import CacheIllegalParameter

      try:
          raise CacheIllegalParameter("n_way")
      except CacheIllegalParameter as e:
          print(e)  # Output: Parameter n_way value is illegal

- `Total`: Class to keep track of total read and write operations.
  
  Example:
  .. code-block:: python

      from cache_performance_model.types import Total

      total = Total()
      total.read = 5
      total.write = 3
      print(total.sum)  # Output: 8

- `Miss`: Class to keep track of different types of cache misses.
  
  Example:
  .. code-block:: python

      from cache_performance_model.types import Miss

      miss = Miss()
      miss.conflict = 2
      miss.capacity = 1
      miss.compulsory = 3
      print(miss.sum)  # Output: 6

Cache Models
------------

The ` module defines the abstract base class `Cache` and specific implementations for different cache architectures.

- `Cache`: Abstract base class for cache models. Defines common properties and methods for all cache types.
  
  Example:
  .. code-block:: python

      from cache_performance_model import Cache

      class MyCache(Cache):
          def read(self, addr: int):
              pass

          def write(self, addr: int):
              pass

          def clear(self):
              pass

- `DirectMappedCache`: Class for Direct Mapped Cache.
  
  Example:
  .. code-block:: python

      from cache_performance_model import DirectMappedCache

      cache = DirectMappedCache(cache_size_kib=8)
      cache.read(0x1A2B)
      cache.write(0x1A2B)

- `SetAssociativeCache`: Class for Set Associative Cache.
  
  Example:
  .. code-block:: python

      from cache_performance_model import SetAssociativeCache, ReplacementPolicy

      cache = SetAssociativeCache(n_way=4, replacement_policy=ReplacementPolicy.LRU)
      cache.read(0x1A2B)
      cache.write(0x1A2B)

- `FullyAssociativeCache`: Class for Fully Associative Cache.
  
  Example:
  .. code-block:: python

      from cache_performance_model import FullyAssociativeCache, ReplacementPolicy

      cache = FullyAssociativeCache(replacement_policy=ReplacementPolicy.RANDOM)
      cache.read(0x1A2B)
      cache.write(0x1A2B)

Each cache model class implements the following methods:

- `read(addr)`: Abstract method to read from the cache.
- `write(addr)`: Abstract method to write to the cache.
- `clear()`: Clear the cache.
- `clog2(n)`: Calculate the ceiling of log2.
- `create_mask(x)`: Create a bitmask of length x.
- `check_addr(address)`: Check if the address is within the valid range.
- `hits`: Property to get and set the number of hits.
- `misses`: Property to get the total number of misses.
- `update_miss(miss_type, value)`: Update a specific type of miss.
- `hit_ratio`: Property to get the hit ratio.
- `miss_ratio`: Property to get the miss ratio.
- `name`: Property to get the name of the cache.
- `topology`: Property to get the topology of the cache.
- `amat`: Property to get the Average Memory Access Time (AMAT).
- `stats()`: Print cache statistics.

