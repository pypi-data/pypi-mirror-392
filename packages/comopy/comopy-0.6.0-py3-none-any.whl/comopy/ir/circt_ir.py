# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
CIRCT IR utilities.
"""

import io
from typing import Any, Sequence

import circt.ir as IR
from circt.dialects import comb, hw, sv
from circt.support import get_value

from .aux_ir import ConcatLHS


# hw.module
#
def ir_get_module_symbols(module_ir: hw.HWModuleOp) -> dict[str, Any]:
    """Build module symbol table from the module IR."""
    assert isinstance(module_ir, hw.HWModuleOp)
    symbols = {}
    entry_block = module_ir.regions[0].blocks[0]
    for op in entry_block.operations:
        match op:
            case sv.LogicOp():
                assert isinstance(op.name, IR.StringAttr)
                symbols[op.name.value] = op
            case hw.InstanceOp():
                assert isinstance(op.instanceName, IR.StringAttr)
                symbols[op.instanceName.value] = op
    return symbols


def ir_get_module_input(
    module_ir: hw.HWModuleOp, port_name: str
) -> IR.BlockArgument:
    """Get an input port by name from the module IR."""
    assert isinstance(module_ir, hw.HWModuleOp)
    assert isinstance(port_name, str)
    assert port_name in module_ir.input_indices
    index = module_ir.input_indices[port_name]
    entry_block = module_ir.regions[0].blocks[0]
    port = entry_block.arguments[index]
    assert isinstance(port, IR.BlockArgument)
    return port


# hw.instance
#
def ir_get_instance_output(
    instance_ir: hw.InstanceOp, port_name: str
) -> IR.Value:
    """Get a port by name from the instance IR."""
    assert isinstance(instance_ir, hw.InstanceOp)
    assert isinstance(port_name, str)
    output = None
    for index, name in enumerate(instance_ir.resultNames):
        assert isinstance(name, IR.StringAttr)
        if name.value == port_name:
            output = instance_ir.results[index]
            break
    assert isinstance(output, IR.Value)
    return output


# IR Attributes
#
def ir_enum_attr(value: int) -> IR.IntegerAttr:
    """Create an IR enumeration attribute from an integer value."""
    assert isinstance(value, int) and value >= 0
    attr_type = IR.IntegerType.get_signless(32)
    return IR.IntegerAttr.get(attr_type, value)


def ir_case_pattern_attr(pattern: str) -> IR.IntegerAttr | IR.UnitAttr:
    """Create an IR case pattern attribute from a string."""
    assert isinstance(pattern, str)

    # "default"
    if not pattern:
        return IR.UnitAttr.get()

    # '0' -> 00
    # '1' -> 01
    # '?' -> 11 (z)
    assert all(c in "01?" for c in pattern)
    attr_value = 0
    for bit in pattern:
        attr_value <<= 2
        if bit == "1":
            attr_value |= 1
        elif bit == "?":
            attr_value |= 3

    attr_width = len(pattern) * 2
    attr_type = IR.IntegerType.get_signless(attr_width)
    return IR.IntegerAttr.get(attr_type, attr_value)


# IR types
#
def ir_integer_type(width: int) -> IR.IntegerType:
    """Create an IR integer type with the given width."""
    assert isinstance(width, int) and width > 0
    return IR.IntegerType.get_signless(width)


def ir_unpacked_array_type(element_width: int, size: int) -> IR.Type:
    """Create an IR unpacked array type."""
    assert isinstance(element_width, int) and element_width > 0
    assert isinstance(size, int) and size > 0
    # No Python binding for hw.UnpackedArrayType; construct by parsing string.
    type_str = f"!hw.uarray<{size}xi{element_width}>"
    return IR.Type.parse(type_str)


def ir_is_unpacked_array(ir: Any) -> bool:
    """Check if an IR element is an unpacked array type."""
    if isinstance(ir, int):
        return False

    value = get_value(ir)
    # OpResult for sv.read_inout
    if not isinstance(value, (IR.OpResult, sv.LogicOp)):
        return False

    value_type = value.type
    if hw.InOutType.isinstance(value_type):
        value_type = hw.InOutType(value_type).element_type
    assert isinstance(value_type, IR.Type)
    type_str = str(value_type)
    if type_str.startswith("!hw.uarray"):
        return True
    return False


def ir_array_size(ir: Any) -> int:
    """Get the size of an unpacked array IR element."""
    value = get_value(ir)
    # OpResult for sv.read_inout
    assert isinstance(value, (IR.OpResult, sv.LogicOp))
    value_type = value.type
    if hw.InOutType.isinstance(value_type):
        value_type = hw.InOutType(value_type).element_type
    assert isinstance(value_type, IR.Type)

    # Parse !hw.uarray<16xi8> to extract size (16)
    type_str = str(value_type)
    start = type_str.find("<") + 1
    end = type_str.find("x", start)
    size = int(type_str[start:end])
    return size


def ir_width(ir: Any) -> int:
    """Get the width of an IR element."""
    if isinstance(ir, ConcatLHS):
        return ir.width
    value = get_value(ir)
    assert isinstance(value, (IR.BlockArgument, IR.Value))
    value_type = value.type
    assert isinstance(value_type, IR.Type)
    if isinstance(value_type, IR.IntegerType):
        return value_type.width
    elif hw.InOutType.isinstance(value_type):
        element_type = hw.InOutType(value_type).element_type
        assert isinstance(element_type, IR.IntegerType)
        return element_type.width
    assert False, "UNIMPLEMENTED"


def ir_is_indexable(ir: Any) -> bool:
    """Check if an IR element can be indexed.

    In Verilog, only direct signals (wires, regs, ports) can be indexed,
    not expression results.
    """
    if isinstance(ir, int):
        return False

    # Unpacked array
    if ir_is_unpacked_array(ir):
        return True

    # Input port, logic
    if isinstance(ir, (IR.BlockArgument, sv.LogicOp)):
        width = ir_width(ir)
        return width > 1

    # sv.ReadInOutOp
    if isinstance(ir, IR.OpResult):
        op = ir.owner
        assert isinstance(op, IR.Operation)
        owners = ("hw.instance", "sv.array_index_inout", "sv.read_inout")
        if op.name in owners:
            width = ir_width(ir)
            return width > 1

    return False


# IR values
#
def ir_rvalue(ir: Any) -> IR.Value:
    """Get the right value of an IR operation."""
    if isinstance(ir, sv.LogicOp):
        value = sv.read_inout(ir)
    else:
        value = get_value(ir)
    assert isinstance(value, IR.Value)
    return value


# IR operations
#
def ir_last_op() -> Any:
    """Get the last operation in the current insertion point block."""
    insertion_point = IR.InsertionPoint.current
    assert isinstance(insertion_point, IR.InsertionPoint)
    block = insertion_point.block
    assert isinstance(block, IR.Block)
    operations = block.operations

    # Empty block
    if not operations:
        return None

    # Inserting at end of the block
    ref_op = insertion_point.ref_operation
    if ref_op is None:
        return operations[-1]

    # Position by a reference operation
    idx = len(operations) - 1
    while operations[idx] != ref_op:
        idx -= 1
        assert idx >= 0
    if idx > 0:
        return operations[idx - 1]
    return None


def ir_constant_op(width: int, value: int) -> IR.OpResult:
    """Create a constant operation."""
    assert isinstance(width, int) and width > 0
    assert isinstance(value, int)
    # High bits may be lost for widths > 64
    assert value == 0 or width <= 64
    constant_type = ir_integer_type(width)
    ir_op = hw.ConstantOp.create(constant_type, value)
    return ir_op.result


def ir_extract_op(value: IR.Value, start: int, width: int) -> IR.OpResult:
    """Create an extract operation: value[stop-1:start]."""
    assert isinstance(value, IR.Value)
    assert isinstance(start, int) and isinstance(width, int)
    result_type = ir_integer_type(width)
    ir_op = comb.ExtractOp.create(start, result_type, input=value)
    return ir_op.result.value


def ir_invert_op(value: IR.Value) -> IR.OpResult:
    """Create a bitwise NOT operation: ~x -> x ^ -1."""
    assert isinstance(value, IR.Value)
    width = ir_width(value)
    neg_one = __ir_neg_one_op(width)
    ir_op = comb.XorOp.create(value, neg_one)
    return ir_op.result


def __ir_neg_one_op(width: int) -> IR.OpResult:
    if width <= 64:
        return ir_constant_op(width, -1)
    one = ir_constant_op(1, 1)
    ir_type = ir_integer_type(width)
    ir_op = comb.ReplicateOp(ir_type, one)
    return ir_op.result


def ir_pass_op(value: IR.Value) -> IR.Value:
    """Create a unary plus operation: +x -> x (identity operation)."""
    assert isinstance(value, IR.Value)
    return value  # Pass through unchanged


def ir_negate_op(value: IR.Value) -> IR.OpResult:
    """Create a negation operation: -x -> 0 - x."""
    assert isinstance(value, IR.Value)
    width = ir_width(value)
    zero = ir_constant_op(width, 0)
    ir_op = comb.SubOp.create(zero, value)
    return ir_op.result.value


def ir_bool_bit_op(value: IR.Value) -> IR.OpResult:
    """Convert a value to a boolean bit: Bool(x) -> x != 0."""
    assert isinstance(value, IR.Value)
    width = ir_width(value)
    if width == 1:
        return value
    zero = ir_constant_op(width, 0)
    ir_op = comb.NeOp.create(value, zero)
    return ir_op.result.value


def ir_bool_not_op(value: IR.Value) -> IR.OpResult:
    """Create a boolean NOT operation: !x -> Bool(x) ^ 1."""
    value_bool = ir_bool_bit_op(value)
    one = ir_constant_op(1, 1)
    ir_op = comb.XorOp.create(value_bool, one)
    return ir_op.result


def ir_bool_and_op(*operands: IR.Value) -> IR.OpResult:
    """Create a boolean AND operation: x && y && ... -> Bool(x) & Bool(y)..."""
    assert len(operands) >= 2
    bool_operands = [ir_bool_bit_op(operand) for operand in operands]
    ir_op = comb.AndOp.create(*bool_operands)
    return ir_op.result


def ir_bool_or_op(*operands: IR.Value) -> IR.OpResult:
    """Create a boolean OR operation: x || y || ... -> Bool(x) | Bool(y)..."""
    assert len(operands) >= 2
    bool_operands = [ir_bool_bit_op(operand) for operand in operands]
    ir_op = comb.OrOp.create(*bool_operands)
    return ir_op.result


def ir_reduce_and_op(value: IR.Value) -> IR.OpResult:
    """Create a reduce AND operation: x.AO -> x == -1."""
    assert isinstance(value, IR.Value)
    width = ir_width(value)
    neg_one = __ir_neg_one_op(width)
    ir_op = comb.EqOp.create(value, neg_one)
    return ir_op.result.value


def ir_reduce_or_op(value: IR.Value) -> IR.OpResult:
    """Create a reduce OR operation: x.NZ -> x != 0."""
    assert isinstance(value, IR.Value)
    width = ir_width(value)
    zero = ir_constant_op(width, 0)
    ir_op = comb.NeOp.create(value, zero)
    return ir_op.result.value


def ir_reduce_nor_op(value: IR.Value) -> IR.OpResult:
    """Create a reduce NOR operation: x.Z -> x == 0."""
    assert isinstance(value, IR.Value)
    width = ir_width(value)
    zero = ir_constant_op(width, 0)
    ir_op = comb.EqOp.create(value, zero)
    return ir_op.result.value


def ir_reduce_xor_op(value: IR.Value) -> IR.OpResult:
    """Create a reduce XOR operation: x.P -> parity(x)."""
    assert isinstance(value, IR.Value)
    ir_op = comb.ParityOp.create(value)
    return ir_op.result.value


def ir_concat_op(values: list[IR.Value]) -> IR.OpResult:
    """Create a concatenation operation: cat(x, ...) -> {x, ...}."""
    assert len(values) > 1
    assert all(isinstance(value, IR.Value) for value in values)
    ir_op = comb.ConcatOp(values)
    return ir_op.result


def ir_replicate_op(count: int, values: list[IR.Value]) -> IR.OpResult:
    """Create a replicate operation: rep(n, x, ...) -> n{x, ...}."""
    assert isinstance(count, int)
    assert len(values) >= 1
    if len(values) == 1:
        value = values[0]
        assert isinstance(value, IR.Value)
    else:
        value = ir_concat_op(values)
    value_width = ir_width(value)
    result_width = value_width * count
    result_type = ir_integer_type(result_width)
    ir_op = comb.ReplicateOp(result_type, value)
    return ir_op.result


# sv.verbatim: new line and code comment
#
def ir_match_sv_verbatim(ir: Any, text: str) -> bool:
    """Check if an IR element is an sv.verbatim with the given text string."""
    assert isinstance(text, str)
    if ir is None:
        return False
    assert hasattr(ir, "operation")
    ir = ir.operation
    assert isinstance(ir, IR.Operation)
    if ir.name != "sv.verbatim":
        return False
    opview = ir.opview
    assert isinstance(opview, sv.VerbatimOp)
    return opview.format_string.value == text


def ir_is_sv_newline(ir: Any) -> bool:
    """Check if an IR element is a Verilog newline."""
    return ir_match_sv_verbatim(ir, "")


def ir_sv_newline() -> sv.VerbatimOp | None:
    """Create a Verilog newline. Merge with previous if possible."""
    last_op = ir_last_op()
    if ir_is_sv_newline(last_op):
        return None
    return sv.verbatim("", [])


def ir_force_sv_newline() -> sv.VerbatimOp:
    """Force creating a Verilog new line."""
    return sv.verbatim("", [])


def ir_sv_comment_code(code_lines: Sequence[str]):
    """Insert Verilog comment for the given source code lines."""

    def count_indent(line: str) -> int:
        n = len(line)
        for i in range(n):
            if line[i] != " ":
                return i
        return n

    # The first non-empty line
    assert code_lines
    min_indent = 0
    for line in code_lines:
        if line.strip():
            min_indent = count_indent(line)
            break
    # Get the minimum indent
    for line in code_lines:
        if line.strip():
            min_indent = min(min_indent, count_indent(line))

    # Use // for short comments, /* ... */ for longer comments
    if len(code_lines) <= 3:
        for line in code_lines:
            if line.strip():
                unindented = line[min_indent:]
            else:
                unindented = ""
            sv.verbatim(f"// {unindented}", [])
    else:
        sv.verbatim("/*", [])
        for line in code_lines:
            if line.strip():
                unindented = line[min_indent:]
            else:
                unindented = ""
            sv.verbatim("  " + unindented, [])
        sv.verbatim(" */", [])


# IR representation
#
def ir_type_name(ir: Any) -> str:
    """Get the type name of a CIRCT IR element."""
    return ir.__class__.__name__


def ir_to_str(ir: Any) -> str:
    """Get the pretty-form representation of a CIRCT IR element."""
    assert hasattr(ir, "operation")
    output = io.StringIO()
    ir.operation.print(
        file=output, enable_debug_info=False, print_generic_op_form=False
    )
    return output.getvalue()


def ir_to_raw_str(ir: Any) -> str:
    """Get the generic-form representation of a CIRCT IR element."""
    assert hasattr(ir, "operation")
    output = io.StringIO()
    ir.operation.print(
        file=output, enable_debug_info=False, print_generic_op_form=True
    )
    return output.getvalue()
