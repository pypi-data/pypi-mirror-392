# Tests for IOStruct
#

import pytest

from comopy.bits import *
from comopy.hdl.assemble_hdl import AssembleHDL
from comopy.hdl.io_struct import IOStruct
from comopy.hdl.raw_module import RawModule, build
from comopy.hdl.signal import Input, Logic, Output
from comopy.utils import HDLAssemblyError


def test_IOStruct_init():
    class Ports(IOStruct):
        in1 = Input(4)
        in2 = Input(8)
        out1 = Output(4)
        out2 = Output(8)

    io = Ports()
    assert io.in1 is Ports.in1
    assert io.in2 is Ports.in2
    assert io.out1 is Ports.out1
    assert io.out2 is Ports.out2
    assert io.assembled is False
    assert io.simulating is False
    assert io.is_module is False
    assert io.is_package is False
    assert io.direction is None
    assert io.is_input_port is False
    assert io.is_output_port is False
    assert io.is_inout_port is False
    assert io.is_scalar_input is False
    assert io.is_port is False
    assert io._part_names == ["in1", "in2", "out1", "out2"]
    assert io._has_input is True
    assert io._has_output is True


def test_IOStruct_match_module_io():
    class Top(RawModule):
        @build
        def build_all(s):
            s.in_ = "Not a signal"
            s.in1 = Input()
            s.in2 = Input(8)
            s.out = Output(4)
            s.x = Logic(4)

    top = Top()
    AssembleHDL()(top)

    # Matched I/O
    class MatchedIO(IOStruct):
        in1 = Input()
        in2 = Input(8)
        out = Output(4)

    assert MatchedIO().match_module_io(top)

    # No port in module
    class NoPort(IOStruct):
        out2 = Output(4)

    assert not NoPort().match_module_io(top)

    # Not a signal
    class NotSignal(IOStruct):
        in_ = Input()

    assert not NotSignal().match_module_io(top)

    # Different width
    class DiffWidth(IOStruct):
        in1 = Input(4)

    assert not DiffWidth().match_module_io(top)

    # No direction
    class NoDirection(IOStruct):
        x = Input(4)

    assert not NoDirection().match_module_io(top)

    # Wrong direction
    class WrongDirection(IOStruct):
        in1 = Output()

    assert not WrongDirection().match_module_io(top)


def _check_error(top: RawModule, error: str):
    with pytest.raises(HDLAssemblyError, match=error):
        AssembleHDL()(top)


def test_IOStruct_init_errors():
    # Conflicting part name
    class ConflictedName(RawModule):
        class Ports(IOStruct):
            node = Input(4)

        @build
        def build_all(s):
            s.ports = s.Ports()

    _check_error(ConflictedName(), "Cannot overwrite attribute 'node'")

    # Non-directional port
    class LogicPort(RawModule):
        class Ports(IOStruct):
            in1 = Logic(4)

        @build
        def build_all(s):
            s.ports = s.Ports()

    _check_error(LogicPort(), "Non-directional member 'in1' .* 'Ports'")

    # Non-directional IOStruct
    class NonPortIOStruct(RawModule):
        class Outer(IOStruct):
            class Inner(IOStruct):
                in_ = Input(4)
                out = Output(4)

            a = Inner()

        @build
        def build_all(s):
            s.outer = s.Outer()

    _check_error(NonPortIOStruct(), "Non-directional member 'a' .* 'Outer'")

    # Empty I/O structure
    class NoPort(RawModule):
        class Ports(IOStruct):
            info = "Not a port"

        @build
        def build_all(s):
            s.ports = s.Ports()

    _check_error(NoPort(), "Empty I/O structure 'Ports'")


def test_IOStruct_match_data():
    class IO(IOStruct):
        in1 = Input()
        in2 = Input(8)
        out = Output(4)

    assert IO().match_data((0, 0, 0))
    assert IO().match_data((0, None, 0))
    assert IO().match_data((b1(1), b8(2), b4(3)))
    assert not IO().match_data((0, 0))
    assert not IO().match_data((0, "0", 0))
    assert not IO().match_data((0b11, 0, 0))


# Print all error messages by replacing _check_error
#
def _print_assembly_error(top: RawModule, error: str):
    try:
        AssembleHDL()(top)
    except HDLAssemblyError as e:
        print(e)


def print_IOStruct_errors():
    global _check_error
    orig_check_error = _check_error
    _check_error = _print_assembly_error
    test_IOStruct_init_errors()
    _check_error = orig_check_error
