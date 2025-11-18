"""Exception hierarchy for Flamehaven-Doc-Sanity.

This module defines all custom exceptions used throughout the system,
including the TribunalConflictError for governance arbitration failures.
"""


class DocSanityError(Exception):
    """Base exception for all Flamehaven-Doc-Sanity errors."""

    pass


class ValidationError(DocSanityError):
    """Raised when document validation fails."""

    def __init__(self, message, file_path=None, violations=None):
        self.file_path = file_path
        self.violations = violations or []
        super().__init__(message)


class GovernanceError(DocSanityError):
    """Raised when governance policy violations are detected."""

    def __init__(self, message, policy=None, severity=None):
        self.policy = policy
        self.severity = severity
        super().__init__(message)


class TribunalConflictError(DocSanityError):
    """Raised when tribunal perspectives cannot reach consensus.

    This occurs when the Advocate and Archangel perspectives produce
    irreconcilable positions and the Oracle cannot synthesize a valid
    decision within the configured iteration limit.

    Attributes:
        advocate_position: The Advocate's recommended action
        archangel_position: The Archangel's strict standard verdict
        oracle_attempt: The Oracle's attempted synthesis
    """

    def __init__(self, advocate_pos, archangel_pos, oracle_attempt):
        self.advocate_position = advocate_pos
        self.archangel_position = archangel_pos
        self.oracle_attempt = oracle_attempt

        message = (
            f"Tribunal conflict: Advocate vs Archangel "
            f"(Oracle synthesis: {oracle_attempt})\n"
            f"  Advocate: {advocate_pos}\n"
            f"  Archangel: {archangel_pos}\n"
            f"Manual arbitration required."
        )
        super().__init__(message)


class DriftDetectedError(DocSanityError):
    """Raised when configuration drift exceeds acceptable thresholds."""

    def __init__(self, message, jsd_score=None, threshold=None):
        self.jsd_score = jsd_score
        self.threshold = threshold
        super().__init__(message)


class PerformanceWarning(UserWarning):
    """Warning issued when SLO performance targets are exceeded."""

    pass
