# pydatastruct

Educational DSA implementations

## Installation

```bash
pip install pydatastruct
```

## 💡 Usage Examples

### Basic Operations

```python
from pylib_datastruct import Stack, Queue, Graph, Tree

# Stack
stack = Stack()
stack.push(1)
stack.push(2)
stack.pop()  # 2

# Queue
queue = Queue()
queue.enqueue(1)
queue.enqueue(2)
queue.dequeue()  # 1

# Graph
graph = Graph()
graph.add_edge("A", "B")
graph.add_edge("B", "C")
neighbors = graph.get_neighbors("A")

# Tree
tree = Tree(5)
tree.insert(3)
tree.insert(7)
inorder = tree.inorder()
```

### AI/ML Use Cases

```python
from pylib_datastruct import Stack, Queue, Graph, Tree

# Use stack for DFS in ML graph algorithms
stack = Stack()
stack.push(start_node)
# Process nodes...

# Use queue for BFS
queue = Queue()
queue.enqueue(root)
# Process nodes...
```

## 📚 API Reference

See package documentation for complete API reference.


## 🤖 AI Agent Friendly

This package is optimized for AI agents and code generation tools:
- **Clear function names** and signatures
- **Comprehensive docstrings** with examples
- **Type hints** for better IDE support
- **Common use cases** documented
- **Zero dependencies** for reliability

## License

MIT
