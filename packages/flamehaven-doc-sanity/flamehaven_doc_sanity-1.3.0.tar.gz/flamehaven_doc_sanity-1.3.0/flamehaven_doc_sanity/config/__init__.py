"""Configuration management for Flamehaven-Doc-Sanity."""

import os
from pathlib import Path
from typing import Any, Dict

import yaml


def get_config_dir() -> Path:
    """Get the configuration directory path."""
    return Path(__file__).parent


def load_golden_baseline() -> Dict[str, Any]:
    """Load the golden baseline configuration for drift detection.

    Returns:
        Dict containing golden baseline metrics and thresholds.
    """
    baseline_path = get_config_dir() / "golden_baseline.yaml"

    if baseline_path.exists():
        with open(baseline_path, "r") as f:
            return yaml.safe_load(f)

    # Default baseline if file doesn't exist
    return {
        "golden_baseline": {
            "version": "1.2.0",
            "dimensions": {
                "integrity": 0.90,
                "governance": 0.90,
                "reliability": 0.88,
                "maintainability": 0.90,
                "security": 0.88,
            },
            "jsd_tolerance": 0.04,
        }
    }


def load_policies() -> Dict[str, Any]:
    """Load governance policies configuration.

    Returns:
        Dict containing policy definitions.
    """
    policies_path = get_config_dir() / "policies.yaml"

    if policies_path.exists():
        with open(policies_path, "r") as f:
            return yaml.safe_load(f)

    # Default policies
    return {
        "policies": {
            "version_control": [
                "all_changes_must_have_drift_check",
                "no_deployment_above_jsd_0.08",
            ],
            "documentation": [
                "readme_enhancement_required_for_modules",
                "architecture_docs_updated_with_changes",
            ],
            "governance": [
                "tribunal_verdict_final",
                "policy_violation_triggers_alert",
            ],
        }
    }


__all__ = [
    "get_config_dir",
    "load_golden_baseline",
    "load_policies",
]
