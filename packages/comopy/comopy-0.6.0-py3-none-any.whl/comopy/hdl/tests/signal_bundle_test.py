# Tests for SignalBundle
#

import pytest

from comopy.bits import *
from comopy.datatypes import Bits, BitsData
from comopy.hdl.signal import Signal
from comopy.hdl.signal_bundle import SignalBundle, _count_bits_parts, cat, rep
from comopy.hdl.signal_slice import SignalSlice
from comopy.utils import BitsAssignError, BitsWidthError


def _fake_in_sim(signal):
    signal._assembled = True
    signal._simulating = True


def test_SignalBundle_init():
    b1 = Bits(1)
    b2 = Bits(2)
    b3 = Bits(3)
    bundle = SignalBundle(b1, b2, b3)
    assert isinstance(bundle, BitsData)
    assert bundle.data_bits == 0
    assert bundle.nbits == 6
    assert not bundle.mutable
    assert bundle == 0

    s1 = Signal()
    s2 = Signal(8)
    s3 = Signal(3)
    bundle = SignalBundle(s1, s2, s3)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        bundle == 0

    _fake_in_sim(s1)
    _fake_in_sim(s2)
    _fake_in_sim(s3)
    bundle = SignalBundle(s1, s2, s3)
    assert isinstance(bundle, BitsData)
    assert bundle.nbits == 12
    assert bundle.mutable

    bundle = SignalBundle(s1, s2, Bits3(3))
    assert isinstance(bundle, BitsData)
    assert bundle.nbits == 12
    assert not bundle.mutable

    with pytest.raises(TypeError, match=r"All parts .* constant or Signal"):
        SignalBundle(b1, b2, 3)
    with pytest.raises(TypeError, match=r"All parts .* constant or Signal"):
        SignalBundle([b1, b2])


def test_SignalBundle_empty():
    bundle = SignalBundle()
    assert bundle.nbits == 0
    assert bundle.mutable
    with pytest.raises(ValueError, match=r"empty signal bundle"):
        bundle.data_bits

    # empty bundle in a bundle
    b1 = Bits(1, 1, mutable=True)
    b2 = Bits(2, 2, mutable=True)
    b3 = Bits(3, 3, mutable=True)
    bundle = SignalBundle(b1, SignalBundle(), b2, b3)
    assert bundle.nbits == 6
    assert bundle.mutable
    assert len(bundle._parts) == 4
    assert bundle._parts[1].nbits == 0
    assert bundle == 0b110011
    bundle /= 0b101010
    assert bundle == 0b101010


def test_SignalBundle_data():
    b1 = Bits(1, 1)
    bundle = SignalBundle(b1)
    assert type(bundle.data_bits) is Bits1
    assert bundle.data_bits == b1

    b1 = Bits(1, 1)
    b2 = Bits(2, 2)
    b3 = Bits(3, 3, mutable=True)
    bundle = SignalBundle(b1, b2, b3)
    assert type(bundle.data_bits) is Bits6
    assert bundle.data_bits == 0b110011
    assert Bits6(0b110011) == bundle
    assert type(Bits6(0b111000) & bundle) is Bits6
    assert Bits6(0b111000) & bundle == 0b110000
    assert type(Bits6(0b000111) | bundle) is Bits6
    assert Bits6(0b000111) | bundle == 0b110111
    assert type(Bits6(0b000111) ^ bundle) is Bits6
    assert Bits6(0b000111) ^ bundle == 0b110100

    # evaluation order
    assert bundle.data_bits == 0b110011
    b3 /= 0b101
    assert bundle.data_bits == 0b110101
    b3[1:] = 0b01
    assert bundle.data_bits == 0b110011
    b3 = 0b110  # new int
    assert not isinstance(b3, Bits)
    assert bundle.data_bits == 0b110011

    s6 = Signal(6)
    _fake_in_sim(s6)
    s6 /= bundle
    assert s6 == 0b110011
    assert type(s6 & bundle) is Bits6
    assert s6 & bundle == 0b110011
    assert type(s6 | bundle) is Bits6
    assert s6 | bundle == 0b110011
    assert type(s6 ^ bundle) is Bits6
    assert s6 ^ bundle == 0b000000

    with pytest.raises(ValueError, match=r"mismatch .* Bits6, RHS Bits3"):
        s6 /= SignalBundle(b1, b2)


