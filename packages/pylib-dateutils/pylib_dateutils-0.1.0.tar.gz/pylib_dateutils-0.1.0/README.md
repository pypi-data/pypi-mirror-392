# pydateutils

Date helpers

## Installation

```bash
pip install pydateutils
```

## 💡 Usage Examples

### Basic Operations

```python
from pylib_dateutils import days_between, add_days, format_date

from datetime import datetime

# Calculate days between dates
date1 = datetime(2024, 1, 1)
date2 = datetime(2024, 1, 15)
days = days_between(date1, date2)
# 14

# Add days to date
new_date = add_days(date1, 10)
# datetime(2024, 1, 11)

# Format date
formatted = format_date(date1, "%Y-%m-%d")
# '2024-01-01'
```

### AI/ML Use Cases

```python
from pylib_dateutils import days_between, add_days, format_date

# Calculate training duration
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 1, 20)
training_days = days_between(start_date, end_date)

# Schedule next model evaluation
last_eval = datetime.now()
next_eval = add_days(last_eval, 7)  # Weekly evaluation
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
