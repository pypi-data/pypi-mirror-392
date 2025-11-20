# Tests for Bits
#

import pytest

from comopy.bits import *
from comopy.datatypes.bits import Bits, Bool, SignedBits
from comopy.datatypes.bits_data import BitsData
from comopy.datatypes.param_const import ParamConst
from comopy.hdl import Signal, SignalBundle, cat
from comopy.utils import BitsAssignError, BitsWidthError


def _fake_in_sim(signal: Signal):
    signal._assembled = True
    signal._simulating = True


def test_Bits_new():
    x = Bits(5)
    assert isinstance(x, Bits)
    assert type(x) is not Bits
    assert type(x) is type(Bits(5))  # noqa: E721
    assert type(x) is not type(Bits(6))  # noqa: E721
    assert x.__class__.__name__ == "Bits5"
    assert x.__class__.__module__ == Bits.__module__
    assert x.unsigned == 0
    assert isinstance(x, BitsData)
    assert x.data_bits is x
    assert x.nbits == 5
    assert x.mutable is False
    assert x.is_signed is False

    T = type(x)
    y = T(17)
    assert type(y) is T
    assert y.nbits == 5
    assert y.unsigned == 17

    y = T(mutable=True)
    assert type(y) is type(Bits(5, 7))  # noqa: E721
    assert y.nbits == 5
    assert y.unsigned == 0
    assert y.mutable is True

    with pytest.raises(TypeError, match=r"at least one argument: 'nbits'"):
        Bits()
    with pytest.raises(TypeError, match=r"integer for the 'nbits' argument"):
        Bits("5")


def test_BitsN():
    x = Bits4(2)
    assert type(x) is Bits4
    assert x.nbits == 4
    assert x.unsigned == 2

    x = b32(-15)
    assert type(x) is type(Bits(32))  # noqa: E721
    assert type(x) is b32
    assert x.nbits == 32
    assert x.unsigned == 0xFFFFFFF1
    assert x.signed == -15

    B260 = type(Bits(260))
    x = B260()
    assert x.__class__.__name__ == "Bits260"
    assert x.nbits == 260
    assert x.unsigned == 0

    with pytest.raises(ValueError, match=r"No Bits\(0\)"):
        Bits(0)
    with pytest.raises(ValueError, match=r"No Bits\(1026\)"):
        Bits(1026)


def test_Bits_init():
    x = Bits(2, mutable=True)
    assert x.nbits == 2
    assert x.unsigned == 0
    assert x.signed == 0
    assert x.changed() is False
    assert not x
    assert x.mutable is True

    x = Bits(2, 1)
    assert x.nbits == 2
    assert x.unsigned == 1
    assert x.signed == 1
    assert x.changed() is False
    assert int(x) == 1
    assert x

    x = Bits(2, 3)
    assert x.nbits == 2
    assert x.unsigned == 3
    assert x.signed == -1
    assert x.changed() is False
    assert int(x) == 3
    assert bool(x) is True

    x = Bits(2, -2)
    assert x.nbits == 2
    assert x.signed == -2
    assert x.unsigned == 0x2
    assert x.changed() is False
    assert int(x) == 0x2
    assert bool(x)

    x = Bits(8, b8(123))
    assert x.nbits == 8
    assert x.unsigned == 123
    assert x.changed() is False

    s = Signal(8)
    with pytest.raises(TypeError, match=r"Wrong type .* to construct Bits8"):
        x = Bits(8, s)

    # BitsData
    assert isinstance(x, BitsData)
    assert isinstance(x.data_bits, Bits)
    assert isinstance(x.data_bits, BitsData)
    assert x.data_bits is x

    # nbits range
    x = Bits(1)
    x = Bits(1025)
    with pytest.raises(ValueError, match=r"nbits in"):
        x = Bits(0)
    with pytest.raises(ValueError, match=r"nbits in"):
        x = Bits(1026)
    with pytest.raises(ValueError, match=r"too wide for"):
        x = Bits(2, 4)
    with pytest.raises(ValueError, match=r"mismatch .* Bits8 from Bits32"):
        x = Bits(8, b32(0))


def test_Bits_param():
    x = Bits(8, 0)
    assert isinstance(x.width_param, ParamConst)
    assert x.width_param.param_value == 8
    assert x.width_param.is_literal

    WIDTH = ParamConst(8, "WIDTH")
    x = Bits(WIDTH)
    assert type(x) is Bits8
    assert x.nbits == 8
    assert isinstance(x.width_param, ParamConst)
    assert x.width_param is WIDTH
    assert x.width_param.param_value == 8
    assert x.width_param.param_name == "WIDTH"
    assert not x.width_param.is_expr
    assert not x.width_param.is_literal

    COLS = ParamConst(4, "COLS")
    y = Bits(WIDTH * COLS)
    assert type(y) is b32
    assert y.nbits == 32
    assert isinstance(y.width_param, ParamConst)
    assert y.width_param.param_value == 32
    assert y.width_param.param_name == ""
    assert y.width_param.is_expr
    assert not y.width_param.is_literal
    assert y.width_param.op == ParamConst.Op.MUL
    assert y.width_param.left is WIDTH
    assert y.width_param.right is COLS

    with pytest.raises(TypeError, match=r"integer for the 'nbits' argument"):
        Bits(ParamConst("8"))
    with pytest.raises(ValueError, match=r"No Bits\(1026\)"):
        Bits(ParamConst(1026))

    z = Bits8(1)
    assert isinstance(z.width_param, ParamConst)
    assert z.width_param.param_value == 8
    assert z.width_param.is_literal


