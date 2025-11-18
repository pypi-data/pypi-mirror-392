#!/usr/bin/env python3
"""
Timeout and Retry Handler for Cite-Agent
Provides intelligent retry logic with exponential backoff for timeout and transient failures
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar, Coroutine
import aiohttp

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryReason(Enum):
    """Reasons for retry"""
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    HTTP_503 = "http_503"
    HTTP_429 = "http_429"
    HTTP_500 = "http_500"
    HTTP_502 = "http_502"
    HTTP_504 = "http_504"
    RATE_LIMIT = "rate_limit"
    TRANSIENT_ERROR = "transient_error"


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0
    exponential_base: float = 2.0
    timeout_seconds: float = 60.0
    jitter_enabled: bool = True
    jitter_max_seconds: float = 1.0

    # Which HTTP status codes should trigger retry
    retryable_status_codes: List[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])

    # Which exception types should trigger retry
    retryable_exceptions: List[type] = field(default_factory=lambda: [
        asyncio.TimeoutError,
        aiohttp.ClientError,
        ConnectionError,
    ])


@dataclass
class RetryAttempt:
    """Information about a retry attempt"""
    attempt_number: int
    reason: RetryReason
    delay_seconds: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: Optional[str] = None
    http_status: Optional[int] = None


@dataclass
class RetryResult:
    """Result of retry operation"""
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    attempts: List[RetryAttempt] = field(default_factory=list)
    total_duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/metrics"""
        return {
            "success": self.success,
            "total_attempts": len(self.attempts),
            "total_duration_seconds": self.total_duration_seconds,
            "error": str(self.error) if self.error else None,
            "attempts": [
                {
                    "attempt": a.attempt_number,
                    "reason": a.reason.value,
                    "delay": a.delay_seconds,
                    "timestamp": a.timestamp.isoformat(),
                    "error": a.error_message,
                    "http_status": a.http_status
                }
                for a in self.attempts
            ]
        }


