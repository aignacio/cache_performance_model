#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : cache_model.py
# License           : MIT license <Check LICENSE>
# Author            : Anderson I. da Silva (aignacio) <anderson@aignacio.com>
# Date              : 07.02.2025
# Last Modified Date: 24.02.2025
import logging
import math
import numpy as np
import inspect
import random

from typing import Any
from abc import ABC, abstractmethod
from .types import AccessType, ReplacementPolicy
from .types import Total, Miss, CacheUnexpectedCaller, CacheIllegalParameter

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s"
)


class Cache(ABC):
    """Abstract base class for cache models."""
    ADDR_WIDTH = 32

    def __init__(
        self,
        cache_line_bytes: int = 64,
        cache_size_kib: int = 4,
        hit_latency: int = 1,
        miss_latency: int = 10,
    ) -> None:
        """
        Initialize the cache with given parameters.

        :param cache_line_bytes: Size of each cache line in bytes, defaults to 64
        :type cache_line_bytes: int, optional
        :param cache_size_kib: Size of the cache in KiB, defaults to 4
        :type cache_size_kib: int, optional
        :param hit_latency: Latency for a cache hit, defaults to 1
        :type hit_latency: int, optional
        :param miss_latency: Latency for a cache miss, defaults to 10
        :type miss_latency: int, optional
        """
        self.cache_line_bytes = cache_line_bytes
        self.cache_size_kib = cache_size_kib
        self.cl_bits = self.clog2(self.cache_line_bytes)
        self.hit_latency = hit_latency
        self.miss_latency = miss_latency
        self._name = ""
        self._topology = ""
        self._n_way = 1
        self._rp = ReplacementPolicy.NONE

        # counters
        self._hits = 0
        self._misses = Miss()
        self._total = Total()

        if self.ADDR_WIDTH <= 8:
            self.dtype = np.int8
        elif self.ADDR_WIDTH <= 16:
            self.dtype = np.int16
        elif self.ADDR_WIDTH <= 32:
            self.dtype = np.int32
        elif self.ADDR_WIDTH <= 64:
            self.dtype = np.int64
        else:
            raise ValueError("NumPy does not support integers larger than 64 bits.")

    @abstractmethod
    def read(self, addr: int):
        """
        Abstract method to read from the cache.

        :param addr: Address to read from
        :type addr: int
        """
        pass

    @abstractmethod
    def write(self, addr: int):
        """
        Abstract method to write to the cache.

        :param addr: Address to write to
        :type addr: int
        """
        pass

    @abstractmethod
    def clear(self):
        """Clear the cache."""
        self._hits = 0
        self._misses = Miss()
        self._total.sum = (0, 0)

    def clog2(self, n):
        """
        Calculate the ceiling of log2.

        :param n: Number to calculate log2 for
        :type n: int
        :return: Ceiling of log2 of n
        :rtype: int
        """
        return math.floor(math.log2(n + 1))

    def create_mask(self, x):
        """
        Create a bitmask of length x.

        :param x: Length of the bitmask
        :type x: int
        :return: Bitmask of length x
        :rtype: int
        """
        return (1 << x) - 1

    def check_addr(self, address):
        """
        Check if the address is within the valid range.

        :param address: Address to check
        :type address: int
        :raises ValueError: If the address is out of range
        """
        if address > (2**Cache.ADDR_WIDTH) - 1:
            raise ValueError(
                f"Address value is greater than max ({Cache.ADDR_WIDTH} bits)."
            )

    @property
    def hits(self):
        """
        Get the number of hits.

        :return: Number of hits
        :rtype: int
        """
        return self._hits

    @hits.setter
    def hits(self, value):
        """
        Set the number of hits and update the total read/write counters.

        :param value: Number of hits
        :type value: int
        :raises CacheUnexpectedCaller: If the caller is not read or write method
        """
        self._hits = value

        if inspect.stack()[1].function == "read":
            self._total.read += 1
        elif inspect.stack()[1].function == "write":
            self._total.write += 1
        else:
            raise CacheUnexpectedCaller()

    @property
    def misses(self):
        """
        Get the total number of misses.

        :return: Total number of misses
        :rtype: int
        """
        return self._misses.sum

    def update_miss(self, miss_type, value):
        """
        Update a specific type of miss (conflict, capacity, or compulsory).

        :param miss_type: Type of miss ('conflict', 'capacity', or 'compulsory')
        :type miss_type: str
        :param value: Value to increment the miss count by
        :type value: int
        :raises ValueError: If the miss type is invalid
        :raises CacheUnexpectedCaller: If the caller is not read or write method
        """
        if miss_type not in ("conflict", "capacity", "compulsory"):
            raise ValueError(
                "Invalid miss type. Choose from 'conflict', 'capacity', or 'compulsory'."
            )

        # Increment the specified miss type
        if miss_type == "conflict":
            self._misses.conflict += value
        elif miss_type == "capacity":
            self._misses.capacity += value
        elif miss_type == "compulsory":
            self._misses.compulsory += value

        if inspect.stack()[1].function == "read":
            self._total.read += 1
        elif inspect.stack()[1].function == "write":
            self._total.write += 1
        else:
            raise CacheUnexpectedCaller()

    @property
    def hit_ratio(self):
        """
        Get the hit ratio.

        :return: Hit ratio
        :rtype: float
        """
        return round(self._hits / self._total.sum, 3)

    @property
    def miss_ratio(self):
        """
        Get the miss ratio.

        :return: Miss ratio
        :rtype: float
        """
        return round(self._misses.sum / self._total.sum, 3)

    @property
    def name(self):
        """
        Get the name of the cache.

        :return: Name of the cache
        :rtype: str
        """
        return self._name

    @property
    def topology(self):
        """
        Get the topology of the cache.

        :return: Topology of the cache
        :rtype: str
        """
        return self._topology

    @property
    def amat(self):
        """
        Return the AMAT - Average Memory Access Time.

        :return: AMAT in clock cycles
        :rtype: float
        """
        # Hit time + Instruction miss rate Miss penalty
        return round(self.hit_latency + (self.miss_ratio * self.miss_latency), 3)

    def stats(self):
        """
        Print cache statistics.

        :return: AMAT in clock cycles
        :rtype: float
        """
        print(f"----------- {self.name} -----------")
        print(f" -> Name:\t{self.name}")
        print(f" -> Topology:\t{self.topology}")
        print(f" -> Replacement Policy:\t{self._rp.name}")
        print(f" -> N-Way:\t{self._n_way}")
        print(f" -> Cache size:\t{self.cache_size_kib} KiB")
        print(f" -> Cache line:\t{self.cache_line_bytes} bytes")
        print(f" -> Hit lat.:\t{self.hit_latency}")
        print(f" -> Miss lat.:\t{self.miss_latency}")
        print(f" -> AMAT:\t{self.amat} clock cycles")
        print(f" -> Hit Ratio:\t{self.hit_ratio} / {self.hit_ratio * 100:.2f}%")
        print(f" -> Miss Ratio:\t{self.miss_ratio} / {self.miss_ratio * 100:.2f}%")
        print(f" -> Miss info:\t{self._misses}")
        print(f" -> Total:\t{self._total}")
        return round(self.hit_latency + (self.miss_ratio * self.miss_latency), 3)


