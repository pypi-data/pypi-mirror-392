# pytzconvert

Timezone conversion

## Installation

```bash
pip install pytzconvert
```

## 💡 Usage Examples

### Basic Operations

```python
from pylib_tzconvert import convert_timezone

from datetime import datetime

# Convert timezone
dt = datetime(2024, 1, 1, 12, 0)
converted = convert_timezone(dt, "UTC", "America/New_York")
# Converted datetime
```

### AI/ML Use Cases

```python
from pylib_tzconvert import convert_timezone

# Normalize timestamps for ML
normalized = convert_timezone(timestamp, source_tz, "UTC")
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