def test_Bits_S():
    # Positive value
    x = Bits(8, 100)
    sx = x.S
    assert isinstance(sx, SignedBits)
    assert isinstance(sx, Bits)
    assert type(sx) is not Bits8
    assert not sx.mutable
    assert sx.is_signed
    assert not x.is_signed
    assert sx.nbits == x.nbits
    assert sx.unsigned == x.unsigned
    assert sx.signed == 100
    assert int(sx) == 100
    assert int(x) == 100

    # Negative value
    y = Bits(8, 0x80)  # 128 in unsigned, -128 in signed
    sy = y.S
    assert not sy.mutable
    assert sy.is_signed
    assert sy.unsigned == 128
    assert sy.signed == -128
    assert int(sy) == -128
    assert int(y) == 128

    # Zero
    zero = Bits(8, 0)
    szero = zero.S
    assert not sy.mutable
    assert sy.is_signed
    assert int(szero) == 0

    # Expression
    assert (x & y).S.is_signed
    assert (x + y).S == -28
    assert (y - x).S == 28

    # Mutable Bits
    mut = Bits(8, 50, mutable=True)
    smut = mut.S
    assert mut.mutable
    assert not smut.mutable
    assert smut.is_signed
    assert int(smut) == 50

    # Modify original Bits
    mut /= 200
    smut2 = mut.S
    assert smut2 == -56
    assert smut == 50

    # String representation
    x = Bits(8, 0xAB)
    sx = x.S
    assert repr(sx) == "SignedBits8(0xAB)"

    # S property creates new instances each time
    a = Bits(8, 123)
    sa1 = a.S
    sa2 = a.S
    assert sa1 is not sa2
    assert sa1 == sa2
    assert type(sa1) is type(sa2)


def test_Bits_W():
    a = Bits(4, 0b1010)
    assert a.W == 4
    b = b8(0xAB)
    assert b.W == 8
    c = b32(0x12345678)
    assert c.W == 32
    d = Bits(260, 0)
    assert d.W == 260


def test_Bits_N():
    # Most significant bit (MSB)
    a = Bits(4, 0b1010)
    b = a.N
    assert type(b) is not Bits4
    assert type(b) is Bits1
    assert isinstance(b, Bits)
    assert b.nbits == 1
    assert b == 1  # MSB is 1

    # Different bit widths
    a = Bits(8, 0b11111111)
    assert a.N == 1
    a = Bits(8, 0b01111111)
    assert a.N == 0
    a = Bits(1, 0b1)
    assert a.N == 1
    a = Bits(1, 0b0)
    assert a.N == 0

    # Slices
    a = Bits(8, 0b11110000)
    assert a[:4].N == 0  # lower 4 bits: MSB is 0
    assert a[4:].N == 1  # upper 4 bits: MSB is 1


def test_Bits_AO():
    # All 1
    a = Bits(4, 0b1111)
    b = a.AO
    assert type(b) is not Bits4
    assert type(b) is Bits1
    assert isinstance(b, Bits)
    assert b.nbits == 1
    assert b == 1

    # Not all 1
    a = Bits(4, 0b1110)
    b = a.AO
    assert type(b) is not Bits4
    assert type(b) is Bits1
    assert isinstance(b, Bits)
    assert b.nbits == 1
    assert b == 0

    # All 0
    a = Bits(4, 0b0000)
    b = a.AO
    assert type(b) is not Bits4
    assert type(b) is Bits1
    assert isinstance(b, Bits)
    assert b.nbits == 1
    assert b == 0

    # Different bit widths
    a = Bits(8, 0b11111111)
    assert a.AO == 1
    a = Bits(8, 0b11111110)
    assert a.AO == 0
    a = Bits(1, 0b1)
    assert a.AO == 1
    a = Bits(1, 0b0)
    assert a.AO == 0

    # Slices
    a = Bits(8, 0b11110000)
    assert a[:4].AO == 0  # lower 4 bits: 0000
    assert a[4:].AO == 1  # upper 4 bits: 1111


def test_Bits_NZ():
    # All 0
    a = Bits(4, 0b0000)
    b = a.NZ
    assert type(b) is not Bits4
    assert type(b) is Bits1
    assert isinstance(b, Bits)
    assert b.nbits == 1
    assert b == 0

    # Not all 0 (has some 1s)
    a = Bits(4, 0b0001)
    b = a.NZ
    assert type(b) is not Bits4
    assert type(b) is Bits1
    assert isinstance(b, Bits)
    assert b.nbits == 1
    assert b == 1

    # All 1
    a = Bits(4, 0b1111)
    b = a.NZ
    assert type(b) is not Bits4
    assert type(b) is Bits1
    assert isinstance(b, Bits)
    assert b.nbits == 1
    assert b == 1

    # Different bit widths
    a = Bits(8, 0b00000000)
    assert a.NZ == 0
    a = Bits(8, 0b00000001)
    assert a.NZ == 1
    a = Bits(1, 0b0)
    assert a.NZ == 0
    a = Bits(1, 0b1)
    assert a.NZ == 1

    # Slices
    a = Bits(8, 0b11110000)
    assert a[:4].NZ == 0  # lower 4 bits: 0000
    assert a[4:].NZ == 1  # upper 4 bits: 1111


