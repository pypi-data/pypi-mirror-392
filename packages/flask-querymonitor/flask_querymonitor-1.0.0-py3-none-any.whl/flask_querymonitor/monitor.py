"""
Database query monitoring.

Tracks query count and execution time per request.
Logs slow queries and detects potential N+1 patterns.
"""

import logging
import time
from flask import g, request
from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


class QueryMonitor:
    """Monitor database queries."""

    def __init__(self, app=None):
        self.enabled = False
        self.slow_query_threshold_ms = 100
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize query monitoring."""
        self.enabled = app.config.get("QUERY_MONITORING_ENABLED", False)
        self.slow_query_threshold_ms = app.config.get("SLOW_QUERY_THRESHOLD_MS", 100)

        if not self.enabled:
            return

        @app.before_request
        def before_request():
            g.query_count = 0
            g.query_start_time = time.time()
            g.queries = []

        @app.after_request
        def after_request(response):
            if hasattr(g, "query_count"):
                duration = (time.time() - g.query_start_time) * 1000

                if g.query_count > 20:
                    logger.warning(
                        f"HIGH QUERY COUNT: {request.path} - "
                        f"{g.query_count} queries in {duration:.2f}ms - "
                        f"Potential N+1 detected!"
                    )
                elif g.query_count > 10:
                    logger.info(
                        f"Moderate query count: {request.path} - "
                        f"{g.query_count} queries in {duration:.2f}ms"
                    )

                if app.debug:
                    response.headers["X-Query-Count"] = str(g.query_count)
                    response.headers["X-Query-Time-Ms"] = f"{duration:.2f}"

            return response

        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault("query_start_time", []).append(time.time())
            if hasattr(g, "query_count"):
                g.query_count += 1

        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total_time = (time.time() - conn.info["query_start_time"].pop()) * 1000

            if total_time > self.slow_query_threshold_ms:
                query_display = statement[:200]
                if len(statement) > 200:
                    query_display += "..."

                logger.warning(f"SLOW QUERY ({total_time:.2f}ms): {query_display}")

            if hasattr(g, "queries"):
                g.queries.append({
                    "statement": statement,
                    "time_ms": total_time,
                    "params": parameters
                })


query_monitor = QueryMonitor()


def init_query_monitoring(app):
    """Initialize query monitoring."""
    query_monitor.init_app(app)
    logger.info(f"Query monitoring {'enabled' if query_monitor.enabled else 'disabled'}")


def get_request_query_stats():
    """Get query stats for current request."""
    if not hasattr(g, "queries"):
        return {"count": 0, "total_time_ms": 0, "slow_queries": []}

    slow_queries = [
        q for q in g.queries
        if q["time_ms"] > query_monitor.slow_query_threshold_ms
    ]

    total_time = sum(q["time_ms"] for q in g.queries)

    return {
        "count": len(g.queries),
        "total_time_ms": total_time,
        "slow_queries": slow_queries,
        "queries": g.queries if query_monitor.enabled else []
    }
