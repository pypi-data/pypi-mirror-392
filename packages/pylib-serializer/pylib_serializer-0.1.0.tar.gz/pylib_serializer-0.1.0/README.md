# pyserializer

Safe JSON/YAML serialization

## Installation

```bash
pip install pyserializer
```

## 💡 Usage Examples

### Basic Operations

```python
from pylib_serializer import serialize, to_json, to_yaml

# Serialize to JSON
data = {"name": "John", "age": 30}
json_str = serialize(data)
# '{"name": "John", "age": 30}'

# Convert to JSON
json_output = to_json(data)

# Convert to YAML
yaml_output = to_yaml(data)
# 'name: John
age: 30'
```

### AI/ML Use Cases

```python
from pylib_serializer import serialize, to_json, to_yaml

# Serialize ML model predictions
predictions = {"class": "cat", "confidence": 0.95}
json_predictions = serialize(predictions)

# Save model config
config = {"model": "resnet50", "epochs": 100}
yaml_config = to_yaml(config)
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
