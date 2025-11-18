# Flask-QueryMonitor

Detects N+1 queries and slow database operations in Flask apps.

## What it does

- Warns when >20 queries in single request (potential N+1)
- Logs queries slower than threshold (default: 100ms)
- Adds `X-Query-Count` and `X-Query-Time-Ms` response headers
- Uses SQLAlchemy event listeners

Built while working on [wallmarkets](https://wallmarkets.store).

## Installation

```bash
pip install flask-querymonitor
```

## Usage

```python
from flask import Flask
from flask_querymonitor import QueryMonitor

app = Flask(__name__)
app.config['QUERY_MONITORING_ENABLED'] = True
app.config['SLOW_QUERY_THRESHOLD_MS'] = 100

monitor = QueryMonitor(app)
```

## What it logs

```
WARNING: HIGH QUERY COUNT: /products - 47 queries in 823ms - Potential N+1!
WARNING: SLOW QUERY (234ms): SELECT * FROM products WHERE ...
```

## Response headers (in debug mode)

```
X-Query-Count: 12
X-Query-Time-Ms: 145.23
```

## Configuration

```python
app.config['QUERY_MONITORING_ENABLED'] = True  # Enable monitoring
app.config['SLOW_QUERY_THRESHOLD_MS'] = 100    # Log if >100ms
```

## License

MIT

## Contributing

Pull requests welcome. Please add tests.
