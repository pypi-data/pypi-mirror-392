# Tests for TaggedClass.py
#

import pytest

from comopy.hdl.tagged_class import (
    MethodRegistry,
    TaggedClass,
    _register_method,
    tagged_method,
)


def test_MethodRegistry_register_method():
    def func():  # pragma: no cover
        ...

    reg2 = MethodRegistry("comopy.hdl", "Module")
    assert reg2.full_path == "comopy.hdl.Module"
    assert reg2.methods == {}
    reg2.register_method("build", func)
    assert len(reg2.methods) == 1
    assert "build" in reg2.methods
    assert len(reg2.methods["build"]) == 1
    assert reg2.methods["build"][0] == func
    assert reg2.get_methods("build") == (func,)
    # Permit duplication. Check duplication in Module.
    reg2.register_method("build", func)
    assert len(reg2.methods["build"]) == 2
    assert reg2.methods["build"][1] == func
    assert reg2.get_methods("build") == (func, func)

    reg2.register_method("init", func)
    assert len(reg2.methods) == 2
    assert "init" in reg2.methods
    assert len(reg2.methods["init"]) == 1
    assert reg2.methods["init"][0] == func
    assert reg2.get_methods("init") == (func,)


def test_MethodRegistry_get_add_remove_registry():
    old = len(MethodRegistry._registries)

    # Add one registry
    reg1 = MethodRegistry.get_registry("comopy.hdl.x1", "MethodRegistry")
    assert reg1 is None
    reg = MethodRegistry.add_registry("comopy.hdl.x1", "MethodRegistry")
    reg1 = MethodRegistry.get_registry("comopy.hdl.x1", "MethodRegistry")
    assert isinstance(reg1, MethodRegistry)
    assert reg1 is reg
    assert reg1.full_path == "comopy.hdl.x1.MethodRegistry"
    assert len(MethodRegistry._registries) == old + 1
    assert "comopy.hdl.x1.MethodRegistry" in MethodRegistry._registries

    # Add another registry
    reg2 = MethodRegistry.get_registry("comopy.hdl.x1", "Method")
    assert reg2 is None
    reg = MethodRegistry.add_registry("comopy.hdl.x1", "Method")
    reg2 = MethodRegistry.get_registry("comopy.hdl.x1", "Method")
    assert isinstance(reg2, MethodRegistry)
    assert reg2 is reg
    assert reg2 != reg1
    assert reg2.full_path == "comopy.hdl.x1.Method"
    assert len(MethodRegistry._registries) == old + 2
    assert "comopy.hdl.x1.Method" in MethodRegistry._registries

    # Get existing registry
    reg3 = MethodRegistry.get_registry("comopy.hdl.x1", "MethodRegistry")
    assert isinstance(reg3, MethodRegistry)
    assert reg3 is reg1
    assert len(MethodRegistry._registries) == old + 2

    # Add existing registry
    with pytest.raises(AssertionError):
        MethodRegistry.add_registry("comopy.hdl.x1", "MethodRegistry")

    # Remove registry
    MethodRegistry.remove_registry("comopy.hdl.x1", "MethodRegistry")
    assert "comopy.hdl.x1.MethodRegistry" not in MethodRegistry._registries
    assert "comopy.hdl.x1.Method" in MethodRegistry._registries
    reg = MethodRegistry.get_registry("comopy.hdl.x1", "MethodRegistry")
    assert reg is None
    assert len(MethodRegistry._registries) == old + 1
    # Remove nonexistent registry
    MethodRegistry.remove_registry("comopy.hdl.x1", "MethodRegistry")
    assert "comopy.hdl.x1.MethodRegistry" not in MethodRegistry._registries
    assert "comopy.hdl.x1.Method" in MethodRegistry._registries
    reg = MethodRegistry.get_registry("comopy.hdl.x1", "MethodRegistry")
    assert reg is None
    assert len(MethodRegistry._registries) == old + 1
    # Remove another registry
    MethodRegistry.remove_registry("comopy.hdl.x1", "Method")
    assert "comopy.hdl.x1.Method" not in MethodRegistry._registries
    reg = MethodRegistry.get_registry("comopy.hdl.x1", "Method")
    assert reg is None
    assert len(MethodRegistry._registries) == old


class Outer:
    def foo(s):  # pragma: no cover
        ...

    def bar(s):  # pragma: no cover
        ...