def test_SignalBundle_blocking_assign():
    b1 = Bits(1, 1, mutable=True)
    b2 = Bits(2, 2, mutable=True)
    b3 = Bits(3, 3, mutable=True)
    bundle = SignalBundle(b1, b2, b3)
    assert bundle.mutable
    bundle /= 0b011001
    assert bundle == 0b011001
    assert b1 == 0b0
    assert b2 == 0b11
    assert b3 == 0b001
    bundle /= 1
    assert bundle == 1
    assert b1 == 0b0
    assert b2 == 0b00
    assert b3 == 0b001

    with pytest.raises(BitsWidthError, match=r"mismatch .* Bits6, RHS Bits3"):
        bundle /= Bits3()
    with pytest.raises(ValueError, match=r"too wide for 6 bits"):
        bundle /= 128
    with pytest.raises(TypeError, match=r"Wrong RHS type .* for assignment"):
        bundle /= "128"

    s1 = Signal(1)
    s2 = Signal(2)
    s3 = Signal(3)
    _fake_in_sim(s1)
    _fake_in_sim(s2)
    _fake_in_sim(s3)
    bundle = SignalBundle(s1, s2, s3)
    bundle /= 0b011001
    assert bundle == 0b011001
    assert s1 == 0b0
    assert s2 == 0b11
    assert s3 == 0b001
    bundle /= 1
    assert bundle == 1
    assert s1 == 0b0
    assert s2 == 0b00
    assert s3 == 0b001

    # slice in bundle
    bundle = SignalBundle(s1, s2[1], s3[:2])
    assert bundle.nbits == 4
    assert bundle.mutable
    assert bundle == 0b0001
    bundle /= 0b1010
    assert bundle == 0b1010
    assert s1 == 0b1
    assert s2 == 0b00
    assert s3 == 0b010

    # const in bundle
    bundle = SignalBundle(s1, s2, Bits(3, 3))
    assert bundle.nbits == 6
    assert not bundle.mutable
    assert bundle == 0b100011
    with pytest.raises(BitsAssignError, match=r"immutable signal bundle"):
        bundle /= 0b101010


def test_SignalBundle_nonblocking_assign():
    b1 = Bits(1, 1, mutable=True)
    b2 = Bits(2, 2, mutable=True)
    b3 = Bits(3, 3, mutable=True)
    bundle = SignalBundle(b1, b2, b3)
    assert bundle.mutable
    assert bundle == 0b110011
    bundle <<= 0b011001
    assert bundle == 0b110011
    b1.flip()
    b2.flip()
    b3.flip()
    assert bundle == 0b011001
    assert b1 == 0b0
    assert b2 == 0b11
    assert b3 == 0b001
    bundle <<= 1
    assert bundle == 0b011001
    b1.flip()
    b2.flip()
    b3.flip()
    assert bundle == 1
    assert b1 == 0b0
    assert b2 == 0b00
    assert b3 == 0b001

    with pytest.raises(BitsWidthError, match=r"mismatch .* Bits6, RHS Bits3"):
        bundle <<= Bits3()
    with pytest.raises(ValueError, match=r"too wide for 6 bits"):
        bundle <<= 128
    with pytest.raises(TypeError, match=r"Wrong RHS type .* for assignment"):
        bundle <<= "128"

    s1 = Signal(1)
    s2 = Signal(2)
    s3 = Signal(3)
    _fake_in_sim(s1)
    _fake_in_sim(s2)
    _fake_in_sim(s3)
    bundle = SignalBundle(s1, s2, s3)
    bundle /= 0b110011
    assert bundle == 0b110011
    bundle <<= 0b011001
    assert bundle == 0b110011
    s1.flip()
    s2.flip()
    s3.flip()
    assert bundle == 0b011001
    assert s1 == 0b0
    assert s2 == 0b11
    assert s3 == 0b001
    bundle <<= 1
    assert bundle == 0b011001
    s1.flip()
    s2.flip()
    s3.flip()
    assert bundle == 1
    assert s1 == 0b0
    assert s2 == 0b00
    assert s3 == 0b001

    # slice in bundle
    bundle = SignalBundle(s1, s2[1], s3[:2])
    assert bundle.nbits == 4
    assert bundle.mutable
    assert bundle == 0b0001
    bundle <<= 0b1010
    assert bundle == 0b0001
    s1.flip()
    s2.flip()
    s3.flip()
    assert bundle == 0b1010
    assert s1 == 0b1
    assert s2 == 0b00
    assert s3 == 0b010

    # const in bundle
    bundle = SignalBundle(s1, s2, Bits(3, 3))
    assert bundle.nbits == 6
    assert not bundle.mutable
    assert bundle == 0b100011
    with pytest.raises(BitsAssignError, match=r"immutable signal bundle"):
        bundle <<= 0b101010


