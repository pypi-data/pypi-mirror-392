"""
Metrics collection and export for the Rust Crate Pipeline.

Provides Prometheus-compatible metrics for monitoring pipeline health,
performance, and trust decisions.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    from prometheus_client import Counter, Gauge, Histogram, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    Counter = None
    Gauge = None
    Histogram = None
    generate_latest = None

logger = logging.getLogger(__name__)


@dataclass
class PipelineMetrics:
    """Metrics for pipeline operations."""

    crates_processed: int = 0
    crates_allowed: int = 0
    crates_denied: int = 0
    crates_flagged: int = 0
    crates_deferred: int = 0
    api_errors: int = 0
    scraping_errors: int = 0
    analysis_errors: int = 0
    average_quality_score: float = 0.0
    total_processing_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    ml_predictions_made: int = 0
    llm_calls: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "crates_processed": self.crates_processed,
            "crates_allowed": self.crates_allowed,
            "crates_denied": self.crates_denied,
            "crates_flagged": self.crates_flagged,
            "crates_deferred": self.crates_deferred,
            "api_errors": self.api_errors,
            "scraping_errors": self.scraping_errors,
            "analysis_errors": self.analysis_errors,
            "average_quality_score": self.average_quality_score,
            "total_processing_time": self.total_processing_time,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "ml_predictions_made": self.ml_predictions_made,
            "llm_calls": self.llm_calls,
        }


class MetricsCollector:
    """Collects and exports pipeline metrics."""

    def __init__(self, enable_prometheus: bool = True):
        """Initialize metrics collector."""
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE
        self.metrics = PipelineMetrics()
        self.quality_scores: List[float] = []
        self.processing_times: List[float] = []

        # Initialize Prometheus metrics if available
        if self.enable_prometheus:
            self._init_prometheus_metrics()
        else:
            logger.warning("Prometheus not available, using basic metrics collection")

    def _init_prometheus_metrics(self) -> None:
        """Initialize Prometheus metrics."""
        if not PROMETHEUS_AVAILABLE:
            return

        self.crates_processed_counter = Counter(
            "rust_crate_pipeline_crates_processed_total",
            "Total number of crates processed",
        )
        self.crates_allowed_counter = Counter(
            "rust_crate_pipeline_crates_allowed_total",
            "Total number of crates allowed",
        )
        self.crates_denied_counter = Counter(
            "rust_crate_pipeline_crates_denied_total",
            "Total number of crates denied",
        )
        self.crates_flagged_counter = Counter(
            "rust_crate_pipeline_crates_flagged_total",
            "Total number of crates flagged",
        )
        self.crates_deferred_counter = Counter(
            "rust_crate_pipeline_crates_deferred_total",
            "Total number of crates deferred",
        )
        self.api_errors_counter = Counter(
            "rust_crate_pipeline_api_errors_total",
            "Total number of API errors",
        )
        self.quality_score_gauge = Gauge(
            "rust_crate_pipeline_average_quality_score",
            "Average quality score of processed crates",
        )
        self.processing_time_histogram = Histogram(
            "rust_crate_pipeline_processing_time_seconds",
            "Time taken to process a crate",
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0],
        )
        self.cache_hits_counter = Counter(
            "rust_crate_pipeline_cache_hits_total",
            "Total number of cache hits",
        )
        self.cache_misses_counter = Counter(
            "rust_crate_pipeline_cache_misses_total",
            "Total number of cache misses",
        )

    def record_crate_processed(
        self, verdict: str, quality_score: float, processing_time: float
    ) -> None:
        """Record a processed crate."""
        self.metrics.crates_processed += 1
        self.quality_scores.append(quality_score)
        self.processing_times.append(processing_time)

        # Update average quality score
        self.metrics.average_quality_score = sum(self.quality_scores) / len(
            self.quality_scores
        )
        self.metrics.total_processing_time += processing_time

        # Update verdict counters
        if verdict == "ALLOW":
            self.metrics.crates_allowed += 1
            if self.enable_prometheus:
                self.crates_allowed_counter.inc()
        elif verdict == "DENY":
            self.metrics.crates_denied += 1
            if self.enable_prometheus:
                self.crates_denied_counter.inc()
        elif verdict == "FLAG":
            self.metrics.crates_flagged += 1
            if self.enable_prometheus:
                self.crates_flagged_counter.inc()
        elif verdict == "DEFER":
            self.metrics.crates_deferred += 1
            if self.enable_prometheus:
                self.crates_deferred_counter.inc()

        # Update Prometheus metrics
        if self.enable_prometheus:
            self.crates_processed_counter.inc()
            self.quality_score_gauge.set(self.metrics.average_quality_score)
            self.processing_time_histogram.observe(processing_time)

    def record_error(self, error_type: str) -> None:
        """Record an error."""
        if error_type == "api":
            self.metrics.api_errors += 1
            if self.enable_prometheus:
                self.api_errors_counter.inc()
        elif error_type == "scraping":
            self.metrics.scraping_errors += 1
        elif error_type == "analysis":
            self.metrics.analysis_errors += 1

    def record_cache_hit(self) -> None:
        """Record a cache hit."""
        self.metrics.cache_hits += 1
        if self.enable_prometheus:
            self.cache_hits_counter.inc()

    def record_cache_miss(self) -> None:
        """Record a cache miss."""
        self.metrics.cache_misses += 1
        if self.enable_prometheus:
            self.cache_misses_counter.inc()

    def record_ml_prediction(self) -> None:
        """Record an ML prediction."""
        self.metrics.ml_predictions_made += 1

    def record_llm_call(self) -> None:
        """Record an LLM API call."""
        self.metrics.llm_calls += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics as dictionary."""
        metrics_dict = self.metrics.to_dict()
        metrics_dict["cache_hit_rate"] = (
            self.metrics.cache_hits
            / (self.metrics.cache_hits + self.metrics.cache_misses)
            if (self.metrics.cache_hits + self.metrics.cache_misses) > 0
            else 0.0
        )
        metrics_dict["average_processing_time"] = (
            self.metrics.total_processing_time / self.metrics.crates_processed
            if self.metrics.crates_processed > 0
            else 0.0
        )
        return metrics_dict

    def export_prometheus(self) -> Optional[bytes]:
        """Export metrics in Prometheus format."""
        if not self.enable_prometheus:
            return None
        return generate_latest()

    def reset(self) -> None:
        """Reset metrics (useful for testing)."""
        self.metrics = PipelineMetrics()
        self.quality_scores.clear()
        self.processing_times.clear()


# Global metrics collector instance
_global_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector(enable_prometheus: bool = True) -> MetricsCollector:
    """Get global metrics collector instance."""
    global _global_metrics_collector
    if _global_metrics_collector is None:
        _global_metrics_collector = MetricsCollector(enable_prometheus=enable_prometheus)
    return _global_metrics_collector

