# Tests for HDLBits examples, sequential logic
#

import comopy.testcases.ex_HDLBits_seq as ex
from comopy.hdl import Input, IOStruct, Output
from comopy.testcases.base_test_case import BaseTestCase


class TestDff_raw(BaseTestCase):
    class IO(IOStruct):
        clk = Input()
        d = Input()
        q = Output()

    TV = [
        IO(),
        (0, 1, None),
        (1, 1, 1),
        (0, 0, 1),
        (1, 0, 0),
        (0, 1, 0),
        (1, 1, 1),
        (0, 1, 1),
        (1, 1, 1),
    ]

    def test_dff_raw(self):
        self.simulate(ex.Dff_raw(), self.TV)


class TestDff(BaseTestCase):
    class IO(IOStruct):
        d = Input()
        q = Output()

    TV = [
        IO(),
        (1, 1),
        (0, 0),
        (1, 1),
        (1, 1),
    ]

    def test_dff(self):
        self.simulate(ex.Dff(), self.TV)


class TestDff8_raw(BaseTestCase):
    class IO(IOStruct):
        clk = Input()
        d = Input(8)
        q = Output(8)

    TV = [
        IO(),
        (0, 0x12, None),
        (1, 0x12, 0x12),
        (0, 0x34, 0x12),
        (1, 0x34, 0x34),
        (0, 0x56, 0x34),
        (1, 0x56, 0x56),
        (0, 0x78, 0x56),
        (1, 0x78, 0x78),
        (0, 0x9A, 0x78),
        (1, 0x9A, 0x9A),
    ]

    def test_dff8_raw(self):
        self.simulate(ex.Dff8_raw(), self.TV)


class TestDff8(BaseTestCase):
    class IO(IOStruct):
        d = Input(8)
        q = Output(8)

    TV = [
        IO(),
        (0x12, 0x12),
        (0x34, 0x34),
        (0x56, 0x56),
        (0x78, 0x78),
        (0x9A, 0x9A),
    ]

    def test_dff8(self):
        self.simulate(ex.Dff8(), self.TV)


class TestDff8r_raw(BaseTestCase):
    class IO(IOStruct):
        clk = Input()
        reset = Input()
        d = Input(8)
        q = Output(8)

    TV = [
        IO(),
        (0, 1, 0x12, None),
        (1, 1, 0x12, 0x00),  # reset active, q should be 0
        (0, 1, 0x34, 0x00),
        (1, 1, 0x34, 0x00),  # reset still active, q remains 0
        (0, 0, 0x56, 0x00),
        (1, 0, 0x56, 0x56),  # reset inactive, d gets clocked to q
        (0, 0, 0x78, 0x56),
        (1, 0, 0x78, 0x78),  # normal operation
        (0, 1, 0x9A, 0x78),
        (1, 1, 0x9A, 0x00),  # reset active again, q becomes 0
        (0, 0, 0xBC, 0x00),
        (1, 0, 0xBC, 0xBC),  # reset inactive, normal operation resumes
    ]

    def test_dff8r_raw(self):
        self.simulate(ex.Dff8r_raw(), self.TV)


class TestDff8r(BaseTestCase):
    class IO(IOStruct):
        reset = Input()
        d = Input(8)
        q = Output(8)

    TV = [
        IO(),
        (1, 0x12, 0x00),  # reset active, q should be 0
        (1, 0x34, 0x00),  # reset still active, q remains 0
        (0, 0x56, 0x56),  # reset inactive, d gets clocked to q
        (0, 0x78, 0x78),  # normal operation
        (1, 0x9A, 0x00),  # reset active again, q becomes 0
        (0, 0xBC, 0xBC),  # reset inactive, normal operation resumes
    ]

    def test_dff8r(self):
        self.simulate(ex.Dff8r(), self.TV)


class TestDff8p(BaseTestCase):
    class IO(IOStruct):
        clk = Input()
        reset = Input()
        d = Input(8)
        q = Output(8)

    TV = [
        IO(),
        (1, 1, 0x12, None),
        (0, 1, 0x12, 0x34),  # reset active on negedge, q should be 0x34
        (1, 1, 0x56, 0x34),
        (0, 1, 0x56, 0x34),  # reset still active, q remains 0x34
        (1, 0, 0x78, 0x34),
        (0, 0, 0x78, 0x78),  # reset inactive on negedge, d gets clocked to q
        (1, 0, 0x9A, 0x78),
        (0, 0, 0x9A, 0x9A),  # normal negedge operation
        (1, 1, 0xBC, 0x9A),
        (0, 1, 0xBC, 0x34),  # reset active again on negedge, q becomes 0x34
        (1, 0, 0xDE, 0x34),
        (0, 0, 0xDE, 0xDE),  # reset inactive, normal operation resumes
    ]

    def test_dff8p(self):
        # Only test Dff8p_raw. There's no Module version (negedge triggered)
        self.simulate(ex.Dff8p_raw(), self.TV)


