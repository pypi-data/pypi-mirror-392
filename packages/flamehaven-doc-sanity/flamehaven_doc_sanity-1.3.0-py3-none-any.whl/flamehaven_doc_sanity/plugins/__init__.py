"""Plugin system for Flamehaven-Doc-Sanity.

The plugin system allows extending functionality through modular plugins.

Plugin Types:
- ValidatorPlugin: Custom document validation rules
- FormatterPlugin: Document formatting and transformation
- ReporterPlugin: Custom reporting and output formats
- GovernancePlugin: Custom governance policies and checks
"""

from flamehaven_doc_sanity.plugins.base import (
    FormatterPlugin,
    GovernancePlugin,
    Plugin,
    PluginMetadata,
    ReporterPlugin,
    ValidatorPlugin,
)
from flamehaven_doc_sanity.plugins.loader import PluginLoader
from flamehaven_doc_sanity.plugins.registry import PluginRegistry

__all__ = [
    "Plugin",
    "ValidatorPlugin",
    "FormatterPlugin",
    "ReporterPlugin",
    "GovernancePlugin",
    "PluginMetadata",
    "PluginRegistry",
    "PluginLoader",
]