class DirectMappedCache(Cache):
    """Class for Direct Mapped Cache."""
    _inst_cnt = 0

    def __init__(self, name: str = None, *args, **kwargs: Any) -> None:
        """
        Initialize the Direct Mapped Cache with given parameters.

        :param name: Name of the cache instance, defaults to None
        :type name: str, optional
        """
        super().__init__(*args, **kwargs)
        if name is None:  # Default name handling
            name = f"direct_mapped_cache_{DirectMappedCache._inst_cnt}"
        DirectMappedCache._inst_cnt += 1
        self._name = name
        self._topology = "direct_mapped"

        self.n_lines = (self.cache_size_kib * 1024) // (self.cache_line_bytes)
        self.n_lines_bits = self.clog2(self.n_lines)
        self.tag_size_bits = self.ADDR_WIDTH - self.n_lines_bits - self.cl_bits
        self.tag_size_kib = ((self.tag_size_bits * self.n_lines) / 8) / 1024

        # Memories
        self.tags = np.full((self.n_lines, 1), -1, dtype=self.dtype)
        self.valid = np.zeros(self.n_lines, dtype=bool)
        self.dirty = np.zeros(self.n_lines, dtype=bool)

        self.log = logging.getLogger("DirectMappedCache")
        self.log.info("Created new Direct Mapped cache - Writeback")
        self.log.info(f" - Instance name  : {self.name}")
        self.log.info(f" - Cache size kib : {self.cache_size_kib} KiB")
        self.log.info(f" - Tag size kib   : {self.tag_size_kib:.3f} KiB")
        self.log.debug(f" - Cache line size: {self.cache_line_bytes} bytes")
        self.log.debug(f" - Number of lines : {self.n_lines}")
        self.log.debug(f" - Tag size width : {self.tag_size_bits} bits")
        self.log.debug(
            f" - Ratio tag mem/data size: "
            f"{100 * self.tag_size_kib / self.cache_size_kib:.2f}%"
        )

    def clear(self):
        """Clear the Direct Mapped Cache."""
        super().clear()
        self.tags = np.full((self.n_lines, 1), -1, dtype=self.dtype)
        self.valid = np.zeros(self.n_lines, dtype=bool)  # Valid bits
        self.dirty = np.zeros(self.n_lines, dtype=bool)  # Dirty bits

    def read(self, addr: int):
        """
        Read from the Direct Mapped Cache.

        :param addr: Address to read from
        :type addr: int
        """
        self.check_addr(addr)
        index = (addr >> self.cl_bits) % ((1 << self.n_lines_bits))
        tag_addr = addr >> (self.n_lines_bits + self.cl_bits)

        # self.log.debug(f"--- {addr} / {tag_addr} / {index} / {self.tags[index]}")
        if self.valid[index]:
            if self.tags[index] == tag_addr:
                self.hits += 1
                self.log.debug(
                    f" [READ - {self.name}] Hit @ Address"
                    f" {hex(addr)} / Line {index}"
                )
            else:
                if np.all(self.valid):
                    self.update_miss("capacity", 1)
                    self.tags[index] = tag_addr
                    self.log.debug(
                        f" [READ - {self.name}] Capacity miss @ Address"
                        f" {hex(addr)} / Line {index}"
                    )
                else:
                    self.update_miss("conflict", 1)
                    self.tags[index] = tag_addr
                    self.log.debug(
                        f" [READ - {self.name}] Conflict miss @ Address"
                        f" {hex(addr)} / Line {index}"
                    )
        else:
            self.update_miss("compulsory", 1)
            self.tags[index] = tag_addr
            self.valid[index] = True
            self.log.debug(
                f" [READ - {self.name}] Compulsory miss @ Address"
                f" {hex(addr)} / Line {index}"
            )

    def write(self, addr: int):
        """
        Write to the Direct Mapped Cache.

        :param addr: Address to write to
        :type addr: int
        """
        self.check_addr(addr)
        index = (addr >> self.cl_bits) % ((1 << self.n_lines_bits))
        tag_addr = addr >> (self.n_lines_bits + self.cl_bits)

        if self.valid[index]:
            self.dirty[index] = 1

            if self.tags[index] == tag_addr:
                self.hits += 1
                self.log.debug(
                    f" [WRITE - {self.name}] Hit @ Address"
                    f" {hex(addr)} / Line {index}"
                )
            else:
                if np.all(self.valid):
                    self.update_miss("capacity", 1)
                    self.tags[index] = tag_addr
                    self.log.debug(
                        f" [WRITE - {self.name}] Capacity miss @ Address"
                        f" {hex(addr)} / Line {index}"
                    )
                else:
                    self.update_miss("conflict", 1)
                    self.tags[index] = tag_addr
                    self.log.debug(
                        f" [WRITE - {self.name}] Conflict miss @ Address"
                        f" {hex(addr)} / Line {index}"
                    )
        else:
            self.update_miss("compulsory", 1)
            self.tags[index] = tag_addr
            self.valid[index] = True
            self.log.debug(
                f" [WRITE - {self.name}] Compulsory miss @ Address"
                f" {hex(addr)} / Line {index}"
            )


