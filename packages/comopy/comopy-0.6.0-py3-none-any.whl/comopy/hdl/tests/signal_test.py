# Tests for Signal
#

import pytest

from comopy.bits import *
from comopy.datatypes import Bits, BitsData, SignedBits
from comopy.hdl.signal import Logic, Signal
from comopy.hdl.signal_array import SignalArray
from comopy.hdl.signal_bundle import SignalBundle
from comopy.hdl.signal_slice import SignalSlice
from comopy.utils import BitsAssignError, BitsWidthError


def _fake_in_sim(signal: Signal):
    signal._assembled = True
    signal._simulating = True


def test_Signal_init():
    s = Signal()
    assert s.data_type == Bits1
    assert issubclass(s.data_type, Bits)
    assert issubclass(s.data_type, BitsData)
    assert isinstance(s, BitsData)
    assert isinstance(s._data, Bits)
    assert s._data.nbits == 1
    assert s._data.unsigned == 0
    assert s._data.mutable is True
    assert s.nbits == 1
    assert s.mutable is True
    assert s.is_signed is False
    assert not s.assembled
    assert not s.simulating
    assert not s.is_module
    assert not s.is_package

    s = Signal(4)
    assert s.data_type == Bits4
    assert isinstance(s._data, Bits4)
    assert s._data.nbits == 4
    assert s.nbits == 4

    with pytest.raises(ValueError, match=r"No Bits\(0\)"):
        s = Signal(0)


def test_Signal_direction():
    s = Signal(4)
    assert s.direction is None
    assert s.is_port is False
    assert s.is_input_port is False
    assert s.is_output_port is False
    assert s.is_scalar_input is False

    p = s.input()
    assert p is s
    assert p.is_port is True
    assert p.is_input_port is True
    assert p.is_output_port is False
    assert p.is_scalar_input is False
    with pytest.raises(RuntimeError, match=r"Cannot change signal direction"):
        s.output()

    s = Signal().input()
    assert s.is_input_port
    assert s.is_scalar_input
    with pytest.raises(RuntimeError, match=r"Cannot change signal direction"):
        s.input()

    s = Signal(8).output()
    assert s.is_output_port
    with pytest.raises(RuntimeError, match=r"Cannot change signal direction"):
        s.input()


def test_Signal_create():
    s = Signal(4)
    c = s.create()
    assert type(c) is Signal
    assert not c.is_port
    assert c.data_type == Bits4
    assert isinstance(c._data, Bits4)
    assert c is not s
    assert c._data is not s._data

    # Logic
    logic = Logic(8)
    c = logic.create()
    assert type(c) is Logic
    assert not c.is_port
    assert c.data_type == Bits8
    assert isinstance(c._data, Bits8)
    assert c is not logic
    assert c._data is not logic._data

    # port
    input = Logic(8).input()
    c = input.create()
    assert type(c) is Logic
    assert c.is_input_port
    assert not c.is_scalar_input
    assert c.data_type == Bits8
    assert isinstance(c._data, Bits8)
    assert c is not input
    assert c._data is not input._data

    # flipped port
    c = input.create(flipped=True)
    assert type(c) is Logic
    assert c.is_output_port
    assert not c.is_input_port
    assert c.data_type == Bits8
    assert isinstance(c._data, Bits8)
    assert c is not input
    assert c._data is not input._data

    # link
    a = Logic(8)
    b = a.create()
    c = a.create(b)
    assert type(c) is Logic
    assert not c.is_port
    assert c.data_type == Bits8
    assert c is not a
    assert c is not b
    _fake_in_sim(a)
    _fake_in_sim(b)
    _fake_in_sim(c)
    a /= 0xAB
    b /= 0xCD
    assert a == 0xAB
    assert b == 0xCD
    assert c == 0xCD
    c /= 0xEF
    assert a == 0xAB
    assert b == 0xEF
    assert c == 0xEF


def test_Signal_matmul():
    s = Signal(8)
    array = s @ 10
    assert isinstance(array, SignalArray)
    assert array.size == 10
    assert len(array) == 10

    # check elements
    for i in range(10):
        elem = array[i]
        assert isinstance(elem, Signal)
        assert elem.nbits == 8
        assert elem is not s  # should be different instances
        assert type(elem) is type(s)

    # with Logic signal
    logic = Logic(4)
    array = logic @ 5
    assert isinstance(array, SignalArray)
    assert array.size == 5
    for i in range(5):
        elem = array[i]
        assert isinstance(elem, Logic)
        assert elem.nbits == 4

    # single element array
    array = s @ 1
    assert isinstance(array, SignalArray)
    assert array.size == 1

    # errors
    with pytest.raises(TypeError, match=r"Array size must be an integer"):
        s @ 3.5
    with pytest.raises(TypeError, match=r"Array size must be an integer"):
        s @ "10"
    with pytest.raises(ValueError, match=r"Array size must be positive"):
        s @ 0
    with pytest.raises(ValueError, match=r"Array size must be positive"):
        s @ -1


