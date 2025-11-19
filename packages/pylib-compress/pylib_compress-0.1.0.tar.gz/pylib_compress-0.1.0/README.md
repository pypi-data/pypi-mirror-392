# pycompress

Compress/decompress files

## Installation

```bash
pip install pycompress
```

## 💡 Usage Examples

### Basic Operations

```python
from pylib_compress import compress, decompress

# Compress data
compressed = compress("original data")
# Compressed bytes

# Decompress data
decompressed = decompress(compressed)
# 'original data'
```

### AI/ML Use Cases

```python
from pylib_compress import compress, decompress

# Compress model weights for storage
compressed_weights = compress(model_weights)

# Compress training data
compressed_data = compress(json.dumps(training_data))
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
