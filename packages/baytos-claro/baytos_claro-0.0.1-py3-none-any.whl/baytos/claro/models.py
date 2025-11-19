"""
Data models for the Bayt SDK
"""

from typing import Dict, Any, Optional, List
import re
from .context import ContextItem


class Prompt:
    """
    Represents a Bayt prompt with all its content and metadata.

    Provides both dictionary-style and attribute access to prompt data.
    """

    def __init__(self, data: Dict[str, Any]):
        """
        Initialize a Prompt from API response data.

        Args:
            data: Dictionary containing prompt data from the API
        """
        self._data = data

    def _get_str_field(self, key: str, default: str = "") -> str:
        """Get a string field value with default

        Args:
            key: Field name to retrieve
            default: Default value if field is missing

        Returns:
            Field value as string, or default
        """
        value = self._data.get(key)
        if value is None:
            return default
        return str(value)

    # Dictionary-style access
    def __getitem__(self, key: str) -> Any:
        """Get a field value using dictionary syntax."""
        return self._data.get(key)

    def __contains__(self, key: str) -> bool:
        """Check if a field exists using 'in' operator."""
        return key in self._data

    def get(self, key: str, default: Any = None) -> Any:
        """Get a field value with a default if not found."""
        return self._data.get(key, default)

    def keys(self) -> List[str]:
        """Get all available field names."""
        return list(self._data.keys())

    def values(self) -> List[Any]:
        """Get all field values."""
        return list(self._data.values())

    def items(self) -> List[tuple]:
        """Get all field name-value pairs."""
        return list(self._data.items())

    # Property access for common fields
    @property
    def id(self) -> str:
        """Prompt ID"""
        return self._get_str_field("id", "")

    @property
    def title(self) -> str:
        """Prompt title"""
        return self._get_str_field("title", "")

    @property
    def content(self) -> str:
        """Main prompt content (same as generator)"""
        return self._get_str_field("content", "")

    @property
    def generator(self) -> str:
        """Main prompt content (generator)"""
        return self._get_str_field("content", "")

    @property
    def system(self) -> str:
        """System prompt content"""
        return self._get_str_field("systemPrompt", "")

    @property
    def critique(self) -> str:
        """Critique prompt content"""
        return self._get_str_field("critiquePrompt", "")

    @property
    def version_content(self) -> Optional[Dict[str, Any]]:
        """Version content including actual prompt text for variable extraction"""
        return self._data.get("versionContent")

    @property
    def description(self) -> Optional[str]:
        """Prompt description"""
        return self._data.get("description")

    @property
    def category(self) -> str:
        """Prompt category"""
        return self._get_str_field("category", "")

    @property
    def namespace(self) -> str:
        """Namespace (workspace slug)"""
        return self._get_str_field("workspaceSlug", "")

    @property
    def slug(self) -> str:
        """URL-friendly identifier (package name)"""
        return self._get_str_field("packageName", "")

    @property
    def version(self) -> str:
        """Version (v0 for draft, v1+ for published)"""
        return self._get_str_field("version", "v0")

    @property
    def is_draft(self) -> bool:
        """Check if this is a draft version (v0)"""
        return self.version == "v0" or self._data.get("is_draft", False)

    @property
    def package_name(self) -> str:
        """Full package name"""
        return f"@{self.namespace}/{self.slug}:{self.version}"

    @property
    def context(self) -> List[ContextItem]:
        """List of context items (files and URLs) attached to this prompt"""
        context_data = self._data.get("context", [])
        return [ContextItem(item) for item in context_data]

    def get_file_contexts(self) -> List[ContextItem]:
        """Get only file-type context items"""
        return [item for item in self.context if item.is_file()]

    def get_url_contexts(self) -> List[ContextItem]:
        """Get only URL-type context items"""
        return [item for item in self.context if item.is_url()]

    def has_context(self) -> bool:
        """Check if the prompt has any context items"""
        return len(self.context) > 0

    def __repr__(self) -> str:
        """String representation of the prompt."""
        return f"<Prompt '{self.title}' {self.package_name}>"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return self.title

    def to_dict(self) -> Dict[str, Any]:
        """Get the full dictionary representation of the prompt."""
        return self._data.copy()

    def has_system_prompt(self) -> bool:
        """Check if the prompt has a system prompt."""
        return bool(self._data.get("systemPrompt"))

    def has_critique_prompt(self) -> bool:
        """Check if the prompt has a critique prompt."""
        return bool(self._data.get("critiquePrompt"))

    def extract_variables(self) -> List[Dict[str, str]]:
        """
        Extract variables from prompt content with optional type hints.

        Returns:
            List of dictionaries containing variable information:
            - name: Variable name
            - type: Variable type (if specified)
            - description: Type description or default value
        """
        variables = []
        seen = set()

        # Get the actual content from versionContent if available
        content_to_scan = []
        if self.version_content:
            vc = self.version_content
            if isinstance(vc, dict):
                content_to_scan.extend(
                    [
                        vc.get("content", ""),
                        vc.get("systemPrompt", ""),
                        vc.get("critiquePrompt", ""),
                    ]
                )
        else:
            # Fall back to regular content
            content_to_scan.extend([self.generator, self.system, self.critique])

        # Pattern to match {{variable}} or {{variable:type}} or {{variable:type // description}}
        pattern = r"\{\{([^}:]+)(?::([^}/]+))?(?:\s*//\s*([^}]+))?\}\}"

        for content in content_to_scan:
            if not content:
                continue

            for match in re.finditer(pattern, content):
                var_name = match.group(1).strip()
                var_type = match.group(2).strip() if match.group(2) else None
                var_desc = match.group(3).strip() if match.group(3) else None

                # Avoid duplicates
                if var_name not in seen:
                    seen.add(var_name)

                    variable_info = {"name": var_name}
                    if var_type:
                        variable_info["type"] = var_type
                    if var_desc:
                        variable_info["description"] = var_desc

                    variables.append(variable_info)

        return variables

    def validate_variables(self, provided_variables: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate provided variables against expected variables.

        Args:
            provided_variables: Dictionary of variable names to values

        Returns:
            Dictionary of validation errors (empty if all valid)
        """
        errors = {}
        expected = self.extract_variables()
        expected_names = {v["name"] for v in expected}

        # Check for missing required variables
        for var in expected:
            if var["name"] not in provided_variables:
                errors[var["name"]] = f"Missing required variable: {var['name']}"

        # Check for unexpected variables
        for key in provided_variables:
            if key not in expected_names:
                errors[key] = f"Unexpected variable: {key}"

        # Basic type validation if types are specified
        for var in expected:
            if var["name"] in provided_variables and "type" in var:
                value = provided_variables[var["name"]]
                var_type = var["type"].lower()

                # Basic type checking
                if var_type in ["string", "str", "text"]:
                    if not isinstance(value, str):
                        errors[var["name"]] = (
                            f"Expected string, got {type(value).__name__}"
                        )
                elif var_type in ["number", "int", "integer"]:
                    if not isinstance(value, (int, float)):
                        errors[var["name"]] = (
                            f"Expected number, got {type(value).__name__}"
                        )
                elif var_type in ["boolean", "bool"]:
                    if not isinstance(value, bool):
                        errors[var["name"]] = (
                            f"Expected boolean, got {type(value).__name__}"
                        )
                elif var_type in ["array", "list"]:
                    if not isinstance(value, (list, tuple)):
                        errors[var["name"]] = (
                            f"Expected array, got {type(value).__name__}"
                        )
                elif var_type in ["object", "dict"]:
                    if not isinstance(value, dict):
                        errors[var["name"]] = (
                            f"Expected object, got {type(value).__name__}"
                        )

        return errors
