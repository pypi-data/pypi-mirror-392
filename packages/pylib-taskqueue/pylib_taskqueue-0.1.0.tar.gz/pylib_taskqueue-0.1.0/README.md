# pytaskqueue

In-memory async queue

## Installation

```bash
pip install pytaskqueue
```

## 💡 Usage Examples

### Basic Operations

```python
from pylib_taskqueue import TaskQueue

# Create task queue
queue = TaskQueue()
queue.enqueue(task_function, args=[1, 2, 3])
queue.process()
```

### AI/ML Use Cases

```python
from pylib_taskqueue import TaskQueue

# Queue ML prediction tasks
queue.enqueue(predict_task, data=data_point)
queue.enqueue(train_task, data=training_batch)
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
