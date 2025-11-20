# Tests for SetupSimulator
#

import pytest

from comopy import *
from comopy.simulator.base_simulator import BaseSimulator
from comopy.simulator.event_simulator import EventSimulator
from comopy.simulator.scheduled_simulator import ScheduledSimulator
from comopy.simulator.setup_simulator import SetupSimulator
from comopy.simulator.simple_simulator import SimpleSimulator


def test_SetupSimulator_init():
    assert get_comopy_context().sim_config.simulator_type == "auto"
    sim = SetupSimulator()
    assert sim._sim_class == ScheduledSimulator

    with comopy_context(sim_config=SimulatorConfig.event()):
        sim = SetupSimulator()
        assert sim._sim_class == EventSimulator

    with comopy_context(sim_config=SimulatorConfig.scheduled()):
        sim = SetupSimulator()
        assert sim._sim_class == ScheduledSimulator

    with comopy_context(sim_config=SimulatorConfig.simple()):
        sim = SetupSimulator()
        assert sim._sim_class == SimpleSimulator

    with comopy_context(sim_config=SimulatorConfig(simulator_type="unknown")):
        with pytest.raises(ValueError, match="Unknown .* type: 'unknown'"):
            SetupSimulator()


def test_SetupSimulator_top():
    class Top(RawModule):
        @build
        def build_all(s):
            s.in1 = Input(8)
            s.in2 = Input(8)
            s.out = Output(8)
            s.a = Logic(8)
            s.b = Logic(8)
            s.sum = Logic(8)

        @comb
        def update_a(s):
            s.a /= s.in1 & s.in2

        @comb
        def update_b(s):
            s.b /= s.in1 | s.in2

        @comb
        def update_sum(s):
            s.sum /= s.a + s.b
            s.out /= ~s.sum

    top = Top(name="top")
    tree = HDLStage()(top)
    tree_ir = IRStage()(tree)
    assert top.simulator is None
    assert not top.simulating
    tree_sim = SetupSimulator()(tree_ir)
    assert tree_sim is tree_ir
    sim = top.simulator
    assert isinstance(sim, BaseSimulator)

    sim.start()
    assert top.simulating
    top.in1 /= 0b11001100
    top.in2 /= 0b00110011
    sim.evaluate()
    assert top.out == 0b00000000
    sim.stop()
    assert not top.simulating

    with pytest.raises(RuntimeError, match=r"Simulator .* 'top' has already"):
        SetupSimulator()(tree_ir)


def test_SetupSimulator_auto():
    # Bottom layer: Simple module (no cycles, should use ScheduledSimulator)
    class Bottom(RawModule):
        @build
        def build_all(s):
            s.data_in = Input(8)
            s.data_out = Output(8)
            s.processed = Logic(8)
            s.processed @= s.data_in + 1
            s.data_out @= s.processed << 1

    # Middle layer: Module with combinational loop (should use EventSimulator)
    class MiddleWithLoop(RawModule):
        @build
        def build_all(s):
            s.input = Input(8)
            s.enable = Input()
            s.output = Output(8)

            # Bottom submodule
            s.bottom = Bottom(s.input)

            # Create combinational feedback loop similar to DLatch
            s.feedback_a = Logic(8)
            s.feedback_b = Logic(8)
            s.feedback_a @= s.bottom.data_out + s.feedback_b
            s.feedback_b @= s.feedback_a >> 1

            # Output depends on the feedback loop
            s.output @= s.feedback_a if s.enable else s.bottom.data_out

    # Top layer: Module with sequential logic (should use ScheduledSimulator)
    class Top(Module):
        @build
        def build_all(s):
            s.start = Input()
            s.data = Input(8)
            s.enable_middle = Input()
            s.result = Output(8)
            s.top_reg = Logic(8)

            # Middle submodule (which has cycles)
            s.middle = MiddleWithLoop(s.data, s.enable_middle)

            # Simple output logic
            s.result @= s.top_reg + s.middle.output

        @seq
        def update_top_reg(s):
            if s.start:
                s.top_reg <<= s.data

    top = Top(name="top")
    tree = HDLStage()(top)
    tree_ir = IRStage()(tree)
    with comopy_context(sim_config=SimulatorConfig.auto()):
        SetupSimulator()(tree_ir)
    assert isinstance(top.simulator, ScheduledSimulator)
    assert isinstance(top.middle.simulator, EventSimulator)
    assert isinstance(top.middle.bottom.simulator, ScheduledSimulator)
