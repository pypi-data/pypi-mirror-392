# pycompare

Deep diff for dicts/lists

## Installation

```bash
pip install pycompare
```

## 💡 Usage Examples

### Basic Operations

```python
from pylib_compare import deep_diff, patch, compare

# Deep diff between dictionaries
dict1 = {"a": 1, "b": 2}
dict2 = {"a": 1, "b": 3, "c": 4}
diff = deep_diff(dict1, dict2)
# {'b': {'op': 'replace', 'old': 2, 'new': 3}, 'c': {'op': 'add', 'value': 4}}

# Apply patch
patched = patch(dict1, diff)
# {'a': 1, 'b': 3, 'c': 4}

# Compare objects
is_equal = compare(dict1, dict2)
# False
```

### AI/ML Use Cases

```python
from pylib_compare import deep_diff, patch, compare

# Track model configuration changes
old_config = {"lr": 0.01, "batch_size": 32}
new_config = {"lr": 0.001, "batch_size": 64}
changes = deep_diff(old_config, new_config)

# Compare model outputs
output1 = {"prediction": "cat", "confidence": 0.9}
output2 = {"prediction": "cat", "confidence": 0.9}
are_same = compare(output1, output2)
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
