"""Performance benchmarking and SLO monitoring for Flamehaven-Doc-Sanity.

This module provides Service Level Objective (SLO) definitions and
benchmarking capabilities to prevent performance degradation.
"""

import time
import warnings
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class PerformanceSLO:
    """Service Level Objective for component performance."""

    component: str
    max_latency_ms: float
    percentile: str = "P95"


class PerformanceBenchmark:
    """Benchmark wrapper to track and enforce SLOs.

    Usage:
        benchmark = PerformanceBenchmark(PerformanceBenchmark.SLO_DEEP_VALIDATOR)

        @benchmark.measure
        def validate_doc(content):
            return validator.validate(content)

        # Run operations
        for doc in documents:
            validate_doc(doc)

        # Verify SLO compliance
        assert benchmark.verify_slo()
    """

    # Defined SLOs for all components
    SLO_README_GENERATION = PerformanceSLO("readme_generator", 500.0)
    SLO_VALIDATOR_DEEP = PerformanceSLO("deep_validator", 150.0)
    SLO_VALIDATOR_SHALLOW = PerformanceSLO("shallow_validator", 50.0)
    SLO_FUSION_ORACLE = PerformanceSLO("fusion_oracle", 100.0)
    SLO_MODAL_ROUTER = PerformanceSLO("modal_router", 75.0)

    def __init__(self, slo: PerformanceSLO):
        """Initialize benchmark with SLO target.

        Args:
            slo: PerformanceSLO defining the target metrics
        """
        self.slo = slo
        self.measurements = []

    def measure(self, func: Callable) -> Callable:
        """Decorator to measure function latency.

        Args:
            func: Function to measure

        Returns:
            Wrapped function that tracks execution time
        """

        def wrapper(*args, **kwargs) -> Any:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration_ms = (time.perf_counter() - start) * 1000

            self.measurements.append(duration_ms)

            if duration_ms > self.slo.max_latency_ms:
                from flamehaven_doc_sanity.exceptions import PerformanceWarning

                warnings.warn(
                    f"{self.slo.component} exceeded SLO: "
                    f"{duration_ms:.1f}ms > {self.slo.max_latency_ms}ms",
                    category=PerformanceWarning,
                )

            return result

        return wrapper

    def get_percentile(self, p: int = 95) -> float:
        """Get Pth percentile latency.

        Uses linear interpolation method consistent with numpy.percentile
        for accurate percentile calculation.

        Args:
            p: Percentile to calculate (e.g., 95 for P95)

        Returns:
            Percentile latency in milliseconds
        """
        if not self.measurements:
            return 0.0

        sorted_measurements = sorted(self.measurements)
        n = len(sorted_measurements)

        # Use linear interpolation formula: rank = (p/100) * n - 1
        # This maps percentiles directly to array positions with interpolation
        rank = (p / 100.0) * n - 1

        # Clamp rank to valid range
        rank = max(0, min(rank, n - 1))

        # Get lower and upper indices
        lower_idx = int(rank)
        upper_idx = min(lower_idx + 1, n - 1)

        # Linear interpolation between the two values
        fraction = rank - lower_idx
        lower_value = sorted_measurements[lower_idx]
        upper_value = sorted_measurements[upper_idx]

        percentile = lower_value + fraction * (upper_value - lower_value)
        return percentile

    def verify_slo(self) -> bool:
        """Verify current measurements meet SLO.

        Returns:
            True if P95 latency is within SLO target
        """
        p95 = self.get_percentile(95)
        return p95 <= self.slo.max_latency_ms

    def get_statistics(self) -> dict:
        """Get performance statistics.

        Returns:
            Dict with min, max, mean, P50, P95, P99 statistics
        """
        if not self.measurements:
            return {
                "min": 0.0,
                "max": 0.0,
                "mean": 0.0,
                "p50": 0.0,
                "p95": 0.0,
                "p99": 0.0,
            }

        return {
            "min": min(self.measurements),
            "max": max(self.measurements),
            "mean": sum(self.measurements) / len(self.measurements),
            "p50": self.get_percentile(50),
            "p95": self.get_percentile(95),
            "p99": self.get_percentile(99),
        }


__all__ = [
    "PerformanceSLO",
    "PerformanceBenchmark",
]