def test_Bits_P():
    # Even parity (even number of 1s)
    a = Bits(4, 0b1100)  # 2 ones
    b = a.P
    assert type(b) is not Bits4
    assert type(b) is Bits1
    assert isinstance(b, Bits)
    assert b.nbits == 1
    assert b == 0  # even parity

    # Odd parity (odd number of 1s)
    a = Bits(4, 0b1110)  # 3 ones
    b = a.P
    assert type(b) is not Bits4
    assert type(b) is Bits1
    assert isinstance(b, Bits)
    assert b.nbits == 1
    assert b == 1  # odd parity

    # All 0 (even parity)
    a = Bits(4, 0b0000)  # 0 ones
    b = a.P
    assert type(b) is not Bits4
    assert type(b) is Bits1
    assert isinstance(b, Bits)
    assert b.nbits == 1
    assert b == 0  # even parity

    # All 1 (even parity for 4 bits)
    a = Bits(4, 0b1111)  # 4 ones
    b = a.P
    assert type(b) is not Bits4
    assert type(b) is Bits1
    assert isinstance(b, Bits)
    assert b.nbits == 1
    assert b == 0  # even parity

    # Different bit widths
    a = Bits(8, 0b11100111)  # 6 ones (even)
    assert a.P == 0
    a = Bits(8, 0b11101111)  # 7 ones (odd)
    assert a.P == 1
    a = Bits(1, 0b0)  # 0 ones (even)
    assert a.P == 0
    a = Bits(1, 0b1)  # 1 one (odd)
    assert a.P == 1

    # Slices
    a = Bits(8, 0b11110001)
    assert a[:4].P == 1  # lower 4 bits: 0001 (odd parity)
    assert a[4:].P == 0  # upper 4 bits: 1111 (even parity)


def test_Bits_Z():
    # All 0
    a = Bits(4, 0b0000)
    b = a.Z
    assert type(b) is not Bits4
    assert type(b) is Bits1
    assert isinstance(b, Bits)
    assert b.nbits == 1
    assert b == 1

    # Not all 0 (has some 1s)
    a = Bits(4, 0b0001)
    b = a.Z
    assert type(b) is not Bits4
    assert type(b) is Bits1
    assert isinstance(b, Bits)
    assert b.nbits == 1
    assert b == 0

    # All 1
    a = Bits(4, 0b1111)
    b = a.Z
    assert type(b) is not Bits4
    assert type(b) is Bits1
    assert isinstance(b, Bits)
    assert b.nbits == 1
    assert b == 0

    # Different bit widths
    a = Bits(8, 0b00000000)
    assert a.Z == 1
    a = Bits(8, 0b00000001)
    assert a.Z == 0
    a = Bits(1, 0b0)
    assert a.Z == 1
    a = Bits(1, 0b1)
    assert a.Z == 0

    # Slices
    a = Bits(8, 0b11110000)
    assert a[:4].Z == 1  # lower 4 bits: 0000
    assert a[4:].Z == 0  # upper 4 bits: 1111


def test_Bits_ext():
    a = Bits(4, 0b0111)
    b = Bits(4, 0b1110)

    # Bits4 -> Bits5
    assert type(a.ext(5)) is Bits5
    assert a.ext(5) == b5(0b00111)
    assert type(b.ext(5)) is Bits5
    assert b.ext(5) == b5(0b01110)

    # Bits4 -> Bits8
    assert type(a.ext(8)) is Bits8
    assert a.ext(8) == b8(0b0000_0111)
    assert type(b.ext(8)) is Bits8
    assert b.ext(8) == b8(0b0000_1110)

    # Bits64 ->Bits65
    c = Bits(64, 0x7000_0000_1111_2222)
    d = Bits(64, 0xF000_0000_1111_2222)
    assert type(c.ext(65)) is Bits65
    assert c.ext(65) == Bits(65, 0x07000_0000_1111_2222)
    assert type(d.ext(65)) is Bits65
    assert d.ext(65) == Bits(65, 0x0F000_0000_1111_2222)

    # Signed extension
    assert type(a.S.ext(5)) is Bits5
    assert not a.S.ext(5).is_signed
    assert a.S.ext(5) == b5(0b00111)
    assert type(b.S.ext(8)) is Bits8
    assert not b.S.ext(8).is_signed
    assert b.S.ext(8) == b8(0b1111_1110)

    # Expression
    assert type((a + b).ext(6)) is Bits6
    assert (a + b).ext(6) == b6(0b000101)
    assert a.ext(5) + b.ext(5) == b5(0b10101)

    # Mutable Bits
    m = Bits(4, 0b1010, mutable=True)
    ext_m = m.ext(8)
    assert type(ext_m) is Bits8
    assert ext_m == b8(0b00001010)
    assert not ext_m.mutable


def test_Bits_index_hash():
    s = "0123456789"
    x = Bits8(5)
    assert s[x] == "5"
    assert x[b8(2)].unsigned == 1

    y = Bits8(5)
    assert y is not x
    assert hash(y) == hash(x)
    z = Bits8(5, mutable=True)
    assert z is not x
    assert hash(z) != hash(x)

    w = Bits8(5, mutable=True)
    assert hash(w) == hash(z)
    w <<= 1
    assert hash(w) != hash(z)  # w._next != z._next
    w.flip()
    w.save()
    w <<= 5
    w.flip()
    assert hash(w) != hash(z)  # w._last != z._last
    w.save()
    assert hash(w) == hash(z)


def test_Bits_string():
    assert str(Bits(16, 0xAB)) == "00AB"
    assert f"{Bits(15, 0x12)!r}" == "Bits15(0x0012)"
    assert f"{b8(0x12)!r}" == "Bits8(0x12)"
    assert f"{Bits(9, 0x34)!r}" == "Bits9(0x034)"
    assert b8(0x2).bin() == "0b00000010"
    assert b8(0xA).oct() == "0o012"
    assert Bits(15, 0xCD).hex() == "0x00CD"
    assert b8(0xAB).pattern() == "10101011"


