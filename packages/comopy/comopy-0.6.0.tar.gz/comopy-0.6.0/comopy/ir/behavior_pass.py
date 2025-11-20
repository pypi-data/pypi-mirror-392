# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Transform behavioral blocks into the CIRCUIT IR.
"""

import circt.ir as IR
from circt.dialects import hw, sv

import comopy.hdl as HDL
from comopy.utils import BasePass, FuncCodeInfo

from .circt_ir import *
from .function_parser import FunctionParser
from .parser_defs import *


class BehaviorPass(BasePass):
    """A pass to transform behavioral blocks into the CIRCUIT IR."""

    def __call__(self, tree: HDL.CircuitNode) -> HDL.CircuitNode:
        assert isinstance(tree, HDL.CircuitNode)
        assert tree.is_root and tree.is_assembled_module
        ir_top = tree.ir_top
        assert isinstance(ir_top, IR.Module)

        template_modules: dict[str, HDL.CircuitNode] = {}

        context = ir_top.context
        with context, IR.Location.unknown():
            for node in tree:
                if not node.is_assembled_module:
                    continue  # Not a module node

                module_obj = node.obj
                assert isinstance(module_obj, HDL.RawModule)
                module_cls = module_obj.__class__.__qualname__
                if module_obj.ir is None:
                    # Already parsed in the first instance (template)
                    assert module_cls in template_modules
                    template = template_modules[module_cls]
                    self.__copy_behavior_info(template, node)
                    continue

                assert module_cls not in template_modules
                template_modules[module_cls] = node

                module_ir = module_obj.ir
                assert isinstance(module_ir, hw.HWModuleOp)
                entry_block = module_ir.regions[0].blocks[0]

                # Create insertion point for local parameters
                localparam_marker_op = None
                for op in entry_block.operations:
                    if ir_match_sv_verbatim(op, COMMENT_LOCALPARAMS_END):
                        localparam_marker_op = op
                        break
                assert isinstance(localparam_marker_op, sv.VerbatimOp)
                localparam_ip = IR.InsertionPoint(localparam_marker_op)

                # Locate the block end to determine insertion point
                end_marker_op = None
                for op in reversed(entry_block.operations):
                    if ir_is_sv_newline(op):
                        end_marker_op = op
                        break
                assert isinstance(end_marker_op, sv.VerbatimOp)
                insertion_point = IR.InsertionPoint(end_marker_op)

                # Parse behavioral blocks
                parser = FunctionParser(node, localparam_ip)
                with insertion_point:
                    for inst in node.inst_blocks:
                        self.__parse_submodule(parser, node, inst)
                    for conn in node.conn_blocks:
                        self.__parse_connection(parser, node, conn)
                    for comb in node.comb_blocks:
                        self.__parse_procedural(parser, node, comb)
                    for seq in node.seq_blocks:
                        self.__parse_procedural(parser, node, seq)

                    # Remove redundant newlines at the end
                    last_op = ir_last_op()
                    if ir_is_sv_newline(last_op):
                        last_op.erase()

                # Verify module driving
                parser.verify_module_driving()

                # Cleanup placeholder comments for local parameters
                self.__cleanup_localparam_placeholders(entry_block)

        return tree

    def __copy_behavior_info(self, src: HDL.CircuitNode, dst: HDL.CircuitNode):
        # Module instances
        assert len(src.inst_blocks) == len(dst.inst_blocks)
        for src_block, dst_block in zip(src.inst_blocks, dst.inst_blocks):
            assert isinstance(src_block, HDL.Behavior)
            assert isinstance(dst_block, HDL.Behavior)
            assert not src_block.edges.pos_edges
            assert not src_block.edges.neg_edges
            dst_block.deps.reads = set(src_block.deps.reads)
            dst_block.deps.writes = set(src_block.deps.writes)

        # Connections
        assert len(src.conn_blocks) == len(dst.conn_blocks)
        for src_block, dst_block in zip(src.conn_blocks, dst.conn_blocks):
            assert isinstance(src_block, HDL.Behavior)
            assert isinstance(dst_block, HDL.Behavior)
            assert not src_block.edges.pos_edges
            assert not src_block.edges.neg_edges
            dst_block.deps.reads = set(src_block.deps.reads)
            dst_block.deps.writes = set(src_block.deps.writes)
            assert isinstance(dst_block.conn, HDL.Connection)
            if dst_block.conn.internal:
                assert len(dst_block.deps.writes) == 1
                target_id = list(dst_block.deps.writes)[0]
                dst_block.set_conn_target_id(target_id)

        # Combinational blocks
        assert len(src.comb_blocks) == len(dst.comb_blocks)
        for src_block, dst_block in zip(src.comb_blocks, dst.comb_blocks):
            assert isinstance(src_block, HDL.Behavior)
            assert isinstance(dst_block, HDL.Behavior)
            assert not src_block.edges.pos_edges
            assert not src_block.edges.neg_edges
            dst_block.deps.reads = set(src_block.deps.reads)
            dst_block.deps.writes = set(src_block.deps.writes)

        # Sequential blocks
        assert len(src.seq_blocks) == len(dst.seq_blocks)
        for src_block, dst_block in zip(src.seq_blocks, dst.seq_blocks):
            assert isinstance(src_block, HDL.Behavior)
            assert isinstance(dst_block, HDL.Behavior)
            dst_block.edges.pos_edges = list(src_block.edges.pos_edges)
            dst_block.edges.neg_edges = list(src_block.edges.neg_edges)
            dst_block.deps.reads = set(src_block.deps.reads)
            dst_block.deps.writes = set(src_block.deps.writes)

    def __parse_submodule(
        self,
        parser: FunctionParser,
        module_node: HDL.CircuitNode,
        inst_block: HDL.Behavior,
    ):
        assert isinstance(inst_block, HDL.Behavior)
        assert isinstance(inst_block.inst, HDL.ModuleInst)

        submodule_node = inst_block.inst.module_obj.node
        assert isinstance(submodule_node, HDL.CircuitNode)
        assert submodule_node.owner is module_node
        assert submodule_node.code_pos is not None
        parser.behavior(inst_block, submodule_node.code_pos.func_info)

    def __parse_connection(
        self,
        parser: FunctionParser,
        module_node: HDL.CircuitNode,
        conn_block: HDL.Behavior,
    ):
        assert isinstance(conn_block, HDL.Behavior)
        assert isinstance(conn_block.conn, HDL.Connection)

        conn = conn_block.conn
        builder_name = conn.builder_name
        builder_info = module_node.get_func_info_by_name(builder_name)
        assert isinstance(builder_info, FuncCodeInfo)
        parser.behavior(conn_block, builder_info)

    def __parse_procedural(
        self,
        parser: FunctionParser,
        module_node: HDL.CircuitNode,
        block: HDL.Behavior,
    ):
        assert isinstance(block, HDL.Behavior)
        assert callable(block.func)

        block_type = block.kind.value
        comment_text = f"// @{block_type} {block.func.__name__}():"
        ir_sv_newline()
        sv.verbatim(comment_text, [])

        # The source code and AST of a behavioral block are identical for all
        # instances, so they can be cached in the HDL module for efficiency.
        func_info = module_node.load_func_info(block.func)
        parser.behavior(block, func_info)

    def __cleanup_localparam_placeholders(self, entry_block: IR.Block):
        start_op = None
        end_op = None
        start_index = -1
        end_index = -1
        for i, op in enumerate(entry_block.operations):
            if ir_match_sv_verbatim(op, COMMENT_LOCALPARAMS):
                start_op = op
                start_index = i
            elif ir_match_sv_verbatim(op, COMMENT_LOCALPARAMS_END):
                end_op = op
                end_index = i
        assert isinstance(start_op, sv.VerbatimOp)
        assert isinstance(end_op, sv.VerbatimOp)
        if end_index == start_index + 1:
            # Remove the empty local parameter section
            if start_index > 0:
                prev_op = entry_block.operations[start_index - 1]
            else:
                prev_op = None
            assert end_index < len(entry_block.operations) - 1
            next_op = entry_block.operations[end_index + 1]
            start_op.erase()
            end_op.erase()
            if ir_is_sv_newline(prev_op) and ir_is_sv_newline(next_op):
                # Merge surrounding newlines
                next_op.erase()
        else:
            # Remove the end marker of the local parameter section
            assert end_index < len(entry_block.operations) - 1
            next_op = entry_block.operations[end_index + 1]
            end_op.erase()
            if not ir_is_sv_newline(next_op):
                with IR.InsertionPoint(next_op):
                    ir_sv_newline()
