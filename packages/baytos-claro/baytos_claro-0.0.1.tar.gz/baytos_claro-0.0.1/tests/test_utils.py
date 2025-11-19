"""Tests for utility functions"""

import pytest
from baytos.claro.utils import parse_package_name, validate_api_key


class TestParsePackageName:
    """Test parse_package_name function"""

    def test_valid_package_with_version(self):
        """Test parsing a valid package name with version"""
        result = parse_package_name("@alice/my-prompt:v1")
        assert result is not None
        assert result["namespace"] == "alice"
        assert result["slug"] == "my-prompt"
        assert result["version"] == "v1"

    def test_valid_package_without_version(self):
        """Test parsing a valid package name without version"""
        result = parse_package_name("@alice/my-prompt")
        assert result is not None
        assert result["namespace"] == "alice"
        assert result["slug"] == "my-prompt"
        assert result["version"] is None

    def test_organization_namespace(self):
        """Test parsing with organization namespace"""
        result = parse_package_name("@acme-corp/product-description:v2")
        assert result is not None
        assert result["namespace"] == "acme-corp"
        assert result["slug"] == "product-description"
        assert result["version"] == "v2"

    def test_complex_slug(self):
        """Test parsing with complex slug"""
        result = parse_package_name("@user/my-complex-prompt-name:v0")
        assert result is not None
        assert result["namespace"] == "user"
        assert result["slug"] == "my-complex-prompt-name"
        assert result["version"] == "v0"

    def test_invalid_formats(self):
        """Test various invalid package name formats"""
        invalid_names = [
            "alice/my-prompt",  # Missing @
            "@alice/",  # Missing slug
            "@/my-prompt",  # Missing namespace
            "my-prompt",  # Missing namespace and @
            "@alice",  # Missing slash and slug
            "@alice/my-prompt:",  # Empty version
            "",  # Empty string
            "@alice/my prompt",  # Space in slug
            "@alice space/my-prompt",  # Space in namespace
        ]

        for name in invalid_names:
            result = parse_package_name(name)
            assert result is None, f"Expected None for '{name}', got {result}"


class TestValidateApiKey:
    """Test validate_api_key function for WorkOS format keys"""

    def test_valid_workos_keys(self):
        """Test valid WorkOS API keys (sk_* format)"""
        # Typical WorkOS key format
        assert (
            validate_api_key("sk_test_mock_key_1234567890abcdefghijklmnopqrstuvwxyz")
            is True
        )
        assert (
            validate_api_key("sk_box9fStIm0DbDgmlgjyMw3rk0srw4TQYkeFmCtwF9LVFv6")
            is True
        )
        assert validate_api_key("sk_prod_1234567890abcdefABCDEF") is True

        # Minimum length (30 chars)
        assert (
            validate_api_key("sk_test_1234567890abcdefghijkl") is True
        )  # 30 chars exactly

        # With underscores
        assert validate_api_key("sk_test_with_underscores_123456789abcdef") is True

    def test_whitespace_handling(self):
        """Test that whitespace is properly stripped"""
        # Leading/trailing whitespace should be stripped
        assert (
            validate_api_key("  sk_test_key_1234567890abcdefghijklmnopqrst  ") is True
        )
        assert (
            validate_api_key("\nsk_test_key_1234567890abcdefghijklmnopqrst\n") is True
        )
        assert (
            validate_api_key("\tsk_test_key_1234567890abcdefghijklmnopqrst\t") is True
        )

    def test_invalid_prefix(self):
        """Test keys with invalid prefixes are rejected"""
        # Old format keys
        assert validate_api_key("b_prod_abcd_1234567890") is False
        assert validate_api_key("b_dev_ABC_1234567890") is False

        # Wrong prefix
        assert validate_api_key("pk_test_1234567890abcdefghijklmnopqrst") is False
        assert validate_api_key("key_test_1234567890abcdefghijklmnopqrst") is False

    def test_invalid_length(self):
        """Test keys with invalid lengths are rejected"""
        # Too short (< 30 chars)
        assert validate_api_key("sk_short") is False
        assert validate_api_key("sk_test_12345") is False
        assert validate_api_key("sk_test_1234567890abc") is False  # 25 chars

        # Too long (> 200 chars)
        assert validate_api_key("sk_" + "x" * 200) is False

    def test_invalid_characters(self):
        """Test keys with invalid characters are rejected"""
        invalid_keys = [
            "sk_test_key!1234567890abcdefghijklmnopqrst",  # Special char
            "sk_test_key@1234567890abcdefghijklmnopqrst",  # @ symbol
            "sk_test_key 1234567890abcdefghijklmnopqrst",  # Space in middle
            "sk_test_key-1234567890abcdefghijklmnopqrst",  # Hyphen
            "sk_test_key.1234567890abcdefghijklmnopqrst",  # Period
        ]

        for key in invalid_keys:
            result = validate_api_key(key)
            assert result is False, f"Expected False for '{key}', got {result}"

    def test_edge_cases(self):
        """Test edge cases"""
        assert validate_api_key("") is False  # Empty string
        assert validate_api_key(None) is False  # None
        assert validate_api_key("sk_") is False  # Just prefix
        assert validate_api_key("   ") is False  # Only whitespace
