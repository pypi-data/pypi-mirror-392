# Tests for ParamConst
#

import pytest

from comopy.datatypes.bits import Bits
from comopy.datatypes.param_const import ParamConst
from comopy.hdl import Signal


def _fake_in_sim(signal: Signal):
    signal._assembled = True
    signal._simulating = True


def test_ParamConst_init():
    x = ParamConst(1)
    assert isinstance(x.param_value, int)
    assert x.param_name == ""
    assert x.param_value == 1
    assert x.op == ParamConst.Op.NOP
    assert x.left is None
    assert x.right is None
    assert x.is_expr is False
    assert x.is_literal is True
    x.param_name = "X"
    assert x.param_name == "X"
    assert x.is_literal is False

    y = ParamConst(Bits(8, 1), "Y")
    assert isinstance(y.param_value, Bits)
    assert y.param_name == "Y"
    assert y.param_value == Bits(8, 1)
    assert y.param_value.nbits == 8
    assert y.param_value == 1
    assert x.is_expr is False
    assert x.is_literal is False

    z = ParamConst("Hello", "Z")
    assert isinstance(z.param_value, str)
    assert z.param_name == "Z"
    assert z.param_value == "Hello"
    assert x.is_expr is False
    assert x.is_literal is False

    a = ParamConst(x)
    assert isinstance(a.param_value, int)
    assert a.param_name == ""
    assert a.param_value == 1
    assert a.is_expr is False
    assert a.is_literal is True


def test_ParamConst_index():
    s = Signal(8)
    _fake_in_sim(s)
    s /= 0b10101100
    W = ParamConst(4)
    assert s[W] == 0
    assert s[W + 1] == 1
    assert s[:W] == 0b1100
    assert s[W, W - 2] == 0b10

    W = ParamConst("Hello")
    with pytest.raises(TypeError, match=r"Cannot convert .* to an index"):
        s[W] == 0


def test_ParamConst_arith():
    # __add__
    a = ParamConst(1)
    b = ParamConst(2)
    c = a + b
    assert isinstance(c, ParamConst)
    assert c.param_name == ""
    assert c.param_value == 3
    assert c.op == ParamConst.Op.ADD
    assert c.left is a
    assert c.right is b
    assert c.is_expr is True
    assert c.is_literal is False

    c = a + Bits(8, 2)
    assert isinstance(c, ParamConst)
    assert c.param_name == ""
    assert isinstance(c.param_value, Bits)
    assert c.param_value == 3
    assert c.param_value.nbits == 8
    assert c.op == ParamConst.Op.ADD
    assert c.left is a
    assert isinstance(c.right, Bits) and c.right == 2

    # __radd__
    c = 1 + a
    assert isinstance(c, ParamConst)
    assert c.param_name == ""
    assert c.param_value == 2
    assert c.op == ParamConst.Op.ADD
    assert isinstance(c.left, int) and c.left == 1
    assert c.right is a

    c = Bits(8, 1) + a
    assert isinstance(c, ParamConst)
    assert c.param_name == ""
    assert isinstance(c.param_value, Bits)
    assert c.param_value == 2
    assert c.param_value.nbits == 8
    assert c.op == ParamConst.Op.ADD
    assert isinstance(c.left, Bits) and c.left == 1
    assert c.right is a

    # __sub__
    a = ParamConst(Bits(8, 8))
    b = ParamConst(Bits(8, 1))
    c = a - b
    assert isinstance(c, ParamConst)
    assert c.param_name == ""
    assert isinstance(c.param_value, Bits)
    assert c.param_value == 7
    assert c.param_value.nbits == 8
    assert c.op == ParamConst.Op.SUB
    assert c.left is a
    assert c.right is b

    # __rsub__
    c = Bits(8, 16) - a
    assert isinstance(c, ParamConst)
    assert c.param_name == ""
    assert isinstance(c.param_value, Bits)
    assert c.param_value == 8
    assert c.param_value.nbits == 8
    assert c.op == ParamConst.Op.SUB
    assert isinstance(c.left, Bits) and c.left == 16
    assert c.right is a

    # __mul__
    a = ParamConst(3)
    c = a * 4
    assert isinstance(c, ParamConst)
    assert c.param_name == ""
    assert c.param_value == 12
    assert c.op == ParamConst.Op.MUL
    assert c.left is a
    assert isinstance(c.right, int) and c.right == 4

    # __rmul__
    c = Bits(8, 5) * a
    assert isinstance(c, ParamConst)
    assert c.param_name == ""
    assert isinstance(c.param_value, Bits)
    assert c.param_value == 15
    assert c.param_value.nbits == 8
    assert c.op == ParamConst.Op.MUL
    assert isinstance(c.left, Bits) and c.left == 5
    assert c.right is a

    # __neg__
    a = ParamConst(3)
    c = -a
    assert isinstance(c, ParamConst)
    assert c.param_name == ""
    assert c.param_value == -3
    assert c.op == ParamConst.Op.NEG
    assert c.left is a
    assert c.right is None


