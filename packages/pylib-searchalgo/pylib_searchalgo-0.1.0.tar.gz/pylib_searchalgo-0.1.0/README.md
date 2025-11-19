# pysearchalgo

Search & sort algorithms

## Installation

```bash
pip install pysearchalgo
```

## 💡 Usage Examples

### Basic Operations

```python
from pylib_searchalgo import binary_search, linear_search, quick_sort, merge_sort

# Binary search in sorted array
arr = [1, 3, 5, 7, 9]
index = binary_search(arr, 5)
# 2

# Linear search
index = linear_search([1, 2, 3, 4, 5], 3)
# 2

# Quick sort
sorted_arr = quick_sort([3, 1, 4, 1, 5])
# [1, 1, 3, 4, 5]

# Merge sort
sorted_arr = merge_sort([3, 1, 4, 1, 5])
# [1, 1, 3, 4, 5]
```

### AI/ML Use Cases

```python
from pylib_searchalgo import binary_search, linear_search, quick_sort, merge_sort

# Search sorted feature vectors
features = sorted([0.1, 0.5, 0.9, 0.3])
target_index = binary_search(features, 0.5)

# Sort training data
sorted_data = quick_sort(training_data, key=lambda x: x['score'])
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