def test_Signal_hdl_interfaces():
    a = Signal(4)
    _fake_in_sim(a)
    b = Signal(4)
    _fake_in_sim(b)

    # .S
    a /= 5
    assert a.data_bits == b4(5)
    assert a == 5
    assert isinstance(a.S, SignedBits)
    assert a.S == 5
    a /= -1
    assert a.data_bits == b4(15)
    assert a == 15
    assert isinstance(a.S, SignedBits)
    assert a.S == -1

    # .W
    assert type(a.W) is int
    assert a.W == 4

    # .N
    a /= 0b1000
    assert type(a.N) is Bits1
    assert a.N == 1
    a /= 0b0111
    assert a.N == 0
    a /= 0
    assert a.N == 0
    a /= -1
    assert a.N == 1

    # .AO
    a /= 0b1111
    assert type(a.AO) is Bits1
    assert a.AO == 1
    a /= 0b1011
    assert a.AO == 0
    a /= 0
    assert a.AO == 0
    a /= -1
    assert a.AO == 1

    # .NZ
    a /= 0b0010
    assert type(a.NZ) is Bits1
    assert a.NZ == 1
    a /= 0b0000
    assert a.NZ == 0
    a /= 0
    assert a.NZ == 0
    a /= -1
    assert a.NZ == 1

    # .P
    a /= 0b0010
    assert type(a.P) is Bits1
    assert a.P == 1
    a /= 0b0101
    assert a.P == 0
    a /= 0
    assert a.P == 0
    a /= -1
    assert a.P == 0

    # .Z
    a /= 0b0000
    assert type(a.Z) is Bits1
    assert a.Z == 1
    a /= 0b0010
    assert a.Z == 0
    a /= 0
    assert a.Z == 1
    a /= -1
    assert a.Z == 0

    # .ext()
    a /= 5
    assert type(a.ext(8)) is Bits8
    assert a.ext(8) == b8(5)
    a /= -1
    assert a.ext(8) == b8(0x0F)
    assert a.ext(16).W == 16


def test_Signal_bool():
    s = Signal()
    assert bool(s) is True

    _fake_in_sim(s)
    assert bool(s) is False
    s /= 1
    assert bool(s) is True


def test_Signal_hash():
    a = Signal(8)
    _fake_in_sim(a)
    b = Bits8(0xAB)
    a /= b
    c = Signal(8)
    _fake_in_sim(c)
    c /= a
    # hash by id, implemented in BitsData
    s = set()
    s.add(a)
    assert a in s
    assert b not in s
    assert c not in s
    d = a
    assert d in s


def test_Signal_blocking_assign():
    a = Signal(4)
    _fake_in_sim(a)
    b = Signal(4)
    _fake_in_sim(b)
    a.save()
    b.save()
    a /= 5
    b /= a
    assert a.data_bits == b4(5)
    assert a == 5
    assert a.changed() is True
    assert b.data_bits == b4(5)
    assert b == 5
    assert b.changed() is True
    assert str(a) == "Signal{Bits4(0x5)}"

    a /= b4(-1)
    assert a.data_bits == b4(15)
    assert a == 15

    c = Signal(8)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        c.data_bits
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        c /= a
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        c.save()
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        c.changed()
    _fake_in_sim(c)
    with pytest.raises(BitsWidthError, match=r"Width mismatch"):
        c /= a


def test_Signal_nonblocking_assign():
    a = Signal(4)
    _fake_in_sim(a)
    a /= 1
    b = Signal(4)
    _fake_in_sim(b)
    b /= 2
    a.save()
    b.save()
    a <<= 5
    b <<= a
    assert a.data_bits == b4(1)
    assert b.data_bits == b4(2)
    assert a == 1
    assert b == 2
    assert a.changed() is False
    assert b.changed() is False
    a.flip()
    b.flip()
    assert a == 5
    assert b == 1
    assert a.changed() is True
    assert b.changed() is True

    c = Signal(8)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        c <<= a
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        c.flip()
    _fake_in_sim(c)
    with pytest.raises(BitsWidthError, match=r"Width mismatch"):
        c <<= a


