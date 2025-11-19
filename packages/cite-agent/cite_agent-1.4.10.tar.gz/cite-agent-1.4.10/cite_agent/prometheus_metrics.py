#!/usr/bin/env python3
"""
Prometheus Metrics Exporter for Cite-Agent
Exports metrics in Prometheus format for monitoring and alerting
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Try to import prometheus_client, fallback gracefully if not available
try:
    from prometheus_client import (
        Counter, Gauge, Histogram, Summary, Info,
        CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    logger.warning("prometheus_client not installed. Metrics export disabled. Install with: pip install prometheus-client")
    PROMETHEUS_AVAILABLE = False


class PrometheusMetrics:
    """
    Prometheus metrics collector for Cite-Agent

    Exports metrics for:
    - Request counts (total, success, failure)
    - Request latency (histogram)
    - Queue depth
    - Circuit breaker state
    - Memory usage
    - Provider performance
    - Session metrics
    """

    def __init__(self, registry: Optional['CollectorRegistry'] = None):
        """
        Initialize Prometheus metrics

        Args:
            registry: Custom registry (uses default if None)
        """
        if not PROMETHEUS_AVAILABLE:
            logger.warning("Prometheus metrics disabled (library not available)")
            self.enabled = False
            return

        self.enabled = True
        self.registry = registry or CollectorRegistry()

        # Request metrics
        self.requests_total = Counter(
            'cite_agent_requests_total',
            'Total number of requests processed',
            ['user_id', 'status'],
            registry=self.registry
        )

        self.requests_duration_seconds = Histogram(
            'cite_agent_requests_duration_seconds',
            'Request duration in seconds',
            ['user_id', 'status'],
            buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
            registry=self.registry
        )

        self.requests_in_progress = Gauge(
            'cite_agent_requests_in_progress',
            'Number of requests currently in progress',
            registry=self.registry
        )

        # Queue metrics
        self.queue_depth = Gauge(
            'cite_agent_queue_depth',
            'Current number of requests in queue',
            registry=self.registry
        )

        self.queue_rejections_total = Counter(
            'cite_agent_queue_rejections_total',
            'Total number of requests rejected due to full queue',
            registry=self.registry
        )

        # Circuit breaker metrics
        self.circuit_breaker_state = Gauge(
            'cite_agent_circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=half-open, 2=open)',
            ['provider'],
            registry=self.registry
        )

        self.circuit_breaker_trips_total = Counter(
            'cite_agent_circuit_breaker_trips_total',
            'Total number of circuit breaker trips',
            ['provider'],
            registry=self.registry
        )

        # Provider metrics
        self.provider_requests_total = Counter(
            'cite_agent_provider_requests_total',
            'Total requests per provider',
            ['provider', 'status'],
            registry=self.registry
        )

        self.provider_latency_seconds = Histogram(
            'cite_agent_provider_latency_seconds',
            'Provider response latency',
            ['provider'],
            buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
            registry=self.registry
        )

        self.provider_errors_total = Counter(
            'cite_agent_provider_errors_total',
            'Total provider errors',
            ['provider', 'error_type'],
            registry=self.registry
        )

        # Memory metrics
        self.memory_usage_bytes = Gauge(
            'cite_agent_memory_usage_bytes',
            'Current memory usage in bytes',
            registry=self.registry
        )

        self.conversation_history_size = Gauge(
            'cite_agent_conversation_history_size',
            'Number of messages in conversation history',
            ['user_id'],
            registry=self.registry
        )

        self.session_archived_messages_total = Counter(
            'cite_agent_session_archived_messages_total',
            'Total messages archived',
            registry=self.registry
        )

        # Rate limit metrics
        self.rate_limit_hits_total = Counter(
            'cite_agent_rate_limit_hits_total',
            'Total rate limit hits',
            ['user_id'],
            registry=self.registry
        )

        # Retry metrics
        self.retry_attempts_total = Counter(
            'cite_agent_retry_attempts_total',
            'Total retry attempts',
            ['reason', 'success'],
            registry=self.registry
        )

        # System info
        self.info = Info(
            'cite_agent',
            'Cite-Agent system information',
            registry=self.registry
        )
        self.info.info({
            'version': '1.4.10',
            'name': 'cite-agent'
        })

        logger.info("Prometheus metrics initialized successfully")

    def record_request(
        self,
        user_id: str,
        duration_seconds: float,
        success: bool
    ):
        """Record a completed request"""
        if not self.enabled:
            return

        status = 'success' if success else 'failure'
        self.requests_total.labels(user_id=user_id, status=status).inc()
        self.requests_duration_seconds.labels(user_id=user_id, status=status).observe(duration_seconds)

    def record_request_start(self):
        """Record request starting"""
        if not self.enabled:
            return
        self.requests_in_progress.inc()

    def record_request_end(self):
        """Record request ending"""
        if not self.enabled:
            return
        self.requests_in_progress.dec()

    def update_queue_depth(self, depth: int):
        """Update current queue depth"""
        if not self.enabled:
            return
        self.queue_depth.set(depth)

    def record_queue_rejection(self):
        """Record a queue rejection"""
        if not self.enabled:
            return
        self.queue_rejections_total.inc()

    def update_circuit_breaker_state(self, provider: str, state: str):
        """
        Update circuit breaker state

        Args:
            provider: Provider name
            state: 'closed', 'half_open', or 'open'
        """
        if not self.enabled:
            return

        state_value = {
            'closed': 0,
            'half_open': 1,
            'open': 2
        }.get(state, 0)

        self.circuit_breaker_state.labels(provider=provider).set(state_value)

    def record_circuit_breaker_trip(self, provider: str):
        """Record a circuit breaker trip"""
        if not self.enabled:
            return
        self.circuit_breaker_trips_total.labels(provider=provider).inc()

    def record_provider_request(
        self,
        provider: str,
        duration_seconds: float,
        success: bool,
        error_type: Optional[str] = None
    ):
        """Record a provider request"""
        if not self.enabled:
            return

        status = 'success' if success else 'failure'
        self.provider_requests_total.labels(provider=provider, status=status).inc()
        self.provider_latency_seconds.labels(provider=provider).observe(duration_seconds)

        if not success and error_type:
            self.provider_errors_total.labels(provider=provider, error_type=error_type).inc()

    def update_memory_usage(self, bytes_used: int):
        """Update current memory usage"""
        if not self.enabled:
            return
        self.memory_usage_bytes.set(bytes_used)

    def update_conversation_history_size(self, user_id: str, size: int):
        """Update conversation history size"""
        if not self.enabled:
            return
        self.conversation_history_size.labels(user_id=user_id).set(size)

    def record_session_archived_messages(self, count: int):
        """Record messages archived"""
        if not self.enabled:
            return
        self.session_archived_messages_total.inc(count)

    def record_rate_limit_hit(self, user_id: str):
        """Record a rate limit hit"""
        if not self.enabled:
            return
        self.rate_limit_hits_total.labels(user_id=user_id).inc()

    def record_retry_attempt(self, reason: str, success: bool):
        """Record a retry attempt"""
        if not self.enabled:
            return
        success_str = 'success' if success else 'failure'
        self.retry_attempts_total.labels(reason=reason, success=success_str).inc()

    def generate_metrics(self) -> bytes:
        """Generate metrics in Prometheus format"""
        if not self.enabled:
            return b"# Prometheus metrics disabled (library not available)\n"

        return generate_latest(self.registry)

    def get_content_type(self) -> str:
        """Get content type for metrics endpoint"""
        if not self.enabled:
            return "text/plain"
        return CONTENT_TYPE_LATEST


# Global singleton
_global_prometheus_metrics: Optional[PrometheusMetrics] = None


def get_prometheus_metrics() -> PrometheusMetrics:
    """Get global Prometheus metrics instance"""
    global _global_prometheus_metrics

    if _global_prometheus_metrics is None:
        _global_prometheus_metrics = PrometheusMetrics()

    return _global_prometheus_metrics


def create_metrics_endpoint_handler():
    """
    Create a simple HTTP handler for the /metrics endpoint

    Returns a function that can be used as an HTTP handler
    """
    metrics = get_prometheus_metrics()

    def metrics_handler():
        """HTTP handler for /metrics endpoint"""
        return {
            'content': metrics.generate_metrics(),
            'content_type': metrics.get_content_type()
        }

    return metrics_handler


# Flask integration (if Flask is available)
try:
    from flask import Response

    def create_flask_metrics_route():
        """Create a Flask route handler for /metrics"""
        metrics = get_prometheus_metrics()

        def metrics_route():
            return Response(
                metrics.generate_metrics(),
                mimetype=metrics.get_content_type()
            )

        return metrics_route

except ImportError:
    def create_flask_metrics_route():
        logger.warning("Flask not available, cannot create Flask metrics route")
        return None


# FastAPI integration (if FastAPI is available)
try:
    from fastapi import Response as FastAPIResponse

    def create_fastapi_metrics_route():
        """Create a FastAPI route handler for /metrics"""
        metrics = get_prometheus_metrics()

        async def metrics_route():
            return FastAPIResponse(
                content=metrics.generate_metrics(),
                media_type=metrics.get_content_type()
            )

        return metrics_route

except ImportError:
    def create_fastapi_metrics_route():
        logger.warning("FastAPI not available, cannot create FastAPI metrics route")
        return None
