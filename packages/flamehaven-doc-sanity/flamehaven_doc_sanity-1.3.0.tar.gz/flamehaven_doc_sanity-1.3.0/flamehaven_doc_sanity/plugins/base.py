"""Base classes for Flamehaven-Doc-Sanity plugins."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class PluginType(Enum):
    """Plugin type enumeration."""

    VALIDATOR = "validator"
    FORMATTER = "formatter"
    REPORTER = "reporter"
    GOVERNANCE = "governance"


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""

    name: str
    version: str
    author: str
    description: str
    plugin_type: PluginType
    dependencies: List[str] = None
    config_schema: Dict[str, Any] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.config_schema is None:
            self.config_schema = {}


class Plugin(ABC):
    """Base class for all plugins.

    All plugins must inherit from this class and implement the required methods.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize plugin with configuration.

        Args:
            config: Plugin configuration dictionary
        """
        self.config = config or {}
        self._enabled = True

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata.

        Returns:
            PluginMetadata instance
        """
        pass

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the plugin.

        Called when the plugin is loaded. Use this for setup tasks.

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup plugin resources.

        Called when the plugin is unloaded or system shuts down.
        """
        pass

    def enable(self) -> None:
        """Enable the plugin."""
        self._enabled = True

    def disable(self) -> None:
        """Disable the plugin."""
        self._enabled = False

    def is_enabled(self) -> bool:
        """Check if plugin is enabled.

        Returns:
            True if enabled, False otherwise
        """
        return self._enabled


class ValidatorPlugin(Plugin):
    """Base class for validator plugins.

    Validator plugins provide custom document validation logic.
    """

    @abstractmethod
    def validate(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate document content.

        Args:
            content: Document content to validate
            context: Validation context (file path, metadata, etc.)

        Returns:
            Validation result dictionary:
            {
                'valid': bool,
                'errors': List[str],
                'warnings': List[str],
                'metadata': Dict[str, Any]
            }
        """
        pass

    @abstractmethod
    def get_validation_rules(self) -> List[str]:
        """Get list of validation rules this plugin implements.

        Returns:
            List of rule names
        """
        pass


class FormatterPlugin(Plugin):
    """Base class for formatter plugins.

    Formatter plugins transform or format document content.
    """

    @abstractmethod
    def format(self, content: str, options: Dict[str, Any]) -> str:
        """Format document content.

        Args:
            content: Document content to format
            options: Formatting options

        Returns:
            Formatted content
        """
        pass

    @abstractmethod
    def supports_format(self, format_type: str) -> bool:
        """Check if plugin supports a specific format.

        Args:
            format_type: Format type (e.g., 'markdown', 'html', 'json')

        Returns:
            True if supported, False otherwise
        """
        pass


class ReporterPlugin(Plugin):
    """Base class for reporter plugins.

    Reporter plugins generate custom reports and outputs.
    """

    @abstractmethod
    def generate_report(self, data: Dict[str, Any]) -> str:
        """Generate report from data.

        Args:
            data: Report data

        Returns:
            Generated report as string
        """
        pass

    @abstractmethod
    def get_output_format(self) -> str:
        """Get output format for this reporter.

        Returns:
            Format identifier (e.g., 'json', 'html', 'pdf')
        """
        pass


class GovernancePlugin(Plugin):
    """Base class for governance plugins.

    Governance plugins implement custom governance policies and checks.
    """

    @abstractmethod
    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate governance policy.

        Args:
            context: Evaluation context (configuration, metrics, etc.)

        Returns:
            Evaluation result:
            {
                'passed': bool,
                'severity': str,
                'violations': List[str],
                'recommendations': List[str]
            }
        """
        pass

    @abstractmethod
    def get_policy_name(self) -> str:
        """Get policy name.

        Returns:
            Policy name identifier
        """
        pass

    @abstractmethod
    def get_severity_threshold(self) -> str:
        """Get minimum severity level this policy enforces.

        Returns:
            Severity level ('minor', 'moderate', 'severe', 'critical')
        """
        pass
