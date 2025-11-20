# Tests for CircuitNode
#

import pytest

from comopy.hdl.circuit_node import CircuitNode
from comopy.hdl.circuit_object import CircuitObject


def test_CircuitNode_init():
    obj = CircuitObject()
    node = CircuitNode(obj)
    assert node.obj == obj
    assert node.ir_top is None
    assert node.owner is None
    assert node.elements == ()
    assert node.level == 0
    assert node.name == "_Unknown_"
    assert node.full_name == "_Unknown_"
    assert node._top is None
    assert node.code_pos is None
    assert node.inst_blocks == ()
    assert node.conn_blocks == ()
    assert node.comb_blocks == ()
    assert node.seq_blocks == ()
    assert not node.is_root
    assert not node.is_assembled_module
    assert not node.is_assembled_package
    assert str(node) == "Circuit(_Unknown_)"

    # .top property applies only to nodes attached to a tree
    with pytest.raises(AssertionError):
        node.top

    obj = CircuitObject(name="obj")
    node = CircuitNode(obj)
    assert node.obj == obj
    assert node.name == "obj"
    assert node.full_name == "obj"
    assert str(node) == "Circuit(obj)"

    # Reject assembled object
    obj = CircuitObject()
    obj._assembled = True
    with pytest.raises(AssertionError):
        CircuitNode(obj)


def test_CircuitNode_append_element():
    parent = CircuitNode(CircuitObject(name="top"))
    parent._top = parent  # fake top
    assert parent.is_root
    assert str(parent) == "Circuit(top)"

    child1 = CircuitNode(CircuitObject(name="child1"))
    parent.append_element(child1)
    assert len(parent.elements) == 1
    assert child1 in parent.elements
    assert child1.owner == parent
    assert child1.level == 1
    assert child1.full_name == "top.child1"
    assert child1.top == parent
    assert not child1.is_root
    assert str(child1) == "Circuit(top.child1)"

    child2 = CircuitNode(CircuitObject(name="child2"))
    parent.append_element(child2)
    assert len(parent.elements) == 2
    assert child2 in parent.elements
    assert child2.owner == parent
    assert child2.level == 1
    assert child2.full_name == "top.child2"
    assert child2.top == parent
    assert not child2.is_root
    assert str(child2) == "Circuit(top.child2)"

    grandchild = CircuitNode(CircuitObject(name="grandchild"))
    child2.append_element(grandchild)
    assert len(child2.elements) == 1
    assert len(parent.elements) == 2
    assert grandchild in child2.elements
    assert grandchild.owner == child2
    assert grandchild.level == 2
    assert grandchild.full_name == "top.child2.grandchild"
    assert grandchild.top == parent
    assert not grandchild.is_root
    assert str(grandchild) == "Circuit(top.child2.grandchild)"

    assert parent.get_element("top") is parent
    assert parent.get_element("child") is None
    assert parent.get_element("top.child1") is child1
    assert parent.get_element("top.child2") is child2
    assert parent.get_element("top.child3") is None
    assert parent.get_element("top1.child1") is None
    assert parent.get_element("top.child1.grandchild") is None
    assert parent.get_element("top.child2.grandchild") is grandchild
    assert child1.get_element("child1.grandchild") is None
    assert child1.get_element("top.child1") is None
    assert child2.get_element("top.child2") is None
    assert child2.get_element("child1.grandchild") is None
    assert child2.get_element("child2.grandchild") is grandchild


def test_CircuitNode_remove_element():
    parent = CircuitNode(CircuitObject(name="top"))
    parent._top = parent  # fake top
    assert parent.is_root

    child1 = CircuitNode(CircuitObject(name="child1"))
    child2 = CircuitNode(CircuitObject(name="child2"))
    parent.append_element(child1)
    parent.append_element(child2)
    assert len(parent.elements) == 2
    assert child1 in parent.elements
    assert child2 in parent.elements
    assert child1.owner == parent
    assert child1.level == 1
    assert child1.full_name == "top.child1"
    assert child1.top == parent
    assert not child1.is_root
    assert str(child1) == "Circuit(top.child1)"
    parent.remove_element(child1)
    assert child1 not in parent.elements
    assert child1.owner is None
    assert child1.level == 0
    assert child1.full_name == "child1"
    assert child1._top is None
    assert not child1.is_root
    assert str(child1) == "Circuit(child1)"
    assert child2 in parent.elements
    assert child2.owner == parent
    assert child2.level == 1
    assert child2.full_name == "top.child2"
    assert child2.top == parent
    assert not child2.is_root
    assert str(child2) == "Circuit(top.child2)"
    assert len(parent.elements) == 1

    # remove a non-existent element
    assert child1 not in parent.elements
    with pytest.raises(ValueError):
        parent.remove_element(child1)

    # remove a non-leaf element
    child1 = CircuitNode(CircuitObject(name="child1"))
    parent.append_element(child1)
    grandchild = CircuitNode(CircuitObject(name="grandchild1"))
    child1.append_element(grandchild)
    assert grandchild.top == parent
    assert grandchild.full_name == "top.child1.grandchild1"
    with pytest.raises(AssertionError):
        parent.remove_element(child1)


