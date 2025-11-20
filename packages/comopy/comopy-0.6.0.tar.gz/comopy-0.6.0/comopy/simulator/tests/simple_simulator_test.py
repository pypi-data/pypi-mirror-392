# Tests for SimpleSimulator
#

import pytest

from comopy import *
from comopy.simulator.simple_simulator import SimpleSimulator


def test_SimpleSimulator_eval_ordered():
    class Ordered(RawModule):
        @build
        def build_all(s):
            s.in1 = Input(8)
            s.in2 = Input(8)
            s.out = Output(8)
            s.a = Logic(8)
            s.b = Logic(8)
            s.sum = Logic(8)

        @comb
        def calc(s):
            s.a /= s.in1 + 1
            s.b /= s.in2 - 2

        @comb
        def calc_sum(s):
            s.sum /= s.a + s.b
            s.out /= ~s.sum

    top = Ordered()
    tree = HDLStage()(top)
    tree_ir = IRStage()(tree)
    assert top.simulator is None
    assert not top.simulating
    sim = SimpleSimulator(tree_ir)
    assert sim.module is top
    sim.start()
    assert top.simulating
    top.in1 /= 0b10101010
    top.in2 /= 0b01010100
    sim.evaluate()
    assert top.out == 0b00000010
    top.in1 /= 0b11111111
    sim.evaluate()
    assert top.out == 0b10101101
    sim.stop()
    assert not top.simulating

    with pytest.raises(RuntimeError, match=r"requires a Module with clock"):
        sim.tick()


def test_SimpleSimulator_eval_seq():
    class Sequential(RawModule):
        @build
        def build_all(s):
            s.clk = Input(1)
            s.in1 = Input(8)
            s.in2 = Input(8)
            s.out = Output(8)
            s.a = Logic(8)
            s.b = Logic(8)
            s.sum = Logic(8)

        @seq
        def calc(s, posedge="clk"):
            s.a <<= s.in1 + 1
            s.b <<= s.in2 - 2

        @seq
        def calc_sum(s, posedge="clk"):
            s.sum <<= s.a + s.b
            s.out <<= ~s.sum

    top = Sequential()
    tree = HDLStage()(top)
    tree_ir = IRStage()(tree)
    assert top.simulator is None
    assert not top.simulating
    sim = SimpleSimulator(tree_ir)
    assert sim.module is top
    sim.start()
    assert top.simulating

    # Set inputs when clk=0
    top.clk /= 0
    top.in1 /= 0b10101010
    top.in2 /= 0b01010100
    sim.evaluate()

    # Clock rising edge: first stage updates
    top.clk /= 1
    sim.evaluate()
    assert top.a == 0b10101011  # in1 + 1
    assert top.b == 0b01010010  # in2 - 2

    # Set new inputs when clk=0
    top.clk /= 0
    top.in1 /= 0b11111111
    sim.evaluate()

    # Clock rising edge: second stage updates
    top.clk /= 1
    sim.evaluate()
    assert top.a == 0b00000000  # in1 + 1
    assert top.b == 0b01010010  # in2 - 2
    assert top.sum == 0b11111101  # a + b from previous cycle

    # Another cycle to check out value
    top.clk /= 0
    sim.evaluate()

    top.clk /= 1
    sim.evaluate()
    assert top.sum == 0b01010010  # a + b from previous cycle
    assert top.out == 0b00000010  # ~sum from previous cycle

    sim.stop()
    assert not top.simulating
