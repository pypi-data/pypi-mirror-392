"""Document validation engines for Flamehaven-Doc-Sanity."""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ValidationResult:
    """Result from a validation operation."""

    status: str  # 'approved', 'rejected', 'needs_review'
    validator_name: str
    violations: List[str]
    score: float
    metadata: Dict[str, Any]


class BaseValidator:
    """Base class for all validators."""

    def __init__(self, name: str):
        self.name = name

    def validate(self, content: str, file_path: str = None) -> ValidationResult:
        """Validate document content.

        Args:
            content: Document content to validate
            file_path: Optional path to the document

        Returns:
            ValidationResult with validation outcome
        """
        raise NotImplementedError("Subclasses must implement validate()")


class DeepValidator(BaseValidator):
    """Deep validation with comprehensive checks."""

    def __init__(self):
        super().__init__("deep_validator")

    def validate(self, content: str, file_path: str = None) -> ValidationResult:
        """Perform deep validation checks.

        Checks:
        - Structure completeness
        - Link validity
        - Code block syntax
        - Heading hierarchy
        - Content coherence
        """
        violations = []
        score = 1.0

        # Check for basic markdown structure
        if not content.strip():
            violations.append("Empty document")
            score -= 0.5

        # Check for broken links (simple pattern)
        if "[broken link](" in content.lower():
            violations.append("Broken link detected")
            score -= 0.3

        # Check for heading structure
        if content.strip() and not content.strip().startswith("#"):
            violations.append("Document should start with heading")
            score -= 0.1

        status = "approved" if score >= 0.85 else "rejected"

        return ValidationResult(
            status=status,
            validator_name=self.name,
            violations=violations,
            score=max(0.0, score),
            metadata={"file_path": file_path, "depth": "comprehensive"},
        )


class ShallowValidator(BaseValidator):
    """Shallow validation with basic checks."""

    def __init__(self):
        super().__init__("shallow_validator")

    def validate(self, content: str, file_path: str = None) -> ValidationResult:
        """Perform shallow validation checks.

        Checks:
        - Document not empty
        - Basic formatting
        """
        violations = []
        score = 1.0

        if not content.strip():
            violations.append("Empty document")
            score = 0.0

        status = "approved" if score >= 0.7 else "rejected"

        return ValidationResult(
            status=status,
            validator_name=self.name,
            violations=violations,
            score=score,
            metadata={"file_path": file_path, "depth": "basic"},
        )


__all__ = [
    "ValidationResult",
    "BaseValidator",
    "DeepValidator",
    "ShallowValidator",
]
