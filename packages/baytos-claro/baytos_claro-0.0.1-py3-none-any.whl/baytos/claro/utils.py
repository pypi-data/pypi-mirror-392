"""
Utility functions for the Bayt SDK
"""

import re
import json
from typing import Optional, Dict, Any


def parse_package_name(package_name: str) -> Optional[Dict[str, Optional[str]]]:
    """
    Parse a package name to extract components.

    Format: @namespace/slug:version

    Args:
        package_name: Package identifier (e.g., "@bijou/team-analysis:v0")

    Returns:
        Dictionary with namespace, slug, and optional version, or None if invalid
    """
    # Stricter regex: only allow alphanumeric, hyphens, underscores
    # No spaces, special chars, or path traversal patterns
    package_regex = r"^@([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)(?::(.+))?$"
    match = re.match(package_regex, package_name)

    if not match:
        return None

    namespace = match.group(1)
    slug = match.group(2)
    version = match.group(3) if match.group(3) else None

    # Reject path traversal attempts
    if ".." in namespace or ".." in slug:
        return None

    # Reject empty namespace or slug
    if not namespace or not slug:
        return None

    return {"namespace": namespace, "slug": slug, "version": version}


def validate_api_key(api_key: str) -> bool:
    """
    Validate the format of a WorkOS API key.

    WorkOS keys start with 'sk_' and are typically 40-50+ characters.

    Args:
        api_key: The API key to validate

    Returns:
        True if valid, False otherwise
    """
    if not api_key:
        return False

    # Strip whitespace (handles copy/paste errors)
    api_key = api_key.strip()

    # Must start with sk_
    if not api_key.startswith("sk_"):
        return False

    # Reasonable length range (30-200 chars for flexibility)
    if not (30 <= len(api_key) <= 200):
        return False

    # Only alphanumeric characters and underscores allowed
    if not api_key.replace("_", "").isalnum():
        return False

    return True


def mask_api_key(api_key: str, show_prefix: bool = True, show_env: bool = True) -> str:
    """
    Mask an API key for safe display.

    Args:
        api_key: The API key to mask
        show_prefix: Deprecated parameter (kept for backward compatibility)
        show_env: Deprecated parameter (kept for backward compatibility)

    Returns:
        Masked API key string
    """
    if not api_key:
        return "***"

    # WorkOS format
    if api_key.startswith("sk_"):
        if len(api_key) < 10:
            return "***"
        # Show first 7 chars (sk_xxxx), hide rest, show last 4
        return (
            api_key[:7] + "..." + api_key[-4:]
            if len(api_key) > 11
            else api_key[:7] + "***"
        )

    return "***"


def interpolate_variables(template: str, variables: Dict[str, Any]) -> str:
    """
    Interpolate variables into a template string.

    Args:
        template: Template string with {{variable}} placeholders
        variables: Dictionary of variable values

    Returns:
        Interpolated string
    """
    result = template

    # Find all variables in the template (with or without type hints)
    pattern = r"\{\{([^}:]+)(?::[^}]+)?\}\}"

    for match in re.finditer(pattern, template):
        var_name = match.group(1).strip()
        full_match = match.group(0)

        if var_name in variables:
            value = variables[var_name]
            # Convert non-string values to JSON for proper representation
            if isinstance(value, (list, dict)):
                value_str = json.dumps(value)
            else:
                value_str = str(value)

            result = result.replace(full_match, value_str)

    return result


def estimate_token_count(text: str) -> int:
    """
    Estimate the number of tokens in a text string.

    This is a rough estimation based on typical tokenization patterns.
    For exact counts, use the tiktoken library with the specific model.

    Args:
        text: The text to estimate tokens for

    Returns:
        Estimated token count
    """
    # Rough estimation: ~4 characters per token on average
    # This varies by language and content type
    return len(text) // 4
