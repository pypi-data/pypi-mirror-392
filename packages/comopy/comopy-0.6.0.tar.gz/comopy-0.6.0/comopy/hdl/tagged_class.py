# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Base class for tagging and collecting special methods.

A specific decorator tags class methods with a category, and the class collects
them based on the category.
"""

from __future__ import annotations

from types import FunctionType
from typing import Callable, Optional, Sequence, Type

# Reserved method names in HDL, which cannot be used for tagged methods
_hdl_reserved_names = (
    "assemble",
    "assemble_connection",  # at call path of _get_builder_frame_from_stack()
)


# Register method with a category tag, and return the method
#
def tagged_method(method: Callable, category: str) -> Callable:
    """Tag a method with a category."""
    assert callable(method)
    name = method.__name__
    if name in _hdl_reserved_names:
        raise NameError(
            f"Tagged method {name}() conflicts with a reserved name."
        )
    tagged_class_names = dir(TaggedClass())
    if name in tagged_class_names:
        raise NameError(
            f"Tagged method {name}() conflicts with a TaggedClass attribute."
        )
    _register_method(category, method)
    return method


def _register_method(category: str, method: Callable):
    class_name = _get_method_class(method)
    reg = MethodRegistry.get_registry(method.__module__, class_name)
    if not reg:
        reg = MethodRegistry.add_registry(method.__module__, class_name)
    reg.register_method(category, method)


def _get_method_class(method: Callable) -> str:
    qual_name = method.__qualname__
    func_name = method.__name__
    assert qual_name.endswith(func_name)
    class_name = qual_name[: -len(func_name) - 1]
    assert class_name
    return class_name


class MethodRegistry:
    """Registry for tagged (decorated) methods.

    In Python, decorators are called at import time. If a decorator is used
    for a class method, it is called before the class definition is complete,
    so it cannot access the class for any registration.
    MethodRegistry provides a mechanism to register decorated methods.
    It creates a registry for each class and registers the methods by their
    qualified names.
    """

    py_module: str
    class_name: str
    methods: dict[str, list[Callable]]  # category -> methods

    # Global registries
    _registries: dict[str, MethodRegistry] = {}

    def __init__(self, py_module: str, class_name: str):
        self.py_module = py_module
        self.class_name = class_name
        self.methods = {}

    @property
    def full_path(self) -> str:
        return self.__full_path(self.py_module, self.class_name)

    @staticmethod
    def __full_path(py_module: str, class_name: str) -> str:
        return f"{py_module}.{class_name}"

    def register_method(self, category: str, method: Callable):
        s = self.methods.setdefault(category, [])
        # Don't check duplication. Decorators are called at import time.
        s.append(method)

    def get_methods(self, category: str) -> tuple[Callable, ...]:
        return tuple(self.methods.get(category, []))

    # Class methods for global registries
    #
    @classmethod
    def get_registry(
        cls, py_module: str, class_name: str
    ) -> Optional[MethodRegistry]:
        full_path = cls.__full_path(py_module, class_name)
        return cls._registries.get(full_path, None)

    @classmethod
    def add_registry(cls, py_module: str, class_name: str) -> MethodRegistry:
        full_path = cls.__full_path(py_module, class_name)
        assert full_path not in cls._registries
        reg = MethodRegistry(py_module, class_name)
        cls._registries[full_path] = reg
        return reg

    @classmethod
    def remove_registry(cls, py_module: str, class_name: str):
        full_path = cls.__full_path(py_module, class_name)
        cls._registries.pop(full_path, None)

    @classmethod
    def get_class_registry(cls, class_type: Type) -> Optional[MethodRegistry]:
        py_module = class_type.__module__
        class_name = class_type.__qualname__
        return cls.get_registry(py_module, class_name)

    @classmethod
    def remove_class_registry(cls, class_type: Type):
        py_module = class_type.__module__
        class_name = class_type.__qualname__
        cls.remove_registry(py_module, class_name)

    @classmethod
    def get_class_methods(
        cls, class_type: Type, category: str
    ) -> tuple[Callable, ...]:
        reg = cls.get_class_registry(class_type)
        return reg.get_methods(category) if reg else ()


class TaggedClass:
    """Base class for supporting tagged (decorated) methods.

    TaggedClass enables collection and management of methods that are
    registered with specific category tags via decorators. Subclasses
    can define tags and retrieve methods grouped by those tags.
    """

    _tags: tuple[str, ...] = ()
    _tagged_methods: dict[str, tuple[Callable, ...]] = {}
    _bound_methods: dict[str, tuple[Callable]] = {}

    def __init_subclass__(subclass):
        super().__init_subclass__()
        # Subclasses inherit the _tags attribute. However, they should have
        # their own _tagged/bound_methods to support method overriding.
        subclass._tagged_methods = {}
        subclass._bound_methods = {}

    @classmethod
    def init_tagged_methods(cls):
        """Initialize tagged methods."""
        if not cls._tags or cls._tagged_methods:
            return
        for k in cls.__get_mro_classes():
            assert isinstance(k._tagged_methods, dict)
            if not k._tagged_methods:
                for tag in k._tags:
                    methods = MethodRegistry.get_class_methods(k, tag)
                    cls.__check_tagged_methods(k, methods)
                    k._tagged_methods[tag] = methods
                MethodRegistry.remove_class_registry(k)

    @classmethod
    def __get_mro_classes(cls):
        mro = reversed(cls.mro())
        classes = [k for k in mro if issubclass(k, TaggedClass)]
        assert classes[-1] == cls
        return classes

    @classmethod
    def __check_tagged_methods(
        cls, class_type: type[TaggedClass], methods: Sequence[Callable]
    ):
        for method in methods:
            class_name = class_type.__name__
            name = method.__name__
            full_name = f"{class_name}.{name}"
            if type(method) is not FunctionType:
                raise TypeError(
                    f"Tagged {full_name} is not a function."
                    f"\n- Tagged method for builder or behavior "
                    "must be a function."
                )
            if not hasattr(class_type, name):
                raise ValueError(
                    f"Tagged {full_name}() is not found in {class_name}."
                    f"\n- Class {class_name} was redefined?"
                )
            now = getattr(class_type, name)
            if now != method:
                raise ValueError(
                    f"Tagged {full_name}() is not current {full_name}()."
                    f"\n- Class {class_name} or method {full_name}() "
                    "was redefined?"
                )

    @classmethod
    def get_tagged_methods(cls, category: str) -> tuple[Callable, ...]:
        """Get bound tagged methods for the category."""
        if category not in cls._tags:
            return ()
        # Don't call init_tagged_methods() here.
        # If an exception occurs in init_tagged_methods(), AssembleHDL will try
        # to get builder names and reach here.
        if not cls._tagged_methods:
            return ()
        if category not in cls._bound_methods:
            cls.__bind_tagged_methods(category)
        return cls._bound_methods[category]

    @classmethod
    def __bind_tagged_methods(cls, category: str):
        """Bind tagged methods for the current class."""
        assert category in cls._tags
        assert category not in cls._bound_methods
        # All methods of MRO classes with the tag
        methods = []
        for k in cls.__get_mro_classes():
            methods.extend(k._tagged_methods.get(category, []))
        # Deduplicate method names
        names = [m.__name__ for m in methods]
        names = list(dict.fromkeys(names))
        # Resolve method names
        bound = []
        for name in names:
            func = getattr(cls, name, None)
            assert callable(func)
            if func not in methods:
                base_func = [m for m in methods if m.__name__ == name][-1]
                raise ValueError(
                    f"Method {func.__name__}() is not tagged with @{category}."
                    f"\n- Overriding tagged {base_func.__qualname__}()?"
                )
            bound.append(func)
        cls._bound_methods[category] = tuple(bound)

    @classmethod
    def get_mro_tagged_methods(cls, category: str) -> tuple[Callable, ...]:
        """Get all tagged methods for the category in reversed MRO."""
        if category not in cls._tags:
            return ()
        if not cls._tagged_methods:
            return ()
        methods = []
        for k in cls.__get_mro_classes():
            methods.extend(k._tagged_methods.get(category, []))
        return tuple(methods)
