# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Abstract base class for connectable objects.

A connectable object can be used on the left-hand side (LHS) of a continuous
assignment (connection).
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from comopy.datatypes import Bits, BitsData
from comopy.utils import HDLAssemblyError

if TYPE_CHECKING:
    from .signal_bundle import SignalBundle


class Connectable(BitsData):
    """Base class for connectable objects."""

    # Abstract methods
    #
    @property
    @abstractmethod
    def data_driven(self) -> Bits:
        """Get bits that has been driven."""

    @data_driven.setter
    @abstractmethod
    def data_driven(self, value: Bits | int):
        """Mark bits that has been driven."""

    # Assignment
    # @=: continuous assignment (connection)
    #
    def __imatmul__(self, value: Any) -> Connectable:
        from .assemble_hdl import AssembleHDL

        if not AssembleHDL.is_assembling():
            raise RuntimeError("@= (connection) is an assembly-time API.")
        # Check drivers
        if self.data_driven != 0:
            cls_name = self.__class__.__name__
            raise HDLAssemblyError(
                f"Multiple drivers are not allowed for '{cls_name}'."
                f"\n- Calling one builder in another builder?"
            )
        # Check value width by Bits
        try:
            d = Bits(self.nbits, mutable=True)
            d /= value
        except Exception as e:
            raise HDLAssemblyError(f"{e}")
        # Connect
        AssembleHDL.assemble_connection()
        # Mark bits driven
        self.data_driven = (1 << self.nbits) - 1
        return self

    # Replication
    def __pow__(self, count: int) -> SignalBundle:
        from .signal_bundle import rep

        if not isinstance(count, int):
            raise TypeError(
                f"Replication count must be an integer, got {type(count)}."
            )
        if count < 0:
            raise ValueError("Replication count must be non-negative.")
        return rep(count, self)
