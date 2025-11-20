# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang
#         Shixuan Chen

"""
Base class for test cases.
"""

from typing import Any

import comopy.hdl as HDL
from comopy.hdl import HDLStage
from comopy.ir import IRStage
from comopy.simulator import BaseSimulator, SimulatorStage
from comopy.translator import BaseTranslator, TranslatorStage
from comopy.utils import JobPipeline, match_lines


class BaseTestCase:
    """Base class for test cases."""

    def simulate(
        self, top: HDL.RawModule, tv: list, init: dict[str, Any] = {}
    ):
        if not tv:
            raise RuntimeError(f"No TV for DUT module {top}.")
        io = self.__get_tv_io(tv)

        pipeline = JobPipeline(HDLStage(), IRStage(), SimulatorStage())
        pipeline(top)

        self.__check_module_io(top, io)
        self.__init_data(top, init)
        self.__run_ticks(top, io, tv)

    def __get_tv_io(self, tv: list) -> HDL.IOStruct:
        io = tv[0]
        if not isinstance(io, HDL.IOStruct):
            raise RuntimeError("No IOStruct at TV[0].")
        for i, data in enumerate(tv[1:], 1):
            if not io.match_data(data):
                io_cls = io.__class__.__name__
                raise RuntimeError(f"TV[{i}] doesn't match {io_cls}: {data}")
        return io

    def __check_module_io(self, top: HDL.RawModule, io: HDL.IOStruct):
        if not io.match_module_io(top):
            io_cls = io.__class__.__name__
            raise RuntimeError(
                f"{io_cls}() at TV[0] doesn't match module {top}."
            )

    def __init_data(self, top: HDL.RawModule, init: dict[str, Any]):
        root = top.node
        assert isinstance(root, HDL.CircuitNode)
        assert root.is_root
        for name, value in init.items():
            node = root.get_element(name)
            assert isinstance(node, HDL.CircuitNode)
            obj = node.obj
            assert isinstance(obj, HDL.SignalArray)
            obj.read_mem(value)

    def __run_ticks(self, top: HDL.RawModule, io: HDL.IOStruct, tv: list):
        sim = top.simulator
        assert isinstance(sim, BaseSimulator)
        sim.start()
        for i, data in enumerate(tv[1:], 1):
            io.assign_inputs(top, data)
            assert isinstance(top, HDL.RawModule)
            if isinstance(top, HDL.Module):
                sim.tick()
            else:
                sim.evaluate()
            try:
                io.verify_outputs(top, data)
            except Exception as e:
                raise RuntimeError(f"{e} : TV[{i}] {data}")
        sim.stop()

    def translate(self, top: HDL.RawModule, match: str):
        pipeline = JobPipeline(HDLStage(), IRStage(), TranslatorStage())
        pipeline(top)

        trans = top.translator
        assert isinstance(trans, BaseTranslator)
        sv = trans.emit()
        assert isinstance(sv, str)
        match_lines(sv, match)