def test_Signal_inplace_assign():
    a = Signal(4)
    _fake_in_sim(a)

    with pytest.raises(BitsAssignError, match=r"wrong assignment type"):
        a += 1
    with pytest.raises(BitsAssignError, match=r"wrong assignment type"):
        a -= 1
    with pytest.raises(BitsAssignError, match=r"wrong assignment type"):
        a *= 1
    with pytest.raises(BitsAssignError, match=r"wrong assignment type"):
        a //= 1
    with pytest.raises(BitsAssignError, match=r"wrong assignment type"):
        a %= 1
    with pytest.raises(BitsAssignError, match=r"wrong assignment type"):
        a **= 1
    with pytest.raises(BitsAssignError, match=r"wrong assignment type"):
        a &= 1
    with pytest.raises(BitsAssignError, match=r"wrong assignment type"):
        a |= 1
    with pytest.raises(BitsAssignError, match=r"wrong assignment type"):
        a ^= 1
    with pytest.raises(BitsAssignError, match=r"wrong assignment type"):
        a >>= 1


def test_Signal_link():
    a = Signal(8)
    b = Signal(8, link=a)
    _fake_in_sim(a)
    _fake_in_sim(b)

    # /=
    assert b is not a
    a /= 0b10101010
    assert b == 0b10101010
    b /= 0b01010101
    assert a == 0b01010101
    a /= 0xDB
    assert str(a) == "Signal{Bits8(0xDB)}"
    assert str(b) == "Signal{Bits8(0xDB)}"

    # <<=
    b <<= 0b11110000
    assert a == 0xDB
    a.flip()
    assert a == 0b11110000
    assert b == 0b11110000
    a <<= 0b00001111
    assert b == 0b11110000
    a.flip()
    assert b == 0b00001111
    assert a == 0b00001111

    # slice
    b[:4] /= 0b1010
    assert b == 0b00001010
    assert a == 0b00001010
    a[4:] /= 0b1010
    assert a == 0b10101010
    assert b == 0b10101010
    c = Signal(4, a[4:])
    _fake_in_sim(c)
    assert c == 0b1010
    c /= 0b1111
    assert a == 0b11111010
    assert b == 0b11111010

    with pytest.raises(ValueError, match=r"Incompatible bit width .* link"):
        Signal(4, a)


def test_Signal_slice():
    # get item
    a = Signal(8)
    _fake_in_sim(a)
    a /= 0b10010110
    assert isinstance(a[0], SignalSlice)
    assert isinstance(a[2:4], SignalSlice)
    assert type(a[:4] & a[4:]) is Bits4
    assert a[:4] | a[4:] == b4(0b1111)
    assert ~a[0] == b1(1)
    assert ~a[:2] == b2(0b01)

    # set item
    aa = a
    a[0] /= 1
    assert a is aa
    assert a == 0b10010111
    a[2:6] /= a[:4] & a[4:]
    assert a is aa
    assert a == 0b10000111

    # TODO @=
    # with pytest.raises(RuntimeError, match=r"@= .* assembly-time API"):
    #     a[2] @= a[4]
    with pytest.raises(BitsAssignError, match=r"wrong assignment type."):
        a[2] = a[4]
    with pytest.raises(BitsAssignError, match=r"wrong assignment type."):
        a[2:4] = 1
    with pytest.raises(BitsAssignError, match=r"wrong assignment type."):
        a[2] += a[4]
    with pytest.raises(BitsAssignError, match=r"wrong assignment type."):
        a[2:4] *= 1

    # Exceptional case, side effect of supporting `a[] /= ...`
    a[2] = a[2]
    assert a is aa
    assert a == 0b10000111
    a[2:6] = a[2:6]
    assert a is aa
    assert a == 0b10000111
    t = a[:]
    assert t is not aa
    assert type(t) is SignalSlice
    a[:] = t
    assert a is aa
    assert a == 0b10000111
    with pytest.raises(BitsAssignError, match=r"wrong assignment type."):
        a[:] = t & 0b1111
    a[:] = a[:]
    assert a is aa
    assert a == 0b10000111
    with pytest.raises(BitsAssignError, match=r"wrong assignment type."):
        a[:] = a[:] | -1

    # Signal as index
    b = Signal(3)
    _fake_in_sim(b)
    b /= 2
    assert a[b] == 1


