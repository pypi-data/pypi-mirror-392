#!/usr/bin/env python3
"""
Unified Observability Bridge
Connects all observability systems: prometheus_metrics, observability, telemetry
Ensures all metrics flow to all systems without duplication
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

# Import all observability systems
try:
    from .prometheus_metrics import get_prometheus_metrics
    PROMETHEUS_AVAILABLE = True
except ImportError:
    logger.warning("prometheus_metrics not available")
    PROMETHEUS_AVAILABLE = False

try:
    from .observability import ObservabilitySystem, ObservableEvent, EventType
    OBSERVABILITY_AVAILABLE = True
except ImportError:
    logger.warning("observability not available")
    OBSERVABILITY_AVAILABLE = False

try:
    from .telemetry import TelemetryManager
    TELEMETRY_AVAILABLE = True
except ImportError:
    logger.warning("telemetry not available")
    TELEMETRY_AVAILABLE = False


@dataclass
class MetricsContext:
    """Context for a single operation being measured"""
    operation_name: str
    user_id: str
    request_id: Optional[str] = None
    provider: Optional[str] = None
    metadata: Dict[str, Any] = None
    start_time: float = None

    def __post_init__(self):
        if self.start_time is None:
            self.start_time = time.time()
        if self.metadata is None:
            self.metadata = {}


class UnifiedObservability:
    """
    Unified observability system that bridges all metric collection systems

    Features:
    - Single API for recording metrics
    - Automatic propagation to Prometheus, Observability, Telemetry
    - Context management for timing operations
    - Graceful degradation if systems unavailable
    """

    def __init__(self):
        """Initialize unified observability system"""
        # Initialize all subsystems
        self.prometheus = get_prometheus_metrics() if PROMETHEUS_AVAILABLE else None
        self.observability = ObservabilitySystem() if OBSERVABILITY_AVAILABLE else None
        self.telemetry = TelemetryManager() if TELEMETRY_AVAILABLE else None

        # Tracking
        self.active_operations: Dict[str, MetricsContext] = {}

        logger.info(
            f"UnifiedObservability initialized: "
            f"prometheus={PROMETHEUS_AVAILABLE}, "
            f"observability={OBSERVABILITY_AVAILABLE}, "
            f"telemetry={TELEMETRY_AVAILABLE}"
        )

    def start_operation(
        self,
        operation_name: str,
        user_id: str = "default",
        request_id: Optional[str] = None,
        provider: Optional[str] = None,
        **metadata
    ) -> MetricsContext:
        """
        Start tracking an operation

        Returns context that should be passed to complete_operation()
        """
        ctx = MetricsContext(
            operation_name=operation_name,
            user_id=user_id,
            request_id=request_id,
            provider=provider,
            metadata=metadata,
            start_time=time.time()
        )

        # Track active operation
        op_key = f"{user_id}:{request_id or operation_name}"
        self.active_operations[op_key] = ctx

        # Prometheus: increment in_progress
        if self.prometheus and self.prometheus.enabled:
            self.prometheus.record_request_start()

        # Observability: record event
        if self.observability:
            event = ObservableEvent(
                event_type=EventType.REQUEST_STARTED,
                user_id=user_id,
                request_id=request_id,
                provider=provider,
                metadata=metadata
            )
            self.observability.record_event(event)

        return ctx

    def complete_operation(
        self,
        ctx: MetricsContext,
        success: bool = True,
        error: Optional[Exception] = None,
        result_metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Complete a tracked operation

        Args:
            ctx: Context returned from start_operation()
            success: Whether operation succeeded
            error: Exception if failed
            result_metadata: Additional metadata about the result
        """
        duration_seconds = time.time() - ctx.start_time
        duration_ms = duration_seconds * 1000

        # Remove from active operations
        op_key = f"{ctx.user_id}:{ctx.request_id or ctx.operation_name}"
        self.active_operations.pop(op_key, None)

        # Combine metadata
        combined_metadata = {**(ctx.metadata or {}), **(result_metadata or {})}
        if error:
            combined_metadata["error"] = str(error)
            combined_metadata["error_type"] = type(error).__name__

        # Prometheus: record metrics
        if self.prometheus and self.prometheus.enabled:
            self.prometheus.record_request_end()
            self.prometheus.record_request(
                user_id=ctx.user_id,
                duration_seconds=duration_seconds,
                success=success
            )

            if ctx.provider:
                self.prometheus.record_provider_request(
                    provider=ctx.provider,
                    duration_seconds=duration_seconds,
                    success=success,
                    error_type=combined_metadata.get("error_type") if not success else None
                )

        # Observability: record completion event
        if self.observability:
            event_type = EventType.REQUEST_COMPLETED if success else EventType.REQUEST_FAILED
            event = ObservableEvent(
                event_type=event_type,
                user_id=ctx.user_id,
                request_id=ctx.request_id,
                duration_ms=duration_ms,
                status="success" if success else "failure",
                provider=ctx.provider,
                error_message=str(error) if error else None,
                metadata=combined_metadata
            )
            self.observability.record_event(event)

            # Update provider metrics if provider specified
            if ctx.provider:
                provider_metrics = self.observability.provider_metrics.get(ctx.provider)
                if not provider_metrics:
                    from .observability import ProviderMetrics
                    provider_metrics = ProviderMetrics(provider_name=ctx.provider)
                    self.observability.provider_metrics[ctx.provider] = provider_metrics

                if success:
                    provider_metrics.record_success(duration_ms)
                else:
                    provider_metrics.record_failure(
                        error_type=combined_metadata.get("error_type", "unknown"),
                        latency_ms=duration_ms
                    )

        # Telemetry: record if available
        if self.telemetry:
            try:
                self.telemetry.track_request(
                    request=ctx,
                    success=success,
                    extra=combined_metadata
                )
            except Exception as e:
                logger.warning(f"Failed to record telemetry: {e}")

    def record_retry(self, reason: str, success: bool):
        """Record a retry attempt"""
        if self.prometheus and self.prometheus.enabled:
            self.prometheus.record_retry_attempt(reason=reason, success=success)

        if self.observability:
            event = ObservableEvent(
                event_type=EventType.REQUEST_FAILED if not success else EventType.REQUEST_COMPLETED,
                metadata={"retry_reason": reason, "retry_success": success}
            )
            self.observability.record_event(event)

    def record_rate_limit(self, user_id: str):
        """Record a rate limit hit"""
        if self.prometheus and self.prometheus.enabled:
            self.prometheus.record_rate_limit_hit(user_id=user_id)

        if self.observability:
            self.observability.counters["rate_limits"] += 1
            event = ObservableEvent(
                event_type=EventType.RATE_LIMIT_HIT,
                user_id=user_id
            )
            self.observability.record_event(event)

    def record_circuit_breaker_trip(self, provider: str):
        """Record circuit breaker opening"""
        if self.prometheus and self.prometheus.enabled:
            self.prometheus.record_circuit_breaker_trip(provider=provider)

        if self.observability:
            self.observability.counters["circuit_breaks"] += 1
            event = ObservableEvent(
                event_type=EventType.CIRCUIT_BREAKER_STATE_CHANGE,
                provider=provider,
                metadata={"state": "open"}
            )
            self.observability.record_event(event)

    def update_circuit_breaker_state(self, provider: str, state: str):
        """Update circuit breaker state"""
        if self.prometheus and self.prometheus.enabled:
            self.prometheus.update_circuit_breaker_state(provider=provider, state=state)

        if self.observability:
            event = ObservableEvent(
                event_type=EventType.CIRCUIT_BREAKER_STATE_CHANGE,
                provider=provider,
                metadata={"state": state}
            )
            self.observability.record_event(event)

    def record_queue_rejection(self):
        """Record a queue rejection"""
        if self.prometheus and self.prometheus.enabled:
            self.prometheus.record_queue_rejection()

        if self.observability:
            event = ObservableEvent(event_type=EventType.QUEUE_FULL)
            self.observability.record_event(event)

    def update_queue_depth(self, depth: int):
        """Update current queue depth"""
        if self.prometheus and self.prometheus.enabled:
            self.prometheus.update_queue_depth(depth=depth)

    def update_memory_usage(self, bytes_used: int):
        """Update current memory usage"""
        if self.prometheus and self.prometheus.enabled:
            self.prometheus.update_memory_usage(bytes_used=bytes_used)

    def record_session_archived(self, message_count: int):
        """Record session archival"""
        if self.prometheus and self.prometheus.enabled:
            self.prometheus.record_session_archived_messages(count=message_count)

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics from all systems"""
        stats = {
            "active_operations": len(self.active_operations),
        }

        if self.prometheus and self.prometheus.enabled:
            stats["prometheus"] = self.prometheus.get_stats() if hasattr(self.prometheus, 'get_stats') else {"enabled": True}

        if self.observability:
            stats["observability"] = {
                "total_events": len(self.observability.events),
                "counters": self.observability.counters,
                "provider_count": len(self.observability.provider_metrics)
            }

        return stats

    async def __aenter__(self):
        """Async context manager support"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on exit"""
        # Flush any pending data
        if self.observability:
            try:
                self.observability.flush()
            except:
                pass


# Global singleton
_global_unified_observability: Optional[UnifiedObservability] = None


def get_unified_observability() -> UnifiedObservability:
    """Get global unified observability instance"""
    global _global_unified_observability

    if _global_unified_observability is None:
        _global_unified_observability = UnifiedObservability()

    return _global_unified_observability


# Convenience decorator for automatic operation tracking
def track_operation(operation_name: str, provider: Optional[str] = None):
    """
    Decorator to automatically track operation metrics

    Usage:
        @track_operation("api_call", provider="openai")
        async def call_api(user_id: str):
            # Your code here
            pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            obs = get_unified_observability()

            # Try to extract user_id from args/kwargs
            user_id = kwargs.get('user_id', 'default')
            if not user_id and args and hasattr(args[0], 'user_id'):
                user_id = args[0].user_id

            ctx = obs.start_operation(
                operation_name=operation_name,
                user_id=user_id,
                provider=provider
            )

            try:
                result = await func(*args, **kwargs)
                obs.complete_operation(ctx, success=True)
                return result
            except Exception as e:
                obs.complete_operation(ctx, success=False, error=e)
                raise

        return wrapper
    return decorator
