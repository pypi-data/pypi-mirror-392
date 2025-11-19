# pydaterange

Date ranges

## Installation

```bash
pip install pydaterange
```

## 💡 Usage Examples

### Basic Operations

```python
from pylib_daterange import DateRange

from datetime import datetime

# Create date range
start = datetime(2024, 1, 1)
end = datetime(2024, 1, 31)
date_range = DateRange(start, end)

# Check if date is in range
date_range.contains(datetime(2024, 1, 15))
# True
```

### AI/ML Use Cases

```python
from pylib_daterange import DateRange

# Filter training data by date range
training_range = DateRange(start_date, end_date)
filtered_data = [d for d in data if training_range.contains(d['date'])]
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
