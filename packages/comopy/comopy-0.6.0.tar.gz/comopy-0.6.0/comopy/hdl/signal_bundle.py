# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Signal bundle for concatenation operations.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Sequence

from comopy.datatypes import Bits, BitsData
from comopy.utils import BitsAssignError

from .connectable import Connectable
from .signal import Signal
from .signal_slice import SignalSlice


def _count_bits_parts(bits: BitsData) -> Counter:
    assert isinstance(bits, BitsData)
    counter: Counter = Counter()
    if isinstance(bits, SignalBundle):
        for part in bits._parts:
            counter.update(_count_bits_parts(part))
    elif isinstance(bits, SignalSlice):
        counter.update(_count_bits_parts(bits._owner))
    else:
        assert bits.mutable
        counter[bits] += 1
    return counter


def _mark_bundle_driven(bundle: SignalBundle, value: Bits | int):
    assert isinstance(bundle, SignalBundle)
    driven = value.unsigned if isinstance(value, Bits) else value
    assert isinstance(driven, int)
    for part in reversed(bundle._parts):
        k = part.nbits
        if k == 0:
            continue
        d = driven & _bits_mask(k)
        if isinstance(part, SignalBundle):
            _mark_bundle_driven(part, d)
        else:
            assert isinstance(part, (Signal, SignalSlice))
            part.data_driven = d  # type: ignore
        driven >>= k
    assert driven == 0


def _bits_mask(n: int) -> int:
    return (1 << n) - 1


class SignalBundle(Connectable):
    """Signal bundle for concatenation operations."""

    _parts: Sequence[BitsData]
    _nbits: int
    _mutable: bool

    def __init__(self, *parts: BitsData):
        if not parts:
            # Empty signal bundle, only used as an inner bundle
            super().__init__()
            self._parts = []
            self._nbits = 0
            # Do not affect the mutability of the outer bundle
            self._mutable = True
            return

        if not all(isinstance(p, BitsData) for p in parts):
            raise TypeError(
                "All parts of a bundle must be Bits constant or Signal"
            )

        super().__init__()
        self._parts = parts
        self._nbits = sum(p.nbits for p in parts)
        self._mutable = all(p.mutable for p in parts)
        if self._mutable and self._nbits > 0:
            # Check the counter first to avoid checking for overlap
            counter = _count_bits_parts(self)
            if counter.most_common(1)[0][1] > 1:
                self._mutable = not self.__has_overlapped_parts()

    def __has_overlapped_parts(self) -> bool:
        saved = self.data_driven
        value = 1
        overlapped = False
        for _ in range(self._nbits):
            self.data_driven = value  # type: ignore
            if self.data_driven != value:
                overlapped = True
                break
            value <<= 1
        self.data_driven = saved
        return overlapped

    # BitsData
    #
    @property
    def data_bits(self) -> Bits:
        if self._nbits == 0:
            assert not self._parts
            raise ValueError("Cannot directly access an empty signal bundle.")

        value = 0
        nbits = 0
        for part in self._parts:
            k = part.nbits
            if k == 0:
                # Enable nested empty bundles for parameterized 0-width.
                assert isinstance(part, SignalBundle)
                continue
            value = (value << k) | part.data_bits.unsigned
            nbits += k
        assert nbits == self._nbits
        return Bits(nbits, value, mutable=self._mutable)

    @property
    def nbits(self) -> int:
        return self._nbits

    @property
    def mutable(self) -> bool:
        return self._mutable

    # Connectable
    #
    @property
    def data_driven(self) -> Bits:
        if self._nbits == 0:
            assert not self._parts
            raise ValueError("Cannot directly access an empty signal bundle.")

        value = 0
        nbits = 0
        for part in self._parts:
            k = part.nbits
            if k == 0:
                # Enable nested empty bundles for parameterized 0-width.
                assert isinstance(part, SignalBundle)
                continue
            if isinstance(part, Bits):
                data = Bits(k, _bits_mask(k))  # all bits driven
            else:
                assert isinstance(part, Connectable)
                data = part.data_driven
            value = (value << k) | data.unsigned
            nbits += k
        assert nbits == self._nbits
        return Bits(nbits, value, mutable=self._mutable)

    @data_driven.setter
    def data_driven(self, value: Bits | int):
        _mark_bundle_driven(self, value)

    # Assignment
    #
    # /= : blocking assignment
    def __itruediv__(self, value: Any) -> SignalBundle:
        if not self._mutable:
            raise BitsAssignError(self._nbits, "immutable signal bundle")

        # Check value width by Bits
        bits = Bits(self._nbits, mutable=True)
        bits /= value  # Better error message than Bits(nbits, value)

        # Dispatch to parts
        data = bits.unsigned
        for part in reversed(self._parts):
            k = part.nbits
            if k == 0:  # Empty bundle
                assert isinstance(part, SignalBundle)
                continue
            part /= data & _bits_mask(k)  # type: ignore
            data >>= k
        assert data == 0
        return self

    # <<= : nonblocking assignment
    def __ilshift__(self, value: Any) -> SignalBundle:
        if not self._mutable:
            raise BitsAssignError(self._nbits, "immutable signal bundle")

        # Check value width by Bits
        bits = Bits(self._nbits, mutable=True)
        bits /= value  # Better error message than Bits(nbits, value)

        # Dispatch to parts
        data = bits.unsigned
        for part in reversed(self._parts):
            k = part.nbits
            if k == 0:  # Empty bundle
                assert isinstance(part, SignalBundle)
                continue
            part <<= data & _bits_mask(k)  # type: ignore
            data >>= k
        assert data == 0
        return self

    # @= : continuous assignment (connection)
    # Use Connectable.@=()

    # Slice
    # See Signal.__setitem__ for slice assignment.
    #
    def __getitem__(self, key: Any) -> SignalSlice:
        return SignalSlice(self, key)

    def __setitem__(self, key: Any, value: SignalSlice):
        if isinstance(value, SignalSlice):
            if value._owner is self and value._key == key:
                # Assignment has been done in `__itruediv__`
                return
        super().__setitem__(key, value)

    # Replication
    #
    def __pow__(self, count: int) -> SignalBundle:
        if not isinstance(count, int):
            raise TypeError(
                f"Replication count must be an integer, got {type(count)}."
            )
        if count < 0:
            raise ValueError("Replication count must be non-negative.")
        if count == 0:
            return SignalBundle()
        if count == 1:  # Avoid unnecessary nesting
            return self
        return SignalBundle(*[self for _ in range(count)])


def cat(*parts: BitsData) -> SignalBundle:
    return SignalBundle(*parts)


def rep(count: int, *parts: BitsData) -> SignalBundle:
    if not isinstance(count, int):
        raise TypeError(f"rep() count must be an integer, got {type(count)}.")
    if not parts:
        raise ValueError("rep() expects at least one part.")
    if count < 0:
        raise ValueError("rep() count must be non-negative.")
    if count == 0:
        return SignalBundle()
    parts = parts * count
    return SignalBundle(*parts)