def test_SignalBundle_nested():
    s1 = Signal(1)
    s2 = Signal(2)
    s3 = Signal(3)
    s4 = Signal(4)
    _fake_in_sim(s1)
    _fake_in_sim(s2)
    _fake_in_sim(s3)
    _fake_in_sim(s4)
    s1 /= 1
    s2 /= 2
    s3 /= 3
    s4 /= 4
    # {b1, b2, b3}
    bundle1 = SignalBundle(s1, s2, s3)
    # {{b1, b2, b3}, b4}
    bundle2 = SignalBundle(bundle1, s4)
    # {{{b1, b2, b3}, b4}, b1, b2, b4}
    bundle3 = SignalBundle(bundle2, s1, s2, s4)
    # {{b1, b2, b3}[3:], b4, {b1, b2, b3}[:3]}
    bundle4 = SignalBundle(bundle1[3:], s4, bundle1[0:3])

    # immutable
    assert bundle1.mutable
    d = _count_bits_parts(bundle2)
    assert d[s1] == 1
    assert d[s2] == 1
    assert d[s3] == 1
    assert d[s4] == 1
    assert bundle2.mutable
    d = _count_bits_parts(bundle3)
    assert d[s1] == 2
    assert d[s2] == 2
    assert d[s3] == 1
    assert d[s4] == 2
    assert not bundle3.mutable
    d = _count_bits_parts(bundle4)
    assert d[s1] == 2  # in 2 bundle slices
    assert d[s2] == 2
    assert d[s3] == 2
    assert d[s4] == 1
    assert bundle4.mutable

    # data
    assert bundle1.nbits == 6
    assert bundle1 == 0b110011
    assert bundle2.nbits == 10
    assert bundle2 == 0b1100110100
    assert bundle3.nbits == 17
    assert bundle3 == 0b11001101001100100
    assert bundle4.nbits == 10
    assert bundle4 == 0b1100100011

    # assignment
    bundle2 /= 0b1010101010
    assert bundle2 == 0b1010101010
    assert s4 == 0b1010
    assert bundle1 == 0b101010
    assert s1 == 0b1
    assert s2 == 0b01
    assert s3 == 0b010
    with pytest.raises(BitsAssignError, match=r"immutable signal bundle"):
        bundle3 /= 0b10101010101010101


def test_SignalBundle_slice():
    b1 = Bits(1, 1, mutable=True)
    b2 = Bits(2, 2, mutable=True)
    b3 = Bits(3, 3, mutable=True)
    bundle = SignalBundle(b1, b2, b3)
    assert bundle == 0b110011

    assert type(bundle[0]) is SignalSlice
    assert bundle[0] == 0b1
    assert type(bundle[1:3]) is SignalSlice
    assert bundle[1:3] == 0b01
    assert type(bundle[3:]) is SignalSlice
    assert bundle[3:] == 0b110
    assert type(bundle[:3]) is SignalSlice
    assert bundle[:3] == 0b011
    assert type(bundle[:]) is SignalSlice
    assert bundle[:] == 0b110011

    bundle[5] /= 0b0
    assert b1 == 0b0
    bundle[3:5] /= 0b01
    assert b2 == 0b01
    bundle[0:3] /= 0b111
    assert b3 == 0b111
    bundle[:] /= 0b101010
    assert bundle == 0b101010
    assert b1 == 0b1
    assert b2 == 0b01
    assert b3 == 0b010
    bundle[1:4] /= 0b011
    assert b1 == 0b1
    assert b2 == 0b00
    assert b3 == 0b110

    SignalBundle(b1, b2, b3)[:] /= 0
    assert b1 == 0b0
    assert b2 == 0b00
    assert b3 == 0b000

    with pytest.raises(BitsAssignError, match=r"wrong assignment type"):
        bundle[1:4] = 0b011
    with pytest.raises(BitsAssignError, match=r"immutable Bits8"):
        SignalBundle(b1, b2, b3, Bits(2))[:] /= 0b101010


