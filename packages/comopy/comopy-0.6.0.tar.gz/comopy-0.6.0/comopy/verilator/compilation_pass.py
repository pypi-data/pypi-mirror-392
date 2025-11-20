# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang
#         Shixuan Chen

"""
Build Python extension module from verilated model.
"""

import os
import subprocess
from pathlib import Path

import setuptools
from pybind11.setup_helpers import Pybind11Extension, build_ext

from comopy.hdl import CircuitNode, RawModule
from comopy.translator import BaseTranslator
from comopy.utils import BasePass

from .vsimulator import VSimulator


class CompilationPass(BasePass):

    top_module: RawModule
    top_module_name: str
    dest_dir: Path
    obj_dir: Path
    sv_files: list[Path]
    extension_path: Path

    def __call__(self, tree: CircuitNode) -> CircuitNode:
        assert isinstance(tree, CircuitNode)
        assert tree.is_root and tree.is_assembled_module
        assert isinstance(tree.obj, RawModule)
        self.top_module = tree.obj
        translator = self.top_module.translator
        assert isinstance(translator, BaseTranslator)

        self.top_module_name = type(self.top_module).__name__
        self.dest_dir = translator.dest_path.parent
        self.obj_dir = self.dest_dir / "obj_dir"
        self.sv_files = list(self.dest_dir.glob("*.sv"))
        self.verilate()
        self.build_extension()
        self.setup_vsimulator()

        return tree

    def verilate(self):
        options = [
            "--cc",
            "--no-timing",
            "--top-module",
            f"{self.top_module_name}",
            "--assert",
            "--output-split",
            "20000",
            "--x-assign",
            "unique",
            "-O3",
            "--Wno-UNOPTFLAT",
            "--Mdir",
            str(self.obj_dir),
        ]

        command = ["verilator"] + options + self.sv_files

        try:
            subprocess.run(command, check=True, cwd=self.dest_dir)
        except subprocess.CalledProcessError:
            command_str = " ".join(str(arg) for arg in command)
            raise RuntimeError(
                "Verilator failed to generate C++ code "
                f"(top module: '{self.top_module_name}').\n"
                f"Command: {command_str}"
            ) from None
        except FileNotFoundError:
            command_str = " ".join(str(arg) for arg in command)
            env_path = os.environ.get("PATH", "")
            raise RuntimeError(
                "'verilator' command not found "
                f"(top module: '{self.top_module_name}').\n"
                f"Command: {command_str}\n"
                f"Current PATH: {env_path}"
            ) from None

    def build_extension(self):
        include_path = self.__verilator_include_path()
        binding_file = self.dest_dir / f"V{self.top_module_name}_binding.cpp"
        verilated_sources = sorted(self.obj_dir.glob("*.cpp"))

        # Create extension module
        ext_modules = [
            Pybind11Extension(
                f"V{self.top_module_name}",
                [
                    str(binding_file),
                    str(include_path / "verilated.cpp"),
                    str(include_path / "verilated_threads.cpp"),
                ]
                + [str(src) for src in verilated_sources],
                extra_compile_args=[
                    f"-I{include_path}",
                    f"-I{include_path / 'vltstd'}",
                    f"-I{self.obj_dir}",
                    "-O3",
                ],
                cxx_std=17,
            )
        ]

        # Build extension using setuptools
        setuptools.setup(
            name=f"V{self.top_module_name}",
            ext_modules=ext_modules,
            cmdclass={"build_ext": build_ext},
            options={
                "build": {"build_base": str(self.dest_dir)},
                "build_ext": {"inplace": False},
            },
            zip_safe=False,
            script_args=["build_ext", "--force"],
        )

    def __verilator_include_path(self) -> Path:
        command = ["verilator", "--getenv", "VERILATOR_ROOT"]
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, check=True
            )
        except FileNotFoundError:
            command_str = " ".join(command)
            env_path = os.environ.get("PATH", "")
            raise RuntimeError(
                "'verilator' command not found.\n"
                f"Command: {command_str}\n"
                f"Current PATH: {env_path}"
            ) from None

        verilator_root = result.stdout.strip()
        assert verilator_root
        include_path = Path(verilator_root) / "include"
        if not include_path.exists():
            raise RuntimeError(
                f"Verilator include directory not found: {include_path}"
            )

        return include_path

    def setup_vsimulator(self):
        ext_name = f"V{self.top_module_name}"
        found_files = []
        for root, _, files in os.walk(self.dest_dir):
            for file in files:
                if file.startswith(f"{ext_name}.") and file.endswith(".so"):
                    found_files.append(Path(root) / file)

        if not found_files:
            raise FileNotFoundError(
                f"Extension '{ext_name}.so' not found "
                f"in destination directory: {self.dest_dir}"
            )

        if len(found_files) > 1:
            files_str = "\n  ".join(str(f) for f in found_files)
            raise RuntimeError(
                f"Multiple extension files found for '{ext_name}':"
                f"\n  {files_str}"
            )

        vsim = VSimulator(self.top_module, found_files[0])
        self.top_module.attach_vsimulator(vsim)
