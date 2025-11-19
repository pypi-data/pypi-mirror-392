# pychecksum

File hashes

## Installation

```bash
pip install pychecksum
```

## 💡 Usage Examples

### Basic Operations

```python
from pylib_checksum import md5_hash, sha256_hash

# Calculate MD5 hash
hash_value = md5_hash("data")
# MD5 hash string

# Calculate SHA256 hash
hash_value = sha256_hash("data")
# SHA256 hash string
```

### AI/ML Use Cases

```python
from pylib_checksum import md5_hash, sha256_hash

# Hash training data for caching
data_hash = sha256_hash(str(training_data))
# Use hash as cache key

# Verify model file integrity
file_hash = sha256_hash(file_content)
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