class TimeoutRetryHandler:
    """
    Intelligent retry handler for timeout and transient failures

    Features:
    - Exponential backoff with configurable parameters
    - Jitter to prevent thundering herd
    - Different strategies for different failure types
    - Metrics collection for retry attempts
    - Integration with circuit breaker pattern
    """

    def __init__(self, config: Optional[RetryConfig] = None):
        """
        Initialize timeout retry handler

        Args:
            config: Retry configuration (uses defaults if not provided)
        """
        self.config = config or RetryConfig()

        # Metrics
        self.total_retries = 0
        self.successful_retries = 0
        self.failed_retries = 0
        self.retry_by_reason: Dict[RetryReason, int] = {reason: 0 for reason in RetryReason}

        logger.info(
            f"TimeoutRetryHandler initialized: "
            f"max_attempts={self.config.max_attempts}, "
            f"initial_delay={self.config.initial_delay_seconds}s, "
            f"max_delay={self.config.max_delay_seconds}s"
        )

    def _classify_error(
        self,
        error: Exception,
        http_status: Optional[int] = None
    ) -> Optional[RetryReason]:
        """
        Classify an error to determine if it's retryable and why

        Args:
            error: The exception that occurred
            http_status: HTTP status code if applicable

        Returns:
            RetryReason if retryable, None otherwise
        """
        # Check HTTP status codes first
        if http_status:
            if http_status == 429:
                return RetryReason.HTTP_429
            elif http_status == 500:
                return RetryReason.HTTP_500
            elif http_status == 502:
                return RetryReason.HTTP_502
            elif http_status == 503:
                return RetryReason.HTTP_503
            elif http_status == 504:
                return RetryReason.HTTP_504
            elif http_status in self.config.retryable_status_codes:
                return RetryReason.TRANSIENT_ERROR

        # Check exception types
        if isinstance(error, asyncio.TimeoutError):
            return RetryReason.TIMEOUT
        elif isinstance(error, aiohttp.ClientError):
            error_str = str(error).lower()
            if 'timeout' in error_str:
                return RetryReason.TIMEOUT
            elif 'rate limit' in error_str or '429' in error_str:
                return RetryReason.RATE_LIMIT
            else:
                return RetryReason.CONNECTION_ERROR
        elif isinstance(error, ConnectionError):
            return RetryReason.CONNECTION_ERROR
        elif any(isinstance(error, exc_type) for exc_type in self.config.retryable_exceptions):
            return RetryReason.TRANSIENT_ERROR

        return None  # Not retryable

    def _calculate_delay(
        self,
        attempt_number: int,
        reason: RetryReason
    ) -> float:
        """
        Calculate delay before next retry using exponential backoff

        Args:
            attempt_number: Current attempt number (1-indexed)
            reason: Reason for retry

        Returns:
            Delay in seconds
        """
        # Base exponential backoff
        delay = self.config.initial_delay_seconds * (
            self.config.exponential_base ** (attempt_number - 1)
        )

        # Cap at max delay
        delay = min(delay, self.config.max_delay_seconds)

        # For rate limits, use longer delays
        if reason in [RetryReason.HTTP_429, RetryReason.RATE_LIMIT]:
            delay = delay * 2

        # Add jitter to prevent thundering herd
        if self.config.jitter_enabled:
            import random
            jitter = random.uniform(0, min(self.config.jitter_max_seconds, delay * 0.1))
            delay += jitter

        return delay

    async def execute_with_retry(
        self,
        operation: Callable[[], Coroutine[Any, Any, T]],
        operation_name: str = "operation",
        custom_timeout: Optional[float] = None,
        custom_max_attempts: Optional[int] = None
    ) -> RetryResult:
        """
        Execute an async operation with automatic retry on failure

        Args:
            operation: Async function to execute
            operation_name: Name for logging purposes
            custom_timeout: Override default timeout for this operation
            custom_max_attempts: Override max attempts for this operation

        Returns:
            RetryResult with success status and result/error
        """
        max_attempts = custom_max_attempts or self.config.max_attempts
        timeout = custom_timeout or self.config.timeout_seconds

        result = RetryResult(success=False)
        start_time = time.time()

        for attempt_num in range(1, max_attempts + 1):
            try:
                logger.debug(
                    f"Executing {operation_name} (attempt {attempt_num}/{max_attempts})"
                )

                # Execute with timeout
                operation_result = await asyncio.wait_for(
                    operation(),
                    timeout=timeout
                )

                # Success!
                result.success = True
                result.result = operation_result
                self.total_retries += (attempt_num - 1)
                if attempt_num > 1:
                    self.successful_retries += 1
                    logger.info(
                        f"{operation_name} succeeded on attempt {attempt_num}/{max_attempts}"
                    )

                break

            except Exception as error:
                # Classify error
                http_status = None
                if isinstance(error, aiohttp.ClientResponseError):
                    http_status = error.status

                retry_reason = self._classify_error(error, http_status)

                # Not retryable or last attempt
                if retry_reason is None or attempt_num >= max_attempts:
                    result.error = error
                    self.total_retries += attempt_num
                    self.failed_retries += 1

                    logger.error(
                        f"{operation_name} failed after {attempt_num} attempts: {error}"
                    )

                    # Record final attempt
                    result.attempts.append(RetryAttempt(
                        attempt_number=attempt_num,
                        reason=retry_reason or RetryReason.TRANSIENT_ERROR,
                        delay_seconds=0,
                        error_message=str(error),
                        http_status=http_status
                    ))

                    break

                # Retryable - calculate delay and retry
                delay = self._calculate_delay(attempt_num, retry_reason)

                # Record attempt
                attempt = RetryAttempt(
                    attempt_number=attempt_num,
                    reason=retry_reason,
                    delay_seconds=delay,
                    error_message=str(error),
                    http_status=http_status
                )
                result.attempts.append(attempt)

                # Update metrics
                self.retry_by_reason[retry_reason] = self.retry_by_reason.get(retry_reason, 0) + 1

                logger.warning(
                    f"{operation_name} failed (attempt {attempt_num}/{max_attempts}): "
                    f"{retry_reason.value} - {error}. "
                    f"Retrying in {delay:.2f}s..."
                )

                # Wait before retry
                await asyncio.sleep(delay)

        result.total_duration_seconds = time.time() - start_time

        return result

    async def execute_with_fallback(
        self,
        primary_operation: Callable[[], Coroutine[Any, Any, T]],
        fallback_operation: Callable[[], Coroutine[Any, Any, T]],
        operation_name: str = "operation"
    ) -> RetryResult:
        """
        Execute primary operation with retry, fall back to fallback on failure

        Args:
            primary_operation: Primary async function to try
            fallback_operation: Fallback async function if primary fails
            operation_name: Name for logging

        Returns:
            RetryResult from primary or fallback
        """
        # Try primary with retry
        primary_result = await self.execute_with_retry(
            primary_operation,
            operation_name=f"{operation_name} (primary)"
        )

        if primary_result.success:
            return primary_result

        # Primary failed, try fallback
        logger.info(f"{operation_name} primary failed, trying fallback...")

        fallback_result = await self.execute_with_retry(
            fallback_operation,
            operation_name=f"{operation_name} (fallback)",
            custom_max_attempts=1  # Only try fallback once
        )

        # Combine attempt history
        fallback_result.attempts = primary_result.attempts + fallback_result.attempts
        fallback_result.total_duration_seconds += primary_result.total_duration_seconds

        return fallback_result

    def get_stats(self) -> Dict[str, Any]:
        """Get retry handler statistics"""
        success_rate = 0.0
        if self.total_retries > 0:
            success_rate = self.successful_retries / self.total_retries

        return {
            "total_retries": self.total_retries,
            "successful_retries": self.successful_retries,
            "failed_retries": self.failed_retries,
            "success_rate": success_rate,
            "retry_by_reason": {
                reason.value: count
                for reason, count in self.retry_by_reason.items()
                if count > 0
            },
            "config": {
                "max_attempts": self.config.max_attempts,
                "initial_delay": self.config.initial_delay_seconds,
                "max_delay": self.config.max_delay_seconds,
                "timeout": self.config.timeout_seconds
            }
        }

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"TimeoutRetryHandler("
            f"retries={self.total_retries}, "
            f"success_rate={self.successful_retries / max(1, self.total_retries):.2%})"
        )


# Global singleton for easy access
_global_retry_handler: Optional[TimeoutRetryHandler] = None


def get_retry_handler(config: Optional[RetryConfig] = None) -> TimeoutRetryHandler:
    """Get global retry handler instance"""
    global _global_retry_handler

    if _global_retry_handler is None:
        _global_retry_handler = TimeoutRetryHandler(config=config)

    return _global_retry_handler
