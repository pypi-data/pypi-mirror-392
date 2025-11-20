# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Abstract base class defining the interface for all translators.
"""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseTranslator(ABC):
    """Base class for all translators."""

    # Abstract properties and methods
    #
    @property
    @abstractmethod
    def target_language(self) -> str:
        """Get the name of the target language."""

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Get the file extension for the target language."""

    @property
    @abstractmethod
    def dest_path(self) -> Path:
        """Get the destination file path."""

    @abstractmethod
    def emit(self) -> str:
        """Emit the bound IR module as target language code."""

    # Concrete methods
    #
    def emit_to_file(self):
        """Emit the code to the destination file."""
        code = self.emit()
        dest = self.dest_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(code, encoding="utf-8")