def test_Bits_blocking_assign():
    # Bits /= Bits
    a = Bits4(0, mutable=True)
    b = Bits4(3)
    a.save()
    a /= b
    assert a.unsigned == 3
    assert a is not b
    assert a.changed() is True

    # object assignment
    a = b
    assert a is b

    # Bits /= int
    a = Bits4(0, mutable=True)
    aa = a
    a.save()
    a /= 1
    assert a is aa
    assert type(a) is Bits4
    assert a.unsigned == 1
    assert a.changed() is True
    a /= False
    assert a.unsigned == 0
    assert a.changed() is False

    # Bits /= Signal
    a = Bits4(0, mutable=True)
    s = Signal(4)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        a /= s
    _fake_in_sim(s)
    s /= 3
    a /= s
    assert a is not s
    assert a == 3

    a = Bits4(0)
    with pytest.raises(BitsAssignError, match=r"immutable Bits4"):
        a /= 1
    a = Bits4(0, mutable=True)
    b = Bits8(4)
    with pytest.raises(BitsWidthError, match=r"mismatch for assignment"):
        a /= b
    with pytest.raises(ValueError, match=r"too wide for"):
        a /= 16
    with pytest.raises(ValueError, match=r"too wide for"):
        a /= -9
    with pytest.raises(TypeError, match=r"Wrong RHS type .* for assignment"):
        a /= "4"
    with pytest.raises(TypeError, match=r"Wrong RHS type .* for assignment"):
        a /= 4.0


def test_Bits_nonblocking_assign():
    # Bits <<= Bits
    a = Bits4(0, mutable=True)
    b = Bits4(3)
    a.save()
    a <<= b
    assert a == 0
    assert a is not b
    assert a._next == 3
    assert a.changed() is False
    a.flip()
    assert a == 3
    assert a.changed() is True

    # Bits <<= int
    a = Bits4(0, mutable=True)
    aa = a
    a.save()
    a <<= 2
    assert a is aa
    assert type(a) is Bits4
    assert a == 0
    assert a.changed() is False
    a.flip()
    assert a == 2
    assert a.changed() is True
    a <<= True
    assert a == 2
    a.flip()
    a == 1

    # Bits <<= Signal
    a = Bits4(1, mutable=True)
    s = Signal(4)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        a <<= s
    _fake_in_sim(s)
    s /= 3
    a <<= s
    assert a is not s
    assert a == 1
    a.flip()
    assert a == 3

    a = Bits4(0)
    with pytest.raises(BitsAssignError, match=r"immutable Bits4"):
        a <<= 1
    a = Bits4(0, mutable=True)
    b = Bits8(4)
    with pytest.raises(BitsWidthError, match=r"mismatch for assignment"):
        a <<= b
    with pytest.raises(ValueError, match=r"too wide for"):
        a <<= 16
    with pytest.raises(ValueError, match=r"too wide for"):
        a <<= -9
    with pytest.raises(TypeError, match=r"Wrong RHS type .* for assignment"):
        a <<= "4"
    with pytest.raises(TypeError, match=r"Wrong RHS type .* for assignment"):
        a <<= 4.0


def test_Bits_slice():
    # get item & slice indices
    x = Bits(8, 0b10110110)
    assert isinstance(x[0], Bits)
    assert type(x[0]) is Bits1
    assert x[0].unsigned == 0
    assert x[1].unsigned == 1
    assert isinstance(x[0:1], Bits)
    assert type(x[0:1]) is Bits1
    assert x[0:1].unsigned == 0
    assert isinstance(x[4:8], Bits)
    assert type(x[4:8]) is Bits4
    assert x[4:8].unsigned == 0b1011

    with pytest.raises(IndexError, match=r"Bits8 index .* out of range"):
        x = x[8]
    with pytest.raises(IndexError, match=r"Bits8 index .* out of range"):
        x = x[-1]
    with pytest.raises(IndexError, match=r"Bits8 index .* wrong order"):
        x = x[3:1]
    with pytest.raises(IndexError, match=r"Bits8 index .* out of range"):
        x = x[-1:]
    with pytest.raises(IndexError, match=r"Bits8 index .* out of range"):
        x = x[:9]
    with pytest.raises(IndexError, match=r"Bits index cannot contain step"):
        x = x[::2]

    # set item
    x = Bits(8, 0b10110110, mutable=True)
    x[0] = 1
    assert x[0].unsigned == 1
    x[1] = b1(0)
    assert x[1].unsigned == 0
    x[4:7] = b3(0b101)
    assert x[4:7].unsigned == 0b101
    x[4:] = 0xF
    assert x[4:].unsigned == 0xF

    # blocking assignment
    x = Bits(4, 0b1010, mutable=True)
    s = Signal(4)
    _fake_in_sim(s)
    s /= x
    x[0] /= s[1]
    assert x == 0b1011
    x[1:3] /= s[2:4]
    assert x == 0b1101
    x[2:] /= s[:2]
    assert x == 0b1001
    x[:2] /= s[2:]
    assert x == 0b1010
    x[:] /= ~s
    assert x == 0b0101

    # errors
    x = Bits(8)
    with pytest.raises(BitsAssignError, match=r"slice of immutable Bits8"):
        x[0:2] = 1
    x = Bits(8, mutable=True)
    with pytest.raises(IndexError, match=r"Bits8 index .* out of range"):
        x[8] = 0
    with pytest.raises(IndexError, match=r"Bits8 index .* out of range"):
        x[-1] = 0
    with pytest.raises(IndexError, match=r"Bits8 index .* wrong order"):
        x[3:0] = 0  # `if key.stop` vs `if key.stop is not None`
    with pytest.raises(IndexError, match=r"Bits8 index .* wrong order"):
        x[3:1] = 0
    with pytest.raises(IndexError, match=r"Bits8 index .* out of range"):
        x[-1:] = 0
    with pytest.raises(ValueError, match=r"Value .* is too wide for 1 bit"):
        x[2] = 2
    with pytest.raises(ValueError, match=r"Value .* is too wide for 1 bit"):
        x[2] = b8(2)
    with pytest.raises(TypeError, match=r"Wrong RHS .* indexed assignment"):
        x[2] = "2"
    with pytest.raises(BitsWidthError, match=r"mismatch .* slice assign"):
        x[:4] = b3(2)
    with pytest.raises(BitsWidthError, match=r"mismatch .* slice assign"):
        x[:4] = b8(2)
    with pytest.raises(ValueError, match=r"is too wide for 8 bits"):
        x[:] = 256
    with pytest.raises(TypeError, match=r"Wrong RHS type .* slice assignment"):
        x[:] = "128"
    with pytest.raises(TypeError, match=r"Wrong RHS type .* slice assignment"):
        x[:2] = s[:2]


