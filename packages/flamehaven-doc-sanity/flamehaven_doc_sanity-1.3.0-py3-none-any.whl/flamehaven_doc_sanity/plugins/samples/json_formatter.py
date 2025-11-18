"""Sample formatter plugin: JSON document formatting."""

import json
from typing import Any, Dict

from flamehaven_doc_sanity.plugins.base import (
    FormatterPlugin,
    PluginMetadata,
    PluginType,
)


class JSONFormatterPlugin(FormatterPlugin):
    """Formats documents as JSON with customizable options.

    Supports:
    - Pretty printing with indentation
    - Compact formatting
    - Custom key sorting
    - ASCII-only encoding
    """

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="json-formatter",
            version="1.0.0",
            author="Flamehaven Doc-Sanity Team",
            description="Formats documents as JSON with customizable options",
            plugin_type=PluginType.FORMATTER,
            dependencies=[],
            config_schema={
                "indent": {
                    "type": "integer",
                    "default": 2,
                    "description": "Number of spaces for indentation",
                },
                "sort_keys": {
                    "type": "boolean",
                    "default": True,
                    "description": "Sort object keys alphabetically",
                },
                "ensure_ascii": {
                    "type": "boolean",
                    "default": False,
                    "description": "Escape non-ASCII characters",
                },
                "compact": {
                    "type": "boolean",
                    "default": False,
                    "description": "Compact formatting (no indentation)",
                },
            },
        )

    def initialize(self) -> bool:
        """Initialize the plugin."""
        self.indent = self.config.get("indent", 2)
        self.sort_keys = self.config.get("sort_keys", True)
        self.ensure_ascii = self.config.get("ensure_ascii", False)
        self.compact = self.config.get("compact", False)
        return True

    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass

    def format(self, content: str, options: Dict[str, Any]) -> str:
        """Format content as JSON.

        Args:
            content: Content to format (should be JSON string or dict)
            options: Formatting options (overrides config)

        Returns:
            Formatted JSON string
        """
        # Parse content if it's a string
        if isinstance(content, str):
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                # If not valid JSON, return error message
                return json.dumps(
                    {
                        "error": "Invalid JSON input",
                        "message": str(e),
                        "original": content,
                    },
                    indent=self.indent,
                )
        else:
            data = content

        # Apply options (override config)
        indent = options.get("indent", None if self.compact else self.indent)
        sort_keys = options.get("sort_keys", self.sort_keys)
        ensure_ascii = options.get("ensure_ascii", self.ensure_ascii)

        # Handle compact mode
        if options.get("compact", self.compact):
            indent = None
            separators = (",", ":")  # Minimal whitespace
        else:
            separators = (", ", ": ")  # Standard whitespace

        # Format JSON
        formatted = json.dumps(
            data,
            indent=indent,
            sort_keys=sort_keys,
            ensure_ascii=ensure_ascii,
            separators=separators,
        )

        return formatted

    def supports_format(self, format_type: str) -> bool:
        """Check if plugin supports a format type.

        Args:
            format_type: Format type to check

        Returns:
            True if supported
        """
        return format_type.lower() in ["json", "application/json"]
