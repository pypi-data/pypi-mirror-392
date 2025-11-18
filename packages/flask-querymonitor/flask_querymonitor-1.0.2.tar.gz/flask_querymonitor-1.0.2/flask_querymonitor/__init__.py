"""
Flask-QueryMonitor
==================

Detects N+1 queries and slow database operations.

Usage:
    from flask import Flask
    from flask_querymonitor import QueryMonitor

    app = Flask(__name__)
    app.config['QUERY_MONITORING_ENABLED'] = True
    app.config['SLOW_QUERY_THRESHOLD_MS'] = 100

    monitor = QueryMonitor(app)
"""

__version__ = "1.0.0"

from .monitor import QueryMonitor, init_query_monitoring, get_request_query_stats

__all__ = ["QueryMonitor", "init_query_monitoring", "get_request_query_stats"]
