# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Pass, stage, and pipeline in a workflow.
"""

from abc import ABC, abstractmethod
from typing import Any


class BasePass(ABC):
    """Abstract base class for workflow passes.

    A workflow pass processes input data and returns the result.
    Subclasses must implement the __call__ method.
    """

    @abstractmethod
    def __call__(self, input: Any):
        """Execute the pass."""


class PassGroup(BasePass):
    """Executes a sequence of passes as a group.

    Each pass receives the output of the previous pass as its input.
    The group's final output is the result of the last pass.
    """

    def __init__(self, *passes: BasePass):
        assert passes
        assert all(isinstance(p, BasePass) for p in passes)
        self.passes = passes

    def __call__(self, input: Any):
        output = input
        for p in self.passes:
            output = p(output)
            if output is None:
                pass_name = p.__class__.__name__
                raise Exception(f"No return value from {pass_name} pass.")
        return output


class BaseStage:
    """Abstract base class for workflow stages.

    A stage receives an input, applies a pass or pass group, and returns the
    output. Subclasses may override input validation as needed.
    """

    def __init__(self, pass_instance: BasePass, name=None):
        super().__init__()
        assert isinstance(
            pass_instance, BasePass
        ), f"'{pass_instance!r}' isn't a BasePass instance"
        self.pass_instance = pass_instance
        self._name = self.__class__.__name__ if not name else str(name)

    @property
    def name(self) -> str:
        return self._name

    def check_input(self, input: Any):
        """Validate the input. Raise an exception if invalid."""

    def __call__(self, input):
        self.check_input(input)
        return self.pass_instance(input)


class JobPipeline:
    """JobPipeline connects workflow stages and executes them in order.

    Each stage processes the output of the previous stage, forming a pipeline.
    """

    def __init__(self, *stages: BaseStage):
        assert all(isinstance(s, BaseStage) for s in stages)
        self.stages = stages

    def __call__(self, input: Any):
        output = input
        for stage in self.stages:
            output = stage(output)
            if output is None:
                raise Exception(f"No return value from {stage.name} stage.")
        return output