def test_SignalBundle_bitwise():
    b1 = Bits(1, 1)
    b2 = Bits(2, 2)
    b3 = Bits(3, 3)
    bundle = SignalBundle(b1, b2, b3)

    assert type(bundle & 0b000111) is Bits6
    assert bundle & 0b000111 == 0b000011
    assert type(0b111000 & bundle) is Bits6
    assert 0b111000 & bundle == 0b110000
    assert type(bundle | 0b000111) is Bits6
    assert bundle | 0b000111 == 0b110111
    assert type(0b111000 | bundle) is Bits6
    assert 0b111000 | bundle == 0b111011
    assert type(bundle ^ 0b000111) is Bits6
    assert bundle ^ 0b000111 == 0b110100
    assert type(0b111000 ^ bundle) is Bits6
    assert 0b111000 ^ bundle == 0b001011
    assert type(~bundle) is Bits6
    assert ~bundle == 0b001100

    s6 = Signal(6)
    _fake_in_sim(s6)
    s6 /= bundle
    s6 /= bundle & bundle
    assert s6 == 0b110011
    s6 /= bundle | bundle
    assert s6 == 0b110011
    s6 /= bundle ^ bundle
    assert s6 == 0b000000


def test_SignalBundle_comparison():
    b1 = Bits(1, 1)
    b2 = Bits(2, 2)
    b3 = Bits(3, 3)
    bundle = SignalBundle(b1, b2, b3)

    assert bundle == 0b110011
    assert 0b110010 != bundle
    assert bundle < 0b110100
    assert 0b110100 >= bundle
    assert bundle > 0b110000
    assert 0b110000 <= bundle
    assert bundle == Bits6(0b110011)
    assert Bits6(0b110010) != bundle
    assert bundle < Bits6(0b110100)
    assert Bits6(0b110100) >= bundle
    assert bundle > Bits6(0b110000)
    assert Bits6(0b110000) <= bundle

    s6 = Signal(6)
    _fake_in_sim(s6)
    s6 /= bundle
    assert type(bundle == s6) is Bits1
    assert bundle == s6
    assert not (bundle != s6)
    assert type(bundle < s6) is Bits1
    assert not bundle < s6
    assert type(bundle <= s6) is Bits1
    assert bundle <= s6
    assert type(bundle > s6) is Bits1
    assert not bundle > s6
    assert type(bundle >= s6) is Bits1
    assert bundle >= s6


def test_SignalBundle_replication():
    s1 = Signal(1)
    s2 = Signal(2)
    s3 = Signal(3)
    _fake_in_sim(s1)
    _fake_in_sim(s2)
    _fake_in_sim(s3)
    s1 /= 1
    s2 /= 2
    s3 /= 3
    bundle = SignalBundle(s1, s3)
    assert bundle == 0b1011

    # 0-replication
    r0 = bundle**0
    assert isinstance(r0, SignalBundle)
    assert r0.nbits == 0
    with pytest.raises(ValueError, match=r"access an empty signal bundle"):
        r0.data_bits
    r0 = SignalBundle(bundle**0, s2, bundle**0)
    assert r0.nbits == 2
    assert r0.mutable
    assert r0 == 0b10
    r0 /= 0b01
    assert r0 == 0b01
    assert s2 == 0b01
    s2 /= 0b10
    assert r0 == 0b10

    # replication
    r1 = bundle**1
    assert r1 is bundle
    r2 = bundle**2
    assert isinstance(r2, SignalBundle)
    assert r2.nbits == 8
    assert r2 == 0b10111011
    assert r2._parts[0] is bundle
    assert r2._parts[1] is bundle
    assert not r2.mutable
    bundle /= 0b1001
    assert r2 == 0b10011001
    r3 = SignalBundle(bundle**3, s2)
    assert isinstance(r3, SignalBundle)
    assert r3.nbits == 14
    assert r3 == 0b10011001100110
    assert r3._parts[0].nbits == 12
    assert r3._parts[0]._parts[0] is bundle
    assert r3._parts[0]._parts[1] is bundle
    assert r3._parts[0]._parts[2] is bundle
    assert r3._parts[1] is s2
    r4 = SignalBundle(Bits2(0b10)) ** 4
    assert isinstance(r4, SignalBundle)
    assert r4.nbits == 8
    assert r4 == 0b10101010

    with pytest.raises(TypeError, match=r"count must be an integer"):
        SignalBundle(s1) ** 3.5
    with pytest.raises(TypeError, match=r"count must be an integer"):
        SignalBundle(s1) ** "3"
    with pytest.raises(ValueError, match=r"Replication .* non-negative"):
        SignalBundle(s1) ** -1