def test_register_method():
    old = len(MethodRegistry._registries)

    # Register methods in global class
    _register_method("foo", Outer.foo)
    assert len(MethodRegistry._registries) == old + 1
    assert f"{__name__}.Outer" in MethodRegistry._registries
    reg = MethodRegistry.get_class_registry(Outer)
    assert isinstance(reg, MethodRegistry)
    assert len(reg.methods) == 1
    assert "foo" in reg.methods
    assert reg.methods["foo"] == [Outer.foo]
    _register_method("foo", Outer.bar)
    assert len(reg.methods) == 1
    assert reg.methods["foo"] == [Outer.foo, Outer.bar]
    _register_method("bar", Outer.bar)
    assert len(reg.methods) == 2
    assert "bar" in reg.methods
    assert reg.methods["bar"] == [Outer.bar]
    methods = MethodRegistry.get_class_methods(Outer, "foo")
    assert methods == (Outer.foo, Outer.bar)
    methods = MethodRegistry.get_class_methods(Outer, "bar")
    assert methods == (Outer.bar,)

    class Inner:
        def foo(s):  # pragma: no cover
            ...

        def bar(s):  # pragma: no cover
            ...

    # Register methods in local class
    _register_method("foo", Inner.foo)
    assert len(MethodRegistry._registries) == old + 2
    func = "test_register_method"
    assert f"{__name__}.{func}.<locals>.Inner" in MethodRegistry._registries
    reg = MethodRegistry.get_class_registry(Inner)
    assert len(reg.methods) == 1
    assert "foo" in reg.methods
    assert reg.methods["foo"] == [Inner.foo]
    _register_method("foo", Inner.bar)
    assert len(reg.methods) == 1
    assert reg.methods["foo"] == [Inner.foo, Inner.bar]
    methods = MethodRegistry.get_class_methods(Inner, "foo")
    assert methods == (Inner.foo, Inner.bar)

    # No class
    with pytest.raises(AssertionError):
        _register_method("foo", test_register_method)

    # Remove registries
    MethodRegistry.remove_class_registry(Outer)
    assert MethodRegistry.get_class_registry(Outer) is None
    MethodRegistry.remove_class_registry(Inner)
    assert MethodRegistry.get_class_registry(Inner) is None
    assert len(MethodRegistry._registries) == old


def tag1(method):
    return tagged_method(method, "tag1")


def tag2(method):
    return tagged_method(method, "tag2")


class Base(TaggedClass):
    _tags = ()

    @tag1
    def foo1(s):  # pragma: no cover
        ...

    @tag2
    def bar1(s):  # pragma: no cover
        ...

    @tag1
    def baz1(s):  # pragma: no cover
        ...


class Common(Base):
    @tag2
    def foo2(s):  # pragma: no cover
        ...

    @tag1
    def bar2(s):  # pragma: no cover
        ...


