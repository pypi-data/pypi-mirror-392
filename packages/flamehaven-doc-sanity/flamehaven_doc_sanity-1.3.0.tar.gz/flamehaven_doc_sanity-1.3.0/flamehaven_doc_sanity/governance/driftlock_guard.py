"""DriftLock Guard: Configuration drift detection system."""

import math
from dataclasses import dataclass
from typing import Any, Dict

# Drift Detection Configuration Constants
# These thresholds define the severity classification of configuration drift
# based on Jensen-Shannon Divergence (JSD) scores.

# JSD Severity Thresholds
JSD_TOLERANCE_NONE = 0.04  # Below this: No drift detected
JSD_TOLERANCE_MINOR = 0.06  # Below this: Minor drift (monitor)
JSD_TOLERANCE_MODERATE = 0.08  # Below this: Moderate drift (review required)
JSD_TOLERANCE_SEVERE = 0.10  # Below this: Severe drift (immediate action)
# Above SEVERE threshold: Critical drift (deployment blocked)

# Dimension Difference Threshold
DIMENSION_DIFF_THRESHOLD = (
    0.05  # Minimum absolute difference to consider a dimension affected
)

# JSD Calculation Weights
# Hybrid approach combining absolute distance and relative divergence
JSD_WEIGHT_ABSOLUTE = 0.7  # Weight for mean absolute difference (captures magnitude)
JSD_WEIGHT_RELATIVE = 0.3  # Weight for KL divergence (captures distribution shift)
# Rationale: Absolute distance is more important for detecting quality degradation
# while relative divergence helps identify structural changes in metric proportions


@dataclass
class DriftVerdict:
    """Verdict from drift detection analysis."""

    severity: str  # 'none', 'minor', 'moderate', 'severe', 'critical'
    jsd_score: float
    drift_detected: bool
    affected_dimensions: list
    recommendation: str


class DriftLockGuard:
    """Detects configuration drift using Jensen-Shannon Divergence.

    Compares current system state against a golden baseline to identify
    architectural drift and prevent quality degradation.
    """

    def __init__(self, baseline: Dict[str, Any]):
        """Initialize DriftLockGuard.

        Args:
            baseline: Golden baseline configuration to compare against
        """
        self.baseline = baseline.get("golden_baseline", {})
        self.baseline_dimensions = self.baseline.get("dimensions", {})
        self.jsd_tolerance = self.baseline.get("jsd_tolerance", 0.04)

    def check(self, current_config: Dict[str, Any]) -> DriftVerdict:
        """Check for configuration drift.

        Args:
            current_config: Current system configuration

        Returns:
            DriftVerdict with analysis results
        """
        # Extract dimensions from current config
        current_dimensions = current_config.get("dimensions", {})

        # Calculate JSD between baseline and current
        jsd_score = self._calculate_jsd(self.baseline_dimensions, current_dimensions)

        # Identify affected dimensions
        affected = []
        for dim_name, baseline_value in self.baseline_dimensions.items():
            current_value = current_dimensions.get(dim_name, 0.0)
            if abs(baseline_value - current_value) > DIMENSION_DIFF_THRESHOLD:
                affected.append(dim_name)

        # Determine severity based on JSD score
        if jsd_score < self.jsd_tolerance:
            severity = "none"
            recommendation = "No action required. System within tolerance."
        elif jsd_score < JSD_TOLERANCE_MINOR:
            severity = "minor"
            recommendation = "Monitor closely. Minor drift detected."
        elif jsd_score < JSD_TOLERANCE_MODERATE:
            severity = "moderate"
            recommendation = "Review affected dimensions. Drift increasing."
        elif jsd_score < JSD_TOLERANCE_SEVERE:
            severity = "severe"
            recommendation = (
                "Immediate review required. Approaching critical threshold."
            )
        else:
            severity = "critical"
            recommendation = (
                "CRITICAL: Deployment blocked. Restore baseline compliance."
            )

        return DriftVerdict(
            severity=severity,
            jsd_score=jsd_score,
            drift_detected=jsd_score >= self.jsd_tolerance,
            affected_dimensions=affected,
            recommendation=recommendation,
        )

    def _calculate_jsd(
        self, p_dist: Dict[str, float], q_dist: Dict[str, float]
    ) -> float:
        """Calculate Jensen-Shannon Divergence between two distributions.

        For drift detection, we use a modified approach that captures absolute
        value differences rather than just relative proportions. This combines
        normalized JSD with absolute distance metrics.

        Args:
            p_dist: First distribution (baseline)
            q_dist: Second distribution (current)

        Returns:
            JSD score (0.0 to 1.0)
        """
        # Get all dimension keys
        all_keys = set(p_dist.keys()) | set(q_dist.keys())

        p_values = [p_dist.get(k, 0.0) for k in all_keys]
        q_values = [q_dist.get(k, 0.0) for k in all_keys]

        # Calculate absolute distance (captures magnitude differences)
        # Use mean absolute difference scaled to [0,1]
        abs_diff = sum(abs(p - q) for p, q in zip(p_values, q_values))
        mean_abs_diff = abs_diff / len(all_keys) if all_keys else 0.0

        # Calculate relative divergence using normalized distributions
        p_sum = sum(p_values) or 1.0
        q_sum = sum(q_values) or 1.0

        p_norm = [v / p_sum for v in p_values]
        q_norm = [v / q_sum for v in q_values]

        # Calculate JSD (simplified symmetric KL divergence)
        # M = (P + Q) / 2
        m_dist = [(p + q) / 2.0 for p, q in zip(p_norm, q_norm)]

        # JSD = 0.5 * KL(P||M) + 0.5 * KL(Q||M)
        kl_pm = sum(
            p * math.log(p / m) if p > 0 and m > 0 else 0
            for p, m in zip(p_norm, m_dist)
        )
        kl_qm = sum(
            q * math.log(q / m) if q > 0 and m > 0 else 0
            for q, m in zip(q_norm, m_dist)
        )

        jsd_relative = 0.5 * kl_pm + 0.5 * kl_qm

        # Combine both metrics using configured weights
        # This hybrid approach ensures we detect both magnitude changes (absolute)
        # and distribution shifts (relative)
        combined_score = (JSD_WEIGHT_ABSOLUTE * mean_abs_diff) + (
            JSD_WEIGHT_RELATIVE * jsd_relative
        )

        # Normalize to [0, 1] range
        return min(1.0, max(0.0, combined_score))
