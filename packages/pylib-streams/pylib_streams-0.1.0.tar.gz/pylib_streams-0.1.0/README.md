# pystreams

Chainable functional API for list processing

## Installation

```bash
pip install pystreams
```

## 💡 Usage Examples

### Basic Operations

```python
from pylib_streams import Stream, map, filter, reduce

# Using Stream class
result = Stream([1, 2, 3, 4, 5])\
    .map(lambda x: x * 2)\
    .filter(lambda x: x > 5)\
    .to_list()
# [6, 8, 10]

# Using functional API
doubled = map(lambda x: x * 2, [1, 2, 3])
filtered = filter(lambda x: x > 2, [1, 2, 3, 4])
summed = reduce(lambda a, b: a + b, [1, 2, 3, 4])
# 10
```

### AI/ML Use Cases

```python
from pylib_streams import Stream, map, filter, reduce

# Process ML predictions
predictions = Stream([0.1, 0.5, 0.9, 0.3])\
    .filter(lambda p: p > 0.5)\
    .map(lambda p: "high" if p > 0.8 else "medium")\
    .to_list()

# Transform training data
features = Stream(raw_data)\
    .map(extract_features)\
    .filter(is_valid)\
    .to_list()
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