def test_TaggedClass_tagged_methods():
    # No tags
    assert Base._tags == ()
    assert Common._tags == ()
    assert Base.get_tagged_methods("tag1") == ()
    assert Common.get_tagged_methods("tag1") == ()
    assert Base.get_mro_tagged_methods("tag1") == ()
    Base.init_tagged_methods()
    Base._tagged_methods == {}
    Base._tagged_methods is not TaggedClass._tagged_methods
    Common.init_tagged_methods()
    Common._tagged_methods == {}
    Common._tagged_methods is not TaggedClass._tagged_methods

    # Initialize subclass
    Base._tags = ("tag1", "tag2")
    assert Base._tags == ("tag1", "tag2")
    assert Common._tags is Base._tags
    assert Base._tagged_methods == {}
    assert Common._tagged_methods == {}
    assert Common._tagged_methods is not Base._tagged_methods
    assert Base._bound_methods == {}
    assert Common._bound_methods == {}
    assert Common._bound_methods is not Base._bound_methods
    assert Base.get_tagged_methods("tag1") == ()
    assert Base.get_mro_tagged_methods("tag1") == ()
    assert Common.get_tagged_methods("tag1") == ()
    assert Common.get_mro_tagged_methods("tag1") == ()

    # Initialize instance
    b1 = Base()
    c1 = Common()
    assert b1._tags is Base._tags
    assert b1._tagged_methods is Base._tagged_methods
    assert c1._tags is Common._tags
    assert c1._tagged_methods is Common._tagged_methods
    assert b1.get_tagged_methods("tag1") == ()
    assert c1.get_tagged_methods("tag1") == ()

    # Initialize tagged methods
    c1.init_tagged_methods()
    assert c1._tagged_methods == {
        "tag1": (Common.bar2,),
        "tag2": (Common.foo2,),
    }
    assert c1._tagged_methods is Common._tagged_methods
    assert b1._tagged_methods == {
        "tag1": (Base.foo1, Base.baz1),
        "tag2": (Base.bar1,),
    }
    assert b1._tagged_methods is Base._tagged_methods
    assert MethodRegistry.get_class_registry(Base) is None
    assert MethodRegistry.get_class_registry(Common) is None

    # Base class initialized
    old_tagged = Base._tagged_methods
    b1.init_tagged_methods()
    assert b1._tagged_methods is old_tagged
    assert Base._tagged_methods is old_tagged

    # Bind tagged methods in subclass
    assert "tag1" not in c1._bound_methods
    c1.get_tagged_methods("tag1")
    assert "tag1" in c1._bound_methods
    methods = Common.get_tagged_methods("tag1")
    assert methods == (Base.foo1, Base.baz1, Common.bar2)
    assert c1.get_mro_tagged_methods("tag1") == methods
    assert b1._bound_methods == {}  # does not affect base class
    assert "tag2" not in Common._bound_methods
    Common.get_tagged_methods("tag2")
    assert "tag2" in Common._bound_methods
    methods = c1.get_tagged_methods("tag2")
    assert methods == (Base.bar1, Common.foo2)
    assert Common.get_mro_tagged_methods("tag2") == methods
    assert b1._bound_methods == {}  # does not affect base class

    # Bind in base class
    assert "tag1" not in b1._bound_methods
    b1.get_tagged_methods("tag1")
    assert "tag1" in b1._bound_methods
    methods = Base.get_tagged_methods("tag1")
    assert methods == (Base.foo1, Base.baz1)
    assert b1.get_mro_tagged_methods("tag1") == methods
    assert c1.get_tagged_methods("tag1") == (Base.foo1, Base.baz1, Common.bar2)
    assert "tag2" not in Base._bound_methods
    Base.get_tagged_methods("tag2")
    assert "tag2" in Base._bound_methods
    methods = b1.get_tagged_methods("tag2")
    assert methods == (Base.bar1,)
    assert b1.get_mro_tagged_methods("tag2") == methods
    assert c1.get_tagged_methods("tag2") == (Base.bar1, Common.foo2)

    # Bind nonexistent tag
    assert "tag3" not in Base._bound_methods
    methods = Base.get_tagged_methods("tag3")
    assert methods == ()
    assert "tag3" not in Base._bound_methods

    class Inner(Common):
        @tag1
        def foo1(s):  # pragma: no cover
            ...

        @tag2
        def foo2(s):  # pragma: no cover
            ...

    # Bind overridden methods
    inner = Inner()
    assert inner._tags == ("tag1", "tag2")
    assert inner._tagged_methods == {}
    assert inner._bound_methods == {}
    inner.init_tagged_methods()
    methods = inner._tagged_methods
    assert methods == {"tag1": (Inner.foo1,), "tag2": (Inner.foo2,)}
    assert "tag1" not in inner._bound_methods
    methods = inner.get_tagged_methods("tag1")
    assert methods == (Inner.foo1, Base.baz1, Common.bar2)
    assert inner.get_tagged_methods("tag1") == methods  # get again
    methods = inner.get_mro_tagged_methods("tag1")
    assert methods == (Base.foo1, Base.baz1, Common.bar2, Inner.foo1)
    assert "tag2" not in inner._bound_methods
    methods = inner.get_tagged_methods("tag2")
    assert methods == (Base.bar1, Inner.foo2)
    assert inner.get_tagged_methods("tag2") == methods  # get again
    methods = inner.get_mro_tagged_methods("tag2")
    assert methods == (Base.bar1, Common.foo2, Inner.foo2)

    class BadOverride(Inner):
        def foo1(s):  # pragma: no cover
            ...

        @tag1
        def foo2(s):  # pragma: no cover
            ...

    # Errors in loading are tested in RawModule_test.py

    # Errors in binding
    bad = BadOverride()
    bad.init_tagged_methods()
    with pytest.raises(ValueError, match="is not tagged with @tag1"):
        bad.get_tagged_methods("tag1")
    with pytest.raises(ValueError, match="is not tagged with @tag2"):
        bad.get_tagged_methods("tag2")