def test_Bits_complex_index():
    # Bits as index
    x = Bits(8, 0b10101100)
    idx = Bits(3, 0b101)
    assert type(x[idx]) is Bits1
    assert x[idx] == 1
    assert x[~idx] == 1
    assert x[idx + 1] == 0
    assert x[idx - 2] == 1

    # Signal as index
    sig = Signal(3)
    _fake_in_sim(sig)
    sig /= 0b101
    assert type(x[sig]) is Bits1
    assert x[sig] == 1
    assert x[~sig] == 1
    assert x[sig + 1] == 0
    assert x[sig - 2] == 1

    # Signal slice as index
    assert type(x[sig[:2]]) is Bits1
    assert x[sig[:2]] == 0
    assert x[~sig[:]] == 1
    assert x[sig[1:] + 1] == 1
    assert x[sig[1:] - 2] == 0

    # Signal bundle as index
    assert type(x[cat(sig[2], sig[0])]) is Bits1
    assert x[cat(sig[2], sig[0])] == 1


def test_Bits_part_select():
    x = Bits(32, 0x0, mutable=True)
    # constant base
    base = 0
    x[base, 32] = 0x1234_5678
    x[base, 16] = 0xAAAA
    assert x == 0x1234_AAAA
    assert x[base + 16, 16] == 0x1234
    # bits base
    base = Bits(32, 16, mutable=True)
    x[base, 16] = 0xFFFF
    assert x == 0xFFFF_AAAA
    base /= 15
    x[base, -16] = 0xCCCC
    assert x == 0xFFFF_CCCC

    # signal base
    base = Signal(5)
    _fake_in_sim(base)
    x = Bits(32, 0x0, mutable=True)
    base /= 7
    x[base, -4] /= 0xF
    assert x == 0xF0
    x2 = Bits(32, 0xABCD_1234, mutable=False)
    base /= 0
    x[base, 4] /= x2[base + 8, 4]
    assert x == 0xF2

    # bits width
    assert x[0, b5(4)] == 0x2
    assert x[7, b5(4), DESC] == 0xF
    assert x[0, b5(2) + b5(2)] == 0x2
    assert x[7, b5(2) + b5(2), DESC] == 0xF

    # errors
    x = Bits(8, 0x0, mutable=True)
    base /= 4
    with pytest.raises(IndexError, match=r"\(base, width\[, ASC\|DESC\]\)"):
        x[(base,)]
    with pytest.raises(IndexError, match=r"\(base, width\[, ASC\|DESC\]\)"):
        x[base, 2, 1, 1] /= 0
    with pytest.raises(IndexError, match=r"Invalid part-select base"):
        x["2", 2]
    with pytest.raises(IndexError, match=r"width must be an integer or Bits"):
        x[base, ParamConst(b8(4))] /= 0x4
    with pytest.raises(IndexError, match=r"width must be an integer or Bits"):
        x[base, ParamConst("hello")] /= 0x4
    with pytest.raises(IndexError, match=r"width must be an integer or Bits"):
        x[base, "2"] /= 0x4
    with pytest.raises(IndexError, match=r"direction must be a Bits1"):
        x[base, 2, b8(0)]
    with pytest.raises(IndexError, match=r"Descending .* negative width"):
        x[base, -2, DESC] /= 0x4
    with pytest.raises(IndexError, match=r"is out of range"):
        x[base, 33] /= 0x4
    with pytest.raises(IndexError, match=r"is out of range"):
        x[base, -8] /= 0x4
    with pytest.raises(IndexError, match=r"is out of range"):
        x[base, b5(8), DESC] /= 0x4
    with pytest.raises(IndexError, match=r"cannot be 0"):
        x[base, 0] /= 0


