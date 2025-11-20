# Tests for SignalSlice
#

import pytest

from comopy.bits import *
from comopy.hdl.signal import Signal
from comopy.hdl.signal_bundle import rep
from comopy.hdl.signal_slice import SignalSlice
from comopy.utils import BitsAssignError


def _fake_in_sim(signal):
    signal._assembled = True
    signal._simulating = True


def test_SignalSlice():
    sig = Signal(4)
    _fake_in_sim(sig)
    sig /= 0b1100
    sig2 = rep(2, sig)
    s = sig2[2:6]
    assert type(s.data_bits) is Bits4
    assert s.data_bits.nbits == 4
    assert s.data_bits == 0b0011
    assert s.nbits == 4
    assert not s.mutable
    assert s == 0b0011

    with pytest.raises(BitsAssignError, match=r"slice of immutable Bits8"):
        s /= 0b1010
    with pytest.raises(BitsAssignError, match=r"slice of immutable Bits8"):
        sig2[2] /= 0
    with pytest.raises(BitsAssignError, match=r"Bits8: immutable Bits8"):
        sig2[:] /= 0

    sig = Signal(8)
    _fake_in_sim(sig)
    sig /= 0b11001100
    s = SignalSlice(sig, slice(2, 6))
    s /= 0b1010
    assert sig == 0b11101000
    assert s.data_bits == 0b1010
    assert s.nbits == 4
    assert s.mutable is True
    assert s == 0b1010

    with pytest.raises(TypeError, match=r"not subscriptable"):
        s[0] /= 1
    with pytest.raises(TypeError, match=r"not subscriptable"):
        s[:2] /= 1

    sig = Signal(8)
    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        sig[:2] == 0


def test_SignalSlice_nonblocking_assign():
    sig = Signal(8)
    _fake_in_sim(sig)
    sig <<= 0b11001100
    sig.flip()
    assert sig == 0b11001100
    sig[2:6] <<= 0b1010
    assert sig == 0b11001100
    sig[:2] <<= 0b11
    assert sig == 0b11001100
    sig.flip()
    assert sig == 0b11101011

    sig2 = rep(2, sig)
    assert not sig2.mutable
    with pytest.raises(BitsAssignError, match=r"slice of immutable Bits16"):
        sig2[:8] <<= 0
    with pytest.raises(BitsAssignError, match=r"slice of immutable Bits16"):
        sig2[2] <<= 0
    with pytest.raises(BitsAssignError, match=r"Bits16: immutable Bits16"):
        sig2[:] <<= 0
