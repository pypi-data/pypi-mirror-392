# Tests for EventSimulator
#

import pytest

from comopy import *
from comopy.simulator.event_simulator import EventSimulator
from comopy.simulator.setup_simulator import SetupSimulator


def test_EventSimulator_ordered_comb():
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
    sim = EventSimulator(tree_ir)
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


def test_EventSimulator_unordered_comb():
    class Unordered(RawModule):
        @build
        def build_all(s):
            s.in1 = Input(8)
            s.in2 = Input(8)
            s.out = Output(8)
            s.a = Logic(8)
            s.b = Logic(8)
            s.sum = Logic(8)

        @comb
        def update_out(s):
            s.out /= s.sum

        @comb
        def update_sum(s):
            s.sum /= s.a + s.b

        @comb
        def update_a(s):
            s.a /= s.in1 + 1

        @comb
        def update_b(s):
            s.b /= s.in2 - 1

    top = Unordered()
    tree = HDLStage()(top)
    tree_ir = IRStage()(tree)
    assert top.simulator is None
    assert not top.simulating
    sim = EventSimulator(tree_ir)
    assert sim.module is top

    sim.start()
    top.in1 /= 0b10101010
    top.in2 /= 0b01010100
    sim.evaluate()
    assert top.out == 0b11111110
    top.in1 /= 0b11111111
    sim.evaluate()
    assert top.out == 0b01010011
    sim.stop()


def test_EventSimulator_ordered_conn():
    class Ordered(RawModule):
        @build
        def build_all(s):
            s.in1 = Input(8)
            s.in2 = Input(8)
            s.out = Output(8)
            s.a = Logic(8)
            s.b = Logic(8)
            s.sum = Logic(8)
            s.a @= s.in1 + 1
            s.b @= s.in2 - 2
            s.sum @= s.a + s.b
            s.out @= ~s.sum

    top = Ordered()
    tree = HDLStage()(top)
    tree_ir = IRStage()(tree)
    assert top.simulator is None
    assert not top.simulating
    sim = EventSimulator(tree_ir)
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


def test_EventSimulator_unordered_conn_comb():
    class Unordered(RawModule):
        @build
        def build_all(s):
            s.in1 = Input(8)
            s.in2 = Input(8)
            s.out = Output(8)
            s.a = Logic(8)
            s.b = Logic(8)
            s.sum = Logic(8)
            s.out @= s.sum

        @comb
        def update_sum(s):
            s.sum /= s.a + s.b

        @comb
        def update_a(s):
            s.a /= s.in1 + 1

        @comb
        def update_b(s):
            s.b /= s.in2 - 1

    top = Unordered()
    tree = HDLStage()(top)
    tree_ir = IRStage()(tree)
    assert top.simulator is None
    assert not top.simulating
    sim = EventSimulator(tree_ir)
    assert sim.module is top

    sim.start()
    top.in1 /= 0b10101010
    top.in2 /= 0b01010100
    sim.evaluate()
    assert top.out == 0b11111110
    top.in1 /= 0b11111111
    sim.evaluate()
    assert top.out == 0b01010011
    sim.stop()


def test_EventSimulator_conn_loop():
    class DLatchConn(RawModule):
        @build
        def build_all(s):
            s.D = Input()
            s.E = Input()
            s.Q = Output()
            s.Qn = Output()
            s.Sn = Logic()
            s.Rn = Logic()
            s.Sn @= ~(s.D & s.E)
            s.Rn @= ~(~s.D & s.E)
            s.Q @= ~(s.Sn & s.Qn)
            s.Qn @= ~(s.Rn & s.Q)

    top = DLatchConn()
    tree = HDLStage()(top)
    tree_ir = IRStage()(tree)
    assert top.simulator is None
    assert not top.simulating
    sim = EventSimulator(tree_ir)
    assert sim.module is top

    sim.start()
    top.D /= 1
    top.E /= 1
    triggered = sim.evaluate()  # Set 1
    assert top.Q == 1
    assert top.Qn == 0
    top.D /= 0
    top.E /= 0
    triggered = sim.evaluate()  # Keep 1
    assert top.Q == 1
    assert top.Qn == 0
    assert not triggered
    top.D /= 0
    top.E /= 1
    triggered = sim.evaluate()  # Set 0
    assert top.Q == 0
    assert top.Qn == 1
    assert triggered == {"Q", "Qn"}
    top.D /= 1
    top.E /= 0
    triggered = sim.evaluate()  # Keep 0
    assert top.Q == 0
    assert top.Qn == 1
    assert not triggered
    top.D /= 0
    top.E /= 1
    triggered = sim.evaluate()  # Set 0
    assert top.Q == 0
    assert top.Qn == 1
    assert not triggered
    top.D /= 1
    top.E /= 1
    triggered = sim.evaluate()  # Set 1
    assert top.Q == 1
    assert top.Qn == 0
    assert triggered == {"Q", "Qn"}
    triggered = sim.evaluate()  # Evaluate again
    assert top.Q == 1
    assert top.Qn == 0
    assert not triggered
    sim.stop()