def test_Bits_arith():
    s1 = Signal(4)
    _fake_in_sim(s1)
    s1 /= 0b1001
    s2 = Signal(4)

    # __add__
    x = Bits(4, 0b1100)
    y = Bits(4, 0b0011)
    assert type(x + y) is Bits4
    assert type(x + s1) is Bits4
    assert type(x + 1) is Bits4
    assert x + y == b4(0b1111)
    assert x + s1 == b4(0b0101)
    assert x + 1 == b4(0b1101)
    assert x + 0b1000 == 0b0100
    assert x + 0b0100 == 0
    with pytest.raises(BitsWidthError, match=r"mismatch for \+"):
        x + b8(0)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        x + s2
    with pytest.raises(ValueError, match=r"Bits4 \+: .* too wide"):
        x + 16
    with pytest.raises(TypeError, match=r"Wrong type .* for \+"):
        x + 1.0

    # __radd__
    assert type(1 + y) is Bits4
    assert 1 + y == b4(0b0100)
    assert 0b1000 + x == 0b0100
    with pytest.raises(ValueError, match=r"Bits4 \+: .* too wide"):
        16 + x
    with pytest.raises(TypeError, match=r"Wrong type .* for \+"):
        1.0 + x

    # __sub__
    x = Bits(4, 0b1100)
    y = Bits(4, 0b0011)
    assert type(x - y) is Bits4
    assert type(x - s1) is Bits4
    assert type(x - 1) is Bits4
    assert x - y == b4(0b1001)
    assert x - s1 == b4(0b0011)
    assert x - 1 == b4(0b1011)
    assert x - 0b1000 == 0b0100
    assert y - x == b4(0b0111)
    assert x - 0b1110 == 0b1110
    with pytest.raises(BitsWidthError, match=r"mismatch for \-"):
        x - b8(0)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        x - s2
    with pytest.raises(ValueError, match=r"Bits4 \-: .* too wide"):
        x - 16
    with pytest.raises(TypeError, match=r"Wrong type .* for \-"):
        x - 1.0

    # __rsub__
    assert type(1 - y) is Bits4
    assert 1 - y == b4(0b1110)
    assert 0b1000 - x == 0b1100
    with pytest.raises(ValueError, match=r"Bits4 \-: .* too wide"):
        16 - x
    with pytest.raises(TypeError, match=r"Wrong type .* for \-"):
        1.0 - x

    # __mul__
    x = Bits(8, 7)
    y = Bits(8, 8)
    s1 = Signal(8)
    _fake_in_sim(s1)
    s1 /= 9
    s2 = Signal(8)
    assert type(x * y) is Bits8
    assert type(x * s1) is Bits8
    assert type(x * 1) is Bits8
    assert x * y == b8(56)
    assert x * s1 == b8(63)
    assert x * 1 == x
    assert x * 0b0 == 0
    assert y * 32 == b8(0)
    with pytest.raises(BitsWidthError, match=r"mismatch for \*"):
        x * b4(0)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        x * s2
    with pytest.raises(ValueError, match=r"Bits8 \*: .* too wide"):
        x * 256
    with pytest.raises(TypeError, match=r"Wrong type .* for \*"):
        x * 1.0

    # __rmul__
    assert type(1 * y) is Bits8
    assert type(0 * y) is Bits8
    assert 1 * y == b8(8)
    assert 2 * y == b8(16)
    with pytest.raises(ValueError, match=r"Bits8 \*: .* too wide"):
        256 * y
    with pytest.raises(TypeError, match=r"Wrong type .* for \*"):
        1.0 * y

    # __pos__
    x = Bits(8, 0b10101100)
    assert type(+x) is Bits8
    assert +x == b8(0b10101100)

    # __neg__
    assert type(-x) is Bits8
    assert -x == b8(0b01010100)
    assert -b8(0b00000000) == b8(0b00000000)


def test_Bits_bitwise():
    s1 = Signal(4)
    _fake_in_sim(s1)
    s1 /= 0b1001
    s2 = Signal(4)

    # __and__
    x = Bits(4, 0b1100)
    y = Bits(4, 0b0011)
    assert type(x & y) is Bits4
    assert type(x & s1) is Bits4
    assert type(x & 1) is Bits4
    assert not isinstance(x & 1, Bits1)
    assert isinstance(x & 1, Bits)
    assert x & y == b4(0b0000)
    assert x & s1 == b4(0b1000)
    assert x & 1 == 0
    with pytest.raises(BitsWidthError, match=r"mismatch for &"):
        x & b8(0)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        x & s2
    with pytest.raises(ValueError, match=r"Bits4 &: .* too wide"):
        x & 16
    with pytest.raises(TypeError, match=r"Wrong type .* for &"):
        x & 1.0

    # __rand__
    assert type(1 & y) is Bits4
    assert 1 & x == 0
    with pytest.raises(ValueError, match=r"Bits4 &: .* too wide"):
        16 & x
    with pytest.raises(TypeError, match=r"Wrong type .* for &"):
        1.0 & x

    # __or__
    x = Bits(4, 0b1100)
    y = Bits(4, 0b0011)
    assert type(x | y) is Bits4
    assert type(x | s1) is Bits4
    assert type(x | 1) is Bits4
    assert x | y == b4(0b1111)
    assert x | s1 == b4(0b1101)
    assert x | 1 == 0b1101
    with pytest.raises(BitsWidthError, match=r"mismatch for \|"):
        x | b8(0)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        x | s2
    with pytest.raises(ValueError, match=r"Bits4 \|: .* too wide"):
        x | 256

    # __ror__
    assert type(1 | y) is Bits4
    assert 1 | y == y
    with pytest.raises(ValueError, match=r"Bits4 \|: .* too wide"):
        256 | x
    with pytest.raises(TypeError, match=r"Wrong type .* for \|"):
        1.0 | x

    # __xor__
    x = Bits(4, 0b1100)
    y = Bits(4, 0b0011)
    assert type(x ^ y) is Bits4
    assert type(x ^ s1) is Bits4
    assert type(x ^ 1) is Bits4
    assert x ^ y == b4(0b1111)
    assert x ^ s1 == b4(0b0101)
    assert x ^ 1 == 0b1101
    with pytest.raises(BitsWidthError, match=r"mismatch for \^"):
        x ^ b8(0)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        x ^ s2
    with pytest.raises(ValueError, match=r"Bits4 \^: .* too wide"):
        x ^ 256
    with pytest.raises(TypeError, match=r"Wrong type .* for \^"):
        x ^ "1"

    # __rxor__
    assert type(1 ^ y) is Bits4
    assert 1 ^ y == 0b0010
    with pytest.raises(ValueError, match=r"Bits4 \^: .* too wide"):
        256 ^ x
    with pytest.raises(TypeError, match=r"Wrong type .* for \^"):
        object() ^ x

    # __invert__
    x = Bits(8, 0b10010110)
    assert type(~x) is Bits8
    assert ~x == b8(0b01101001)

    # on slice
    x = Bits(8, 0b10100101)
    assert not isinstance(x[:4] & x[4:], Bits8)
    assert type(x[:4] & x[4:]) is Bits4
    assert type(~x[:4]) is Bits4
    assert x[:4] | x[4:] == b4(0xF)
    assert x[4] ^ x[5] == 1
    assert x[:1] ^ x[0] == b1(0)
    with pytest.raises(BitsWidthError, match=r"mismatch for \|"):
        x[:4] | x[5:]
    with pytest.raises(BitsWidthError, match=r"mismatch for \^"):
        x[:2] ^ x[7]


