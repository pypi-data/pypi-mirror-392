# Tests for BitPat
#

import pytest

from comopy.bits import *
from comopy.datatypes.bit_pat import BitPat
from comopy.utils import BitsWidthError


def test_BitPat_init():
    pat = BitPat("??0101??")
    assert pat.nbits == 8
    assert pat.unsigned == 0b00010100
    assert pat.mask == 0b00111100
    assert str(pat) == "??0101??"
    assert pat.pattern() == "??0101??"

    pat = BitPat("??01_01??")
    assert pat.nbits == 8
    assert pat.unsigned == 0b00010100
    assert pat.mask == 0b00111100
    assert str(pat) == "??01_01??"
    assert pat.pattern() == "??0101??"

    pat = BitPat("_??01__01??_")
    assert pat.nbits == 8
    assert pat.unsigned == 0b00010100
    assert pat.mask == 0b00111100
    assert str(pat) == "_??01__01??_"
    assert pat.pattern() == "??0101??"

    pat = BitPat("????")
    assert pat.nbits == 4
    assert pat.unsigned == 0
    assert pat.mask == 0
    assert str(pat) == "????"
    assert pat.pattern() == "????"

    pat = BitPat("1111")
    assert pat.nbits == 4
    assert pat.unsigned == 0b1111
    assert pat.mask == 0b1111
    assert str(pat) == "1111"
    assert pat.pattern() == "1111"

    with pytest.raises(ValueError, match=r"Empty bit pattern"):
        pat = BitPat("")
    with pytest.raises(ValueError, match=r"Empty bit pattern"):
        pat = BitPat("__")
    with pytest.raises(ValueError, match=r"Invalid bit pattern"):
        pat = BitPat("0101xxx")
    with pytest.raises(ValueError, match=r"Invalid bit pattern"):
        pat = BitPat("010123")


def test_Bits_compare_BitPat():
    bits = b8(0b11010100)
    pat = BitPat("??0101??")
    assert type(bits == pat) is Bits1
    assert type(pat != bits) is Bits1
    assert bits == pat
    assert pat == bits
    assert bits != BitPat("10????00")
    assert BitPat("10????11") != bits

    with pytest.raises(BitsWidthError, match=r"mismatch .* Bits8.* Bits4"):
        bits == BitPat("????")
