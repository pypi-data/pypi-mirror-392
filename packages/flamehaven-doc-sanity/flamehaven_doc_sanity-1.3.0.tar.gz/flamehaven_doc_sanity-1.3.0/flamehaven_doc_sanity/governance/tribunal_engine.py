"""Tribunal Engine: Three-perspective decision arbitration system."""

from dataclasses import dataclass
from typing import Any, Callable, Dict

from flamehaven_doc_sanity.exceptions import TribunalConflictError


@dataclass
class TribunalCase:
    """A case submitted to the tribunal for judgment."""

    issue: str
    advocate_position: str
    archangel_position: str
    oracle_verdict: str


class TribunalEngine:
    """Three-perspective decision engine.

    The Tribunal consists of:
    - Advocate: Finds constructive interpretations and growth paths
    - Archangel: Applies absolute standards without compromise
    - Oracle: Synthesizes perspectives and renders final judgment
    """

    def __init__(self):
        """Initialize TribunalEngine with default perspectives."""
        self.advocate_perspective = None
        self.archangel_perspective = None
        self.oracle_perspective = None
        self.custom_perspectives = {}

    def register_advocate(self, perspective: Callable):
        """Register the Advocate perspective function."""
        self.advocate_perspective = perspective

    def register_archangel(self, perspective: Callable):
        """Register the Archangel perspective function."""
        self.archangel_perspective = perspective

    def register_oracle(self, perspective: Callable):
        """Register the Oracle perspective function."""
        self.oracle_perspective = perspective

    def register_custom_perspective(self, name: str, bias: str, expertise: list):
        """Register a custom tribunal perspective.

        Args:
            name: Perspective name
            bias: Perspective bias ('conservative', 'progressive', etc.)
            expertise: List of expertise areas
        """
        self.custom_perspectives[name] = {"bias": bias, "expertise": expertise}

    def judge(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """Render tribunal judgment on a case.

        Args:
            case: Case dictionary with issue and positions

        Returns:
            Dict with tribunal decision
        """
        issue = case.get("issue", "Unknown issue")
        advocate_pos = case.get("advocate_position", "Accept with improvements")
        archangel_pos = case.get("archangel_position", "Reject until compliant")
        oracle_verdict = case.get("oracle_verdict", "REVIEW")

        # Detect issue category from issue text for contextual reasoning
        issue_lower = issue.lower()
        issue_context = self._categorize_issue(issue_lower, archangel_pos.lower())

        # Simulate tribunal deliberation
        # In production, this would invoke actual perspective functions

        # Check for irreconcilable conflict
        if "Critical" in archangel_pos and "Minor" in advocate_pos:
            # Try oracle synthesis
            if oracle_verdict == "CRITICAL":
                # Oracle sides with Archangel
                final_verdict = "CRITICAL"
                reasoning = f"Oracle synthesis: {issue_context} standards cannot be compromised."
            elif oracle_verdict == "MINOR":
                # Oracle sides with Advocate
                final_verdict = "MINOR"
                reasoning = "Oracle synthesis: Issue addressable through incremental improvements."
            else:
                # Oracle cannot reconcile - raise conflict error
                raise TribunalConflictError(
                    advocate_pos=advocate_pos,
                    archangel_pos=archangel_pos,
                    oracle_attempt="Unable to synthesize conflicting perspectives",
                )
        else:
            # Positions are reconcilable
            final_verdict = oracle_verdict
            # Include issue context in reasoning
            reasoning = f"Tribunal consensus on {oracle_verdict} severity: {issue_context} addressed."

        return {
            "issue": issue,
            "advocate_position": advocate_pos,
            "archangel_position": archangel_pos,
            "oracle_verdict": final_verdict,
            "reasoning": reasoning,
            "tribunal_decision": final_verdict,
        }

    def _categorize_issue(self, issue_text: str, position_text: str = "") -> str:
        """Categorize issue based on keywords for contextual reasoning.

        Args:
            issue_text: Lowercase issue description
            position_text: Lowercase position text for additional context

        Returns:
            Issue category description
        """
        combined_text = issue_text + " " + position_text

        # Security-related keywords
        if any(
            keyword in combined_text
            for keyword in [
                "security",
                "credential",
                "password",
                "auth",
                "vulnerability",
                "exposure",
                "injection",
                "xss",
                "csrf",
                "token",
                "secret",
            ]
        ):
            return "Security and quality"

        # Quality-related keywords
        if any(
            keyword in combined_text
            for keyword in [
                "quality",
                "standard",
                "compliance",
                "documentation",
                "test",
                "coverage",
                "architecture",
            ]
        ):
            return "Quality"

        # Performance-related keywords
        if any(
            keyword in combined_text
            for keyword in [
                "performance",
                "latency",
                "throughput",
                "slo",
                "optimization",
            ]
        ):
            return "Performance"

        # Governance-related keywords
        if any(
            keyword in combined_text
            for keyword in ["governance", "policy", "drift", "baseline", "tribunal"]
        ):
            return "Governance"

        # Default
        return "Standards"


# Default perspective loaders (simplified implementations)
def load_advocate_perspective() -> Callable:
    """Load the Advocate perspective function."""

    def advocate(case: Dict[str, Any]) -> str:
        return "Focus on constructive improvements and achievable growth."

    return advocate


def load_archangel_perspective() -> Callable:
    """Load the Archangel perspective function."""

    def archangel(case: Dict[str, Any]) -> str:
        return "Apply absolute standards without compromise."

    return archangel


def load_oracle_perspective() -> Callable:
    """Load the Oracle perspective function."""

    def oracle(case: Dict[str, Any]) -> str:
        return "Synthesize optimal path balancing standards and pragmatism."

    return oracle