def test_Bits_shift():
    s1 = Signal(4)
    _fake_in_sim(s1)
    s1 /= 4
    s2 = Signal(4)

    # __lshift__
    x = Bits(8, 0b10101100)
    y = Bits(3, 2)
    assert type(x << y) is Bits8
    assert type(x << s1) is Bits8
    assert type(x << 1) is Bits8
    assert x << y == b8(0b10110000)
    assert x << s1 == 0b11000000
    assert x << 1 == 0b01011000
    assert x << 0 == x
    assert x << 8 == 0
    assert x << b8(100) == 0
    with pytest.raises(ValueError, match=r"Signed shift amount"):
        x << b3(2).S
    with pytest.raises(ValueError, match=r"Signed shift amount"):
        x << -1
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        x << s2
    with pytest.raises(TypeError, match=r"Wrong type .* for <<"):
        x << 1.0
    with pytest.raises(TypeError, match=r"unsupported operand type"):
        4 << y

    # __rshift__
    assert type(x >> y) is Bits8
    assert type(x >> s1) is Bits8
    assert type(x >> 1) is Bits8
    assert x >> y == b8(0b00101011)
    assert x >> s1 == 0b00001010
    assert x >> 1 == 0b01010110
    assert x >> 0 == x
    assert x >> 8 == 0
    assert x >> b8(100) == 0
    with pytest.raises(ValueError, match=r"Signed shift amount"):
        x >> b3(2).S
    with pytest.raises(ValueError, match=r"Signed shift amount"):
        x >> -1
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        x >> s2
    with pytest.raises(TypeError, match=r"Wrong type .* for >>"):
        x >> 1.0
    with pytest.raises(TypeError, match=r"unsupported operand type"):
        4 >> y


def test_Bits_comparison():
    s1 = Signal(8)
    _fake_in_sim(s1)
    s1 /= 100
    s2 = Signal(8)

    # ==, !=
    x = Bits(8, 0xAB)
    assert type(x == b8()) is Bits1
    assert type(b8() != x) is Bits1
    assert not isinstance(b8() == x, Bits8)
    assert type(x == s1) is Bits1
    assert not isinstance(x != s1, Bits8)
    assert x == b8(0xAB)
    assert b8(0xCD) != x
    assert not (x == s1)
    assert x != s1
    assert (x == b8(0xAB)).unsigned == 1
    assert (x != b8(0xAB)).unsigned == 0
    assert (b8(0xCD) == x).unsigned == 0
    assert (b8(0xCD) != x).unsigned == 1
    assert type(x == 0) is Bits1
    assert type(x != object()) is Bits1
    assert (x != 0).unsigned == 1
    assert (x == 0xAB).unsigned == 1
    assert (0 == x).unsigned == 0
    assert (0xAB != x).unsigned == 0
    assert (object() != x).unsigned == 1
    x = Bits(8, 100)
    assert (x == s1).unsigned == 1
    assert (100.0 == x).unsigned == 0
    assert (x != 100.1).unsigned == 1
    with pytest.raises(BitsWidthError, match=r"mismatch .* comparison"):
        x == b4(0xF)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        x == s2
    with pytest.raises(ValueError, match=r"is too wide .* valid range:"):
        x == 0x100

    # ==, != pattern string
    x = Bits(8, 0b10101010)
    assert type(x == "1010_1010") is Bits1
    assert (x == "1010_1010").unsigned == 1
    assert "1010_1010" == x
    assert type(x != "1111_0000") is Bits1
    assert (x != "1111_0000").unsigned == 1
    assert "1111_0000" != x
    assert type(x == "1010_10??") is Bits1
    assert (x == "1010_10??").unsigned == 1
    assert "1010_10??" == x
    assert type(x != "1010_10??") is Bits1
    assert (x != "1010_10??").unsigned == 0
    assert not "1010_10??" != x
    with pytest.raises(ValueError, match=r"Empty bit pattern"):
        x == "__"
    with pytest.raises(ValueError, match=r"Invalid bit pattern"):
        x != "10XX_1010"
    with pytest.raises(ValueError, match=r"Invalid bit pattern"):
        x == "0xAB"
    with pytest.raises(ValueError, match=r"mismatch .* comparison"):
        "??_1010_101" == x

    # <, >
    x = Bits(8, 100)
    assert type(x < b8()) is Bits1
    assert type(x > b8()) is Bits1
    assert x < b8(200)
    assert b8(200) > x
    assert (x < b8(200)) == b1(1)
    assert (x > b8(200)) == b1(0)
    assert type(x < s1) is Bits1
    assert type(x > s1) is Bits1
    assert (x < s1) == b1(0)
    assert (x > s1) == b1(0)
    assert type(x < 100) is Bits1
    assert type(100 > x) is Bits1
    assert (x < 100) == b1(0)
    assert (x > 100) == b1(0)
    assert (100 < x) == b1(0)
    assert (100 > x) == b1(0)
    with pytest.raises(BitsWidthError, match=r"mismatch .* comparison"):
        x < b32(120)
    with pytest.raises(BitsWidthError, match=r"mismatch .* comparison"):
        b32(120) > x
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        x > s2
    with pytest.raises(ValueError, match=r"is too wide for.*valid range:"):
        x < 0x100
    with pytest.raises(TypeError, match=r"Wrong type .* Bits comparison"):
        x > "300"
    with pytest.raises(TypeError, match=r"Wrong type .* Bits comparison"):
        "0x120" < x

    # <=, >=
    x = Bits(8, 100)
    assert type(x <= b8()) is Bits1
    assert type(x >= b8()) is Bits1
    assert x <= b8(100)
    assert b8(100) >= x
    assert (x <= b8(100)) == b1(1)
    assert (b8(100) >= x) == b1(1)
    assert type(x <= s1) is Bits1
    assert type(x >= s1) is Bits1
    assert (x <= s1) == b1(1)
    assert (x >= s1) == b1(1)
    assert type(x <= 100) is Bits1
    assert type(100 >= x) is Bits1
    assert (x <= 100) == b1(1)
    assert (100 >= x) == b1(1)
    assert (x <= 10) == b1(0)
    assert (10 >= x) == b1(0)
    with pytest.raises(BitsWidthError, match=r"mismatch .* comparison"):
        x <= b32(120)
    with pytest.raises(BitsWidthError, match=r"mismatch .* comparison"):
        b32(120) >= x
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        x <= s2
    with pytest.raises(ValueError, match=r"is too wide for.*valid range:"):
        x <= 0x100
    with pytest.raises(TypeError, match=r"Wrong type .* Bits comparison"):
        "300" >= x
    with pytest.raises(TypeError, match=r"Wrong type .* Bits comparison"):
        "0x120" <= x


