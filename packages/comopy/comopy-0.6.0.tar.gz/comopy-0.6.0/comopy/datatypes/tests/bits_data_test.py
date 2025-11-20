# Tests for BitsData
#

import pytest

from comopy.datatypes.bits_data import BitsData


def test_BitsData():
    with pytest.raises(TypeError, match=r"Can't instantiate abstract class"):
        BitsData()

    class TestBitsData(BitsData):
        """Not implement data property."""

    with pytest.raises(TypeError, match=r"Can't instantiate abstract class"):
        TestBitsData()


# Operators are tested in Signal & SignalBundle.
