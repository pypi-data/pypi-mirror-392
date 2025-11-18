"""Fusion Oracle: Multi-validator decision synthesis engine."""

from dataclasses import dataclass
from typing import Any, Dict, List

from flamehaven_doc_sanity.validators import ValidationResult


@dataclass
class FusionDecision:
    """Decision synthesized from multiple validator results."""

    status: str  # 'approved', 'rejected', 'needs_review'
    fusion_score: float
    oracle_verdict: str
    oracle_reasoning: str
    contributing_validators: List[str]
    metadata: Dict[str, Any]


class FusionOracle:
    """Synthesizes decisions from multiple validator perspectives.

    The FusionOracle combines results from different validators using
    weighted fusion and decision cascade logic.
    """

    def __init__(self, weights: Dict[str, float] = None):
        """Initialize FusionOracle.

        Args:
            weights: Optional validator weights (default: equal weighting)
        """
        self.weights = weights or {}

    def fuse(
        self, results: List[ValidationResult], context: Dict[str, Any] = None
    ) -> FusionDecision:
        """Fuse multiple validation results into a single decision.

        Args:
            results: List of ValidationResult from different validators
            context: Optional context for decision making

        Returns:
            FusionDecision with synthesized verdict
        """
        if not results:
            return FusionDecision(
                status="rejected",
                fusion_score=0.0,
                oracle_verdict="no_validators",
                oracle_reasoning="No validation results to fuse",
                contributing_validators=[],
                metadata={},
            )

        context = context or {}
        severity = context.get("severity", "medium")

        # Calculate weighted fusion score
        total_weight = 0.0
        weighted_score = 0.0

        for result in results:
            weight = self.weights.get(result.validator_name, 1.0)
            weighted_score += result.score * weight
            total_weight += weight

        fusion_score = weighted_score / total_weight if total_weight > 0 else 0.0

        # Apply severity-based thresholds
        thresholds = {
            "low": 0.70,
            "medium": 0.85,
            "high": 0.95,
        }
        threshold = thresholds.get(severity, 0.85)

        # Determine status
        if fusion_score >= threshold:
            status = "approved"
            verdict = "acceptable"
        elif fusion_score >= 0.70:
            status = "needs_review"
            verdict = "marginal"
        else:
            status = "rejected"
            verdict = "insufficient"

        # Generate reasoning
        contributing = [r.validator_name for r in results]
        reasoning = (
            f"Fusion score {fusion_score:.2f} with severity '{severity}' "
            f"(threshold: {threshold:.2f}). "
            f"Contributing validators: {', '.join(contributing)}."
        )

        return FusionDecision(
            status=status,
            fusion_score=fusion_score,
            oracle_verdict=verdict,
            oracle_reasoning=reasoning,
            contributing_validators=contributing,
            metadata={
                "severity": severity,
                "threshold": threshold,
                "validator_count": len(results),
            },
        )