def test_ParamConst_bitwise():
    # __and__
    a = ParamConst(0b1010)
    b = ParamConst(0b1100)
    c = a & b
    assert isinstance(c, ParamConst)
    assert c.param_name == ""
    assert c.param_value == 0b1000
    assert c.op == ParamConst.Op.AND
    assert c.left is a
    assert c.right is b
    assert c.is_expr is True
    assert c.is_literal is False

    c = a & Bits(8, 0b1111)
    assert isinstance(c, ParamConst)
    assert c.param_name == ""
    assert isinstance(c.param_value, Bits)
    assert c.param_value == 0b1010
    assert c.param_value.nbits == 8
    assert c.op == ParamConst.Op.AND
    assert c.left is a
    assert isinstance(c.right, Bits) and c.right == 0b1111

    # __rand__
    c = 0b0011 & a
    assert isinstance(c, ParamConst)
    assert c.param_name == ""
    assert c.param_value == 0b0010
    assert c.op == ParamConst.Op.AND
    assert isinstance(c.left, int) and c.left == 0b0011
    assert c.right is a

    c = Bits(8, 0b1001) & a
    assert isinstance(c, ParamConst)
    assert c.param_name == ""
    assert isinstance(c.param_value, Bits)
    assert c.param_value == 0b1000
    assert c.param_value.nbits == 8
    assert c.op == ParamConst.Op.AND
    assert isinstance(c.left, Bits) and c.left == 0b1001
    assert c.right is a

    # __or__
    a = ParamConst(Bits(8, 0b10101100))
    b = ParamConst(Bits(8, 0b11001100))
    c = a | b
    assert isinstance(c, ParamConst)
    assert c.param_name == ""
    assert isinstance(c.param_value, Bits)
    assert c.param_value == 0b11101100
    assert c.param_value.nbits == 8
    assert c.op == ParamConst.Op.OR
    assert c.left is a
    assert c.right is b

    # __ror__
    c = Bits(8, 0b00110011) | a
    assert isinstance(c, ParamConst)
    assert c.param_name == ""
    assert isinstance(c.param_value, Bits)
    assert c.param_value == 0b10111111
    assert c.param_value.nbits == 8
    assert c.op == ParamConst.Op.OR
    assert isinstance(c.left, Bits) and c.left == 0b00110011
    assert c.right is a

    # __xor__
    a = ParamConst(0b10101100)
    c = a ^ 0b11001100
    assert isinstance(c, ParamConst)
    assert c.param_name == ""
    assert c.param_value == 0b01100000
    assert c.op == ParamConst.Op.XOR
    assert c.left is a
    assert isinstance(c.right, int) and c.right == 0b11001100

    # __rxor__
    c = Bits(8, 0b00110011) ^ a
    assert isinstance(c, ParamConst)
    assert c.param_name == ""
    assert isinstance(c.param_value, Bits)
    assert c.param_value == 0b10011111
    assert c.param_value.nbits == 8
    assert c.op == ParamConst.Op.XOR
    assert isinstance(c.left, Bits) and c.left == 0b00110011
    assert c.right is a

    # __invert__
    a = ParamConst(Bits(8, 0b10101100))
    c = ~a
    assert isinstance(c, ParamConst)
    assert c.param_name == ""
    assert isinstance(c.param_value, Bits)
    assert c.param_value == 0b01010011
    assert c.param_value.nbits == 8
    assert c.op == ParamConst.Op.INV
    assert c.left is a
    assert c.right is None


def test_ParamConst_assign():
    # Bits /= ParamConst
    x = Bits(8, 0, mutable=True)
    W = ParamConst(3)
    x /= W
    assert x == 3
    x /= Bits(8, 4) - W
    assert x == 1

    # Bits <<= ParamConst
    x = Bits(8, 0, mutable=True)
    W = ParamConst(Bits(8, 13))
    x <<= W
    assert x == 0
    assert x._next == 13
    x.flip()
    assert x == 13
    x <<= W + 7
    assert x == 13
    x.flip()
    assert x == 20

    # Signal /= ParamConst
    W = ParamConst(3)
    s = Signal(8)
    _fake_in_sim(s)
    s /= W
    assert s == 3
    s /= Bits(8, 4) + W
    assert s == 7

    # Signal <<= ParamConst
    s = Signal(8)
    _fake_in_sim(s)
    W = ParamConst(Bits(8, 0xAB))
    s <<= W
    assert s == 0
    s.flip()
    assert s == 0xAB
    s <<= W + 1
    assert s == 0xAB
    s.flip()
    assert s == 0xAC

    # Signal[] /= ParamConst
    s = Signal(8)
    _fake_in_sim(s)
    W = ParamConst(7)
    s[:4] /= W
    assert s == 7
    s[4:] /= Bits(4, 1) + W
    assert s == 0x87

    # Signal[] <<= ParamConst
    s = Signal(8)
    _fake_in_sim(s)
    W = ParamConst(Bits(4, 7))
    s[:4] <<= W
    assert s == 0
    s.flip()
    assert s == 7
    s[4:] <<= W + 1
    assert s == 7
    s.flip()
    assert s == 0x87


