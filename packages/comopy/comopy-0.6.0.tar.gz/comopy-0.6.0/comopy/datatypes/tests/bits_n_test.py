# Tests for Bits<N>
#

from comopy.datatypes.bits import Bits, _bits_nmax
from comopy.datatypes.bits_n import *  # BitsN.global()
from comopy.datatypes.bits_n import _all_BitsN, _all_bitsN


def test_BitsN():
    for n in range(1, _bits_nmax + 1):
        assert f"Bits{n}" in _all_BitsN
        assert f"b{n}" in _all_bitsN
        assert globals()[f"Bits{n}"] is type(Bits(n))  # noqa: E721
        assert globals()[f"Bits{n}"] == globals()[f"b{n}"]