def test_EventSimulator_seq_conn():
    class SeqConn(Module):
        @build
        def build_all(s):
            s.data_in = Input(8)
            s.data_out = Output(8)
            s.reg1 = Logic(8)
            s.reg2 = Logic(8)
            s.data_out @= s.reg2

        @seq
        def update_reg1(s):
            s.reg1 <<= s.data_in

        @seq
        def update_reg2(s):
            s.reg2 <<= s.reg1  # Uses old value of reg1

    top = SeqConn()
    tree = HDLStage()(top)
    tree_ir = IRStage()(tree)
    sim = EventSimulator(tree_ir)

    sim.start()
    assert top.simulating
    top.data_in /= 0xAB
    sim.tick()
    top.data_in /= 0xCD
    sim.tick()
    assert top.data_out == 0xAB
    top.data_in /= 0xEF
    sim.tick()
    assert top.data_out == 0xCD
    sim.stop()
    assert not top.simulating


def test_EventSimulator_seq_comb():
    class CombSeqComb(Module):
        @build
        def build_all(s):
            s.data_in = Input(8)
            s.data_out = Output(8)
            s.processed = Logic(8)
            s.reg1 = Logic(8)

        @comb
        def process_input(s):
            s.processed /= s.data_in + 1

        @seq
        def update_reg(s):
            s.reg1 <<= s.processed

        @comb
        def generate_output(s):
            s.data_out /= s.reg1 << 2

    top = CombSeqComb()
    tree = HDLStage()(top)
    tree_ir = IRStage()(tree)
    sim = EventSimulator(tree_ir)

    sim.start()
    assert top.simulating
    top.data_in /= 0x10
    sim.tick()  # processed = 0x11, reg1 gets 0x11, data_out = 0x44
    assert top.data_out == 0x44
    top.data_in /= 0x20
    sim.tick()  # processed = 0x21, reg1 gets 0x21, data_out = 0x84
    assert top.data_out == 0x84
    top.data_in /= 0xFF
    sim.tick()  # processed = 0x00 (overflow), reg1 gets 0x00, data_out = 0x00
    assert top.data_out == 0x00
    sim.stop()
    assert not top.simulating


def test_EventSimulator_seq_loop():
    class CombLoopWithSeq(Module):
        @build
        def build_all(s):
            s.input = Input(8)
            s.enable = Input()
            s.output = Output(8)
            s.seq_reg = Logic(8)
            s.comb_a = Logic(8)
            s.comb_b = Logic(8)
            s.feedback = Logic(8)

            # a = lim(reg + reg/2 + reg/4 + ...)
            s.comb_a @= s.seq_reg + s.feedback
            s.output @= s.comb_b

        @comb
        def calc_comb_b(s):
            s.comb_b /= s.comb_a & 0xFF

        @comb
        def calc_feedback(s):
            if s.enable:
                s.feedback /= s.comb_b >> 1
            else:
                s.feedback /= 0

        @seq
        def update_seq_reg(s):
            s.seq_reg <<= s.input

    top = CombLoopWithSeq()
    tree = HDLStage()(top)
    tree_ir = IRStage()(tree)
    sim = EventSimulator(tree_ir)

    sim.start()
    assert top.simulating
    top.input /= 32
    top.enable /= 0
    sim.tick()
    assert top.output == 32
    top.enable /= 1
    sim.tick()
    assert top.output == 63
    top.input /= 8
    top.enable /= 0
    sim.tick()
    assert top.output == 8
    top.enable /= 1
    sim.tick()
    assert top.output == 15
    top.input /= 100
    top.enable /= 0
    sim.tick()
    assert top.output == 100
    top.enable /= 1
    sim.tick()
    assert top.output == 199
    sim.stop()


