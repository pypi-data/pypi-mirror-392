# pyvalidator

Validate Python objects

## Installation

```bash
pip install pyvalidator
```

## 💡 Usage Examples

### Basic Operations

```python
from pylib_validator import Schema, validate

# Define validation schema
schema = Schema({
    "name": lambda x: isinstance(x, str) and len(x) > 0,
    "age": lambda x: isinstance(x, int) and 0 < x < 150,
    "email": lambda x: "@" in str(x)
})

# Validate data
data = {"name": "John", "age": 30, "email": "john@example.com"}
is_valid, errors = validate(data, schema)
# (True, [])
```

### AI/ML Use Cases

```python
from pylib_validator import Schema, validate

# Validate ML model inputs
input_schema = Schema({
    "features": lambda x: isinstance(x, list) and len(x) > 0,
    "model_type": lambda x: x in ["classification", "regression"]
})
is_valid, errors = validate(model_input, input_schema)
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
