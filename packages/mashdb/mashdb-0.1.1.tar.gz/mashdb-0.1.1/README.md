# MashDB

A lightweight Python interface for database operations with JSON support.

## Features

- Simple and intuitive query interface
- JSON output support
- Easy integration with Python applications

## Installation

```bash
pip install mashdb
```

## Usage

```python
from mashdb import query

# Execute a simple query
result = query("SELECT * FROM your_table;")

# Get results as JSON
result_json = query("SELECT * FROM your_table;", as_json=True)
```

## License

MIT - See [LICENSE](LICENSE) for more information.