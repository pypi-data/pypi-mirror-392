# Tests for SignalArray
#

import pytest

from comopy.bits import b8  # type: ignore
from comopy.hdl.assemble_hdl import AssembleHDL
from comopy.hdl.raw_module import RawModule, build
from comopy.hdl.signal import Input, Logic
from comopy.hdl.signal_array import SignalArray


def _fake_in_sim(array: SignalArray):
    array._assemble()
    array.simulating = True


def test_SignalArray_init():
    sa = SignalArray(Logic(8), 16)
    assert sa.assembled is False
    assert sa.simulating is False
    assert sa.is_module is False
    assert sa.is_package is False
    assert sa.direction is None
    assert sa.is_input_port is False
    assert sa.is_output_port is False
    assert len(sa) == 16
    assert sa.size == 16
    assert str(sa) == "Logic{Bits8}[16]"

    with pytest.raises(ValueError, match=r"should be a Signal object"):
        SignalArray(8, 16)
    with pytest.raises(ValueError, match=r"should be a Signal object"):
        SignalArray("Logic", 16)
    with pytest.raises(ValueError, match=r"cannot be assembled"):
        wire = Logic(8)
        wire._assembled = True
        SignalArray(wire, 16)
    with pytest.raises(ValueError, match=r"cannot be a port"):
        SignalArray(Input(8), 16)
    with pytest.raises(ValueError, match=r"size should be a positive"):
        SignalArray(Logic(8), 0)
    with pytest.raises(ValueError, match=r"size should be a positive"):
        SignalArray(Logic(8), -1)


def test_SignalArray_assemble():
    class Top(RawModule):
        @build
        def build_all(s):
            s.sa = SignalArray(Logic(8), 16)

    top = Top()
    AssembleHDL()(top)
    assert isinstance(top.sa, SignalArray)
    assert top.sa.assembled
    assert top.sa.size == 16
    assert isinstance(top.sa[0], Logic)
    assert top.sa[0].nbits == 8
    assert top.sa[0].assembled
    assert isinstance(top.sa[15], Logic)
    assert top.sa[15].nbits == 8
    assert top.sa[15].assembled


def test_SignalArray_item():
    sa = SignalArray(Logic(8), 16)
    assert isinstance(sa[0], Logic)
    assert sa[0].nbits == 8
    assert not sa[0].assembled
    assert isinstance(sa[15], Logic)
    assert sa[15].nbits == 8
    assert not sa[15].assembled
    with pytest.raises(IndexError, match=r"is not sliceable"):
        sa[:1]
    with pytest.raises(IndexError, match=r"is not part-selectable"):
        sa[0, 4]
    with pytest.raises(IndexError, match=r"should be an integer or Bits"):
        sa[0.0]
    with pytest.raises(IndexError, match=r"Array index is out of range"):
        sa[-1]
    with pytest.raises(IndexError, match=r"Array index is out of range"):
        sa[16]
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        sa[0] /= 1

    _fake_in_sim(sa)
    sa[0] /= 0x12
    sa[8] /= 0x34
    sa[15] /= 0x56
    assert sa[0] == 0x12
    assert sa[8] == 0x34
    assert sa[15] == 0x56

    with pytest.raises(IndexError, match=r"is not sliceable"):
        sa[:1] = 0x12
    with pytest.raises(IndexError, match=r"is not part-selectable"):
        sa[0, 4] = 0x12
    with pytest.raises(IndexError, match=r"should be an integer or Bits"):
        sa["0"] = 0x12
    with pytest.raises(ValueError, match=r"Wrong assignment type"):
        sa[0] = Logic(16)
    with pytest.raises(ValueError, match=r"Wrong assignment type"):
        sa[8] = 0x34


def test_SignalArray_dirty_entries():
    sa = SignalArray(Logic(8), 16)
    _fake_in_sim(sa)

    # write to items
    sa[0] <<= 1
    sa[b8(2)] <<= 3
    sa[5] <<= 7
    sa[b8(8)] <<= 8
    assert sa._dirty_entries == {0, 2, 5, 8}
    sa.flip()
    assert sa._dirty_entries == set()
    sa[1] <<= 3
    assert sa._dirty_entries == {1}
    sa[9] <<= 10
    assert sa._dirty_entries == {1, 9}
    sa[3] <<= 8
    assert sa._dirty_entries == {1, 3, 9}
    sa.flip()
    assert sa._dirty_entries == set()

    # write to slice of an item
    sa[1][:4] <<= 0x0A
    assert sa._dirty_entries == {1}
    sa.flip()
    assert sa._dirty_entries == set()

    # read items
    assert sa[0] == 1
    assert sa[2] == 3
    assert sa[5] == 7
    assert sa[8] == 8
    assert sa._dirty_entries == {0, 2, 5, 8}
    sa.flip()
    assert sa._dirty_entries == set()


def test_SignalArray_read_mem():
    sa = SignalArray(Logic(8), 16)
    sa.read_mem([i for i in range(20)])
    _fake_in_sim(sa)
    assert sa[0] == 0
    assert sa[8] == 8
    assert sa[15] == 15
    sa.flip()
    assert sa[0] == 0
    assert sa[8] == 8
    assert sa[15] == 15

    sa.read_mem([-i for i in range(10)])
    assert sa[1] == b8(-1)
    assert sa[9] == b8(-9)
    assert sa[10] == 10
    assert sa[15] == 15

    with pytest.raises(ValueError, match=r"should be a list"):
        sa.read_mem(0)
    with pytest.raises(ValueError, match=r"too wide for 8 bits"):
        sa.read_mem([i * 100 for i in range(16)])
