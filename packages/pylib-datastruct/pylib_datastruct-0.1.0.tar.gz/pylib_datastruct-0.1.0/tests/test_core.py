"""Tests for pydatastruct core functions."""

from pylib-datastruct import Stack, Queue, Graph, Tree


def test_stack():
    """Test Stack."""
    s = Stack()
    s.push(1)
    s.push(2)
    assert s.pop() == 2
    assert s.pop() == 1


def test_queue():
    """Test Queue."""
    q = Queue()
    q.enqueue(1)
    q.enqueue(2)
    assert q.dequeue() == 1
    assert q.dequeue() == 2


def test_graph():
    """Test Graph."""
    g = Graph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    assert len(g.get_neighbors(1)) == 1


def test_tree():
    """Test Tree."""
    t = Tree(5)
    t.insert(3)
    t.insert(7)
    assert 3 in t.inorder()
    assert 7 in t.inorder()
