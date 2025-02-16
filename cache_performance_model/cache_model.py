#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : cache_model.py
# License           : MIT license <Check LICENSE>
# Author            : Anderson I. da Silva (aignacio) <anderson@aignacio.com>
# Date              : 07.02.2025
# Last Modified Date: 16.02.2025
import logging
import math
import numpy as np
import inspect
import random

from typing import Any
from abc import ABC, abstractmethod
from .types import AccessType, ReplacementPolicy
from .types import Total, Miss, CacheUnexpectedCaller

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s"
)


class Cache(ABC):
    ADDR_WIDTH = 32

    def __init__(
        self,
        cache_line_bytes: int = 64,
        cache_size_kib: int = 4,
        hit_latency: int = 1,
        miss_latency: int = 10,
    ) -> None:
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
        pass

    @abstractmethod
    def write(self, addr: int):
        pass

    @abstractmethod
    def clear(self):
        self._hits = 0
        self._misses = Miss()
        self._total.sum = (0, 0)

    def clog2(self, n):
        return math.floor(math.log2(n + 1))

    def create_mask(self, x):
        return (1 << x) - 1

    def check_addr(self, address):
        if address > (2**Cache.ADDR_WIDTH) - 1:
            raise ValueError(
                f"Address value is greater than max ({Cache.ADDR_WIDTH} bits)."
            )

    @property
    def hits(self):
        return self._hits

    @hits.setter
    def hits(self, value):
        self._hits = value

        if inspect.stack()[1].function == "read":
            self._total.read += 1
        elif inspect.stack()[1].function == "write":
            self._total.write += 1
        else:
            raise CacheUnexpectedCaller()

    @property
    def misses(self):
        return self._misses.sum

    def update_miss(self, miss_type, value):
        """Update a specific type of miss (conflict, capacity, or compulsory)."""
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
        return round(self._hits / self._total.sum, 3)

    @property
    def miss_ratio(self):
        return round(self._misses.sum / self._total.sum, 3)

    @property
    def name(self):
        return self._name

    @property
    def topology(self):
        return self._topology

    @property
    def amat(self):
        """Return the AMAT - Average Memory Access Time"""
        # Hit time + Instruction miss rate Miss penalty
        return round(self.hit_latency + (self.miss_ratio * self.miss_latency), 3)

    def stats(self):
        """Print cache statistics"""
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
    _inst_cnt = 0

    def __init__(self, name: str = None, *args, **kwargs: Any) -> None:
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
        self._hits = 0
        self._misses = Miss()
        self._total.sum = (0, 0)
        self.tags = np.full((self.n_lines, 1), -1, dtype=self.dtype)
        self.valid = np.zeros(self.n_lines, dtype=bool)  # Valid bits
        self.dirty = np.zeros(self.n_lines, dtype=bool)  # Dirty bits

    def read(self, addr: int):
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
    _inst_cnt = 0

    def __init__(
        self,
        name: str = None,
        n_way: int = 2,
        replacement_policy: ReplacementPolicy = ReplacementPolicy.RANDOM,
        *args,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        if name is None:  # Default name handling
            name = f"set_associative_cache_{SetAssociativeCache._inst_cnt}"
        SetAssociativeCache._inst_cnt += 1
        self._name = name
        self._topology = "set_associative"
        self._n_way = n_way
        self._rp = replacement_policy

        self.cache_size_set = self.cache_size_kib * 1024 // self._n_way  # in bytes
        self.n_lines = (self.cache_size_set) // self.cache_line_bytes
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
        # elif self._rp == ReplacementPolicy.PLRU:

    def track_access(
        self, index: int = 0, way: int = 0, access_type: AccessType = AccessType.HIT
    ):
        self.log.debug(
            f" [UPDATE REPLACEMENT] Line = {index} / Policy = {self._rp.name}"
        )

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
                arr[way] = arr.max() + 1
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

    def clear(self):
        self._hits = 0
        self._misses = Miss()
        self._total.sum = (0, 0)
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

    def read(self, addr: int):
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
