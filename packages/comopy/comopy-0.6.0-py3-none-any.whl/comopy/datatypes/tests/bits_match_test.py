# Tests for Bits matching
#

# flake8 fails to check match-case
# flake8: noqa

from comopy.bits import *
from comopy.datatypes.bit_pat import BitPat
from comopy.hdl import Signal


def _fake_in_sim(signal: Signal):
    signal._assembled = True
    signal._simulating = True


def test_Bits_match():
    match b2(0b10):
        case b2(_uint=0):
            assert False
        case b2(_uint=1):
            assert False
        case b2(_uint=2):
            assert True
        case _:
            assert False

    match b4(0xA):
        case b2(0):
            assert False
        case b4(1):
            assert False
        case b4(0xA):
            assert True
        case _:
            assert False

    match b4(0xB):
        case b4(x) if x < 10:
            assert False
        case b4(x) if x >= 10:
            assert True
        case _:
            assert False

    match b4(0xC):
        case b8(x):
            assert False
        case b4(x) if x < 10:
            assert False
        case _:
            assert True


def test_Bits_match_BitPat():
    match b8(0b11010100):
        case b8(0):
            assert False
        case x if x == BitPat("??1010??"):
            assert False
        case x if x == BitPat("??0101??"):
            assert True
        case _:
            assert False


def test_Bits_match_pattern_str():
    match b8(0b11010100):
        case 0b0:
            assert False
        case "??1010??":
            assert False
        case "??0101??":
            assert True
        case _:
            assert False
