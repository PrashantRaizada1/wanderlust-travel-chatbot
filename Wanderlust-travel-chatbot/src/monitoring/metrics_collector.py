"""
Fail-safe MLflow metrics collector.
"""

import time
from functools import wraps

import mlflow


class MetricsCollector:
    """Collect application metrics when MLflow is active."""

    @staticmethod
    def _active() -> bool:
        return mlflow.active_run() is not None

    def track_latency(self, function):
        """Decorator that records function latency."""

        @wraps(function)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()

            try:
                return function(*args, **kwargs)
            finally:
                duration = (
                    time.perf_counter()
                    - start_time
                )

                if self._active():
                    mlflow.log_metric(
                        f"{function.__name__}_latency",
                        duration,
                    )

        return wrapper

    def log_token_usage(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str,
    ):
        """Log token counts within an active run."""
        if not self._active():
            return

        total_tokens = (
            prompt_tokens + completion_tokens
        )

        mlflow.log_metric(
            "prompt_tokens",
            prompt_tokens,
        )
        mlflow.log_metric(
            "completion_tokens",
            completion_tokens,
        )
        mlflow.log_metric(
            "total_tokens",
            total_tokens,
        )
        mlflow.log_param("model", model)

    def log_custom_metric(
        self,
        key: str,
        value: float,
    ):
        """Log a custom numerical metric."""
        if self._active():
            mlflow.log_metric(key, value)