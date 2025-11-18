"""Sample governance plugin: Security policy enforcement."""

from typing import Any, Dict

from flamehaven_doc_sanity.plugins.base import (
    GovernancePlugin,
    PluginMetadata,
    PluginType,
)


class SecurityGovernancePlugin(GovernancePlugin):
    """Enforces security governance policies.

    Checks for:
    - Minimum security dimension score
    - Credential exposure in configurations
    - Insecure default settings
    - Security best practices compliance
    """

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="security-governance",
            version="1.0.0",
            author="Flamehaven Doc-Sanity Team",
            description="Enforces security governance policies and best practices",
            plugin_type=PluginType.GOVERNANCE,
            dependencies=[],
            config_schema={
                "min_security_score": {
                    "type": "number",
                    "default": 0.85,
                    "description": "Minimum required security dimension score",
                },
                "check_credentials": {
                    "type": "boolean",
                    "default": True,
                    "description": "Check for exposed credentials",
                },
                "strict_mode": {
                    "type": "boolean",
                    "default": False,
                    "description": "Enable strict security enforcement",
                },
            },
        )

    def initialize(self) -> bool:
        """Initialize the plugin."""
        self.min_security_score = self.config.get("min_security_score", 0.85)
        self.check_credentials = self.config.get("check_credentials", True)
        self.strict_mode = self.config.get("strict_mode", False)

        # Credential patterns to check for
        self.credential_patterns = [
            "password",
            "secret",
            "api_key",
            "apikey",
            "token",
            "private_key",
            "access_key",
            "credentials",
        ]

        return True

    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass

    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate security governance policy.

        Args:
            context: Evaluation context with configuration and metrics

        Returns:
            Evaluation result with violations and recommendations
        """
        violations = []
        recommendations = []
        severity = "none"

        # Check security dimension score
        dimensions = context.get("dimensions", {})
        security_score = dimensions.get("security", 0.0)

        if security_score < self.min_security_score:
            violation_msg = (
                f"Security score {security_score:.2f} below minimum "
                f"threshold {self.min_security_score:.2f}"
            )
            violations.append(violation_msg)
            severity = "severe" if self.strict_mode else "moderate"

            recommendations.append(
                "Improve security practices to meet minimum score threshold"
            )

        # Check for credential exposure
        if self.check_credentials:
            config_data = context.get("configuration", {})
            exposed_credentials = self._check_credentials(config_data)

            if exposed_credentials:
                violations.append(
                    f"Potential credential exposure detected: {', '.join(exposed_credentials)}"
                )
                severity = "critical"  # Credentials are always critical

                recommendations.append(
                    "Remove exposed credentials and use secure secret management"
                )
                recommendations.append(
                    "Consider using environment variables or secret vaults"
                )

        # Check for insecure defaults
        insecure_settings = self._check_insecure_defaults(context)
        if insecure_settings:
            violations.extend(insecure_settings)
            if severity == "none":
                severity = "minor"

            recommendations.append("Review and update insecure default configurations")

        # Determine if passed
        passed = len(violations) == 0

        return {
            "passed": passed,
            "severity": severity,
            "violations": violations,
            "recommendations": recommendations,
            "metadata": {
                "security_score": security_score,
                "min_required": self.min_security_score,
                "strict_mode": self.strict_mode,
            },
        }

    def _check_credentials(self, config: Dict[str, Any]) -> list:
        """Check for exposed credentials in configuration.

        Args:
            config: Configuration to check

        Returns:
            List of exposed credential keys
        """
        exposed = []

        def check_dict(d: Dict[str, Any], path: str = ""):
            """Recursively check dictionary for credentials."""
            for key, value in d.items():
                current_path = f"{path}.{key}" if path else key
                key_lower = key.lower()

                # Check if key matches credential pattern
                if any(pattern in key_lower for pattern in self.credential_patterns):
                    # Check if value looks like a credential (not empty, not placeholder)
                    if isinstance(value, str) and value and not value.startswith("$"):
                        exposed.append(current_path)

                # Recurse into nested dicts
                if isinstance(value, dict):
                    check_dict(value, current_path)

        check_dict(config)
        return exposed

    def _check_insecure_defaults(self, context: Dict[str, Any]) -> list:
        """Check for insecure default settings.

        Args:
            context: Evaluation context

        Returns:
            List of insecure setting violations
        """
        violations = []
        config = context.get("configuration", {})

        # Check for debug mode in production
        if config.get("debug", False) and config.get("environment") == "production":
            violations.append("Debug mode enabled in production environment")

        # Check for missing encryption
        if not config.get("encryption_enabled", True):
            violations.append("Data encryption is disabled")

        # Check for weak authentication
        auth_config = config.get("authentication", {})
        if auth_config.get("allow_anonymous", False):
            violations.append("Anonymous authentication is enabled")

        return violations

    def get_policy_name(self) -> str:
        """Get policy name."""
        return "security-governance-policy"

    def get_severity_threshold(self) -> str:
        """Get minimum severity level."""
        return "critical" if self.strict_mode else "moderate"
