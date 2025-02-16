#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : types.py
# License           : MIT license <Check LICENSE>
# Author            : Anderson I. da Silva (aignacio) <anderson@aignacio.com>
# Date              : 16.02.2025
# Last Modified Date: 16.02.2025
import enum


class AccessType(enum.Flag):
    HIT = False
    MISS = True


class ReplacementPolicy(enum.IntEnum):
    NONE = 0
    RANDOM = 1
    FIFO = 2
    LRU = 3
    NMRU = 4
    PLRU = 5


class CacheUnexpectedCaller(Exception):
    """Exception raised when hit/miss is not coming from read/write methods"""

    def __init__(
        self, message="Hit/Miss needs to be called from read or write methods"
    ):
        self.message = message
        super().__init__(self.message)


class Total:
    def __init__(self):
        self.read = 0
        self.write = 0

    @property
    def sum(self):
        return self.read + self.write

    @sum.setter
    def sum(self, val):
        self.read = val[0]
        self.write = val[1]

    def __repr__(self):
        return (
            f"{self.sum} (read={self.read} / {100 * self.read / self.sum:.2f}%, "
            f"write={self.write} / {100 * self.write / self.sum:.2f}%)"
        )


class Miss:
    def __init__(self):
        self.conflict = 0
        self.capacity = 0
        self.compulsory = 0

    @property
    def sum(self):
        return self.conflict + self.capacity + self.compulsory

    def __repr__(self):
        return (
            f"{self.sum} (conflict={self.conflict}, "
            f"capacity={self.capacity}, compulsory={self.compulsory})"
        )