class TestDff8ar_raw(BaseTestCase):
    class IO(IOStruct):
        clk = Input()
        areset = Input()
        d = Input(8)
        q = Output(8)

    TV = [
        IO(),
        (0, 0, 0x12, None),
        (0, 1, 0x12, 0x00),  # areset goes high, hold d, q should become 0
        (1, 1, 0x12, 0x00),  # clk posedge with areset high, hold d, q=0
        (0, 1, 0x34, 0x00),  # areset still high, q remains 0
        (1, 0, 0x34, 0x34),  # areset released, clk posedge, d -> q
        (0, 0, 0x56, 0x34),  # normal operation, no clock edge
        (1, 0, 0x56, 0x56),  # clk posedge, hold d, normal operation
        (0, 0, 0x78, 0x56),  # no clock edge
        (0, 1, 0x78, 0x00),  # asynchronous reset without clock edge
        (0, 0, 0x9A, 0x00),  # areset released without clock edge
        (1, 0, 0x9A, 0x9A),  # clk posedge, hold d, normal operation
        (1, 1, 0x9A, 0x00),  # asynchronous reset on high clock, hold d
        (0, 1, 0xBC, 0x00),  # reset still active
        (0, 0, 0xDE, 0x00),  # reset released, no posedge yet
        (1, 0, 0xDE, 0xDE),  # clk posedge with reset inactive, hold d
    ]

    def test_dff8ar_raw(self):
        self.simulate(ex.Dff8ar_raw(), self.TV)


class TestDff8ar(BaseTestCase):
    class IO(IOStruct):
        areset = Input()
        d = Input(8)
        q = Output(8)

    TV = [
        IO(),
        (0, 0x12, None),
        (1, 0x12, 0x00),  # areset active, hold d, q should become 0
        (1, 0x34, 0x00),  # areset still active, q remains 0
        (0, 0x56, 0x56),  # areset released, d gets clocked to q
        (0, 0x78, 0x78),  # normal operation
        (1, 0x78, 0x00),  # areset active again, hold d, q becomes 0
        (0, 0x9A, 0x9A),  # areset released, normal operation resumes
    ]

    def test_dff8ar(self):
        self.simulate(ex.Dff8ar(), self.TV)


class TestDff16e_raw(BaseTestCase):
    class IO(IOStruct):
        clk = Input()
        resetn = Input()
        byteena = Input(2)
        d = Input(16)
        q = Output(16)

    TV = [
        IO(),
        (0, 0, 0b00, 0x1234, None),
        (1, 0, 0b00, 0x1234, 0x0000),  # sync reset
        (0, 1, 0b11, 0x5678, 0x0000),
        (1, 1, 0b11, 0x5678, 0x5678),  # both bytes enabled
        (0, 1, 0b01, 0x9ABC, 0x5678),
        (1, 1, 0b01, 0x9ABC, 0x56BC),  # only low byte enabled
        (0, 1, 0b10, 0xDEF0, 0x56BC),
        (1, 1, 0b10, 0xDEF0, 0xDEBC),  # only high byte enabled
        (0, 1, 0b00, 0x1111, 0xDEBC),
        (1, 1, 0b00, 0x1111, 0xDEBC),  # no bytes enabled
        (0, 1, 0b11, 0x2222, 0xDEBC),
        (1, 1, 0b11, 0x2222, 0x2222),  # both bytes enabled again
        (0, 0, 0b11, 0x3333, 0x2222),
        (1, 0, 0b11, 0x3333, 0x0000),  # sync reset active
    ]

    def test_dff16e_raw(self):
        self.simulate(ex.Dff16e_raw(), self.TV)


class TestDff16e(BaseTestCase):
    class IO(IOStruct):
        resetn = Input()
        byteena = Input(2)
        d = Input(16)
        q = Output(16)

    TV = [
        IO(),
        (0, 0b00, 0x1234, 0x0000),  # sync reset
        (1, 0b11, 0x5678, 0x5678),  # both bytes enabled
        (1, 0b01, 0x9ABC, 0x56BC),  # only low byte enabled
        (1, 0b10, 0xDEF0, 0xDEBC),  # only high byte enabled
        (1, 0b00, 0x1111, 0xDEBC),  # no bytes enabled
        (1, 0b11, 0x2222, 0x2222),  # both bytes enabled again
        (0, 0b11, 0x3333, 0x0000),  # sync reset active
    ]

    def test_dff16e(self):
        self.simulate(ex.Dff16e(), self.TV)


class TestMuxDff_raw(BaseTestCase):
    class IO(IOStruct):
        clk = Input()
        L = Input()
        r_in = Input()
        q_in = Input()
        Q = Output()

    TV = [
        IO(),
        (0, 1, 1, 0, None),
        (1, 1, 1, 0, 1),  # clk posedge, L=1, Q should get r_in=1
        (0, 1, 0, 1, 1),
        (1, 1, 0, 1, 0),  # clk posedge, L=1, Q should get r_in=0
        (0, 0, 1, 0, 0),
        (1, 0, 1, 0, 0),  # clk posedge, L=0, Q should get q_in=0
        (0, 0, 0, 1, 0),
        (1, 0, 0, 1, 1),  # clk posedge, L=0, Q should get q_in=1
    ]

    def test_muxdff_raw(self):
        self.simulate(ex.MuxDff_raw(), self.TV)


class TestMuxDff(BaseTestCase):
    class IO(IOStruct):
        L = Input()
        r_in = Input()
        q_in = Input()
        Q = Output()

    TV = [
        IO(),
        (1, 1, 0, 1),  # L=1, Q should get r_in=1
        (1, 0, 1, 0),  # L=1, Q should get r_in=0
        (0, 1, 0, 0),  # L=0, Q should get q_in=0
        (0, 0, 1, 1),  # L=0, Q should get q_in=1
    ]

    def test_muxdff(self):
        self.simulate(ex.MuxDff(), self.TV)