def test_EventSimulator_holding_error():
    class SimpleFlipFlop(Module):
        @build
        def build_all(s):
            s.data = Input(8)
            s.enable = Input()
            s.output = Output(8)
            s.reg = Logic(8)
            s.output @= s.reg

        @seq
        def update_reg(s):
            if s.enable:
                s.reg <<= s.data

    top = SimpleFlipFlop()
    tree = HDLStage()(top)
    tree_ir = IRStage()(tree)
    sim = EventSimulator(tree_ir)

    sim.start()
    top.clk /= 0
    top.data /= 0x42
    top.enable /= 1
    sim.evaluate()
    top.clk /= 1  # Rising edge, reg gets 0x42
    sim.evaluate()
    assert top.output == 0x42
    top.clk /= 0
    sim.evaluate()

    # Violate data holding
    top.clk /= 1
    top.enable /= 0
    top.data /= 0x55
    with pytest.raises(RuntimeError, match=r"'data', 'enable' change.* 'clk'"):
        sim.evaluate()

    sim.stop()


def test_EventSimulator_seq_inst():
    class Counter(Module):
        @build
        def build_all(s):
            s.enable = Input()
            s.reset = Input()
            s.count_out = Output(8)
            s.counter = Logic(8)
            s.count_out @= s.counter

        @seq
        def update_counter(s):
            if s.reset:
                s.counter <<= 0
            elif s.enable:
                s.counter <<= s.counter + 1

    class TopWithSubSeq(Module):
        @build
        def build_all(s):
            s.start = Input()
            s.data_in = Input(8)
            s.result = Output(8)

            # Internal signals
            s.top_reg = Logic(8)
            s.counter_enable = Logic()
            s.counter_reset = Logic()
            s.counter_value = Logic(8)

            # Submodule
            s.counter_enable @= s.start
            s.counter_reset @= ~s.start
            s.sub = Counter(s.counter_enable, s.counter_reset, s.counter_value)

            # Output logic
            s.result @= s.top_reg + s.counter_value

        @seq
        def update_top_reg(s):
            if s.start:
                s.top_reg <<= s.data_in

    top = TopWithSubSeq(name="top")
    tree = HDLStage()(top)
    tree_ir = IRStage()(tree)
    with comopy_context(sim_config=SimulatorConfig.event()):
        SetupSimulator()(tree_ir)
    assert isinstance(top.simulator, EventSimulator)
    assert isinstance(top.sub.simulator, EventSimulator)
    sim = top.simulator

    sim.start()
    assert top.simulating
    assert top.sub.simulating

    # Reset counter (start=0)
    top.start /= 0
    top.data_in /= 0x42
    sim.tick()
    assert top.result == 0

    # Enable counter
    top.start /= 1
    top.data_in /= 0x55
    sim.tick()
    assert top.result == 0x55 + 1
    sim.tick()
    assert top.result == 0x55 + 2
    sim.tick()
    assert top.result == 0x55 + 3

    # Stop counter
    top.start /= 0
    top.data_in /= 0x10
    sim.tick()
    assert top.result == 0x55 + 0  # top_reg unchanged, counter=0

    # Start again with new data
    top.start /= 1
    top.data_in /= 0x10
    sim.tick()
    assert top.result == 0x10 + 1
    sim.tick()
    assert top.result == 0x10 + 2
    sim.stop()
    assert not top.simulating
    assert not top.sub.simulating


def test_EventSimulator_submodule_holding_error():
    class SubFlipFlop(Module):
        @build
        def build_all(s):
            s.data = Input(8)
            s.enable = Input()
            s.output = Output(8)
            s.reg = Logic(8)
            s.output @= s.reg

        @seq
        def update_reg(s):
            if s.enable:
                s.reg <<= s.data

    class TopModule(Module):
        @build
        def build_all(s):
            s.in_ = Input(8)
            s.en = Input()
            s.out = Output(8)

            # Instantiate submodule
            s.sub = SubFlipFlop(s.in_, s.en, s.out)

    top = TopModule(name="top")
    tree = HDLStage()(top)
    tree_ir = IRStage()(tree)
    with comopy_context(sim_config=SimulatorConfig.event()):
        SetupSimulator()(tree_ir)
    assert isinstance(top.simulator, EventSimulator)
    assert isinstance(top.sub.simulator, EventSimulator)
    sim = top.simulator

    sim.start()
    top.clk /= 0
    top.in_ /= 0x33
    top.en /= 1
    sim.evaluate()
    top.clk /= 1  # Rising edge, submodule reg gets 0x33
    sim.evaluate()
    assert top.out == 0x33
    top.clk /= 0
    sim.evaluate()

    # Violate data hold in submodule
    top.clk /= 1
    top.in_ /= 0x66  # Change data signal during clock edge
    with pytest.raises(RuntimeError, match=r"top.sub: 'data' change.* 'clk'"):
        sim.evaluate()

    sim.stop()