def test_cat():
    a = Bits(4, 0b1111, mutable=True)
    b = Bits(4, 0b0000, mutable=True)
    c = cat(a, b)
    assert c == 0b11110000

    c /= ~c
    assert a == 0b0000
    assert b == 0b1111
    assert c == 0b00001111

    cat(a, b)[:] /= ~c
    assert a == 0b1111
    assert b == 0b0000


def test_rep():
    a = Signal(4)
    b = Signal(4)
    _fake_in_sim(a)
    _fake_in_sim(b)
    a /= 0b1111
    b /= 0b0000

    # replicate once
    r = rep(1, a)
    assert not isinstance(r, Bits)
    assert isinstance(r, SignalBundle)
    assert r == 0b1111
    r = rep(1, a, b)
    assert r == 0b11110000
    r /= ~r
    assert r == 0b00001111
    assert a == 0b0000
    assert b == 0b1111

    # replicate twice
    r = rep(2, a)
    assert r.nbits == 8
    assert not r.mutable
    assert r == 0b00000000
    with pytest.raises(BitsAssignError, match=r"immutable signal bundle"):
        r /= 0
    r = rep(2, a, b)
    assert r.nbits == 16
    assert r == 0b0000111100001111

    # replicate more times
    s = Signal(4)
    _fake_in_sim(s)
    s /= 0
    r = cat(rep(4, s[3]), s)  # Note: a[3] is not a Bits slice
    assert r.nbits == 8
    assert not r.mutable
    assert r == 0b00000000
    s /= 0b1111
    assert r == 0b11111111

    # errors
    with pytest.raises(TypeError, match=r"count must be an integer"):
        rep(3.5, a)
    with pytest.raises(TypeError, match=r"count must be an integer"):
        rep("3", a)
    with pytest.raises(ValueError, match=r"expects at least one part"):
        rep(1)
    r = rep(0, a)
    assert r.nbits == 0
    with pytest.raises(ValueError, match=r"access an empty signal bundle"):
        r == 0
    with pytest.raises(ValueError, match=r"rep\(\) count must be non-neg"):
        rep(-1, a, b)


def test_pow_bits():
    # Bits
    a = Bits(4, 0b1100)
    _fake_in_sim(a)
    r = a**1
    assert not isinstance(r, Bits)
    assert isinstance(r, SignalBundle)
    assert r == 0b1100
    r = a**2
    assert r.nbits == 8
    assert not r.mutable
    assert r == 0b11001100

    # slice
    r = a[:2] ** 2
    assert r.nbits == 4
    assert not r.mutable
    assert r == 0b0000

    # bundle
    r = cat(a[:2], a[2:]) ** 2
    assert r.nbits == 8
    assert not r.mutable
    assert r == 0b00110011


def test_pow_connectable():
    # Signal
    s = Signal(4)
    _fake_in_sim(s)
    s /= 0b1100
    r = s**1
    assert not isinstance(r, Bits)
    assert isinstance(r, SignalBundle)
    assert r == 0b1100
    r = s**2
    assert r.nbits == 8
    assert not r.mutable
    assert r == 0b11001100

    # slice
    r = s[:2] ** 2
    assert r.nbits == 4
    assert not r.mutable
    assert r == 0b0000

    # bundle
    r = cat(s[:2], s[2:]) ** 2
    assert r.nbits == 8
    assert not r.mutable
    assert r == 0b00110011
