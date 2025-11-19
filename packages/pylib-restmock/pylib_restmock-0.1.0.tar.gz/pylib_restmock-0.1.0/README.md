# pyrestmock

Mock REST APIs

## Installation

```bash
pip install pyrestmock
```

## 💡 Usage Examples

### Basic Operations

```python
from pylib_restmock import MockServer

# Create mock server
server = MockServer()
server.add_route("GET", "/api/data", {"result": "success"})
response = server.request("GET", "/api/data")
```

### AI/ML Use Cases

```python
from pylib_restmock import MockServer

# Mock AI API for testing
mock_ai_api = MockServer()
mock_ai_api.add_route("POST", "/api/predict", {"prediction": "cat"})
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