def test_ParamConst_inplace_assign():
    x = ParamConst(3)
    with pytest.raises(TypeError, match=r"Cannot assign to a ParamConst"):
        x += 1
    with pytest.raises(TypeError, match=r"Cannot assign to a ParamConst"):
        x -= 1
    with pytest.raises(TypeError, match=r"Cannot assign to a ParamConst"):
        x *= 1
    with pytest.raises(TypeError, match=r"Cannot assign to a ParamConst"):
        x @= 1
    with pytest.raises(TypeError, match=r"Cannot assign to a ParamConst"):
        x /= 1
    with pytest.raises(TypeError, match=r"Cannot assign to a ParamConst"):
        x //= 1
    with pytest.raises(TypeError, match=r"Cannot assign to a ParamConst"):
        x %= 1
    with pytest.raises(TypeError, match=r"Cannot assign to a ParamConst"):
        x **= 1
    with pytest.raises(TypeError, match=r"Cannot assign to a ParamConst"):
        x &= 1
    with pytest.raises(TypeError, match=r"Cannot assign to a ParamConst"):
        x |= 1
    with pytest.raises(TypeError, match=r"Cannot assign to a ParamConst"):
        x ^= 1
    with pytest.raises(TypeError, match=r"Cannot assign to a ParamConst"):
        x <<= 1
    with pytest.raises(TypeError, match=r"Cannot assign to a ParamConst"):
        x >>= 1


def test_ParamConst_replace_operand():
    a = ParamConst(1)
    b = ParamConst(2)
    c = a + b
    d = c * 2
    x = a * (b + d) - c
    y = d.alias()

    # Replace child node
    new_a = ParamConst(1)
    assert c.left is a
    c.replace_operand(a, new_a)
    assert c.left is new_a
    c.replace_operand(new_a, a)
    assert c.left is a

    # Replace grandchild node
    new_b = ParamConst(2)
    assert c.right is b
    assert d.left is c
    d.replace_operand(b, new_b)
    assert d.left is c
    assert c.right is new_b
    d.replace_operand(new_b, b)
    assert c.right is b

    # Replace middle node
    new_c = ParamConst(3)
    assert d.left is c
    d.replace_operand(c, new_c)
    assert d.left is new_c
    d.replace_operand(new_c, c)

    # Replace multiple nodes
    assert x.left.left is a
    assert x.left.right.right is d
    assert x.right is c
    assert d.left is c
    assert c.left is a
    x.replace_operand(a, new_a)
    assert x.left.left is new_a
    assert x.left.right.right is d
    assert x.right is c
    assert d.left is c
    assert c.left is new_a
    x.replace_operand(new_a, a)

    # Replace alias
    new_d = ParamConst(d.param_value)
    assert y.left is d
    assert y.right is None
    y.replace_operand(d, new_d)
    assert y.left is new_d
    assert y.right is None
    assert d.left is c
    y.replace_operand(new_d, d)
    assert y.left is d
    y.replace_operand(c, new_c)
    assert y.left is d
    assert y.right is None
    assert d.left is new_c


def test_ParamConst_iter():
    x = ParamConst(1)
    y = ParamConst(2)
    z = ParamConst(3)
    w = x + (y + 1) * (z - x)

    it = iter(w)
    assert it._it_queue == [w]
    assert it._it_index == 0
    nodes = list(it)
    assert it._it_queue == []
    assert it._it_index == 0
    assert len(nodes) == 9
    assert nodes[0] is w
    assert nodes[1] is x
    assert isinstance(nodes[2], ParamConst)
    assert nodes[2].op == ParamConst.Op.MUL
    assert isinstance(nodes[3], ParamConst)
    assert nodes[3].op == ParamConst.Op.ADD
    assert isinstance(nodes[4], ParamConst)
    assert nodes[4].op == ParamConst.Op.SUB
    assert nodes[5] is y
    assert nodes[6] == 1
    assert nodes[7] is z
    assert nodes[8] is x