def test_CircuitNode_iterator():
    parent = CircuitNode(CircuitObject(name="top"))
    parent._top = parent  # fake top
    assert parent.is_root
    parent.append_element(child1 := CircuitNode(CircuitObject(name="child1")))
    parent.append_element(child2 := CircuitNode(CircuitObject(name="child2")))
    child1.append_element(gch11 := CircuitNode(CircuitObject(name="grand11")))
    child2.append_element(gch21 := CircuitNode(CircuitObject(name="grand21")))
    child2.append_element(gch22 := CircuitNode(CircuitObject(name="grand22")))

    # Default iterator is BFS
    it = iter(parent)
    assert it._queue == [parent]
    assert it._index == 0
    bfs_order = [parent, child1, child2, gch11, gch21, gch22]
    assert list(it) == bfs_order

    # Multiple independent iterators
    it1 = iter(parent)
    it2 = iter(parent)
    assert next(it1) == parent
    assert next(it2) == parent
    assert next(it1) == child1
    assert next(it2) == child1

    # Partial iteration with break
    nodes = []
    for node in child2:
        if node.level > 1:
            break
        nodes.append(node)
    assert nodes == [child2]

    # Iterator on subtree
    child2_nodes = list(iter(child2))
    assert child2_nodes == [child2, gch21, gch22]

    # Explicit BFS iterator
    bfs_it = parent.iter_bfs()
    assert bfs_it._queue == [parent]
    assert bfs_it._index == 0
    assert list(bfs_it) == bfs_order

    # Explicit DFS iterator
    dfs_it = parent.iter_dfs()
    assert dfs_it._stack == [parent]
    dfs_order = [parent, child1, gch11, child2, gch21, gch22]
    assert list(dfs_it) == dfs_order

    # Explicit post-order iterator
    postorder_it = parent.iter_postorder()
    assert postorder_it._index == 0
    postorder_order = [gch11, child1, gch21, gch22, child2, parent]
    assert list(postorder_it) == postorder_order

    # Verify BFS, DFS and post-order orders are different
    assert bfs_order != dfs_order
    assert bfs_order != postorder_order
    assert dfs_order != postorder_order

    # BFS, DFS and post-order on subtree
    child2_bfs = list(child2.iter_bfs())
    child2_dfs = list(child2.iter_dfs())
    child2_postorder = list(child2.iter_postorder())
    assert child2_bfs == [child2, gch21, gch22]
    assert child2_dfs == [child2, gch21, gch22]  # Same for this simple subtree
    assert child2_postorder == [gch21, gch22, child2]  # Children before parent


def test_CircuitNode_hierarchy_till():
    top = CircuitNode(CircuitObject(name="top"))
    level1 = CircuitNode(CircuitObject(name="level1"))
    level2 = CircuitNode(CircuitObject(name="level2"))
    level3 = CircuitNode(CircuitObject(name="level3"))
    top._top = top  # fake top
    top.append_element(level1)
    level1.append_element(level2)
    level2.append_element(level3)
    assert level3.full_name == "top.level1.level2.level3"
    assert level3.get_hierarchy_till("NotExist") == []
    assert level3.get_hierarchy_till("top") == [top, level1, level2, level3]
    assert level3.get_hierarchy_till("level2") == [level2, level3]
    assert level3.get_hierarchy_till("level3") == [level3]
    assert level2.get_hierarchy_till("level3") == []
    assert level2.get_hierarchy_till("top") == [top, level1, level2]
    assert level2.get_hierarchy_till("level1") == [level1, level2]
    assert level2.get_hierarchy_till("level2") == [level2]

    with pytest.raises(AssertionError):
        level3.get_hierarchy_till("top.level1")
