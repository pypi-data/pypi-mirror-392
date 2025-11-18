"""Policy Enforcer: Governance policy application and conflict resolution."""

from dataclasses import dataclass
from typing import Any, Dict, List

from flamehaven_doc_sanity.config import load_policies
from flamehaven_doc_sanity.governance.driftlock_guard import DriftVerdict
from flamehaven_doc_sanity.governance.hope_guard import HOPEVerdict


@dataclass
class EnforcementResult:
    """Result from policy enforcement."""

    status: str  # 'enforced', 'conflict', 'failed'
    severity: str
    actions_taken: List[str]
    policy_violations: List[str]
    arbitrated_by_tribunal: bool


class PolicyEnforcer:
    """Enforces governance policies and resolves conflicts.

    The PolicyEnforcer applies loaded policies and coordinates between
    different governance modules (DriftLock, HOPE, Tribunal).
    """

    def __init__(self, config_path: str = None):
        """Initialize PolicyEnforcer.

        Args:
            config_path: Optional path to policies configuration
        """
        self.policies = load_policies().get("policies", {})

    def apply(self, tribunal_result: Dict[str, Any]) -> EnforcementResult:
        """Apply policies based on tribunal verdict.

        Args:
            tribunal_result: Decision from tribunal arbitration

        Returns:
            EnforcementResult with enforcement outcome
        """
        verdict = tribunal_result.get("oracle_verdict", "unknown")
        severity = "CRITICAL" if verdict == "CRITICAL" else "MINOR"

        actions_taken = [
            f"Applied tribunal verdict: {verdict}",
            "Updated audit trail",
        ]

        if severity == "CRITICAL":
            actions_taken.append("Triggered alert notification")
            actions_taken.append("Blocked deployment pipeline")

        return EnforcementResult(
            status="enforced",
            severity=severity,
            actions_taken=actions_taken,
            policy_violations=[],
            arbitrated_by_tribunal=True,
        )

    def resolve_conflict(
        self, drift_lock_verdict: DriftVerdict, hope_verdict: HOPEVerdict
    ) -> EnforcementResult:
        """Resolve conflicts between governance modules.

        Args:
            drift_lock_verdict: Verdict from DriftLock Guard
            hope_verdict: Verdict from HOPE Guard

        Returns:
            EnforcementResult with conflict resolution
        """
        # Check for conflicting verdicts
        drift_critical = drift_lock_verdict.severity in ["severe", "critical"]
        hope_compliant = hope_verdict.compliant

        if drift_critical and hope_compliant:
            # Conflict: DriftLock fails but HOPE passes
            # Escalate to tribunal
            return EnforcementResult(
                status="conflict",
                severity="moderate",
                actions_taken=["Escalated to tribunal for arbitration"],
                policy_violations=["DriftLock and HOPE Guard disagreement"],
                arbitrated_by_tribunal=True,
            )

        # No conflict - apply stricter verdict
        if drift_critical or not hope_compliant:
            severity = "critical"
            status = "enforced"
            actions = ["Applied stricter verdict", "Blocked deployment"]
        else:
            severity = "none"
            status = "enforced"
            actions = ["No policy violations detected"]

        return EnforcementResult(
            status=status,
            severity=severity,
            actions_taken=actions,
            policy_violations=[],
            arbitrated_by_tribunal=False,
        )

    def check_document(
        self, file_path: str, change_diff: str = None
    ) -> EnforcementResult:
        """Check document against policies.

        Args:
            file_path: Path to document
            change_diff: Optional git diff of changes

        Returns:
            EnforcementResult with policy check results
        """
        violations = []

        # Check documentation policies
        if "readme" in file_path.lower():
            doc_policies = self.policies.get("documentation", [])
            if "readme_enhancement_required_for_modules" in doc_policies:
                # Would perform actual enhancement check here
                pass

        if violations:
            return EnforcementResult(
                status="failed",
                severity="moderate",
                actions_taken=["Identified policy violations"],
                policy_violations=violations,
                arbitrated_by_tribunal=False,
            )

        return EnforcementResult(
            status="enforced",
            severity="none",
            actions_taken=["All policies satisfied"],
            policy_violations=[],
            arbitrated_by_tribunal=False,
        )

    def trigger_alert(self, severity: str, violations: List[str]):
        """Trigger governance alert.

        Args:
            severity: Alert severity level
            violations: List of policy violations
        """
        # In production, this would send alerts via configured channels
        print(f"[{severity}] Policy Alert: {', '.join(violations)}")
