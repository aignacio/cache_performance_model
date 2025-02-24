#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : types.py
# License           : MIT license <Check LICENSE>
# Author            : Anderson I. da Silva (aignacio) <anderson@aignacio.com>
# Date              : 16.02.2025
# Last Modified Date: 17.02.2025
import enum


class AccessType(enum.Flag):
    """Enumeration for cache access types."""
    HIT = False
    MISS = True


class ReplacementPolicy(enum.IntEnum):
    """Enumeration for cache replacement policies."""
    NONE = 0
    RANDOM = 1
    FIFO = 2
    LRU = 3
    NMRU = 4
    PLRU = 5


class CacheUnexpectedCaller(Exception):
    """Exception raised when hit/miss is not coming from read/write methods."""

    def __init__(self, message="Hit/Miss needs to be called from read or write methods"):
        """Initialize the exception with a custom message."""
        self.message = message
        super().__init__(self.message)


class CacheIllegalParameter(Exception):
    """Exception raised when an illegal parameter is set."""

    def __init__(self, param_name: str, message="Parameter {param} value is illegal"):
        """Initialize the exception with the parameter name and a custom message."""
        self.param = param_name
        self.message = message.format(param=param_name)
        super().__init__(self.message)


class Total:
    """Class to keep track of total read and write operations."""

    def __init__(self):
        """Initialize the Total class with read and write counters set to zero."""
        self.read = 0
        self.write = 0

    @property
    def sum(self):
        """Return the sum of read and write operations."""
        return self.read + self.write

    @sum.setter
    def sum(self, val):
        """Set the read and write counters."""
        self.read = val[0]
        self.write = val[1]

    def __repr__(self):
        """Return a string representation of the total operations."""
        return (
            f"{self.sum} (read={self.read} / {100 * self.read / self.sum:.2f}%, "
            f"write={self.write} / {100 * self.write / self.sum:.2f}%)"
        )


class Miss:
    """Class to keep track of different types of cache misses."""

    def __init__(self):
        """Initialize the Miss class with conflict, capacity and compulsory miss counters set to zero."""
        self.conflict = 0
        self.capacity = 0
        self.compulsory = 0

    @property
    def sum(self):
        """Return the sum of all types of cache misses."""
        return self.conflict + self.capacity + self.compulsory

    def __repr__(self):
        """Return a string representation of the cache misses."""
        return (
            f"{self.sum} (conflict={self.conflict}, "
            f"capacity={self.capacity}, compulsory={self.compulsory})"
        )
