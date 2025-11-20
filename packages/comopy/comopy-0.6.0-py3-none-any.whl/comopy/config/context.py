# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
ComoPy execution context management.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Optional

from .ir_config import IRConfig
from .sim_config import SimulatorConfig
from .trans_config import TranslatorConfig


@dataclass
class ComopyContext:
    """ComoPy execution context with configuration and runtime information."""

    ir_config: IRConfig = field(default_factory=IRConfig)
    sim_config: SimulatorConfig = field(default_factory=SimulatorConfig)
    trans_config: TranslatorConfig = field(default_factory=TranslatorConfig)


# ContextVar for storing current context
_current_context: ContextVar[ComopyContext] = ContextVar(
    "comopy_context", default=ComopyContext()
)


@contextmanager
def comopy_context(
    ir_config: Optional[IRConfig] = None,
    sim_config: Optional[SimulatorConfig] = None,
    trans_config: Optional[TranslatorConfig] = None,
):
    """Create and manage a ComoPy execution context."""
    context = ComopyContext(
        ir_config=ir_config or IRConfig(),
        sim_config=sim_config or SimulatorConfig(),
        trans_config=trans_config or TranslatorConfig(),
    )

    token = _current_context.set(context)
    try:
        yield context
    finally:
        _current_context.reset(token)


def get_comopy_context() -> ComopyContext:
    """Get the currently active ComoPy context."""
    return _current_context.get()


def set_comopy_context(context: ComopyContext):
    """Set a new ComoPy context as the current context."""
    _current_context.set(context)
