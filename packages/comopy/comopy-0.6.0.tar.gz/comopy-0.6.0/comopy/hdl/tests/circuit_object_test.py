# Tests for CircuitObject
#

from comopy.hdl.circuit_object import CircuitObject


def test_CircuitObject_init():
    obj = CircuitObject()
    assert obj._args == ()
    assert obj._kwargs == {}
    assert obj._name == ""
    assert obj.name == "_Unknown_"
    assert obj._assembled is False
    assert not obj.assembled
    assert obj._simulating is False
    assert not obj.simulating
    assert str(obj) == "CircuitObject(_Unknown_)"
    assert obj.is_module is False
    assert obj.is_package is False
    assert obj.direction is None
    assert obj.is_input_port is False
    assert obj.is_output_port is False
    assert obj.is_inout_port is False
    assert obj.is_port is False
    assert obj.is_scalar_input is False

    obj = CircuitObject(1, 2, 3, a=4, b=5)
    assert obj._args == (1, 2, 3)
    assert obj._kwargs == {"a": 4, "b": 5}  # Order is not guaranteed
    assert obj._name == ""
    assert obj.name == "_Unknown_"
    assert obj._assembled is False
    assert not obj.assembled
    assert obj._simulating is False
    assert not obj.simulating

    obj = CircuitObject(name="MyObject")
    assert obj._name == "MyObject"
    assert obj.name == "MyObject"
    assert str(obj) == "CircuitObject(MyObject)"
    assert "name" not in obj._kwargs
