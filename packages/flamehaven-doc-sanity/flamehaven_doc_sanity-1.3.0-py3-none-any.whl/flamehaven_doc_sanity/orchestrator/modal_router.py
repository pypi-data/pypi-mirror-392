"""Modal Router: Intelligent document validation routing system."""

from typing import Any, Dict, List

from flamehaven_doc_sanity.orchestrator.fusion_oracle import (
    FusionDecision,
    FusionOracle,
)
from flamehaven_doc_sanity.validators import BaseValidator, ValidationResult


class ModalRouter:
    """Routes document validation requests through appropriate validators.

    The ModalRouter orchestrates the validation pipeline, determining which
    validators to apply and how to combine their results using the FusionOracle.
    """

    def __init__(self, validators: List[BaseValidator], oracle: FusionOracle = None):
        """Initialize ModalRouter.

        Args:
            validators: List of validator instances to use
            oracle: FusionOracle instance (creates default if not provided)
        """
        self.validators = validators
        self.oracle = oracle or FusionOracle()

    def route_request(
        self, file_path: str, content: str, context: Dict[str, Any] = None
    ) -> FusionDecision:
        """Route a validation request through the validator pipeline.

        Args:
            file_path: Path to the document being validated
            content: Document content
            context: Optional context for routing decisions

        Returns:
            FusionDecision with final verdict
        """
        context = context or {}

        # Collect validation results from all validators
        results: List[ValidationResult] = []

        for validator in self.validators:
            try:
                result = validator.validate(content, file_path)
                results.append(result)
            except Exception as e:
                # Log error but continue with other validators
                print(f"Warning: Validator {validator.name} failed: {e}")

        # Use FusionOracle to synthesize final decision
        decision = self.oracle.fuse(results, context)

        return decision

    def get_validator_names(self) -> List[str]:
        """Get names of all registered validators.

        Returns:
            List of validator names
        """
        return [v.name for v in self.validators]