class SetAssociativeCache(Cache):
    """Class for Set Associative Cache."""
    _inst_cnt = 0

    def __init__(
        self,
        name: str = None,
        n_way: int = 2,
        replacement_policy: ReplacementPolicy = ReplacementPolicy.RANDOM,
        *args,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the Set Associative Cache with given parameters.

        :param name: Name of the cache instance, defaults to None
        :type name: str, optional
        :param n_way: Number of ways in the set associative cache, defaults to 2
        :type n_way: int, optional
        :param replacement_policy: Replacement policy for the cache, defaults to ReplacementPolicy.RANDOM
        :type replacement_policy: ReplacementPolicy, optional
        :raises CacheIllegalParameter: If n_way is less than 2 or if replacement policy is invalid
        """
        super().__init__(*args, **kwargs)
        if name is None:  # Default name handling
            name = f"set_associative_cache_{SetAssociativeCache._inst_cnt}"
        SetAssociativeCache._inst_cnt += 1
        self._name = name
        self._topology = "set_associative"
        self._n_way = n_way
        self._rp = replacement_policy

        # Basic checks
        if n_way < 2:
            raise CacheIllegalParameter("n_way")
        if (n_way % 2) != 0 and replacement_policy == ReplacementPolicy.PLRU:
            raise CacheIllegalParameter("n_way")
        if replacement_policy == ReplacementPolicy.NONE:
            raise CacheIllegalParameter("replacement_policy")

        self.cache_size_set = self.cache_size_kib * 1024 // self._n_way  # in bytes
        self.n_lines = self.cache_size_set // self.cache_line_bytes
        self.n_lines_bits = self.clog2(self.n_lines)
        self.tag_size_bits = self.ADDR_WIDTH - self.n_lines_bits - self.cl_bits
        self.tag_size_kib = ((self.tag_size_bits * self.n_lines) / 8) / 1024

        # Memories
        self.tags = np.full((self.n_lines, self._n_way), -1, dtype=self.dtype)
        self.valid = np.zeros((self.n_lines, self._n_way), dtype=bool)
        self.dirty = np.zeros((self.n_lines, self._n_way), dtype=bool)
        if self._rp == ReplacementPolicy.FIFO:
            self.fifo = np.zeros((self.n_lines, 1), dtype=int)
        elif self._rp == ReplacementPolicy.LRU:
            init_row = np.arange(0, self._n_way)
            self.lru = np.tile(init_row, (self.n_lines, 1))
        elif self._rp == ReplacementPolicy.NMRU:
            self.nmru = np.zeros((self.n_lines, 1), dtype=int)
        elif self._rp == ReplacementPolicy.PLRU:
            self.plru_tree = np.zeros((self.n_lines, self._n_way - 1), dtype=bool)

        self.log = logging.getLogger("SetAssociativeCache")
        self.log.info("Created new Set Associative Cache - Writeback")
        self.log.info(f" - Instance name  : {self.name}")
        self.log.info(f" - N-Way  : {self._n_way}")
        self.log.info(f" - Replacement Policy  : {self._rp.name}")
        self.log.info(f" - Cache size kib : {self.cache_size_kib} KiB")
        self.log.info(f" - Tag size kib   : {self.tag_size_kib:.3f} KiB")
        self.log.debug(f" - Cache line size: {self.cache_line_bytes} bytes")
        self.log.debug(f" - Number of lines : {self.n_lines}")
        self.log.debug(f" - Tag size width : {self.tag_size_bits} bits")
        self.log.debug(
            f" - Ratio tag mem/data size: "
            f"{100 * self.tag_size_kib / self.cache_size_kib:.2f}%"
        )

    def get_replacement(self, index: int = 0):
        """
        Get the replacement index based on the replacement policy.

        :param index: Index of the cache line
        :type index: int
        :return: Replacement index
        :rtype: int
        """
        self.log.debug(f" [GET REPLACEMENT] Line = {index} / Policy = {self._rp.name}")

        if self._rp == ReplacementPolicy.RANDOM:
            return random.randint(0, self._n_way - 1)
        elif self._rp == ReplacementPolicy.FIFO:
            return self.fifo[index][0]
        elif self._rp == ReplacementPolicy.LRU:
            # Return the index of the lowest number within the array
            return self.lru[index].argmin()
        elif self._rp == ReplacementPolicy.NMRU:
            return self.nmru[index]
        elif self._rp == ReplacementPolicy.PLRU:
            node = 0
            for level in range(self._n_way.bit_length() - 1):  # log2(n_way) levels
                direction = self.plru_tree[index, node]
                node = (2 * node) + 1 + direction  # Move left (0) or right (1)
            return node - (self._n_way - 1)  # Convert tree node to cache way index

    def track_access(
        self, index: int = 0, way: int = 0, access_type: AccessType = AccessType.HIT
    ):
        """
        Track access for the given index and way.

        :param index: Index of the cache line
        :type index: int
        :param way: Way of the cache line
        :type way: int
        :param access_type: Type of access (HIT or MISS)
        :type access_type: AccessType
        """
        self.log.debug(f" [TRACK ACCESS] Line = {index} / Policy = {self._rp.name}")

        if self._rp == ReplacementPolicy.RANDOM:
            pass
        elif self._rp == ReplacementPolicy.FIFO:
            latest = self.fifo[index]
            self.log.debug(f" [FIFO] Latest: {latest}")
            if access_type == AccessType.MISS:
                self.fifo[index] = latest + 1 if latest + 1 < self._n_way else 0
            self.log.debug(f" [FIFO] Now oldest: {self.fifo[index]}")
        elif self._rp == ReplacementPolicy.LRU:
            arr = self.lru[index]
            accessed_value = self.lru[index, way]
            # If it's already the highest, do nothing
            if accessed_value != max(arr):
                # Decrease values that are greater than the accessed value
                arr[arr > accessed_value] -= 1
                # Move accessed element to the highest position
                arr[way] = self._n_way - 1
                self.lru[index] = arr
            self.log.debug(f" [LRU] {self.lru[index]}")
            assert np.all(
                arr < self._n_way
            ), f" [LRU] All elements must be smaller than N_WAY:{self._n_way}"
            assert len(arr) == len(np.unique(arr)), " [LRU] All elements must be unique"
        elif self._rp == ReplacementPolicy.NMRU:
            if way + 1 == self._n_way:
                self.nmru[index] = 0
            else:
                # Get the next one but not the most recently used
                self.nmru[index] = way + 1
            self.log.debug(
                f" [NMRU] Not the most recently used {self.nmru[index]} (mru+1)"
            )
        elif self._rp == ReplacementPolicy.PLRU:
            node = 0
            for level in range(self._n_way.bit_length() - 1):
                direction = way >> (self._n_way.bit_length() - 2 - level) & 1
                self.plru_tree[index, node] = direction  # Update the node
                node = (2 * node) + 1 + direction  # Move to next level
            self.log.debug(f" [PLRU] Tree @ index {index} --> {self.plru_tree[index]}")

    def clear(self):
        """Clear the Set Associative Cache."""
        super().clear()
        self.tags = np.full((self.n_lines, self._n_way), -1, dtype=self.dtype)
        self.valid = np.zeros((self.n_lines, self._n_way), dtype=bool)
        self.dirty = np.zeros((self.n_lines, self._n_way), dtype=bool)

        if self._rp == ReplacementPolicy.FIFO:
            self.fifo = np.zeros((self.n_lines, 1), dtype=int)
        elif self._rp == ReplacementPolicy.LRU:
            init_row = np.arange(0, self._n_way)
            self.lru = np.tile(init_row, (self.n_lines, 1))
        elif self._rp == ReplacementPolicy.NMRU:
            self.nmru = np.zeros((self.n_lines, 1), dtype=int)
        elif self._rp == ReplacementPolicy.PLRU:
            self.plru_tree = np.zeros((self.n_lines, self._n_way - 1), dtype=bool)

    def read(self, addr: int):
        """
        Read from the Set Associative Cache.

        :param addr: Address to read from
        :type addr: int
        """
        self.check_addr(addr)
        index = (addr >> self.cl_bits) % ((1 << self.n_lines_bits))
        tag_addr = addr >> (self.n_lines_bits + self.cl_bits)
        empty_positions = np.where(self.valid[index] == False)[0]  # noqa: E712

        if np.any(self.valid[index]):
            found = False
            for way in range(self._n_way):
                if self.valid[index, way] and self.tags[index, way] == tag_addr:
                    self.track_access(index, way, AccessType.HIT)
                    self.hits += 1
                    self.log.debug(
                        f" [READ - {self.name}] Hit @ Address"
                        f" {hex(addr)} / Line {index} /"
                        f" Way {way}"
                    )
                    found = True
                    break
            if found is not True:
                if not np.all(self.valid[index]):  # Check whether there's an
                    # empty way in the cache
                    way = empty_positions[0]
                    self.track_access(index, way, AccessType.MISS)
                    self.update_miss("compulsory", 1)
                    self.tags[index, way] = tag_addr
                    self.valid[index, way] = True
                    self.log.debug(
                        f" [READ - {self.name}] Compulsory miss @ Address"
                        f" {hex(addr)} / Line {index}"
                        f" / Allocated way {way}"
                    )
                else:  # No more ways available, lets replace...
                    way = self.get_replacement(index)
                    self.track_access(index, way, AccessType.MISS)
                    # Distinguish between conflict vs capacity miss
                    if np.all(self.valid):
                        self.update_miss("capacity", 1)
                        self.tags[index, way] = tag_addr
                        self.log.debug(
                            f" [READ - {self.name}] Capacity miss @ Address"
                            f" {hex(addr)} / Line {index}"
                            f" / Allocated way {way}"
                        )
                    else:
                        self.update_miss("conflict", 1)
                        self.tags[index, way] = tag_addr
                        self.log.debug(
                            f" [READ - {self.name}] Conflict miss @ Address"
                            f" {hex(addr)} / Line {index}"
                            f" / Allocated way {way}"
                        )
        else:
            way = empty_positions[0]
            self.track_access(index, way, AccessType.MISS)
            self.tags[index, way] = tag_addr
            self.update_miss("compulsory", 1)
            self.tags[index, way] = tag_addr
            self.valid[index, way] = True
            self.log.debug(
                f" [READ - {self.name}] Compulsory miss @ Address"
                f" {hex(addr)} / Line {index}"
                f" / Allocated way {way}"
            )

    def write(self, addr: int):
        """
        Write to the Set Associative Cache.

        :param addr: Address to write to
        :type addr: int
        """
        self.check_addr(addr)
        index = (addr >> self.cl_bits) % ((1 << self.n_lines_bits))
        tag_addr = addr >> (self.n_lines_bits + self.cl_bits)
        empty_positions = np.where(self.valid[index] == False)[0]  # noqa: E712

        if np.any(self.valid[index]):
            found = False
            for way in range(self._n_way):
                if self.valid[index, way] and self.tags[index, way] == tag_addr:
                    self.track_access(index, way, AccessType.HIT)
                    self.hits += 1
                    self.log.debug(
                        f" [WRITE - {self.name}] Hit @ Address"
                        f" {hex(addr)} / Line {index} /"
                        f" Way {way}"
                    )
                    self.dirty[index, way] = True
                    found = True
                    break
            if found is not True:
                if not np.all(self.valid[index]):  # Check whether there's an
                    # empty way in the cache
                    way = empty_positions[0]
                    self.track_access(index, way, AccessType.MISS)
                    self.update_miss("compulsory", 1)
                    self.tags[index, way] = tag_addr
                    self.valid[index, way] = True
                    self.dirty[index, way] = True
                    self.log.debug(
                        f" [WRITE - {self.name}] Compulsory miss @ Address"
                        f" {hex(addr)} / Line {index}"
                        f" / Allocated way {way}"
                    )
                else:  # No more ways available, lets replace...
                    way = self.get_replacement(index)
                    self.track_access(index, way, AccessType.MISS)
                    self.dirty[index, way] = True
                    # Distinguish between conflict vs capacity miss
                    if np.all(self.valid):
                        self.update_miss("capacity", 1)
                        self.tags[index, way] = tag_addr
                        self.log.debug(
                            f" [WRITE - {self.name}] Capacity miss @ Address"
                            f" {hex(addr)} / Line {index}"
                            f" / Allocated way {way}"
                        )
                    else:
                        self.update_miss("conflict", 1)
                        self.tags[index, way] = tag_addr
                        self.log.debug(
                            f" [WRITE - {self.name}] Conflict miss @ Address"
                            f" {hex(addr)} / Line {index}"
                            f" / Allocated way {way}"
                        )
        else:
            way = empty_positions[0]
            self.track_access(index, way, AccessType.MISS)
            self.tags[index, way] = tag_addr
            self.update_miss("compulsory", 1)
            self.tags[index, way] = tag_addr
            self.valid[index, way] = True
            self.dirty[index, way] = True
            self.log.debug(
                f" [WRITE - {self.name}] Compulsory miss @ Address"
                f" {hex(addr)} / Line {index}"
                f" / Allocated way {way}"
            )


class FullyAssociativeCache(Cache):
    """Class for Fully Associative Cache."""
    _inst_cnt = 0

    def __init__(
        self,
        name: str = None,
        replacement_policy: ReplacementPolicy = ReplacementPolicy.RANDOM,
        *args,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the Fully Associative Cache with given parameters.

        :param name: Name of the cache instance, defaults to None
        :type name: str, optional
        :param replacement_policy: Replacement policy for the cache, defaults to ReplacementPolicy.RANDOM
        :type replacement_policy: ReplacementPolicy, optional
        :raises CacheIllegalParameter: If replacement policy is invalid
        """
        super().__init__(*args, **kwargs)
        if name is None:  # Default name handling
            name = f"fully_associative_cache_{FullyAssociativeCache._inst_cnt}"
        SetAssociativeCache._inst_cnt += 1
        self._name = name
        self._topology = "fully_associative"
        self._rp = replacement_policy

        self.cache_size_set = self.cache_size_kib * 1024  # in bytes
        self.n_lines = self.cache_size_set // self.cache_line_bytes
        self.tag_size_bits = self.ADDR_WIDTH - self.cl_bits
        self.tag_size_kib = ((self.tag_size_bits * self.n_lines) / 8) / 1024

        # Basic checks
        if replacement_policy == ReplacementPolicy.NONE:
            raise CacheIllegalParameter("replacement_policy")
        if (self.n_lines % 2) != 0 and replacement_policy == ReplacementPolicy.PLRU:
            raise CacheIllegalParameter(
                "cache_size_kib"
            )  # PLRU requires even entries lines

        # Memories
        self.tags = np.full((self.n_lines, 1), -1, dtype=self.dtype)
        self.valid = np.zeros(self.n_lines, dtype=bool)
        self.dirty = np.zeros(self.n_lines, dtype=bool)

        if self._rp == ReplacementPolicy.FIFO:
            self.fifo = 0
        elif self._rp == ReplacementPolicy.LRU:
            self.lru = np.arange(0, self.n_lines)
        elif self._rp == ReplacementPolicy.NMRU:
            self.nmru = 0
        elif self._rp == ReplacementPolicy.PLRU:
            self.plru_tree = np.zeros((self.n_lines - 1), dtype=bool)

        self.log = logging.getLogger("FullyAssociativeCache")
        self.log.info("Created new fully Associative Cache - Writeback")
        self.log.info(f" - Instance name  : {self.name}")
        self.log.info(f" - Replacement Policy  : {self._rp.name}")
        self.log.info(f" - Cache size kib : {self.cache_size_kib} KiB")
        self.log.info(f" - Tag size kib   : {self.tag_size_kib:.3f} KiB")
        self.log.debug(f" - Cache line size: {self.cache_line_bytes} bytes")
        self.log.debug(f" - Number of lines : {self.n_lines}")
        self.log.debug(f" - Tag size width : {self.tag_size_bits} bits")
        self.log.debug(
            f" - Ratio tag mem/data size: "
            f"{100 * self.tag_size_kib / self.cache_size_kib:.2f}%"
        )

    def clear(self):
        """Clear the Fully Associative Cache."""
        super().clear()
        self.tags = np.full((self.n_lines, 1), -1, dtype=self.dtype)
        self.valid = np.zeros(self.n_lines, dtype=bool)
        self.dirty = np.zeros(self.n_lines, dtype=bool)

        if self._rp == ReplacementPolicy.FIFO:
            self.fifo = 0
        elif self._rp == ReplacementPolicy.LRU:
            self.lru = np.arange(0, self.n_lines)
        elif self._rp == ReplacementPolicy.NMRU:
            self.nmru = 0
        elif self._rp == ReplacementPolicy.PLRU:
            self.plru_tree = np.zeros((self.n_lines - 1), dtype=bool)

    def find_matching_valid_entry(self, addr):
        """
        Find a matching valid entry for the given address.

        :param addr: Address to find
        :type addr: int
        :return: Indices of matching valid entries
        :rtype: np.ndarray
        """
        matching_indices = np.where((self.valid) & (self.tags.flatten() == addr))[0]
        return matching_indices

    def get_replacement(self, index: int = 0):
        """
        Get the replacement index based on the replacement policy.

        :param index: Index of the cache line
        :type index: int
        :return: Replacement index
        :rtype: int
        """
        self.log.debug(f" [GET REPLACEMENT] Line = {index} / Policy = {self._rp.name}")

        if self._rp == ReplacementPolicy.RANDOM:
            return random.randint(0, self.n_lines - 1)
        elif self._rp == ReplacementPolicy.FIFO:
            return self.fifo
        elif self._rp == ReplacementPolicy.LRU:
            return self.lru.argmin()
        elif self._rp == ReplacementPolicy.NMRU:
            return self.nmru
        elif self._rp == ReplacementPolicy.PLRU:
            node = 0
            for level in range(self.n_lines.bit_length() - 1):  # log2(n_lines) levels
                direction = self.plru_tree[node]
                node = (2 * node) + 1 + direction  # Move left (0) or right (1)
            return node - (self.n_lines - 1)  # Convert tree node to cache way index

    def track_access(self, index: int = 0, access_type: AccessType = AccessType.HIT):
        """
        Track access for the given index.

        :param index: Index of the cache line
        :type index: int
        :param access_type: Type of access (HIT or MISS)
        :type access_type: AccessType
        """
        self.log.debug(f" [TRACK ACCESS] Line = {index} / Policy = {self._rp.name}")

        if self._rp == ReplacementPolicy.RANDOM:
            pass
        elif self._rp == ReplacementPolicy.FIFO:
            latest = self.fifo
            self.log.debug(f" [FIFO] Latest: {latest}")
            if access_type == AccessType.MISS:
                self.fifo = latest + 1 if latest + 1 < self.n_lines else 0
                self.log.debug(f" [FIFO] Now oldest: {self.fifo}")
        elif self._rp == ReplacementPolicy.LRU:
            arr = self.lru
            accessed_value = self.lru[index]
            # If it's already the highest, do nothing
            if accessed_value != max(arr):
                # Decrease values that are greater than the accessed value
                arr[arr > accessed_value] -= 1
                # Move accessed element to the highest position
                arr[index] = self.n_lines - 1
                self.lru = arr
            self.log.debug(f" [LRU] {self.lru}")
            assert np.all(
                arr < self.n_lines
            ), f" [LRU] All elements must be smaller than NO ENTRIES: {self.n_lines}"
            assert len(arr) == len(
                np.unique(arr)
            ), f" [LRU] All elements must be unique {arr}"
        elif self._rp == ReplacementPolicy.NMRU:
            if index + 1 == self.n_lines:
                self.nmru = 0
            else:
                # Get the next one but not the most recently used
                self.nmru = index + 1
            self.log.debug(f" [NMRU] Not the most recently used {self.nmru} (mru+1)")
        elif self._rp == ReplacementPolicy.PLRU:
            node = 0
            for level in range(self.n_lines.bit_length() - 1):
                direction = index >> (self.n_lines.bit_length() - 2 - level) & 1
                self.plru_tree[node] = direction  # Update the node
                node = (2 * node) + 1 + direction  # Move to next level
            self.log.debug(f" [PLRU] Tree @ index {index} --> {self.plru_tree}")

    def read(self, addr: int):
        """
        Read from the Fully Associative Cache.

        :param addr: Address to read from
        :type addr: int
        """
        self.check_addr(addr)
        tag_addr = addr >> self.cl_bits

        # Look for a hit
        index = self.find_matching_valid_entry(tag_addr)

        if index.size != 0:
            self.hits += 1
            self.track_access(index[0], AccessType.HIT)
            self.log.debug(
                f" [READ - {self.name}] Hit @ Address {hex(addr)} / Line {index}"
            )
        elif np.all(self.valid):  # If there's no hit and we're full...
            replacement_entry = self.get_replacement()
            self.track_access(replacement_entry, AccessType.MISS)
            self.tags[replacement_entry] = tag_addr
            self.valid[replacement_entry] = True
            self.update_miss("capacity", 1)
            self.log.debug(f" [READ - {self.name}] Capacity miss @ Address {hex(addr)}")
        else:  # If there's not hit and we're NOT full
            empty_position = np.where(self.valid == False)[0][0]  # noqa: E712
            self.track_access(empty_position, AccessType.MISS)
            self.tags[empty_position] = tag_addr
            self.valid[empty_position] = True
            self.update_miss("compulsory", 1)
            self.log.debug(
                f" [READ - {self.name}] Compulsory miss @ Address {hex(addr)}"
            )

    def write(self, addr: int):
        """
        Write to the Fully Associative Cache.

        :param addr: Address to write to
        :type addr: int
        """
        self.check_addr(addr)
        tag_addr = addr >> self.cl_bits

        # Look for a hit
        index = self.find_matching_valid_entry(tag_addr)

        if index.size != 0:
            self.hits += 1
            self.track_access(index[0], AccessType.HIT)
            self.dirty[index[0]] = True
            self.log.debug(
                f" [WRITE - {self.name}] Hit @ Address {hex(addr)} / Line {index}"
            )
        elif np.all(self.valid):  # If there's no hit and we're full...
            replacement_entry = self.get_replacement()
            self.track_access(replacement_entry, AccessType.MISS)
            self.tags[replacement_entry] = tag_addr
            self.valid[replacement_entry] = True
            self.dirty[replacement_entry] = True
            self.update_miss("capacity", 1)
            self.log.debug(
                f" [WRITE - {self.name}] Capacity miss @ Address {hex(addr)}"
            )
        else:  # If there's not hit and we're NOT full
            empty_position = np.where(self.valid == False)[0][0]  # noqa: E712
            self.track_access(empty_position, AccessType.MISS)
            self.tags[empty_position] = tag_addr
            self.valid[empty_position] = True
            self.dirty[empty_position] = True
            self.update_miss("compulsory", 1)
            self.log.debug(
                f" [WRITE - {self.name}] Compulsory miss @ Address {hex(addr)}"
            )
