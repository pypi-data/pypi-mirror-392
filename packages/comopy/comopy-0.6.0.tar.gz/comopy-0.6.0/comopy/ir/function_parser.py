# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Parse a Python function representing a connection or behavioral block.
"""

import ast
from contextlib import contextmanager
from functools import wraps
from itertools import chain
from types import FunctionType
from typing import Any, Callable, NamedTuple, Optional, Sequence

import circt.ir as IR
import circt.support as ir_support
from circt.dialects import comb, hw, sv

import comopy.hdl as HDL
from comopy.bits import DESC
from comopy.config import IRConfig, get_comopy_context
from comopy.datatypes import BitPat, Bits, Bits1, Bool, SignedBits
from comopy.hdl import cat, rep
from comopy.utils import CodePosition, FuncCodeInfo, HDLSyntaxError

from .aux_ir import *
from .circt_ir import *
from .object_parser import ObjectParser
from .parser_defs import *


class ExprContext(NamedTuple):
    """Expression parsing context."""

    at_lhs: bool = False  # Whether parsing at left-hand side of assignment
    connecting: bool = False  # Whether inside @= connection statement


@contextmanager
def parsing_context(func_info: FuncCodeInfo):
    try:
        yield
    except HDLSyntaxError as e:
        # Patch message with code position for AST node
        if e.node:
            assert isinstance(e.node, ast.AST)
            e.attach_code_info(func_info, e.node)
        raise e


class FunctionParser(ast.NodeVisitor):
    """An AST visitor that parses functions as connection or behavioral blocks.

    Analyze the AST of a Python function, check its syntax and symbols, and
    translate it into CIRCT IR.
    """

    # Configuration
    config: IRConfig

    # Module information
    module_node: HDL.CircuitNode
    module_obj: HDL.RawModule
    module_ir: hw.HWModuleOp
    module_symbols: dict[str, Any]  # IR entities collected for hw.HWModuleOp
    localparam_ip: IR.InsertionPoint
    obj_parser: ObjectParser
    constant_exprs: dict[IR.Value, Bits]  # IR -> constant value
    forced_i32_exprs: dict[IR.Value, ForcedI32Type]
    inst_writes: dict[str, HDL.Behavior]
    conn_writes: dict[str, HDL.Behavior]
    comb_writes: dict[str, HDL.Behavior]
    seq_writes: dict[str, HDL.Behavior]

    # Block information
    func_info: FuncCodeInfo
    is_seq: bool
    arg_self: str
    locals: dict[str, Any]
    globals: dict[str, Any]
    loop_vars: dict[str, LoopVar]
    node_ast_stack: list[ast.AST]  # Node AST stack for tracking node path
    body_deps_stack: list[HDL.Dependency]  # Dependencies for nested bodies

    # Statement information
    need_stmt_comment: bool
    expr_ctx_stack: list[ExprContext]  # Expression contexts for statements
    stmt_deps: HDL.Dependency  # Dependency for current statement

    def __init__(
        self, module_node: HDL.CircuitNode, localparam_ip: IR.InsertionPoint
    ):
        super().__init__()
        assert isinstance(localparam_ip, IR.InsertionPoint)
        assert isinstance(module_node, HDL.CircuitNode)
        assert module_node.is_assembled_module
        assert isinstance(module_node.obj, HDL.RawModule)

        # Configuration
        self.config = get_comopy_context().ir_config

        # Module information
        self.module_node = module_node
        self.module_obj = module_node.obj
        self.module_ir = self.module_obj.ir
        assert isinstance(self.module_ir, hw.HWModuleOp)
        self.module_symbols = ir_get_module_symbols(self.module_ir)
        self.localparam_ip = localparam_ip
        self.obj_parser = ObjectParser(module_node, self.module_symbols)
        self.constant_exprs = {}
        self.forced_i32_exprs = {}
        self.inst_writes = {}
        self.conn_writes = {}
        self.comb_writes = {}
        self.seq_writes = {}

        # Block information
        self.is_seq = False
        self.arg_self = ""
        self.locals = {}
        self.globals = {}
        self.loop_vars = {}
        self.node_ast_stack = []
        self.body_deps_stack = []

        # Statement information
        self.need_stmt_comment = True
        self.expr_ctx_stack = []
        self.stmt_deps = HDL.Dependency()

    # Interface methods
    #
    def behavior(self, block: HDL.Behavior, func_info: FuncCodeInfo):
        assert isinstance(block, HDL.Behavior)
        assert isinstance(func_info, FuncCodeInfo)
        self.func_info = func_info
        self.is_seq = block.kind == HDL.Behavior.Kind.SEQ_BLOCK
        self.node_ast_stack = []

        assert block.deps.reads == set()
        assert block.deps.writes == set()
        self.body_deps_stack = [block.deps]
        match block.kind:
            case HDL.Behavior.Kind.MODULE_INST:
                assert isinstance(block.inst, HDL.ModuleInst)
                self.parse_submodule(block.inst)
                self.inst_writes |= {s: block for s in block.deps.writes}
            case HDL.Behavior.Kind.CONNECTION:
                assert isinstance(block.conn, HDL.Connection)
                if block.conn.internal:
                    self.parse_port_connection(block.conn)
                    # Update block ID: [conn]dst -> [conn]dst_signal
                    assert len(block.deps.writes) == 1
                    target_id = list(block.deps.writes)[0]
                    block.set_conn_target_id(target_id)
                else:
                    self.parse_connection(block.conn)
                self.conn_writes |= {s: block for s in block.deps.writes}
            case HDL.Behavior.Kind.COMB_BLOCK:
                assert callable(block.func)
                self.parse_comb_block(block.func)
                self.comb_writes |= {s: block for s in block.deps.writes}
            case HDL.Behavior.Kind.SEQ_BLOCK:
                assert callable(block.func)
                assert not block.edges.pos_edges
                assert not block.edges.neg_edges
                self.parse_seq_block(block.func, block.edges)
                self.seq_writes |= {s: block for s in block.deps.writes}
        assert not self.node_ast_stack
        assert len(self.body_deps_stack) == 1

    def verify_module_driving(self):
        module_class = self.module_obj.__class__.__name__
        all_writes = set(self.inst_writes.keys())
        all_writes |= set(self.conn_writes.keys())
        all_writes |= set(self.comb_writes.keys())
        all_writes |= set(self.seq_writes.keys())

        # Check driving for output ports
        for port in self.module_obj.all_ports:
            assert isinstance(port, HDL.Wire) and port.is_port
            if port.is_input_port:
                all_writes.add(port.name)
            elif port.is_output_port:
                if port.name not in all_writes:
                    raise HDLSyntaxError(
                        None,
                        f"In module {module_class}, output port "
                        f"'{port.name}' is not driven.",
                    )
            else:
                assert port.is_inout_port
                assert False, "UNIMPLEMENTED"

        # Check driving for behavioral blocks
        all_blocks = chain(
            self.module_node.inst_blocks,
            self.module_node.conn_blocks,
            self.module_node.comb_blocks,
            self.module_node.seq_blocks,
        )
        for block in all_blocks:
            if block.kind == HDL.Behavior.Kind.MODULE_INST:
                part = block.inst.module_obj.name
            else:
                part = f"{block.func_name}()"
            for signal in block.deps.reads:
                if signal in all_writes:
                    continue
                raise HDLSyntaxError(
                    None,
                    f"In {module_class}.{part}, '{signal}' is not driven.",
                )

    # Symbol table
    #
    def add_symbol(self, name: str, ir: Any):
        assert name not in self.module_symbols
        assert ir is not None
        self.module_symbols[name] = ir

    def get_symbol(self, name: str) -> Any:
        assert name in self.module_symbols
        return self.module_symbols[name]

    # Constant expressions in the current module
    #
    def is_constant_expr(self, expr: Any) -> bool:
        expr = self.__ir_value(expr)
        return expr in self.constant_exprs

    def __ir_value(self, expr: Any) -> IR.Value:
        assert not isinstance(expr, int)
        ir_value = ir_support.get_value(expr)
        assert isinstance(ir_value, IR.Value)
        return ir_value

    def add_constant_expr(self, expr: IR.Value, value: Bits | bool):
        if isinstance(value, bool):
            value = Bits(1, value)
        assert isinstance(value, Bits)
        assert isinstance(expr, IR.Value)
        self.constant_exprs[expr] = value

    def constant_expr_value(self, expr: IR.Value) -> Bits:
        assert isinstance(expr, IR.Value)
        assert expr in self.constant_exprs
        return self.constant_exprs[expr]

    # Forced i32 expressions in the current module
    #
    # Due to CIRCT IR constraints, some integer expressions must use
    # fixed-width i32 type. This tracks expressions that should be treated
    # as having flexible width for further operations, similar to Verilog
    # integer literals that can adapt to context-dependent widths.
    #
    def is_forced_i32_expr(self, expr: Any) -> bool:
        expr = self.__ir_value(expr)
        return expr in self.forced_i32_exprs

    def add_forced_i32_expr(self, expr: IR.Value, forced_type: ForcedI32Type):
        assert isinstance(expr, IR.Value)
        self.forced_i32_exprs[expr] = forced_type

    def forced_i32_expr_type(self, expr: IR.Value) -> ForcedI32Type:
        assert isinstance(expr, IR.Value)
        assert expr in self.forced_i32_exprs
        return self.forced_i32_exprs[expr]

    # Context
    #
    # Decorator for parsing functions, catching syntax exceptions
    @staticmethod
    def parsing(func: Callable):
        @wraps(func)
        def func_with_context(self, *args, **kwargs):
            with parsing_context(self.func_info):
                return func(self, *args, **kwargs)

        return func_with_context

    # Context for parsing expressions
    @contextmanager
    def expr_context(self, at_lhs: bool, connecting: bool):
        context = ExprContext(at_lhs, connecting)
        self.expr_ctx_stack.append(context)
        try:
            yield context
        finally:
            self.expr_ctx_stack.pop()

    @property
    def at_lhs(self) -> bool:
        assert self.expr_ctx_stack
        return self.expr_ctx_stack[-1].at_lhs

    @property
    def connecting(self) -> bool:
        assert self.expr_ctx_stack
        return self.expr_ctx_stack[-1].connecting

    @property
    def body_deps(self) -> HDL.Dependency:
        assert self.body_deps_stack
        return self.body_deps_stack[-1]

    # Track node AST stack during traversal
    def visit(self, node: ast.AST) -> Any:
        self.node_ast_stack.append(node)
        try:
            return super().visit(node)
        finally:
            self.node_ast_stack.pop()

    # Behavioral blocks
    #
    @parsing
    def parse_submodule(self, inst: HDL.ModuleInst):
        assert isinstance(inst.module_obj, HDL.RawModule)
        submodule = inst.module_obj

        # Check module instance
        inst_id, inst_ir = self.obj_parser(submodule)
        assert inst_id == submodule.name
        assert isinstance(inst_ir, hw.InstanceOp)

        # Track dependency
        self.stmt_deps = self.body_deps
        for port in submodule.all_ports:
            assert isinstance(port, HDL.Wire) and port.is_port
            if port.is_input_port:
                dep_id = f"{inst_id}.{port.name}"
                self.stmt_deps.reads.add(dep_id)
            elif port.is_output_port:
                dep_id = f"{inst_id}.{port.name}"
                self.stmt_deps.writes.add(dep_id)
            else:
                assert port.is_inout_port
                assert False, "UNIMPLEMENTED"

    @parsing
    def parse_port_connection(self, conn: HDL.Connection):
        assert conn.internal
        func = conn.func
        assign_ast = conn.assign_ast
        assert isinstance(assign_ast.op, ast.MatMult)
        assert conn.target_id == "dst"

        # Python symbols
        closure = self.__get_closure(func)
        self.arg_self = ""
        self.globals = closure["builder_globals"]
        self.locals = closure["builder_locals"]
        self.loop_vars = {}

        # Track dependency
        self.stmt_deps = self.body_deps

        # Parse LHS
        # Errors checked during module instantiation in StructurePass
        assert isinstance(assign_ast.target, ast.Name)
        dst_name = assign_ast.target.id
        assert isinstance(dst_name, str) and dst_name in self.locals
        dst = self.locals[dst_name]
        assert isinstance(dst, HDL.Connectable)
        dst_id, _ = self.obj_parser(dst, None, at_lhs=True, query_id_only=True)
        self.stmt_deps.writes.add(dst_id)

        # Verify target is fully driven
        try:
            self.__verify_fully_driven(None, self.stmt_deps.writes)
        except HDLSyntaxError as e:
            code_pos = CodePosition(self.func_info, conn.lineno)
            e.attach_code_pos(code_pos)
            raise e

        # Parse RHS
        # Errors checked during module instantiation in StructurePass
        assert isinstance(assign_ast.value, ast.Name)
        src_name = assign_ast.value.id
        assert isinstance(src_name, str) and src_name in self.locals
        src = self.locals[src_name]
        if isinstance(src, int):
            return
        assert isinstance(src, HDL.Connectable)
        src_id, _ = self.obj_parser(
            src, None, at_lhs=False, query_id_only=True
        )
        self.stmt_deps.reads.add(src_id)

    @parsing
    def parse_connection(self, conn: HDL.Connection):
        assert not conn.internal
        func = conn.func
        assign_ast = conn.assign_ast
        assert isinstance(assign_ast.op, ast.MatMult)

        # Python symbols
        closure = self.__get_closure(func)
        self.arg_self = ""
        self.globals = closure["builder_globals"]
        self.locals = closure["builder_locals"]
        self.loop_vars = {}

        # Prepare context
        self.need_stmt_comment = False
        self.expr_ctx_stack = [ExprContext()]
        self.stmt_deps = self.body_deps
        marker_op = ir_force_sv_newline()

        # Parse LHS
        with self.expr_context(at_lhs=True, connecting=True):
            lhs_ir = self.visit(assign_ast.target)
        assert not isinstance(lhs_ir, int)  # illegal in Python
        lhs_width = ir_width(lhs_ir)

        # Verify targets are fully driven
        self.__verify_fully_driven(assign_ast.target, self.stmt_deps.writes)

        # Parse RHS
        with self.expr_context(at_lhs=False, connecting=False):
            rhs = self.visit(assign_ast.value)
        if isinstance(rhs, int):
            rhs_ir = self.__int_constant(assign_ast.value, lhs_width, rhs)
        else:
            rhs_ir = rhs
        assert isinstance(rhs_ir, IR.Value)
        rhs_width = ir_width(rhs_ir)

        # Truncate forced i32 operand
        if self.is_forced_i32_expr(rhs_ir):
            assert rhs_width == 32
            if lhs_width < 32:
                rhs_ir = ir_extract_op(rhs_ir, 0, lhs_width)
                rhs_width = lhs_width

        # Check operand widths
        # HDL assembler checks widths, but some cases slip through:
        # - Python allows 'Bits8 = Bits8 and Bits8', but HDL may not.
        # - If-expr width may be limited by dry-run.
        # So, IR width checking is still required.
        if lhs_width != rhs_width:
            op = "@="
            raise HDLSyntaxError(
                assign_ast,
                f"Width mismatch: Bits{lhs_width} {op} Bits{rhs_width}"
                f"\n- {FIX_WIDTH}",
            )

        # Create IR operation
        if isinstance(lhs_ir, ConcatLHS):
            if self.config.comment_lhs_concat:
                self.need_stmt_comment = True
            self.__assign_concat(lhs_ir, rhs_ir, sv.AssignOp)
        else:
            sv.AssignOp(lhs_ir, rhs_ir)
        self.__comment_stmt_code(assign_ast, marker_op)

    def __get_closure(self, func: Callable) -> dict[str, Any]:
        # Retrieve the closure variables for the function.
        # For connection blocks, the assembler injects builder's locals and
        # globals into the function's closure, allowing access to the
        # surrounding scope.
        closure = {}
        for i, var in enumerate(func.__code__.co_freevars):
            closure[var] = func.__closure__[i].cell_contents  # type: ignore
        return closure

    def __verify_fully_driven(
        self, target_node: Optional[ast.AST], writes: set[str]
    ):
        assert writes
        for signal_name in writes:
            signal = self.__get_signal(signal_name)

            # Ensure all bits are driven
            # Driven bits are tracked by dry-run in HDL stage.
            driven_bits = signal.data_driven
            expected_mask = (1 << signal.nbits) - 1
            if driven_bits.unsigned != expected_mask:
                raise HDLSyntaxError(
                    target_node, f"Signal '{signal_name}' is not fully driven."
                )

    def __get_signal(self, name: str) -> HDL.Signal:
        # Regular signal
        if "." not in name:
            signal = getattr(self.module_obj, name, None)
            assert isinstance(signal, HDL.Signal)
            return signal

        # Submodule port
        parts = name.split(".")
        assert len(parts) == 2, "UNIMPLEMENTED"
        submodule_name, port_name = parts
        submodule = getattr(self.module_obj, submodule_name, None)
        assert isinstance(submodule, HDL.RawModule)
        signal = getattr(submodule, port_name, None)
        assert isinstance(signal, HDL.Wire) and signal.is_port
        return signal

    # Insert source code comment before statements without direct IR mapping.
    def __comment_stmt_code(self, stmt: ast.stmt, marker_op: Any):
        assert isinstance(stmt, ast.stmt)
        if self.need_stmt_comment:
            code_lines = self.__stmt_code_lines(stmt)
            with IR.InsertionPoint(marker_op):
                ir_sv_comment_code(code_lines)
        marker_op.operation.erase()
        self.need_stmt_comment = False

    def __stmt_code_lines(self, stmt: ast.stmt) -> list[str]:
        assert isinstance(stmt, ast.stmt)
        assert isinstance(self.func_info, FuncCodeInfo)
        start = stmt.lineno - 1
        end = stmt.end_lineno
        assert isinstance(end, int) and end <= len(self.func_info.code_lines)
        return self.func_info.code_lines[start:end]

    @parsing
    def parse_comb_block(self, block_func: Callable):
        assert callable(block_func)
        assert isinstance(self.func_info, FuncCodeInfo)
        tree = self.func_info.ast_root
        assert isinstance(tree, ast.Module)
        assert len(tree.body) == 1
        assert isinstance(tree.body[0], ast.FunctionDef)
        func = tree.body[0]
        assert func.name == block_func.__name__

        # Check arguments
        n_args = len(func.args.args)
        if n_args != 1:
            raise HDLSyntaxError(
                func,
                "@comb block must take exactly one 'self' argument.",
            )
        if func.args.vararg or func.args.kwonlyargs:
            raise HDLSyntaxError(
                func, "@comb block cannot use *args or **kwargs."
            )
        if len(func.args.defaults) == n_args:
            raise HDLSyntaxError(
                func.args.defaults[0],
                "'self' in @comb block cannot have a default value.",
            )
        self.arg_self = func.args.args[0].arg

        # Python symbols
        assert not block_func.__closure__
        self.globals = block_func.__globals__
        self.locals = {}
        self.loop_vars = {}

        # Create always_comb block
        always_comb = sv.alwayscomb()
        always_comb.regions[0].blocks.append()
        with IR.InsertionPoint(always_comb.regions[0].blocks[0]):
            self.__parse_body(func.body)

    def __parse_body(self, body: list[ast.stmt]):
        for stmt in body:
            # Prepare context
            self.need_stmt_comment = False
            self.expr_ctx_stack = [ExprContext()]
            self.stmt_deps = HDL.Dependency()

            # Parse statement
            marker_op = ir_force_sv_newline()
            self.visit(stmt)
            self.__comment_stmt_code(stmt, marker_op)

            # Update dependency
            deps = self.body_deps
            self.stmt_deps.reads -= deps.writes
            deps.reads |= self.stmt_deps.reads
            deps.writes |= self.stmt_deps.writes

    @parsing
    def parse_seq_block(self, block_func: Callable, edges: HDL.Sensitivity):
        assert callable(block_func)
        assert isinstance(self.func_info, FuncCodeInfo)
        tree = self.func_info.ast_root
        assert isinstance(tree, ast.Module)
        assert len(tree.body) == 1
        assert isinstance(tree.body[0], ast.FunctionDef)
        func = tree.body[0]
        assert func.name == block_func.__name__

        # Parse edge arguments
        n_args = len(func.args.args)
        if n_args < 1:
            raise HDLSyntaxError(
                func,
                "@seq block must have a 'self' argument.",
            )
        if n_args > 3:
            raise HDLSyntaxError(
                func,
                "@seq block must have at most 3 arguments: "
                "self, posedge, negedge.",
            )
        if func.args.vararg or func.args.kwonlyargs:
            raise HDLSyntaxError(
                func, "@seq block cannot use *args or **kwargs."
            )
        if len(func.args.defaults) == n_args:
            raise HDLSyntaxError(
                func.args.defaults[0],
                "'self' in @seq block cannot have a default value.",
            )
        self.arg_self = func.args.args[0].arg
        if self.arg_self in ("posedge", "negedge"):
            raise HDLSyntaxError(
                func.args.args[0],
                "@seq block the first argument must be 'self'.",
            )
        pos_edges, neg_edges = self.__parse_edge_args(
            func.args.args[1:], func.args.defaults
        )
        if not pos_edges and not neg_edges:
            # TODO implicit clock
            raise HDLSyntaxError(
                func,
                "@seq block requires at least one edge argument "
                "(posedge=..., negedge=...)."
                "\n- Use HDL.Module, which provides an implicit clock.",
            )
        edges.pos_edges = pos_edges
        edges.neg_edges = neg_edges
        deps = self.body_deps
        deps.reads |= set(pos_edges + neg_edges)

        # Python symbols
        assert not block_func.__closure__
        self.globals = block_func.__globals__
        self.locals = {}
        self.loop_vars = {}

        # EventControl attributes
        AtPosEdge = ir_enum_attr(0)
        AtNegEdge = ir_enum_attr(1)

        # Prepare events ArrayAttr and clocks for sv.AlwaysOp
        events = [AtPosEdge for _ in pos_edges]
        events += [AtNegEdge for _ in neg_edges]
        clocks = [ir_get_module_input(self.module_ir, c) for c in pos_edges]
        clocks += [ir_get_module_input(self.module_ir, c) for c in neg_edges]
        assert all(isinstance(c, IR.BlockArgument) for c in clocks)
        events_attr = IR.ArrayAttr.get(events)

        # Create always block
        always_block = sv.always(events_attr, clocks)
        always_block.regions[0].blocks.append()
        with IR.InsertionPoint(always_block.regions[0].blocks[0]):
            self.__parse_body(func.body)

    def __parse_edge_args(
        self, args: list[ast.arg], defaults: list[ast.expr]
    ) -> tuple[list[str], list[str]]:
        # Find posedge and negedge arguments
        posedge_arg_idx = -1
        negedge_arg_idx = -1
        for i, arg in enumerate(args):
            if arg.arg not in ("posedge", "negedge"):
                pos = "second" if i == 0 else "third"
                raise HDLSyntaxError(
                    arg,
                    f"@seq block the {pos} argument should be "
                    "'posedge' or 'negedge'.",
                )
            if arg.arg == "posedge":
                assert posedge_arg_idx < 0
                posedge_arg_idx = i
            if arg.arg == "negedge":
                assert negedge_arg_idx < 0
                negedge_arg_idx = i
        n_defaults = len(defaults)
        if n_defaults != len(args):
            assert n_defaults < len(args)
            edge = args[0].arg
            raise HDLSyntaxError(
                args[0],
                f"Argument '{edge}' must be a signal or signal tuple.",
            )

        # Parse edge arguments
        pos_edges = []
        neg_edges = []
        if posedge_arg_idx >= 0:
            value = defaults[posedge_arg_idx]
            port_names = self.__parse_edge_signals(
                value, self.module_obj._auto_pos_edges, "posedge"
            )
            assert port_names
            pos_edges = port_names
        if negedge_arg_idx >= 0:
            value = defaults[negedge_arg_idx]
            port_names = self.__parse_edge_signals(
                value, self.module_obj._auto_neg_edges, "negedge"
            )
            assert port_names
            neg_edges = port_names

        # Add auto edges to the final edge lists
        pos_edges = list(self.module_obj._auto_pos_edges) + pos_edges
        neg_edges = list(self.module_obj._auto_neg_edges) + neg_edges

        return pos_edges, neg_edges

    def __parse_edge_signals(
        self, node: ast.expr, auto_edges: Sequence[str], edge_type: str
    ) -> list[str]:
        FIX_EDGE = (
            f'Use {edge_type}="<signal>" or '
            f'{edge_type}=("<signal1>", "<signal2>").'
        )

        if not isinstance(node, (ast.Constant, ast.Tuple)):
            raise HDLSyntaxError(
                node,
                f"Argument '{edge_type}' must be a string or tuple of strings."
                f"\n- {FIX_EDGE}",
            )

        # edge = str
        if isinstance(node, ast.Constant):
            if not isinstance(node.value, str):
                raise HDLSyntaxError(
                    node,
                    f"Argument '{edge_type}' must be a string or "
                    "tuple of strings."
                    f"\n- {FIX_EDGE}",
                )
            if not node.value:
                raise HDLSyntaxError(
                    node,
                    f"Argument '{edge_type}' cannot be an empty string."
                    f"\n- {FIX_EDGE}",
                )
            port_name = self.__parse_edge_port(node)
            if port_name in auto_edges:
                raise HDLSyntaxError(
                    node,
                    f"Signal '{port_name}' is already an automatic edge.",
                )
            return [port_name]

        # edge = tuple[str]
        assert isinstance(node, ast.Tuple)
        if not node.elts:
            raise HDLSyntaxError(
                node,
                f"Argument '{edge_type}' cannot be an empty tuple."
                f"\n- {FIX_EDGE}",
            )
        port_names = []
        for p in node.elts:
            if not (isinstance(p, ast.Constant) and isinstance(p.value, str)):
                raise HDLSyntaxError(
                    p,
                    f"Argument '{edge_type}' must be a string or "
                    "tuple of strings."
                    f"\n- {FIX_EDGE}",
                )
            port_name = self.__parse_edge_port(p)
            if port_name in auto_edges:
                raise HDLSyntaxError(
                    p,
                    f"Signal '{port_name}' is already an automatic edge.",
                )
            if port_name in port_names:
                raise HDLSyntaxError(
                    p,
                    f"Signal '{port_name}' appears multiple times "
                    f"in {edge_type} tuple.",
                )
            port_names.append(port_name)
        return port_names

    def __parse_edge_port(self, node: ast.Constant) -> str:
        assert isinstance(node.value, str)
        port_name = node.value
        module_class = self.module_obj.__class__.__name__
        if not hasattr(self.module_obj, port_name):
            raise HDLSyntaxError(
                node,
                f"Signal '{port_name}' not found in module {module_class}.",
            )
        port = getattr(self.module_obj, port_name, None)
        if not isinstance(port, HDL.Signal):
            raise HDLSyntaxError(
                node,
                f"In module {module_class}, '{port_name}' is not a signal.",
            )
        if not port.is_scalar_input:
            raise HDLSyntaxError(
                node,
                f"Clock/reset signal '{port_name}' must be "
                "a 1-bit input port.",
            )
        return port_name

    # Class and function definition
    #
    def visit_FunctionDef(self, node: ast.FunctionDef):
        raise HDLSyntaxError(
            node, "Nested functions are not supported in behavioral blocks."
        )

    def visit_ClassDef(self, node: ast.ClassDef):
        raise HDLSyntaxError(
            node, "Nested classes are not supported in behavioral blocks."
        )

    # Statements
    #
    def visit_Assign(self, node: ast.Assign):
        func_name = self.func_info.func.__qualname__
        if self.is_seq:
            raise HDLSyntaxError(
                node,
                f"Wrong assignment in @seq {func_name}()."
                "\n- Use <<= (non-blocking assignment) in @seq block.",
            )
        else:
            raise HDLSyntaxError(
                node,
                f"Wrong assignment in @comb {func_name}()."
                "\n- Use /= (blocking assignment) in @comb block.",
            )

    def visit_AugAssign(self, node: ast.AugAssign):
        func_name = self.func_info.func.__qualname__
        if self.is_seq and not isinstance(node.op, ast.LShift):
            raise HDLSyntaxError(
                node,
                f"Wrong assignment in @seq {func_name}()."
                "\n- Use <<= (non-blocking assignment) in @seq block.",
            )
        if not self.is_seq and not isinstance(node.op, ast.Div):
            raise HDLSyntaxError(
                node,
                f"Wrong assignment in @comb {func_name}()."
                "\n- Use /= (blocking assignment) in @comb block.",
            )

        # Parse LHS
        with self.expr_context(at_lhs=True, connecting=False):
            lhs_ir = self.visit(node.target)
        assert lhs_ir is not None, "UNIMPLEMENTED"
        assert not isinstance(lhs_ir, int)  # illegal in Python
        lhs_width = ir_width(lhs_ir)

        # Verify targets are signal driven
        self.__verify_single_driven(node.target, self.stmt_deps.writes)

        # Parse RHS
        with self.expr_context(at_lhs=False, connecting=False):
            rhs = self.visit(node.value)
        if isinstance(rhs, int):
            rhs_ir = self.__int_constant(node.value, lhs_width, rhs)
        else:
            rhs_ir = rhs
        assert isinstance(rhs_ir, IR.Value)
        rhs_width = ir_width(rhs_ir)

        # Truncate forced i32 operand
        if self.is_forced_i32_expr(rhs_ir):
            assert rhs_width == 32
            if lhs_width < 32:
                rhs_ir = ir_extract_op(rhs_ir, 0, lhs_width)
                rhs_width = lhs_width

        # Check operand widths
        if lhs_width != rhs_width:
            op = "<<=" if self.is_seq else "/="
            raise HDLSyntaxError(
                node,
                f"Width mismatch: Bits{lhs_width} {op} Bits{rhs_width}"
                f"\n- {FIX_WIDTH}",
            )

        # Create IR operation
        assign_op = sv.PAssignOp if self.is_seq else sv.BPAssignOp
        if isinstance(lhs_ir, ConcatLHS):
            if self.config.comment_lhs_concat:
                self.need_stmt_comment = True
            self.__assign_concat(lhs_ir, rhs_ir, assign_op)
        else:
            assign_op(lhs_ir, rhs_ir)

    def __verify_single_driven(self, target_node: ast.AST, writes: set[str]):
        assert writes
        for signal in writes:
            if signal in self.conn_writes:
                conn = self.conn_writes[signal]
                assert isinstance(conn, HDL.Behavior)
                assert conn.kind == HDL.Behavior.Kind.CONNECTION
                func = conn.func_name
                raise HDLSyntaxError(
                    target_node,
                    f"Signal '{signal}' has been driven by @= in {func}().",
                )
            if signal in self.comb_writes:
                block = self.comb_writes[signal]
                assert isinstance(block, HDL.Behavior)
                assert block.kind == HDL.Behavior.Kind.COMB_BLOCK
                func = block.func_name
                raise HDLSyntaxError(
                    target_node,
                    f"Signal '{signal}' has been driven by /= in {func}().",
                )
            if signal in self.seq_writes:
                block = self.seq_writes[signal]
                assert isinstance(block, HDL.Behavior)
                assert block.kind == HDL.Behavior.Kind.SEQ_BLOCK
                func = block.func_name
                raise HDLSyntaxError(
                    target_node,
                    f"Signal '{signal}' has been driven by <<= in {func}().",
                )

    def __assign_concat(
        self,
        lhs: ConcatLHS,
        rhs: IR.Value,
        assign_op: type[sv.AssignOp | sv.PAssignOp | sv.BPAssignOp],
    ):
        total_width = ir_width(rhs)
        assert total_width == lhs.width

        pos = total_width
        for part, width in lhs.parts:
            pos -= width
            rhs_ir = ir_extract_op(rhs, pos, width)
            part_rhs = ir_rvalue(rhs_ir)
            if isinstance(part, ConcatLHS):
                self.__assign_concat(part, part_rhs, assign_op)
            else:
                assign_op(part, part_rhs)

    def visit_If(self, node: ast.If):
        # Parse condition
        with self.expr_context(at_lhs=False, connecting=False):
            condition = self.visit(node.test)
        if isinstance(condition, int):
            condition_ir = self.__int_constant(node.test, 1, bool(condition))
        else:
            cond_bool = ir_bool_bit_op(condition)
            condition_ir = ir_rvalue(cond_bool)
        assert isinstance(condition_ir, IR.Value)
        cond_deps = self.stmt_deps
        assert not cond_deps.writes

        # Create sv.IfOp operation
        if_op = sv.IfOp(condition_ir)

        # Create then-body
        assert node.body
        then_deps = HDL.Dependency()
        self.body_deps_stack.append(then_deps)
        if_op.thenRegion.blocks.append()
        with IR.InsertionPoint(if_op.thenRegion.blocks[0]):
            self.__parse_body(node.body)
        self.body_deps_stack.pop()

        # Create else-body
        else_deps = HDL.Dependency()
        if node.orelse:
            self.body_deps_stack.append(else_deps)
            if_op.elseRegion.blocks.append()
            with IR.InsertionPoint(if_op.elseRegion.blocks[0]):
                self.__parse_body(node.orelse)
            self.body_deps_stack.pop()

        # Update dependency
        assert self.stmt_deps is not cond_deps
        self.stmt_deps.reads = (
            cond_deps.reads | then_deps.reads | else_deps.reads
        )
        self.stmt_deps.writes = then_deps.writes | else_deps.writes

    def visit_Match(self, node: ast.Match):
        # CaseStmtType attributes
        CaseStmt = ir_enum_attr(0)
        # CaseXStmt = ir_enum_attr(1)
        CaseZStmt = ir_enum_attr(2)

        # ValidationQualifierTypeEnum attributes
        #
        # SVStatements.td: ValidationQualifierTypeEnum.genSpecializedAttr = 0
        # => No Python binding generated
        # ValidationQualifierTypeAttr: EnumAttr, not I32EnumAttr
        # => Cannot use ir_enum_attr()
        # Use IR.Attribute.parse() to create these enumeration attributes.
        def _validation_qualifier_attr(name: str) -> IR.Attribute:
            return IR.Attribute.parse(f"#sv<validation_qualifier {name}>")

        ValidationQualifierPlain = _validation_qualifier_attr("plain")
        ValidationQualifierUnique = _validation_qualifier_attr("unique")
        # ValidationQualifierUnique0 = _validation_qualifier_attr("unique0")
        # ValidationQualifierPriority = _validation_qualifier_attr('priority')

        # Parse subject
        with self.expr_context(at_lhs=False, connecting=False):
            subject_ir = self.visit(node.subject)
        if isinstance(subject_ir, int) or self.is_constant_expr(subject_ir):
            raise HDLSyntaxError(
                node.subject, "Match subject cannot be a constant."
            )
        assert isinstance(subject_ir, IR.Value)
        # TODO match loop-var, .W, i32 expr
        assert not self.is_forced_i32_expr(subject_ir)
        width = ir_width(subject_ir)
        all_deps = self.stmt_deps
        assert not all_deps.writes

        # Parse patterns
        patterns = self.__parse_patterns(node, width)
        assert len(patterns) == len(node.cases)
        has_wildcard = any(isinstance(p, BitPat) for p in patterns)
        if has_wildcard:
            style = CaseZStmt
            # Use plain casez, let synthesis tools decide priority.
            qualifier = ValidationQualifierPlain
        else:
            style = CaseStmt
            # Use unique case to enforce complete coverage or default.
            qualifier = ValidationQualifierUnique
            self.__verify_patterns(node, width, patterns)

        # Create sv.CaseOp operation
        n_regions = len(node.cases)
        pattern_attrs = [self.__pattern_attr(p, width) for p in patterns]
        case_op = sv.CaseOp(
            cond=subject_ir,
            casePatterns=pattern_attrs,
            num_caseRegions=n_regions,
            caseStyle=style,
            validationQualifier=qualifier,
        )
        for region in case_op.regions:
            region.blocks.append()

        # Parse case bodies
        for i, case in enumerate(node.cases):
            assert isinstance(case, ast.match_case)
            assert case.body
            case_block = case_op.regions[i].blocks[0]
            body_deps = HDL.Dependency()
            self.body_deps_stack.append(body_deps)
            with IR.InsertionPoint(case_block):
                pattern = patterns[i]
                if isinstance(pattern, CaseDefault) and pattern.explicit_empty:
                    sv.verbatim(
                        "// Empty default for unique case completeness", []
                    )
                self.__parse_body(case.body)
            self.body_deps_stack.pop()

            # Update dependency
            assert self.stmt_deps is not all_deps
            all_deps.reads |= body_deps.reads
            all_deps.writes |= body_deps.writes
        self.stmt_deps = all_deps

    def __parse_patterns(
        self, node: ast.Match, width: int
    ) -> list[int | BitPat | CaseDefault]:
        patterns = []
        for item in node.cases:
            assert isinstance(item, ast.match_case)
            if item.guard is not None:
                raise HDLSyntaxError(
                    item.guard,
                    "Guards in match cases are not supported.",
                )

            pattern = self.visit(item.pattern)
            if isinstance(pattern, int):
                try:
                    Bits(width, pattern)
                except ValueError as e:
                    raise HDLSyntaxError(item.pattern, f"{e}\n- {FIX_WIDTH}")
            elif isinstance(pattern, str):
                try:
                    pattern = BitPat(pattern)
                except ValueError as e:
                    raise HDLSyntaxError(item.pattern, str(e))
                if pattern.nbits != width:
                    raise HDLSyntaxError(
                        item.pattern,
                        f"Pattern width mismatch: "
                        f"expected {width}, got {pattern.nbits}.",
                    )
            elif isinstance(pattern, CaseDefault):
                assert item.body
                if isinstance(item.body[0], ast.Pass):
                    if len(item.body) > 1:
                        raise HDLSyntaxError(
                            item.body[0],
                            "'pass' indicates an empty default case, "
                            "but another statement follows.",
                        )
                    pattern.explicit_empty = True
            else:
                # Unsupported pattern types: MatchClass, MatchSingleton, etc.
                raise HDLSyntaxError(
                    item.pattern,
                    "Pattern must be an integer or a bit pattern string."
                    f"\n- {FIX_DEFAULT}",
                )
            patterns.append(pattern)
        return patterns

    def __verify_patterns(
        self,
        node: ast.Match,
        width: int,
        patterns: list[int | BitPat | CaseDefault],
    ):
        seen_values = set()
        has_default = False

        # Check uniqueness and find default
        for i, pattern in enumerate(patterns):
            pattern_node = node.cases[i].pattern

            if isinstance(pattern, CaseDefault):
                has_default = True
                assert i == len(patterns) - 1
                continue

            assert isinstance(pattern, int)
            if pattern in seen_values:
                raise HDLSyntaxError(
                    pattern_node,
                    f"Duplicate pattern {pattern} in match statement.",
                )
            seen_values.add(pattern)

        # Check completeness
        n_all = 1 << width
        n_cases = len(seen_values)
        if n_cases < n_all and not has_default:
            missing_values = [v for v in range(n_all) if v not in seen_values]
            missing = ", ".join(str(v) for v in missing_values[:3])
            if len(missing_values) > 3:
                missing += ", ..."
            raise HDLSyntaxError(
                node,
                f"Match statement must cover all cases for {width}-bit value."
                f"\n- Missing {n_all - n_cases} patterns: {missing}"
                f"\n- {FIX_DEFAULT}",
            )

    def __pattern_attr(
        self, pattern: int | BitPat | CaseDefault, width: int
    ) -> IR.IntegerAttr | IR.UnitAttr:
        assert isinstance(pattern, (int, BitPat, CaseDefault))
        match pattern:
            case int():
                bits = Bits(width, pattern)
                return ir_case_pattern_attr(bits.pattern())
            case BitPat():
                assert pattern.nbits == width
                return ir_case_pattern_attr(pattern.pattern())
            case CaseDefault():
                return ir_case_pattern_attr("")

    def visit_MatchAs(self, node: ast.MatchAs) -> CaseDefault:
        if node.pattern is not None or node.name is not None:
            raise HDLSyntaxError(
                node,
                "Variable capture in match patterns is not supported."
                f"\n- {FIX_DEFAULT}",
            )
        return CaseDefault()

    def visit_MatchValue(self, node: ast.MatchValue) -> int | str:
        value = self.visit(node.value)
        # visit_Constant ensures value is int or str
        assert isinstance(value, (int, str))
        return value

    def visit_For(self, node: ast.For):
        if node.orelse:
            raise HDLSyntaxError(
                node.orelse[0],
                "For-else is not supported in behavioral blocks.",
            )

        # Loop variable
        if not isinstance(node.target, ast.Name):
            raise HDLSyntaxError(
                node.target,
                "For loop variable must be a simple name.",
            )
        loop_var_name = node.target.id
        try:
            var = self.visit(node.target)
        except Exception:
            var = None
        if var is not None:
            raise HDLSyntaxError(
                node.target,
                f"Loop variable '{loop_var_name}' conflicts with "
                "an existing symbol.",
            )

        # Iteration range
        with self.expr_context(at_lhs=False, connecting=False):
            loop_range = self.visit(node.iter)
            if not isinstance(loop_range, LoopRange):
                raise HDLSyntaxError(
                    node.iter,
                    "For loop must iterate over "
                    "range([lower, ]upper[, step]).",
                )

        # Create sv.ForOp operation
        start_ir = ir_constant_op(32, loop_range.start)
        stop_ir = ir_constant_op(32, loop_range.stop)
        step_ir = ir_constant_op(32, loop_range.step)
        for_op = sv.ForOp(
            start_ir, stop_ir, step_ir, inductionVarName=loop_var_name
        )

        # Create loop body
        assert node.body
        for_op.body.blocks.append(start_ir.type)  # Arg0 type for loop var
        for_block = for_op.body.blocks[0]
        loop_var = for_block.arguments[0]
        assert isinstance(loop_var, IR.BlockArgument)
        self.loop_vars[loop_var_name] = LoopVar(loop_var_name, loop_var)
        self.add_forced_i32_expr(loop_var, ForcedI32Type.LOOP_VAR)
        with IR.InsertionPoint(for_block):
            self.__parse_body(node.body)
        self.loop_vars.pop(loop_var_name)

    def visit_Break(self, node: ast.Break):
        raise HDLSyntaxError(
            node,
            "Break statement is not supported in for loops "
            "within behavioral blocks.",
        )

    def visit_Continue(self, node: ast.Continue):
        raise HDLSyntaxError(
            node,
            "Continue statement is not supported in for loops "
            "within behavioral blocks.",
        )

    # Expression: operands
    #
    def __int_constant(
        self, node: ast.AST, width: int, value: int
    ) -> IR.Value:
        assert width > 0
        try:
            bits = Bits(width, value)
        except ValueError as e:
            raise HDLSyntaxError(node, f"{e}\n- {FIX_WIDTH}")
        ir_op = ir_constant_op(width, value)
        assert isinstance(ir_op, IR.Value)
        self.add_constant_expr(ir_op, bits)
        return ir_rvalue(ir_op)

    def visit_Constant(self, node: ast.Constant) -> int | str:
        if self.at_lhs:
            raise HDLSyntaxError(node, "Cannot assign to a constant.")
        if isinstance(node.value, int):
            return node.value
        if isinstance(node.value, str):
            if self.__in_match_value():
                return node.value
            raise HDLSyntaxError(
                node, "String constants are only allowed in match patterns."
            )
        const_type = type(node.value).__name__
        raise HDLSyntaxError(
            node,
            f"Unsupported constant type '{const_type}' in behavioral blocks.",
        )

    def __in_match_value(self) -> bool:
        if len(self.node_ast_stack) < 2:
            return False
        parent = self.node_ast_stack[-2]
        leaf = self.node_ast_stack[-1]
        return isinstance(parent, ast.MatchValue) and leaf is parent.value

    def visit_Name(self, node: ast.Name) -> Any:
        name = node.id
        assert isinstance(name, str)

        # Module's self argument
        if self.arg_self and name == self.arg_self:
            return self.module_obj

        # Loop variable
        if name in self.loop_vars:
            loop_var = self.loop_vars[name]
            return loop_var.var

        # Local variable
        if name in self.locals:
            return self.__local_var(node)

        # Global constant
        if name in self.globals:
            if constant_ir := self.__global_constant(node):
                return constant_ir

        # Lookup name in locals, globals, or builtins
        obj = self.__lookup_name(name)

        # Bits subclasses
        if isinstance(obj, type) and issubclass(obj, Bits):
            return obj

        # HDL functions
        if obj in HDL_SYMBOLS:
            return obj

        raise HDLSyntaxError(node, f"Undefined symbol '{name}'.")

    def __local_var(self, node: ast.Name) -> Any:
        name = node.id
        assert isinstance(name, str)
        obj = self.locals[name]
        if obj is self.module_obj:
            # 'self' in locals
            return self.module_obj
        assert False, "UNIMPLEMENTED"

    def __global_constant(self, node: ast.Name) -> Optional[IR.Value]:
        name = node.id
        assert isinstance(name, str)
        obj = self.globals[name]
        if not isinstance(obj, (int, Bits)):
            return None
        obj_value = obj if isinstance(obj, Bits) else Bits(32, int(obj))

        if self.at_lhs:
            type_name = "integer" if isinstance(obj, int) else "Bits"
            raise HDLSyntaxError(
                node, f"Cannot assign to {type_name} constant '{name}'."
            )

        # HDL Bits constant，FALSE/TRUE/...
        if name in HDL_CONSTANT_NAMES:
            assert isinstance(obj, Bits)
            bits_ir = ir_constant_op(obj.nbits, obj.unsigned)
            self.add_constant_expr(bits_ir, obj)
            return ir_rvalue(bits_ir)

        # Local parameter
        if name in self.module_symbols:
            param_ir = self.get_symbol(name)
            param_value = self.constant_expr_value(param_ir)
            assert param_value == obj_value
            return ir_rvalue(param_ir)

        # Create localparam for a global constant
        if isinstance(obj, int):
            int_type = ir_integer_type(32)
            int_attr = IR.IntegerAttr.get(int_type, obj)
            forced_i32_param = True
        else:
            assert isinstance(obj, Bits)
            int_type = ir_integer_type(obj.nbits)
            int_attr = IR.IntegerAttr.get(int_type, obj.unsigned)
            forced_i32_param = False
        with self.localparam_ip:
            param_ir = sv.localparam(int_attr, name)
        self.add_symbol(name, param_ir)
        self.add_constant_expr(param_ir, obj_value)
        if forced_i32_param:
            self.add_forced_i32_expr(param_ir, ForcedI32Type.LOCAL_PARAM)
        return ir_rvalue(param_ir)

    def __lookup_name(self, name: str) -> Any:
        if name in self.locals:
            return self.locals[name]
        if name in self.globals:
            return self.globals[name]
        assert isinstance(__builtins__, dict)
        if name in __builtins__:
            return __builtins__[name]
        return None

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        # Parse base
        base = self.visit(node.value)

        # Resolve attribute
        assert isinstance(node.attr, str)
        if isinstance(base, HDL.RawModule):
            # Submodule attribute
            if base is not self.module_obj:
                return self.__visit_submodule_port(node, base)

            # Module attribute
            if not hasattr(base, node.attr):
                module_class = base.__class__.__name__
                raise HDLSyntaxError(
                    node,
                    f"Attribute '{node.attr}' not found "
                    f"in module {module_class}.",
                )
            attr = getattr(base, node.attr)
            if not isinstance(attr, HDL.CircuitObject):
                raise HDLSyntaxError(
                    node,
                    f"Type of attribute '{node.attr}' is not supported."
                    f"\n- {FIX_PARAM}",
                )
            assert attr.assembled and attr.name == node.attr
        elif isinstance(base, IR.Value) and self.is_forced_i32_expr(base):
            raise HDLSyntaxError(
                node,
                f"No attribute '{node.attr}' for integer expressions.",
            )
        elif isinstance(base, (IR.Value, sv.LogicOp, SignedValue)):
            # Bits attribute
            # sv.LogicOp at LHS is only for error checking.
            if node.attr in HDL_BITS_PROPERTIES:
                assert not isinstance(base, SignedValue)
                return self.__bits_property(node, base)
            if node.attr in HDL_BITS_METHODS:
                # ext() supports SignedValue
                return self.__bits_method(node, base)
            raise HDLSyntaxError(
                node,
                f"Cannot access attribute '{node.attr}'.",
            )
        else:
            # TODO struct, union, ...
            assert False, "UNIMPLEMENTED"

        # Submodule instance
        if isinstance(attr, HDL.RawModule):
            if not (
                len(self.node_ast_stack) >= 2
                and isinstance(self.node_ast_stack[-2], ast.Attribute)
            ):
                raise HDLSyntaxError(
                    node, "Cannot use a submodule directly as operand."
                )
            return attr
        assert isinstance(attr, (HDL.Signal, HDL.SignalArray))

        # Track dependency
        if self.at_lhs:
            self.stmt_deps.writes.add(node.attr)
        else:
            self.stmt_deps.reads.add(node.attr)

        # Input port
        if attr.is_input_port:
            if self.at_lhs:
                raise HDLSyntaxError(
                    node, f"Cannot assign to input port '{node.attr}'."
                )
            return ir_get_module_input(self.module_ir, node.attr)

        # Output port
        if attr.is_output_port:
            output_wire = auto_module_output(node.attr)
            logic_op = self.get_symbol(output_wire)
            assert isinstance(logic_op, sv.LogicOp)
            return self.__access_signal_ir(logic_op)

        # Variables
        attr_ir = self.get_symbol(node.attr)
        assert isinstance(attr_ir, sv.LogicOp)

        # Signal array
        if isinstance(attr, HDL.SignalArray):
            if not self.__allow_array():
                raise HDLSyntaxError(
                    node, "Unpacked arrays cannot be used without indexing."
                )
            assert ir_is_unpacked_array(attr_ir)
            return attr_ir

        return self.__access_signal_ir(attr_ir)

    def __visit_submodule_port(
        self, node: ast.Attribute, submodule: HDL.RawModule
    ) -> Any:
        assert submodule.node.owner is self.module_node
        if not hasattr(submodule, node.attr):
            raise HDLSyntaxError(
                node,
                f"Attribute '{node.attr}' not found in "
                f"submodule '{submodule.name}'.",
            )
        port = getattr(submodule, node.attr)
        if not (isinstance(port, HDL.CircuitObject) and port.is_port):
            raise HDLSyntaxError(
                node,
                f"Attribute '{node.attr}' in submodule '{submodule.name}' "
                "is not a port.",
            )
        assert port.assembled and port.name == node.attr

        # Track dependency
        port_name = f"{submodule.name}.{node.attr}"
        if self.at_lhs:
            self.stmt_deps.writes.add(port_name)
        else:
            self.stmt_deps.reads.add(port_name)

        assert not port.is_inout_port, "UNIMPLEMENTED"
        if port.is_input_port:
            if not self.at_lhs:
                raise HDLSyntaxError(
                    node, f"Cannot read submodule input port '{port_name}'."
                )
            var_name = auto_inst_input(submodule.name, node.attr)
            var_ir = self.get_symbol(var_name)
            assert isinstance(var_ir, sv.LogicOp)
            return self.__access_signal_ir(var_ir)

        if port.is_output_port:
            if self.at_lhs:
                raise HDLSyntaxError(
                    node,
                    f"Cannot assign to submodule output port '{port_name}'.",
                )
            inst_ir = self.get_symbol(submodule.name)
            assert isinstance(inst_ir, hw.InstanceOp)
            return ir_get_instance_output(inst_ir, node.attr)

    def __access_signal_ir(self, ir_op: Any) -> Any:
        return ir_op if self.at_lhs else ir_rvalue(ir_op)

    def __bits_property(
        self, node: ast.Attribute, bits_ir: IR.Value | sv.LogicOp
    ) -> Any:
        # sv.LogicOp at LHS is only for error checking.
        if self.at_lhs:
            raise HDLSyntaxError(
                node, f"Cannot assign to property '{node.attr}'."
            )
        assert isinstance(bits_ir, IR.Value)
        if node.attr == "V":
            # Only used for Bits class patterns in Python
            return bits_ir
        if node.attr == "S":
            if not self.__allow_signed():
                raise HDLSyntaxError(
                    node,
                    "Signed value only allowed in comparison "
                    "or shift expressions.",
                )
            return SignedValue(bits_ir)
        if node.attr == "W":
            return self.__width_call(bits_ir)
        if node.attr == "N":
            return self.__negation_call(bits_ir)
        if node.attr in HDL_BITS_REDUCE_PROPERTIES:
            return self.__reduce_property(node.attr, bits_ir)
        assert False, "UNIMPLEMENTED"

    def __allow_signed(self) -> bool:
        if len(self.node_ast_stack) < 2:
            return False
        parent = self.node_ast_stack[-2]
        if isinstance(parent, ast.Attribute):
            if parent.attr == "ext":
                return True
        if isinstance(parent, ast.Compare):
            return True
        if isinstance(parent, ast.BinOp):
            if isinstance(parent.op, (ast.LShift, ast.RShift)):
                return True
        return False

    def __width_call(self, bits_ir: IR.Value) -> IR.Value:
        assert isinstance(bits_ir, IR.Value)
        out_type = ir_integer_type(32)
        ir_op = sv.system(out_type, "bits", [bits_ir])
        assert isinstance(ir_op, IR.Value)
        self.add_forced_i32_expr(ir_op, ForcedI32Type.FUNCTION_RET)
        return ir_rvalue(ir_op)

    def __negation_call(self, bits_ir: IR.Value) -> IR.Value:
        assert isinstance(bits_ir, IR.Value)
        width_ir = self.__width_call(bits_ir)
        high_ir = comb.SubOp.create(width_ir, ir_constant_op(32, 1)).result
        ir_op = self.__access_slice(bits_ir, ir_rvalue(high_ir), 1)
        return ir_rvalue(ir_op)

    def __reduce_property(self, op: str, bits_ir: IR.Value) -> IR.Value:
        assert isinstance(bits_ir, IR.Value)
        ir_func = {
            "AO": ir_reduce_and_op,
            "NZ": ir_reduce_or_op,
            "P": ir_reduce_xor_op,
            "Z": ir_reduce_nor_op,
        }.get(op)
        assert callable(ir_func)

        # Create IR operation
        ir_op = ir_func(bits_ir)
        assert isinstance(ir_op, IR.Value)

        # Register constant expression
        if self.is_constant_expr(bits_ir):
            bits = self.constant_expr_value(bits_ir)
            assert hasattr(bits, op)
            result = getattr(bits, op)
            self.add_constant_expr(ir_op, result)

        return ir_rvalue(ir_op)

    def __bits_method(
        self, node: ast.Attribute, bits_ir: IR.Value | sv.LogicOp | SignedValue
    ) -> BitsMethod:
        if self.at_lhs:
            raise HDLSyntaxError(
                node, f"Cannot assign to result of method {node.attr}()."
            )
        assert isinstance(bits_ir, (IR.Value, SignedValue))
        return BitsMethod(node.attr, bits_ir)

    def __allow_array(self) -> bool:
        if len(self.node_ast_stack) < 2:
            return False
        parent = self.node_ast_stack[-2]
        if isinstance(parent, ast.Subscript):
            if parent.value is self.node_ast_stack[-1]:
                return True
        return False

    def visit_Subscript(self, node: ast.Subscript) -> ConcatLHS | IR.Value:
        # Parse value
        value = self.visit(node.value)

        # Allow `cat(...)[:]` as a workaround for LHS concatenation.
        # Not supported for rep(), which is immutable.
        if isinstance(value, ConcatLHS):
            assert self.at_lhs
            if isinstance(node.slice, ast.Slice):
                slice = node.slice
                if not (slice.step or slice.lower or slice.upper):
                    return value
            raise HDLSyntaxError(
                node.slice,
                "Concatenation only supports complete assignment using [:].",
            )

        # Check value type
        if isinstance(node.slice, (ast.Slice, ast.Tuple)):
            op_type = "part-select"
        else:
            op_type = "bit-select"
        is_array = False
        if ir_is_unpacked_array(value):
            is_array = True
            if isinstance(node.slice, (ast.Slice, ast.Tuple)):
                raise HDLSyntaxError(
                    node.slice,
                    f"Array does not support {op_type} operation.",
                )
        elif isinstance(value, IR.Value) and self.is_forced_i32_expr(value):
            raise HDLSyntaxError(
                node.value,
                f"Integer expressions do not support {op_type} operation.",
            )
        elif not ir_is_indexable(value):
            raise HDLSyntaxError(
                node.value,
                f"Value does not support {op_type} operation.",
            )

        if isinstance(node.slice, ast.Slice):
            assert not is_array
            return self.__visit_slice(node.slice, value)
        elif isinstance(node.slice, ast.Tuple):
            assert not is_array
            return self.__visit_part_select(node.slice, value)
        else:
            if is_array:
                return self.__visit_array_index(node.slice, value)
            else:
                return self.__visit_index(node.slice, value)

    def __visit_slice(self, node: ast.Slice, value: Any) -> IR.Value:
        if node.step is not None:
            raise HDLSyntaxError(
                node, "Part-select does not support slice step."
            )

        # Parse slice
        width = ir_width(value)
        with self.expr_context(at_lhs=False, connecting=False):
            start = self.visit(node.lower) if node.lower else 0
            stop = self.visit(node.upper) if node.upper else width

        # Check lower bound
        if not isinstance(start, int):
            if self.is_constant_expr(start):
                start = int(self.constant_expr_value(start))
                if self.config.comment_bits_folding:
                    self.need_stmt_comment = True
            else:
                raise HDLSyntaxError(
                    node.lower,
                    "Lower bound must be an integer or Bits constant."
                    "\n- Use indexed part-select [start, +|-width] "
                    "for variable bounds.",
                )
        if start < 0 or start >= width:
            raise HDLSyntaxError(
                node.lower,
                f"Lower bound {start} is out of range of [0, {width-1}].",
            )

        # Check upper bound
        if not isinstance(stop, int):
            if self.is_constant_expr(stop):
                stop = int(self.constant_expr_value(stop))
                if self.config.comment_bits_folding:
                    self.need_stmt_comment = True
            else:
                raise HDLSyntaxError(
                    node.upper,
                    "Upper bound must be an integer or Bits constant."
                    "\n- Use indexed part-select [start, +|-width] "
                    "for variable bounds.",
                )
        if stop < 0 or stop > width:
            raise HDLSyntaxError(
                node.upper,
                f"Upper bound {stop} is out of range of [1, {width}].",
            )
        if stop <= start:
            raise HDLSyntaxError(
                node.upper, "Upper bound must be greater than lower bound."
            )

        slice_ir = self.__access_slice(value, start, stop - start)
        return slice_ir

    # Handle Tuple in Subscript for part-select, not for general Tuple node.
    def __visit_part_select(self, node: ast.Tuple, value: Any) -> IR.OpResult:
        # Check selector tuple
        if len(node.elts) not in (2, 3):
            raise HDLSyntaxError(
                node,
                "Indexed part-select requires a tuple of "
                "(start, width[, ASC|DESC]).",
            )
        start_node = node.elts[0]
        width_node = node.elts[1]
        descending = False

        # Parse direction
        if len(node.elts) == 3:
            with self.expr_context(at_lhs=False, connecting=False):
                dir = self.visit(node.elts[2])
                if (
                    isinstance(dir, IR.OpResult)
                    and dir.owner.name == "hw.constant"
                    and ir_width(dir) == 1
                ):
                    assert self.is_constant_expr(dir)
                    bits = self.constant_expr_value(dir)
                    assert isinstance(bits, Bits1)
                    descending = bool(bits == DESC)
                else:
                    raise HDLSyntaxError(
                        node.elts[2],
                        "Part-select direction must be a Bits1 constant "
                        "(ASC|DESC).",
                    )

        # Parse start and width
        with self.expr_context(at_lhs=False, connecting=False):
            start = self.visit(start_node)
            if isinstance(width_node, ast.UnaryOp):
                if isinstance(width_node.op, ast.USub):
                    width = self.visit(width_node)
                    if not isinstance(width, int):
                        if self.is_constant_expr(width):
                            raise HDLSyntaxError(
                                width_node,
                                "For descending part-select, use negative "
                                "integer width or explicit DESC direction.",
                            )
                        # Variable width will be checked later
                else:
                    width = self.visit(width_node)
            else:
                width = self.visit(width_node)

        # Check start index
        value_width = ir_width(value)
        self.__check_range(start_node, "Start index", start, value_width)

        # Check width
        if isinstance(width, int):
            width_value = width
            if width < 0:
                if descending:  # Set by DESC flag
                    raise HDLSyntaxError(
                        width_node,
                        "Descending part-select width must be "
                        "a positive constant expression.",
                    )
                else:
                    descending = True
                    width_value = -width
        elif self.is_constant_expr(width):
            width_value = int(self.constant_expr_value(width))
            if self.config.comment_bits_folding:
                self.need_stmt_comment = True
        else:
            raise HDLSyntaxError(
                width_node, "Part-select width must be a constant expression."
            )
        assert width_value > 0

        # Check part range
        if isinstance(start, int):
            start_value = start
        elif self.is_constant_expr(start):
            start_value = int(self.constant_expr_value(start))
        else:
            assert not self.connecting
            start_value = None  # Variable start
        if start_value is not None:
            if descending:
                # signal[start -: width] = signal[start : start-width+1]
                upper = start_value
                lower = start_value - width_value + 1
                if lower < 0:
                    raise HDLSyntaxError(
                        width_node,
                        f"Part-select [{start_value} -: {width_value}] lower "
                        f"bound {lower} exceeds {value_width}-bit vector.",
                    )
            else:
                # signal[start +: width] = signal[start+width-1 : start]
                lower = start_value
                upper = start_value + width_value - 1
                if upper >= value_width:
                    raise HDLSyntaxError(
                        width_node,
                        f"Part-select [{start_value} +: {width_value}] upper "
                        f"bound {upper} exceeds {value_width}-bit vector.",
                    )

        part_ir = self.__access_part(value, start, width_value, descending)
        return part_ir

    def __check_range(
        self,
        node: ast.AST,
        op_type: str,
        value: Any,
        upper: int,
        lower: int = 0,
    ):
        assert isinstance(upper, int) and isinstance(lower, int)
        assert upper > lower

        # Integer value
        if isinstance(value, int):
            if value < 0 or value >= upper:
                raise HDLSyntaxError(
                    node,
                    f"{op_type} {value} is out of range [0, {upper-1}].",
                )
            return

        # Constant expression value
        if self.is_constant_expr(value):
            # 'upper' may be wider than 'value', so convert 'value' to integers
            value_int = int(self.constant_expr_value(value))
            if value_int < 0 or value_int >= upper:
                raise HDLSyntaxError(
                    node,
                    f"{op_type} {value_int} is out of range [0, {upper-1}].",
                )
            return

        # Variable expression value
        assert isinstance(value, IR.Value)
        if self.is_forced_i32_expr(value):
            # TODO check loop variable range
            return
        if self.connecting:
            assert op_type in ("Index", "Start index")
            raise HDLSyntaxError(
                node,
                f"Connection (@=) requires constant {op_type.lower()}."
                "\n- Use /= in @comb blocks for variable indexing.",
            )
        value_width = ir_width(value)
        assert value_width > 0
        if upper & (upper - 1) == 0:  # power of 2
            threshold = upper
        else:
            threshold = upper * 2
        if (1 << value_width) > threshold:
            raise HDLSyntaxError(
                node,
                f"{op_type} width {value_width} is too wide for "
                f"range [0, {upper-1}]."
                f"\n- {FIX_WIDTH}",
            )

    def __access_slice(self, value: Any, base: Any, width: int) -> IR.Value:
        assert isinstance(width, int) and width > 0

        # LHS
        if self.at_lhs:
            # OpResult for sv.array_index_inout
            assert isinstance(value, (IR.OpResult, sv.LogicOp))
            if self.config.comment_lhs_slice:
                self.need_stmt_comment = True
            if isinstance(base, int):
                base = ir_constant_op(32, base)
            assert isinstance(base, IR.Value)
            return sv.indexed_part_select_inout(value, base, width)

        # RHS
        assert isinstance(value, IR.Value)
        if isinstance(base, int):
            ir_op = ir_extract_op(value, base, width)
            assert isinstance(ir_op, IR.Value)
            return ir_rvalue(ir_op)
        else:
            assert isinstance(base, IR.Value)
            return sv.indexed_part_select(value, base, width)

    def __access_part(
        self, value: Any, base: Any, width: int, descending: bool
    ) -> IR.OpResult:
        if not isinstance(width, int):
            assert self.is_constant_expr(width)
            width = int(self.constant_expr_value(width))
        assert isinstance(width, int) and width > 0
        if isinstance(base, int):
            base = ir_constant_op(32, base)
        assert isinstance(base, IR.Value)

        # LHS
        if self.at_lhs:
            # OpResult for sv.array_index_inout
            assert isinstance(value, (IR.OpResult, sv.LogicOp))
            if self.config.comment_lhs_slice:
                self.need_stmt_comment = True
            return sv.indexed_part_select_inout(
                value, base, width, decrement=descending
            )

        # RHS
        assert isinstance(value, IR.Value)
        return sv.indexed_part_select(value, base, width, decrement=descending)

    def __visit_array_index(self, node: ast.AST, value: Any) -> IR.Value:
        # Parse index
        with self.expr_context(at_lhs=False, connecting=False):
            index = self.visit(node)

        # Check index
        size = ir_array_size(value)
        self.__check_range(node, "Index", index, size)
        if isinstance(index, int):
            index = ir_constant_op(32, index)
        assert isinstance(index, IR.Value)

        # Create IR operation
        assert isinstance(value, sv.LogicOp)
        element_ir = sv.array_index_inout(value, index)
        assert isinstance(element_ir, IR.Value)
        if self.at_lhs:
            return element_ir
        result = sv.read_inout(element_ir)
        assert isinstance(result, IR.Value)
        return result

    def __visit_index(self, node: ast.AST, value: Any) -> IR.Value:
        width = ir_width(value)
        with self.expr_context(at_lhs=False, connecting=False):
            index = self.visit(node)
        self.__check_range(node, "Index", index, width)
        return self.__access_slice(value, index, 1)

    # Expression: operators
    #
    _ast_to_ir_ops = {
        # Unary operators
        ast.Invert: ir_invert_op,
        ast.Not: ir_bool_not_op,
        ast.UAdd: ir_pass_op,
        ast.USub: ir_negate_op,
        # Binary operators
        ast.BitAnd: comb.AndOp,
        ast.BitOr: comb.OrOp,
        ast.BitXor: comb.XorOp,
        ast.Add: comb.AddOp,
        ast.Sub: comb.SubOp,
        ast.Mult: comb.MulOp,
        # Boolean operators
        ast.And: ir_bool_and_op,
        ast.Or: ir_bool_or_op,
        # Comparison operators
        ast.Eq: comb.EqOp,
        ast.NotEq: comb.NeOp,
        ast.Lt: comb.LtUOp,
        ast.LtE: comb.LeUOp,
        ast.Gt: comb.GtUOp,
        ast.GtE: comb.GeUOp,
    }

    def visit_UnaryOp(self, node: ast.UnaryOp) -> int | IR.Value:
        if self.at_lhs:
            raise HDLSyntaxError(node, "Cannot assign to a unary expression.")

        # Skip unary '+/-' operator for integers
        if (
            isinstance(node.op, (ast.UAdd, ast.USub))
            and isinstance(node.operand, ast.Constant)
            and isinstance(node.operand.value, int)
        ):
            value = node.operand.value
            if isinstance(node.op, ast.USub):
                value = -value
            return value

        # Get operator
        assert type(node.op) in self._ast_to_ir_ops
        operator = self._ast_to_ir_ops[type(node.op)]
        assert type(operator) is FunctionType

        # Parse operand
        operand = self.visit(node.operand)
        if isinstance(operand, int):
            # Fold integer expression
            eval = ast_eval_func(node.op)
            return eval(operand)

        # Create IR operation
        ir_op = operator(operand)
        if isinstance(ir_op, ir_support.OpOperand):
            ir_op = ir_op.value
        assert isinstance(ir_op, IR.Value)

        # Register constant expression
        constant_expr = self.is_constant_expr(operand)
        if constant_expr:
            bits = self.constant_expr_value(operand)
            eval = ast_eval_func(node.op)
            result = eval(bits)
            self.add_constant_expr(ir_op, result)

        # Register forced i32 expression
        if not isinstance(node.op, ast.Not):
            if self.is_forced_i32_expr(operand):
                if constant_expr:
                    i32_expr_type = ForcedI32Type.CONSTANT_EXPR
                else:
                    i32_expr_type = ForcedI32Type.VARIABLE_EXPR
                self.add_forced_i32_expr(ir_op, i32_expr_type)

        return ir_rvalue(ir_op)

    def visit_BinOp(self, node: ast.BinOp) -> int | IR.Value:
        if self.at_lhs:
            raise HDLSyntaxError(node, "Cannot assign to a binary expression.")

        # Replication (**) operator
        if isinstance(node.op, ast.Pow):
            return self.__pow_op(node)

        # Shift operators
        if isinstance(node.op, (ast.LShift, ast.RShift)):
            return self.__shift_op(node)

        # Check operator
        if type(node.op) not in self._ast_to_ir_ops:
            raise HDLSyntaxError(
                node, f"Operator '{ast_op_name(node.op)}' is not supported."
            )
        operator = self._ast_to_ir_ops[type(node.op)]
        assert type(operator) is not FunctionType

        # Parse operands
        # Width inference rules:
        # 1. Use left operand width if available.
        # 2. Otherwise, use right operand width.
        # 3. If both operands are integers, fold integer expression.
        left = self.visit(node.left)
        right = self.visit(node.right)
        forced_i32_expr = False
        if isinstance(left, int) and isinstance(right, int):
            # Fold integer expression
            eval = ast_eval_func(node.op)
            return eval(left, right)
        if isinstance(left, int):
            assert not isinstance(right, int)
            right_ir = right
            right_width = ir_width(right_ir)
            left_ir = self.__int_constant(node.left, right_width, left)
            left_width = right_width
            if self.is_forced_i32_expr(right_ir):
                forced_i32_expr = True
        elif isinstance(right, int):
            assert not isinstance(left, int)
            left_ir = left
            left_width = ir_width(left_ir)
            right_ir = self.__int_constant(node.right, left_width, right)
            right_width = left_width
            if self.is_forced_i32_expr(left_ir):
                forced_i32_expr = True
        else:
            left_ir = left
            left_width = ir_width(left_ir)
            right_ir = right
            right_width = ir_width(right_ir)

            # Truncate forced i32 operand
            forced_i32_left = self.is_forced_i32_expr(left_ir)
            forced_i32_right = self.is_forced_i32_expr(right_ir)
            if forced_i32_left and forced_i32_right:
                forced_i32_expr = True
            elif forced_i32_left:
                assert left_width == 32
                if right_width < 32:
                    left_ir = ir_extract_op(left_ir, 0, right_width)
                    left_width = right_width
                forced_i32_expr = False
            elif forced_i32_right:
                assert right_width == 32
                if left_width < 32:
                    right_ir = ir_extract_op(right_ir, 0, left_width)
                    right_width = left_width
                forced_i32_expr = False
        assert isinstance(left_ir, IR.Value)
        assert isinstance(right_ir, IR.Value)

        # Check operand widths
        if left_width != right_width:
            op = ast_op_name(node.op)
            raise HDLSyntaxError(
                node,
                f"Width mismatch: Bits{left_width} {op} Bits{right_width}"
                f"\n- {FIX_WIDTH}",
            )

        # Create IR operation
        ir_op = operator.create(left_ir, right_ir).result
        if isinstance(ir_op, ir_support.OpOperand):
            ir_op = ir_op.value
        assert isinstance(ir_op, IR.Value)

        # Register constant expression
        constant_left = self.is_constant_expr(left_ir)
        constant_right = self.is_constant_expr(right_ir)
        constant_expr = constant_left and constant_right
        if constant_expr:
            left_bits = self.constant_expr_value(left_ir)
            right_bits = self.constant_expr_value(right_ir)
            eval = ast_eval_func(node.op)
            result = eval(left_bits, right_bits)
            self.add_constant_expr(ir_op, result)

        # Register forced i32 expression
        if forced_i32_expr:
            if constant_expr:
                i32_expr_type = ForcedI32Type.CONSTANT_EXPR
            else:
                i32_expr_type = ForcedI32Type.VARIABLE_EXPR
            self.add_forced_i32_expr(ir_op, i32_expr_type)

        return ir_rvalue(ir_op)

    def __pow_op(self, node: ast.BinOp) -> IR.Value:
        assert not self.at_lhs

        # Parse operand
        operand = self.visit(node.left)
        if isinstance(operand, int):
            raise HDLSyntaxError(
                node.left,
                "Cannot replicate an integer constant.",
            )
        assert isinstance(operand, IR.Value)
        if self.is_forced_i32_expr(operand):
            raise HDLSyntaxError(
                node.left,
                "Cannot replicate an integer expression.",
            )

        # Parse count
        count = self.visit(node.right)
        if not isinstance(count, int):
            raise HDLSyntaxError(
                node.right,
                "Replication count must be an integer constant.",
            )
        if count < 0:
            raise HDLSyntaxError(
                node.right, "Replication count must be non-negative."
            )

        # Create IR operation
        ir_op = ir_replicate_op(count, [operand])
        assert isinstance(ir_op, IR.Value)

        # Register constant expression
        if self.is_constant_expr(operand):
            bits = self.constant_expr_value(operand)
            result = rep(count, bits).data_bits
            self.add_constant_expr(ir_op, result)
        return ir_rvalue(ir_op)

    def __shift_op(self, node: ast.BinOp) -> int | IR.Value:
        assert not self.at_lhs

        # Operator
        if isinstance(node.op, ast.LShift):
            operator = comb.ShlOp
        elif isinstance(node.op, ast.RShift):
            operator = comb.ShrUOp

        # Parse value and shift amount
        value = self.visit(node.left)
        shamt = self.visit(node.right)
        if isinstance(value, int):
            if isinstance(shamt, int):
                # Fold integer expression
                eval = ast_eval_func(node.op)
                return eval(value, shamt)
            raise HDLSyntaxError(
                node.right,
                "Integer shift supports only integer constant "
                "as shift amount.",
            )
        if isinstance(value, SignedValue):
            if not isinstance(node.op, ast.RShift):
                raise HDLSyntaxError(
                    node.left,
                    "Signed value supports only right shift operation.",
                )
            operator = comb.ShrSOp
            value_ir = value.bits_ir
        else:
            value_ir = value
        assert isinstance(value_ir, IR.Value)
        value_width = ir_width(value_ir)

        # Check shift amount
        self.__check_range(node.right, "Shift amount", shamt, value_width)
        if isinstance(shamt, int):
            shamt_ir = self.__int_constant(node.right, 32, shamt)
        else:
            shamt_ir = shamt
        assert isinstance(shamt_ir, IR.Value)

        # Create IR operation
        ir_op = operator.create(value_ir, shamt_ir).result.value
        assert isinstance(ir_op, IR.Value)

        # Register constant expression
        constant_value = self.is_constant_expr(value_ir)
        constant_shamt = self.is_constant_expr(shamt_ir)
        constant_expr = constant_value and constant_shamt
        if constant_expr:
            value_bits = self.constant_expr_value(value_ir)
            shamt_bits = self.constant_expr_value(shamt_ir)
            eval = ast_eval_func(node.op)
            result = eval(value_bits, shamt_bits)
            self.add_constant_expr(ir_op, result)

        # Register forced i32 expression
        if self.is_forced_i32_expr(value_ir):
            if constant_expr:
                i32_expr_type = ForcedI32Type.CONSTANT_EXPR
            else:
                i32_expr_type = ForcedI32Type.VARIABLE_EXPR
            self.add_forced_i32_expr(ir_op, i32_expr_type)

        return ir_rvalue(ir_op)

    def visit_BoolOp(self, node: ast.BoolOp) -> int | IR.Value:
        if self.at_lhs:
            raise HDLSyntaxError(
                node, "Cannot assign to a boolean expression."
            )

        # Get operator
        assert type(node.op) in self._ast_to_ir_ops
        operator = self._ast_to_ir_ops[type(node.op)]
        assert type(operator) is FunctionType

        # Parse all operands
        operands = [self.visit(v) for v in node.values]
        if all([isinstance(v, int) for v in operands]):
            # Fold integer expression
            eval = ast_eval_func(node.op)
            return eval(operands)
        value_irs = []
        for i, operand in enumerate(operands):
            if isinstance(operand, int):
                if operand == 0 or operand == 1:
                    value_ir = self.__int_constant(node.values[i], 1, operand)
                else:
                    value_ir = self.__int_constant(node.values[i], 32, operand)
            else:
                value_ir = operand
            assert isinstance(value_ir, IR.Value)
            value_irs.append(value_ir)

        # Check if Bool() conversion is needed
        # Ensure Python and/or always produce 1-bit value (0/1/Bits1).
        all_b1 = all([ir_width(v) == 1 for v in value_irs])
        if not all_b1 and not self.__in_bool_context():
            op_name = "and" if isinstance(node.op, ast.And) else "or"
            raise HDLSyntaxError(
                node,
                f"Boolean '{op_name}' requires Bool() conversion."
                f"\n- {FIX_BOOL}",
            )

        # Create IR operation
        ir_op = operator(*value_irs)
        assert isinstance(ir_op, IR.Value)

        # Register constant expression
        all_constant = all([self.is_constant_expr(v) for v in value_irs])
        if all_constant:
            bits_list = [self.constant_expr_value(v) for v in value_irs]
            eval = ast_eval_func(node.op)
            result = eval(bits_list)
            self.add_constant_expr(ir_op, result)

        return ir_rvalue(ir_op)

    def __in_bool_context(self) -> bool:
        if len(self.node_ast_stack) < 2:
            return False
        parent = self.node_ast_stack[-2]
        # Bool()
        if isinstance(parent, ast.Call) and hasattr(parent.func, "id"):
            return parent.func.id == "Bool"
        # not
        if isinstance(parent, ast.UnaryOp):
            return isinstance(parent.op, ast.Not)
        # and/or
        return isinstance(parent, ast.BoolOp)

    def visit_IfExp(self, node: ast.IfExp) -> int | IR.Value:
        if self.at_lhs:
            raise HDLSyntaxError(
                node, "Cannot assign to a conditional expression."
            )

        # Parse condition
        condition = self.visit(node.test)
        if isinstance(condition, int):
            condition_ir = self.__int_constant(node.test, 1, bool(condition))
        else:
            cond_bool = ir_bool_bit_op(condition)
            condition_ir = ir_rvalue(cond_bool)
        assert isinstance(condition_ir, IR.Value)

        # Parse values
        then_value = self.visit(node.body)
        else_value = self.visit(node.orelse)
        forced_i32_expr = False
        if isinstance(then_value, int) and isinstance(else_value, int):
            # Fold integer expression
            if isinstance(condition, int):
                return then_value if condition else else_value
            raise HDLSyntaxError(
                node,
                "Cannot infer width for integer constants "
                "in a conditional expression.",
            )
        if isinstance(then_value, int):
            assert not isinstance(else_value, int)
            else_ir = else_value
            else_width = ir_width(else_ir)
            then_ir = self.__int_constant(node.body, else_width, then_value)
            then_width = else_width
            if self.is_forced_i32_expr(else_ir):
                forced_i32_expr = True
        elif isinstance(else_value, int):
            assert not isinstance(then_value, int)
            then_ir = then_value
            then_width = ir_width(then_ir)
            else_ir = self.__int_constant(node.orelse, then_width, else_value)
            else_width = then_width
            if self.is_forced_i32_expr(then_ir):
                forced_i32_expr = True
        else:
            then_ir = then_value
            then_width = ir_width(then_ir)
            else_ir = else_value
            else_width = ir_width(else_ir)

            # Truncate forced i32 operand
            forced_i32_then = self.is_forced_i32_expr(then_ir)
            forced_i32_else = self.is_forced_i32_expr(else_ir)
            if forced_i32_then and forced_i32_else:
                forced_i32_expr = True
            elif forced_i32_then:
                assert then_width == 32
                if else_width < 32:
                    then_ir = ir_extract_op(then_ir, 0, else_width)
                    then_width = else_width
                forced_i32_expr = False
            elif forced_i32_else:
                assert else_width == 32
                if then_width < 32:
                    else_ir = ir_extract_op(else_ir, 0, then_width)
                    else_width = then_width
                forced_i32_expr = False
        assert isinstance(then_ir, IR.Value)
        assert isinstance(else_ir, IR.Value)

        # Check value widths
        if then_width != else_width:
            raise HDLSyntaxError(
                node,
                f"Width mismatch: <cond> ? Bits{then_width} : Bits{else_width}"
                f"\n- {FIX_WIDTH}",
            )

        # Create IR operation
        ir_op = comb.MuxOp.create(condition_ir, then_ir, else_ir).result
        assert isinstance(ir_op, IR.Value)

        # Register constant expression
        constant_then = self.is_constant_expr(then_ir)
        constant_else = self.is_constant_expr(else_ir)
        constant_expr = False
        if (
            self.is_constant_expr(condition_ir)
            and constant_then
            and constant_else
        ):
            constant_expr = True
            cond_bits = self.constant_expr_value(condition_ir)
            then_bits = self.constant_expr_value(then_ir)
            else_bits = self.constant_expr_value(else_ir)
            result = then_bits if bool(cond_bits) else else_bits
            self.add_constant_expr(ir_op, result)

        # Register forced i32 expression
        if forced_i32_expr:
            if constant_expr:
                i32_expr_type = ForcedI32Type.CONSTANT_EXPR
            else:
                i32_expr_type = ForcedI32Type.VARIABLE_EXPR
            self.add_forced_i32_expr(ir_op, i32_expr_type)

        return ir_rvalue(ir_op)

    _signed_ir_ops = {
        comb.EqOp: comb.EqOp,
        comb.NeOp: comb.NeOp,
        comb.LtUOp: comb.LtSOp,
        comb.LeUOp: comb.LeSOp,
        comb.GtUOp: comb.GtSOp,
        comb.GeUOp: comb.GeSOp,
    }

    def visit_Compare(self, node: ast.Compare) -> int | IR.Value:
        if self.at_lhs:
            raise HDLSyntaxError(
                node, "Cannot assign to a comparison expression."
            )

        if len(node.ops) != 1 or len(node.comparators) != 1:
            raise HDLSyntaxError(
                node, "Only single comparison (a OP b) is supported."
            )

        # Check operator
        cmp_op = node.ops[0]
        if type(cmp_op) not in self._ast_to_ir_ops:
            raise HDLSyntaxError(
                node, f"Operator '{ast_op_name(cmp_op)}' is not supported."
            )
        operator = self._ast_to_ir_ops[type(cmp_op)]
        assert type(operator) is not FunctionType

        # Parse operands
        # Infer operand width as in BinOp.
        left = self.visit(node.left)
        right_node = node.comparators[0]
        right = self.visit(right_node)
        if isinstance(left, int) and isinstance(right, int):
            # Fold integer expression
            eval = ast_eval_func(cmp_op)
            return eval(left, right)
        if isinstance(left, SignedValue):
            if not isinstance(right, (int, SignedValue)):
                raise HDLSyntaxError(
                    right_node,
                    "Signed comparison requires both operands to be signed.",
                )
            operator = self._signed_ir_ops[operator]
            left = left.bits_ir
            if isinstance(right, SignedValue):
                right = right.bits_ir
        elif isinstance(right, SignedValue):
            if not isinstance(left, int):
                raise HDLSyntaxError(
                    node.left,
                    "Signed comparison requires both operands to be signed.",
                )
            operator = self._signed_ir_ops[operator]
            right = right.bits_ir
        if isinstance(left, int):
            assert not isinstance(right, int)
            right_ir = right
            right_width = ir_width(right_ir)
            left_ir = self.__int_constant(node.left, right_width, left)
            left_width = right_width
        elif isinstance(right, int):
            assert not isinstance(left, int)
            left_ir = left
            left_width = ir_width(left_ir)
            right_ir = self.__int_constant(right_node, left_width, right)
            right_width = left_width
        else:
            left_ir = left
            left_width = ir_width(left_ir)
            right_ir = right
            right_width = ir_width(right_ir)

            # Truncate forced i32 operand
            forced_i32_left = self.is_forced_i32_expr(left_ir)
            forced_i32_right = self.is_forced_i32_expr(right_ir)
            if forced_i32_left and forced_i32_right:
                assert left_width == 32 and right_width == 32
            elif forced_i32_left:
                assert left_width == 32
                if right_width < 32:
                    left_ir = ir_extract_op(left_ir, 0, right_width)
                    left_width = right_width
            elif forced_i32_right:
                assert right_width == 32
                if left_width < 32:
                    right_ir = ir_extract_op(right_ir, 0, left_width)
                    right_width = left_width
        assert isinstance(left_ir, IR.Value)
        assert isinstance(right_ir, IR.Value)

        # Check operand widths
        if left_width != right_width:
            op = ast_op_name(cmp_op)
            raise HDLSyntaxError(
                node,
                f"Width mismatch: Bits{left_width} {op} Bits{right_width}"
                f"\n- {FIX_WIDTH}",
            )

        # Create IR operation
        ir_op = operator.create(left_ir, right_ir).result.value
        assert isinstance(ir_op, IR.Value)

        # Register constant expression
        constant_left = self.is_constant_expr(left_ir)
        constant_right = self.is_constant_expr(right_ir)
        if constant_left and constant_right:
            left_bits = self.constant_expr_value(left_ir)
            right_bits = self.constant_expr_value(right_ir)
            eval = ast_eval_func(cmp_op)
            result = eval(left_bits, right_bits)
            self.add_constant_expr(ir_op, result)

        return ir_rvalue(ir_op)

    # Expression: function calls
    # Bits constants, built-in functions, and user-defined functions
    #
    def visit_Call(self, node: ast.Call) -> ConcatLHS | IR.Value:
        obj = self.visit(node.func)
        assert obj

        # Bits subclass
        if isinstance(obj, type) and issubclass(obj, Bits):
            return self.__bits_constructor(node.func, obj, node.args)

        # Bits method
        if isinstance(obj, BitsMethod):
            match obj.method_name:
                case "ext":
                    return self.__bits_ext(node, obj.bits_ir)
                case _:
                    assert False, "UNIMPLEMENTED"

        # Now, it's a constructor or function
        assert callable(obj)
        func = obj
        assert hasattr(node.func, "id") and func.__name__ == node.func.id
        if func is Bool:
            return self.__bool_bit_call(node)
        if func is cat:
            return self.__cat_call(node)
        if func is rep:
            return self.__rep_call(node)
        if func is range:
            return self.__range_call(node)
        assert False, "UNIMPLEMENTED"

    def __bits_constructor(
        self, func: ast.AST, bits_type: type[Bits], args: Sequence[Any]
    ) -> IR.Value:
        if self.at_lhs:
            raise HDLSyntaxError(func, "Cannot assign to a Bits constant.")

        # Check constructor name and argument count
        assert hasattr(func, "id")
        func_name = func.id
        if not func_name.startswith("b") or not func_name[1:].isdigit():
            raise HDLSyntaxError(
                func,
                "Use b<N>() for Bits constants, such as b2(0b01) or b8(0xFF).",
            )
        if (n_args := len(args)) != 1:
            raise HDLSyntaxError(
                func,
                f"{func_name}() requires exactly one argument, got {n_args}.",
            )

        # Parse constant value
        value = self.visit(args[0])
        if not isinstance(value, int):
            raise HDLSyntaxError(
                args[0],
                f"{func_name}() argument must be an integer constant.",
            )

        # Check value with Bits constructor
        try:
            bits = bits_type(value)
        except Exception as e:
            raise HDLSyntaxError(args[0], f"{e}")

        # Create IR operation
        ir_op = ir_constant_op(bits.nbits, value)
        assert isinstance(ir_op, IR.Value)
        self.add_constant_expr(ir_op, bits)
        return ir_rvalue(ir_op)

    def __bits_ext(
        self, node: ast.Call, bits_ir: SignedValue | IR.Value
    ) -> IR.Value:
        assert not self.at_lhs

        # Check argument count
        if (n_args := len(node.args)) != 1:
            raise HDLSyntaxError(
                node,
                f"ext() requires exactly one argument, got {n_args}.",
            )

        # Signed or unsigned extension
        signed = False
        if isinstance(bits_ir, SignedValue):
            signed = True
            bits_ir = bits_ir.bits_ir
        assert isinstance(bits_ir, IR.Value)
        bits_width = ir_width(bits_ir)
        assert isinstance(bits_width, int) and bits_width > 0

        # Parse width argument
        ext_width = self.visit(node.args[0])
        if not isinstance(ext_width, int):
            raise HDLSyntaxError(
                node.args[0],
                "ext() argument must be an integer constant.",
            )
        if ext_width <= bits_width:
            raise HDLSyntaxError(
                node.args[0],
                "ext() argument must be greater than "
                f"the current width {bits_width}.",
            )

        # Create IR operation
        if signed:
            msb_ir = ir_rvalue(ir_extract_op(bits_ir, bits_width - 1, 1))
            padding_ir = ir_replicate_op(ext_width - bits_width, [msb_ir])
        else:
            padding_ir = ir_constant_op(ext_width - bits_width, 0)
        concat_ir = ir_concat_op([padding_ir, bits_ir])
        if self.is_constant_expr(bits_ir):
            bits = self.constant_expr_value(bits_ir)
            if signed:
                bits = bits.S
            self.add_constant_expr(concat_ir, bits.ext(ext_width))
        return ir_rvalue(concat_ir)

    def __bool_bit_call(self, node: ast.Call) -> int | IR.Value:
        if self.at_lhs:
            raise HDLSyntaxError(node, "Cannot assign to a Bool() expression.")

        # Check number of arguments
        n_args = len(node.args)
        if n_args != 1:
            raise HDLSyntaxError(
                node,
                f"Bool() requires exactly one argument, got {n_args}.",
            )

        # Parse operand
        operand = self.visit(node.args[0])
        if isinstance(operand, int):
            # Fold int expr. Bool() returns a Bits1.
            return self.__int_constant(node.args[0], 1, bool(operand))

        # Create IR operation
        ir_op = ir_bool_bit_op(operand)
        assert isinstance(ir_op, IR.Value)
        if self.is_constant_expr(operand):
            bits = self.constant_expr_value(operand)
            self.add_constant_expr(ir_op, Bool(bits))
        return ir_rvalue(ir_op)

    def __cat_call(self, node: ast.Call) -> ConcatLHS | IR.Value:
        # Check number of arguments
        n_args = len(node.args)
        if n_args < 2:
            raise HDLSyntaxError(
                node,
                f"cat() requires at least two arguments, got {n_args}.",
            )

        # Parse all operands
        operands = []
        all_constant = True
        for arg in node.args:
            operand = self.visit(arg)
            if isinstance(operand, int):
                raise HDLSyntaxError(
                    arg,
                    "Cannot concatenate an integer constant.",
                )
            if isinstance(operand, IR.Value):
                if self.is_forced_i32_expr(operand):
                    raise HDLSyntaxError(
                        arg,
                        "Cannot concatenate an integer expression.",
                    )
            operands.append(operand)
            if isinstance(operand, ConcatLHS):
                all_constant = False
            elif not self.is_constant_expr(operand):
                all_constant = False

        # Create IR operation
        if self.at_lhs:
            return ConcatLHS(operands)
        ir_op = ir_concat_op(operands)
        assert isinstance(ir_op, IR.Value)

        # Register constant expression
        if all_constant:
            bits_list = [self.constant_expr_value(x) for x in operands]
            result = cat(*bits_list).data_bits
            self.add_constant_expr(ir_op, result)

        return ir_rvalue(ir_op)

    def __rep_call(self, node: ast.Call) -> IR.Value:
        if self.at_lhs:
            raise HDLSyntaxError(node, "Cannot assign to a rep() expression.")

        # Check number of arguments
        n_args = len(node.args)
        if n_args < 2:
            raise HDLSyntaxError(
                node,
                f"rep() requires at least two arguments, got {n_args}.",
            )

        # Check argument 'count'
        count = self.visit(node.args[0])
        if not isinstance(count, int):
            raise HDLSyntaxError(
                node.args[0],
                "rep() count argument must be an integer constant.",
            )
        if count < 0:
            raise HDLSyntaxError(
                node.args[0],
                "rep() count argument must be non-negative.",
            )

        # Parse all operands
        operands = []
        for arg in node.args[1:]:
            operand = self.visit(arg)
            assert not isinstance(operand, ConcatLHS)
            if isinstance(operand, int):
                raise HDLSyntaxError(
                    arg,
                    "Cannot replicate an integer constant.",
                )
            assert isinstance(operand, IR.Value)
            if self.is_forced_i32_expr(operand):
                raise HDLSyntaxError(
                    arg,
                    "Cannot replicate an integer expression.",
                )
            operands.append(operand)

        # Create IR operation
        ir_op = ir_replicate_op(count, operands)
        assert isinstance(ir_op, IR.Value)

        # Register constant expression
        all_constant = all([self.is_constant_expr(x) for x in operands])
        if all_constant:
            bits_list = [self.constant_expr_value(x) for x in operands]
            result = rep(count, *bits_list).data_bits
            self.add_constant_expr(ir_op, result)

        return ir_rvalue(ir_op)

    def __range_call(self, node: ast.Call) -> LoopRange:
        if not self.__in_for_iter():
            raise HDLSyntaxError(
                node, "range() can only be used in a for loop."
            )

        # Parse arguments
        n_args = len(node.args)
        start = 0
        step = 1
        match n_args:
            case 1:
                stop = self.visit(node.args[0])
            case 2:
                start = self.visit(node.args[0])
                stop = self.visit(node.args[1])
            case 3:
                start = self.visit(node.args[0])
                stop = self.visit(node.args[1])
                step = self.visit(node.args[2])
            case _:
                raise HDLSyntaxError(
                    node,
                    f"range() requires 1 to 3 arguments, got {n_args}.",
                )

        # Check start argument
        if not isinstance(start, int):
            raise HDLSyntaxError(
                node.args[0],
                "range() lower bound must be an integer constant.",
            )
        if n_args >= 2 and start < 0:
            raise HDLSyntaxError(
                node.args[0],
                "range() lower bound must be non-negative.",
            )

        # Check stop argument
        if not isinstance(stop, int):
            raise HDLSyntaxError(
                node.args[1] if n_args >= 2 else node.args[0],
                "range() upper bound must be an integer constant.",
            )
        if n_args == 1 and stop <= 0:
            raise HDLSyntaxError(
                node.args[0], "range() count must be positive."
            )
        elif n_args >= 2 and stop <= start:
            raise HDLSyntaxError(
                node.args[1],
                "range() upper bound must be greater than lower bound.",
            )

        # Check step argument
        if not isinstance(step, int):
            raise HDLSyntaxError(
                node.args[2],
                "range() step must be an integer constant.",
            )
        if n_args >= 3 and step <= 0:
            raise HDLSyntaxError(
                node.args[2], "range() step must be positive."
            )

        return LoopRange(start, stop, step)

    def __in_for_iter(self) -> bool:
        if len(self.node_ast_stack) < 2:
            return False
        parent = self.node_ast_stack[-2]
        leaf = self.node_ast_stack[-1]
        return isinstance(parent, ast.For) and leaf is parent.iter
