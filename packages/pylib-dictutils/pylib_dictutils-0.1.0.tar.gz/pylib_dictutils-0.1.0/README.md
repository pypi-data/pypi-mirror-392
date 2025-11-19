# pydictutils

Deep merge, flatten, pick, omit

## Installation

```bash
pip install pydictutils
```

## 💡 Usage Examples

### Basic Operations

```python
from pylib_dictutils import deep_merge, flatten_dict, pick, omit

# Deep merge dictionaries
dict1 = {"a": 1, "b": {"c": 2}}
dict2 = {"b": {"d": 3}, "e": 4}
merged = deep_merge(dict1, dict2)
# {'a': 1, 'b': {'c': 2, 'd': 3}, 'e': 4}

# Flatten nested dictionary
nested = {"a": 1, "b": {"c": 2, "d": 3}}
flat = flatten_dict(nested)
# {'a': 1, 'b.c': 2, 'b.d': 3}

# Pick specific keys
data = {"name": "John", "age": 30, "city": "NYC"}
picked = pick(data, ["name", "age"])
# {'name': 'John', 'age': 30}

# Omit specific keys
omitted = omit(data, ["age"])
# {'name': 'John', 'city': 'NYC'}
```

### AI/ML Use Cases

```python
from pylib_dictutils import deep_merge, flatten_dict, pick, omit

# Merge API responses with defaults
default_config = {"model": "gpt-4", "temperature": 0.7}
user_config = {"temperature": 0.9}
final_config = deep_merge(default_config, user_config)

# Flatten ML model parameters
model_params = {"layers": {"hidden": 128, "output": 10}}
flat_params = flatten_dict(model_params)
# {'layers.hidden': 128, 'layers.output': 10}
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