def test_Signal_part_select():
    # get item
    a = Signal(8)
    _fake_in_sim(a)
    base = Signal(3)
    _fake_in_sim(base)
    a /= 0b1011_0111
    assert a[4, 4] == b4(0b1011)
    base /= 5
    assert a[base, 2] == b2(0b01)
    assert a[base, -3] == b3(0b110)

    # set item
    base /= 0
    a[base, 3] /= b3(0b010)
    assert a == 0b1011_0010
    base /= 4
    a[base, -2] /= b2(0b01)
    assert a == 0b1010_1010


def test_Signal_arith():
    a = Signal(8)
    _fake_in_sim(a)
    b = Signal(8)
    _fake_in_sim(b)
    a /= 123
    b /= 234

    # __add__, __radd__
    assert type(a + b) is Bits8
    assert type(a + b8(0)) is Bits8
    assert type(b8(0) + b) is Bits8
    assert type(a + 1) is Bits8
    assert type(1 + b) is Bits8
    assert a + b == 357 - 256
    assert a + b8(0) == 123
    assert b8(0) + b == 234
    assert a + 1 == 124
    assert 1 + b == 235
    with pytest.raises(TypeError, match=r"Wrong type"):
        a + object()

    # __sub__, __rsub__
    assert type(a - b) is Bits8
    assert type(a - b8(0)) is Bits8
    assert type(b8(0) - b) is Bits8
    assert type(a - 1) is Bits8
    assert type(1 - b) is Bits8
    assert a - b == -111 + 256
    assert a - b8(0) == 123
    assert b8(0) - b == -234 + 256
    assert a - 1 == 122
    assert 1 - b == -233 + 256
    with pytest.raises(TypeError, match=r"Wrong type"):
        object() - a

    # __mul__, __rmul__
    assert type(a * b) is Bits8
    assert type(a * b8(0)) is Bits8
    assert type(b8(0) * b) is Bits8
    assert type(a * 1) is Bits8
    assert type(1 * b) is Bits8
    assert a * b == 123 * 234 % 256
    assert a * b8(0) == b8(0)
    assert b8(0) * b == 0
    assert a * 1 == 123
    assert 1 * b == 234
    with pytest.raises(TypeError, match=r"Wrong type"):
        a * object()

    # __pos__, __neg__
    assert type(+a) is Bits8
    assert type(-a) is Bits8
    assert +a == 123
    assert -a == -123 + 256  # Two's complement representation

    # not in simulation
    c = Signal(4)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        c + 1
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        2 - c
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        c * b8(0)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        b8(0) * c


def test_Signal_bitwise():
    a = Signal(8)
    _fake_in_sim(a)
    b = Signal(8)
    _fake_in_sim(b)
    a /= 0b10001100
    b /= 0b01110011

    # __and__, __rand__
    assert type(a & b) is Bits8
    assert type(a & b8(0)) is Bits8
    assert type(b8(0) & a) is Bits8
    assert type(a & 1) is Bits8
    assert type(1 & b) is Bits8
    assert a & b == 0
    assert a & b8(0) == b8(0)
    assert b8(0) & b == b8(0)
    assert a & 1 == b8(0)
    assert 1 & b == 1
    with pytest.raises(TypeError, match=r"Wrong type"):
        a & object()

    # __or__, __ror__
    assert type(a | b) is Bits8
    assert type(a | b8(0)) is Bits8
    assert type(b8(0) | b) is Bits8
    assert type(a | 1) is Bits8
    assert type(1 | b) is Bits8
    assert a | b == 0xFF
    assert a | b8(0) == a
    assert b8(0) | b == b
    assert a | 1 == b8(0b10001101)
    assert 1 | b == b
    with pytest.raises(TypeError, match=r"Wrong type"):
        object() | a

    # __xor__, __rxor__
    assert type(a ^ b) is Bits8
    assert type(a ^ b8(0)) is Bits8
    assert type(b8(0) ^ b) is Bits8
    assert type(a ^ 1) is Bits8
    assert type(1 ^ b) is Bits8
    assert a ^ b == 0xFF
    assert a ^ b8(-1) == ~a
    assert b8(-1) ^ b == ~b
    assert a ^ 1 == b8(0b10001101)
    assert 1 ^ b == 0b01110010
    with pytest.raises(TypeError, match=r"Wrong type"):
        object() ^ a

    # __invert__
    assert type(~a) is Bits8
    assert ~a == b8(0b01110011)
    assert ~a == b

    # not in simulation
    c = Signal(4)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        c & 1
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        2 | c
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        ~c
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        c & b8(0)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        b8(0) ^ c


