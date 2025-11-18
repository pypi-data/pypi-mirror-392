"""Sample validator plugin: Markdown link validation."""

import re
from typing import Any, Dict, List

from flamehaven_doc_sanity.plugins.base import (
    PluginMetadata,
    PluginType,
    ValidatorPlugin,
)


class MarkdownLinkValidator(ValidatorPlugin):
    """Validates markdown links in documents.

    Checks for:
    - Broken link syntax
    - Empty link URLs
    - Missing link text
    - Malformed link references
    """

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="markdown-link-validator",
            version="1.0.0",
            author="Flamehaven Doc-Sanity Team",
            description="Validates markdown links for syntax and completeness",
            plugin_type=PluginType.VALIDATOR,
            dependencies=[],
            config_schema={
                "check_references": {
                    "type": "boolean",
                    "default": True,
                    "description": "Check for broken link references",
                },
                "allow_empty_links": {
                    "type": "boolean",
                    "default": False,
                    "description": "Allow links with empty URLs",
                },
            },
        )

    def initialize(self) -> bool:
        """Initialize the plugin."""
        self.check_references = self.config.get("check_references", True)
        self.allow_empty_links = self.config.get("allow_empty_links", False)
        return True

    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass

    def validate(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate markdown links in content.

        Args:
            content: Document content
            context: Validation context

        Returns:
            Validation result with errors and warnings
        """
        errors = []
        warnings = []

        # Pattern for inline links: [text](url)
        inline_pattern = r"\[([^\]]*)\]\(([^\)]*)\)"

        # Pattern for reference links: [text][ref] or [ref]
        reference_pattern = r"\[([^\]]+)\]\[([^\]]*)\]|\[([^\]]+)\](?!\()"

        # Pattern for reference definitions: [ref]: url
        definition_pattern = r"^\[([^\]]+)\]:\s*(.+)$"

        # Check inline links
        for match in re.finditer(inline_pattern, content):
            link_text = match.group(1)
            link_url = match.group(2)

            if not link_text:
                warnings.append(
                    f"Empty link text at position {match.start()}: [{link_text}]({link_url})"
                )

            if not link_url and not self.allow_empty_links:
                errors.append(
                    f"Empty link URL at position {match.start()}: [{link_text}]()"
                )

        # Check reference links if enabled
        if self.check_references:
            # Collect all reference definitions
            definitions = set()
            for match in re.finditer(definition_pattern, content, re.MULTILINE):
                ref_name = match.group(1).lower()
                definitions.add(ref_name)

            # Check reference usage
            for match in re.finditer(reference_pattern, content):
                # Handle [text][ref] format
                if match.group(2) is not None:
                    ref_name = match.group(2).lower()
                # Handle [ref] format
                elif match.group(3) is not None:
                    ref_name = match.group(3).lower()
                else:
                    continue

                if ref_name and ref_name not in definitions:
                    errors.append(
                        f"Undefined reference link at position {match.start()}: [{ref_name}]"
                    )

        # Determine validity
        is_valid = len(errors) == 0

        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "metadata": {
                "inline_links_checked": len(re.findall(inline_pattern, content)),
                "reference_links_checked": (
                    len(re.findall(reference_pattern, content))
                    if self.check_references
                    else 0
                ),
            },
        }

    def get_validation_rules(self) -> List[str]:
        """Get list of validation rules."""
        rules = [
            "no-empty-link-urls",
            "no-empty-link-text",
        ]
        if self.check_references:
            rules.append("no-undefined-references")
        return rules