def test_Bits_pow():
    b = Bits(4, 0b1100)
    result = b**3
    assert isinstance(result, SignalBundle)
    assert result.nbits == 12  # 4 * 3
    assert result == 0b110011001100

    # zero replication
    result = b**0
    assert isinstance(result, SignalBundle)
    assert result.nbits == 0

    # single replication
    result = b**1
    assert isinstance(result, SignalBundle)
    assert result.nbits == 4
    assert result == 0b1100

    # with slice
    result = b[:2] ** 3
    assert isinstance(result, SignalBundle)
    assert result.nbits == 6
    assert result == 0b000000  # b[:2] is 0b00

    # errors
    with pytest.raises(TypeError, match=r"count must be an integer"):
        b**3.5
    with pytest.raises(TypeError, match=r"count must be an integer"):
        b ** "3"
    with pytest.raises(ValueError, match=r"count must be non-negative"):
        b**-1


def test_SignedBits_shift():
    # Left shift
    x = SignedBits(8, 0b01111111)  # 127
    assert x.signed == 127
    assert (x << 1).is_signed is False
    assert (x << 1).signed == -2
    assert (x << 1).unsigned == 254
    assert (x << 7).signed == -128
    assert (x << 8).signed == 0

    # Right shift (arithmetic shift)
    y = SignedBits(8, -128)  # 0b10000000
    assert y.signed == -128
    assert (y >> 1).is_signed is False
    assert (y >> 1).signed == -64
    assert (y >> 2).signed == -32
    assert (y >> 7).signed == -1
    assert (y >> 8).signed == -1

    # Right shift for positive value
    z = SignedBits(8, 0b01111111)  # 127
    assert z.signed == 127
    assert (z >> 1).is_signed is False
    assert (z >> 1).signed == 63
    assert (z >> 2).signed == 31
    assert (z >> 7).signed == 0
    assert (z >> 8).signed == 0

    # Right shift by 0
    assert (z >> 0).signed == 127
    assert (y >> 0).signed == -128

    # Right shift more than bit width
    assert (SignedBits(8, 1) >> 16).signed == 0
    assert (SignedBits(8, -1) >> 16).signed == -1

    # Errors
    with pytest.raises(ValueError, match=r"Signed shift amount"):
        x << -1
    with pytest.raises(ValueError, match=r"Signed shift amount"):
        x >> -1


def test_SignedBits_compare():
    s1 = SignedBits(8, 100)
    s2 = SignedBits(8, -100)
    u1 = Bits(8, 100)
    u2 = Bits(8, -100)

    assert s1.is_signed is True
    assert s2.is_signed is True
    assert u1.is_signed is False
    assert u2.is_signed is False
    assert type(s1) is not Bits8
    assert type(s2) is not Bits8
    assert type(u1) is Bits8
    assert type(u2) is Bits8
    assert (s1 + s2).is_signed is False
    assert (s1 - u1).is_signed is False

    assert s1 == u1
    assert u1 == 100
    assert s1 == 100
    assert s2 == u2
    assert u2 != -100
    assert s2 == -100

    assert s1 > s2
    assert s1 > 99
    assert s1 < 101
    assert s1 < u2
    assert s2 < s1
    assert s2 < -99
    assert s2 > -101
    assert s2 < u1
    assert u1 < u2


def test_Bool():
    a = b4(0b0011)
    assert type(Bool(a)) is Bits1
    assert Bool(a) == 1

    b = b4(0b1100)
    assert type(a and b) is Bits4
    assert (a and b) is b
    assert type(a or b) is Bits4
    assert (a or b) is a
    assert type(not a) is bool
    assert (not a) is False
    assert type(Bool(a and b)) is Bits1
    assert Bool(a and b) == 1
    assert type(Bool(a or b)) is Bits1
    assert Bool(a or b) == 1
    assert type(Bool(not a)) is Bits1
    assert Bool(not a) == 0

    a = b4(0b0000)
    b = b4(0b1111)
    assert type(a and b) is Bits4
    assert (a and b) is a
    assert type(a or b) is Bits4
    assert (a or b) is b
    assert type(not a) is bool
    assert (not a) is True
    assert type(Bool(a and b)) is Bits1
    assert Bool(a and b) == 0
    assert type(Bool(a or b)) is Bits1
    assert Bool(a or b) == 1
    assert type(Bool(not a)) is Bits1
    assert Bool(not a) == 1

    # not BitsData
    assert type(Bool(100)) is Bits1
    assert Bool(100) == 1
    assert type(Bool(True)) is Bits1
    assert Bool(True) == 1
    assert type(Bool(False)) is Bits1
    assert Bool(False) == 0
    assert type(Bool(None)) is Bits1
    assert Bool(None) == 0
    assert type(Bool([])) is Bits1
    assert Bool([]) == 0
    assert type(Bool({})) is Bits1
    assert Bool({}) == 0
    assert type(Bool("")) is Bits1
    assert Bool("") == 0
    assert Bool("False") == 1
    assert type(Bool(object())) is Bits1
    assert Bool(object()) == 1
