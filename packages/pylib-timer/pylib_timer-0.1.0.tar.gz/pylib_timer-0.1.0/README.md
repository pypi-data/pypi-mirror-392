# pytimer

Code timers

## Installation

```bash
pip install pytimer
```

## 💡 Usage Examples

### Basic Operations

```python
from pylib_timer import Timer, timeit

# Timer context manager
with Timer() as timer:
    # Your code here
    pass
print(f"Elapsed: {timer.elapsed} seconds")

# Time function execution
@timeit
def my_function():
    # Your code here
    pass
```

### AI/ML Use Cases

```python
from pylib_timer import Timer, timeit

# Time ML model training
with Timer() as timer:
    model.train(training_data)
print(f"Training took {timer.elapsed:.2f} seconds")

# Profile prediction function
@timeit
def predict_batch(data):
    return model.predict(data)
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