def test_Signal_shift():
    a = Signal(8)
    _fake_in_sim(a)
    b = Signal(4)
    _fake_in_sim(b)
    a /= 0b10101100
    b /= 4

    # __lshift__
    assert type(a << b) is Bits8
    assert type(a << b2(2)) is Bits8
    assert type(a << 1) is Bits8
    assert type(b8(1) << b) is Bits8
    assert a << b == b8(0b11000000)
    assert a << b2(2) == 0b10110000
    assert a << 1 == 0b01011000
    assert b8(1) << b == b8(0b00010000)
    assert a << 0 == a
    assert a << 8 == 0
    assert a << b16(100) == 0
    with pytest.raises(TypeError, match=r"Wrong type"):
        a << object()

    # __rshift__
    assert type(a >> b) is Bits8
    assert type(a >> b2(2)) is Bits8
    assert type(a >> 1) is Bits8
    assert type(b8(0xFF) >> b) is Bits8
    assert a >> b == b8(0b00001010)
    assert a >> b2(2) == 0b00101011
    assert a >> 1 == 0b01010110
    assert b8(0xFF) >> b == b8(0b00001111)
    assert a >> 0 == a
    assert a >> 8 == 0
    assert a >> b16(100) == 0
    with pytest.raises(TypeError, match=r"Wrong type"):
        a >> object()

    # not in simulation
    c = Signal(4)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        c << 1
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        b8(2) >> c
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        c << b8(1)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        b8(1) >> c


def test_Signal_eq_ne():
    # compare to bits
    a = Signal(8)
    _fake_in_sim(a)
    b = Bits8(0xAB)
    a /= b
    assert type(a == 0xAB) is Bits1
    assert type(a == b) is Bits1
    assert a == 0xAB
    assert a == b
    assert a == b8(0xAB)  # Bits==Signal is Bits's __eq__
    assert 0xAB == a
    assert b == a
    assert b8(0xAB) == a
    # compare to signal
    c = Signal(8)
    _fake_in_sim(c)
    c /= a
    assert type(a == c) is Bits1
    assert type(a != c) is Bits1
    assert a == c
    assert a == a
    assert (a != c) == FALSE
    assert (a == a) == TRUE
    # compare to not signal, implemented in Bits
    assert (a == object()) == FALSE
    assert (object() != a) == TRUE

    # not in simulation
    a = Signal(8)
    b = Bits8(0xAB)
    c = Signal(8)
    a._data /= b
    c._data /= b
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        a == b
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        b != a
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        a != c
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        a == a


def test_Signal_comparison():
    a = Signal(8)
    _fake_in_sim(a)
    b = Signal(8)
    _fake_in_sim(b)
    a /= 124
    b /= a
    assert type(a > b) is Bits1
    assert (a > b) == FALSE
    assert type(a > b8(123)) is Bits1
    assert (a > b8(123)) == TRUE
    assert type(a < b) is Bits1
    assert (a < b) == FALSE
    assert type(a < 123) is Bits1
    assert (a < 123) == FALSE
    assert type(a >= b) is Bits1
    assert (a >= b) == TRUE
    assert type(b8(123) >= a) is Bits1
    assert (b8(123) >= b) == FALSE
    assert type(a <= b) is Bits1
    assert (a <= b) == TRUE
    assert type(123 <= a) is Bits1
    assert (123 <= a) == TRUE

    # not in simulation
    a = Signal(8)
    b = Signal(8)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        a > b
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        1 <= b
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        a < b8(0)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        b8(0) >= b


def test_Signal_rep():
    s = Signal(4)
    result = s**3
    assert isinstance(result, SignalBundle)
    assert result.nbits == 12  # 4 * 3

    # zero replication
    result = s**0
    assert isinstance(result, SignalBundle)
    assert result.nbits == 0

    # single replication
    result = s**1
    assert isinstance(result, SignalBundle)
    assert result.nbits == 4

    # Logic type
    logic = Logic(8)
    result = logic**2
    assert isinstance(result, SignalBundle)
    assert result.nbits == 16  # 8 * 2

    # errors
    with pytest.raises(TypeError, match=r"count must be an integer"):
        s**3.5
    with pytest.raises(TypeError, match=r"count must be an integer"):
        s ** "3"
    with pytest.raises(ValueError, match=r"count must be non-negative"):
        s**-1
