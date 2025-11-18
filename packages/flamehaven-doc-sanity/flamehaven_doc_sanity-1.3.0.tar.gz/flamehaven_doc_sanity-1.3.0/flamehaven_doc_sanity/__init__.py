"""Flamehaven-Doc-Sanity: Documentation Validation Framework.

Version: 1.3.0
Status: Active Development
New in v1.3.0: I18n Translation, Enhanced Governance, Improved Test Coverage
"""

__version__ = "1.3.1"
__status__ = "Active Development"

from flamehaven_doc_sanity.exceptions import (
    DocSanityError,
    DriftDetectedError,
    GovernanceError,
    TribunalConflictError,
    ValidationError,
)

__all__ = [
    "__version__",
    "__status__",
    "DocSanityError",
    "ValidationError",
    "GovernanceError",
    "TribunalConflictError",
    "DriftDetectedError",
]
