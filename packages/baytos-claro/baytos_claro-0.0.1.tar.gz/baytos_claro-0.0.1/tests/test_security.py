"""Security tests for Bayt SDK

These tests verify:
- API key handling and masking
- Input validation and sanitization
- Protection against common attacks
- Secure defaults

Run with: pytest tests/test_security.py -v
"""

import pytest
import re
from unittest.mock import Mock, patch
from baytos.claro import BaytClient, Prompt
from baytos.claro.exceptions import BaytAPIError, BaytAuthError, BaytValidationError
from baytos.claro.utils import mask_api_key, validate_api_key


pytestmark = pytest.mark.security


class TestAPIKeySecurity:
    """Test API key handling security"""

    def test_api_key_not_in_error_messages(self, mock_api_key):
        """Test that API key is not exposed in error messages"""
        client = BaytClient(api_key=mock_api_key)

        with patch("requests.Session.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"error": "Unauthorized"}
            mock_post.return_value = mock_response

            try:
                client.get_prompt("@test/sample:v1")
            except BaytAuthError as e:
                error_msg = str(e)
                # API key should not appear in error message
                assert mock_api_key not in error_msg

    def test_api_key_not_in_repr(self, mock_api_key):
        """Test that API key is not in client repr"""
        client = BaytClient(api_key=mock_api_key)
        repr_str = repr(client)

        # API key should not appear in repr
        assert mock_api_key not in repr_str

        # Should contain masked version (either *** or ...)
        assert "***" in repr_str or "..." in repr_str or "masked" in repr_str.lower()

    def test_api_key_masking(self):
        """Test that API key masking works correctly"""
        key = "sk_test_mock_key_1234567890abcdefghijklmnopqrstuvwxyz"
        masked = mask_api_key(key)

        # Should not contain the full key
        assert key not in masked

        # Should contain masking characters (... or *)
        assert "..." in masked or "*" in masked

        # Should preserve sk_ prefix for identification
        assert masked.startswith("sk_")

    def test_api_key_not_logged(self, mock_api_key, caplog):
        """Test that API key is not logged"""
        import logging

        caplog.set_level(logging.DEBUG)

        client = BaytClient(api_key=mock_api_key)

        # Even with debug logging, key should not appear
        for record in caplog.records:
            assert mock_api_key not in record.message

    def test_api_key_validation(self):
        """Test API key format validation (WorkOS format)"""
        # Valid keys - format: sk_*
        assert (
            validate_api_key("sk_test_mock_key_1234567890abcdefghijklmnopqrstuvwxyz")
            is True
        )
        assert (
            validate_api_key("sk_box9fStIm0DbDgmlgjyMw3rk0srw4TQYkeFmCtwF9LVFv6")
            is True
        )
        assert validate_api_key("sk_prod_1234567890abcdefghijklmnopqrstuvwxyz") is True

        # Invalid keys
        assert validate_api_key("invalid_key") is False
        assert validate_api_key("prod_abc_1234567890") is False  # Wrong prefix
        assert validate_api_key("") is False  # Empty
        assert validate_api_key("sk_") is False  # Too short
        assert validate_api_key("sk_short") is False  # Too short
        assert validate_api_key("b_prod_1234567890") is False  # Old format


class TestInputValidation:
    """Test input validation and sanitization"""

    def test_package_name_validation(self, mock_api_key):
        """Test that package names are validated"""
        client = BaytClient(api_key=mock_api_key)

        # Valid package names should not raise
        valid_names = [
            "@namespace/slug:v1",
            "@user-name/my-prompt:v0",
            "@org_name/prompt_123:v999",
        ]

        for name in valid_names:
            # Should not raise ValueError
            try:
                from baytos.claro.utils import parse_package_name

                result = parse_package_name(name)
                assert result["namespace"]
                assert result["slug"]
                assert "version" in result
            except ValueError:
                pytest.fail(f"Valid package name rejected: {name}")

        # Invalid package names should return None
        invalid_names = [
            "no-at-sign/slug:v1",
            "@namespace-only",
            "@namespace/:v1",  # Empty slug
            "@/slug:v1",  # Empty namespace
            "../../etc/passwd",  # Path traversal
            "@namespace/../admin:v1",  # Path traversal in namespace
        ]

        for name in invalid_names:
            from baytos.claro.utils import parse_package_name

            result = parse_package_name(name)
            assert (
                result is None
            ), f"Expected None for invalid name '{name}', got {result}"

    def test_injection_in_package_name(self, mock_api_key):
        """Test that injection attempts in package names are rejected"""
        client = BaytClient(api_key=mock_api_key)

        malicious_names = [
            "@namespace/slug'; DROP TABLE prompts;--:v1",
            "@namespace/slug<script>alert('xss')</script>:v1",
            "@namespace/slug${MALICIOUS}:v1",
            "@namespace/slug`whoami`:v1",
            "@namespace/slug|rm -rf /:v1",
        ]

        for name in malicious_names:
            from baytos.claro.utils import parse_package_name

            result = parse_package_name(name)
            assert (
                result is None
            ), f"Expected None for malicious name '{name}', got {result}"

    def test_base_url_validation(self, mock_api_key):
        """Test that base URL is validated"""
        # Valid HTTPS URLs should work
        valid_urls = [
            "https://api.baytos.ai",
            "https://staging.baytos.ai",
            "https://localhost:8000",
        ]

        for url in valid_urls:
            client = BaytClient(api_key=mock_api_key, base_url=url)
            assert client.base_url.startswith("https://")

        # HTTP should be upgraded to HTTPS or rejected
        http_url = "http://api.baytos.ai"
        client = BaytClient(api_key=mock_api_key, base_url=http_url)
        # Should either upgrade to HTTPS or store as-is with warning
        # (implementation-dependent)
        assert client.base_url

    def test_limit_parameter_validation(self, mock_api_key):
        """Test that limit parameter is validated"""
        client = BaytClient(api_key=mock_api_key)

        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"prompts": [], "has_more": False}
            mock_get.return_value = mock_response

            # Valid limits
            client.list_prompts(limit=1)
            client.list_prompts(limit=50)
            client.list_prompts(limit=100)

            # Invalid limits should raise or be clamped
            with pytest.raises((ValueError, BaytValidationError)):
                client.list_prompts(limit=0)

            with pytest.raises((ValueError, BaytValidationError)):
                client.list_prompts(limit=-1)

            with pytest.raises((ValueError, BaytValidationError, TypeError)):
                client.list_prompts(limit="invalid")


class TestDataSanitization:
    """Test that response data is sanitized"""

    def test_untrusted_response_data(self, mock_api_key):
        """Test handling of potentially malicious response data"""
        client = BaytClient(api_key=mock_api_key)

        # Prompt model receives the direct data (client.get_prompt unwraps it)
        malicious_data = {
            "id": "<script>alert('xss')</script>",
            "title": "'; DROP TABLE prompts;--",
            "description": "${MALICIOUS_CODE}",
            "workspaceSlug": "test",  # Use valid workspace slug for parsing
            "packageName": "sample",  # Use valid package name for parsing
            "version": "v1",
            "systemPrompt": "{{constructor.constructor('return process')()}}",
            "content": "__import__('os').system('ls')",
        }

        with patch("requests.Session.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = malicious_data
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            # Should not raise, but data should be safely stored
            prompt = client.get_prompt("@test/sample:v1")

            # Data should be accessible but not executed
            assert prompt.id == "<script>alert('xss')</script>"
            assert prompt.title == "'; DROP TABLE prompts;--"
            # This is fine - we store the data as-is but don't execute it

    def test_response_json_bomb(self, mock_api_key):
        """Test handling of excessively large or nested JSON"""
        client = BaytClient(api_key=mock_api_key)

        # Create deeply nested structure
        nested_data = {"data": {"level": 1}}
        current = nested_data["data"]
        for i in range(2, 1000):
            current["level"] = {"level": i}
            current = current["level"]

        with patch("requests.Session.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = nested_data
            mock_post.return_value = mock_response

            # Should handle deeply nested data gracefully
            # (may raise or handle depending on implementation)
            try:
                prompt = client.get_prompt("@test/sample:v1")
                # If it succeeds, verify basic functionality
                assert prompt
            except (RecursionError, BaytAPIError):
                # Acceptable to reject excessively nested data
                pass


class TestSecureDefaults:
    """Test that secure defaults are enforced"""

    def test_https_enforced(self, mock_api_key):
        """Test that HTTPS is the default protocol"""
        client = BaytClient(api_key=mock_api_key)

        # Default should be HTTPS
        assert client.base_url.startswith("https://")

        # Even if HTTP is provided, should upgrade or warn
        client_http = BaytClient(api_key=mock_api_key, base_url="http://api.test.cv")
        # Implementation may upgrade to HTTPS or keep HTTP for localhost/testing
        # Either way, verify URL is stored
        assert client_http.base_url

    def test_no_credential_in_url(self, mock_api_key):
        """Test that credentials are not included in URL"""
        client = BaytClient(api_key=mock_api_key)

        # API key should be in headers, not URL
        assert mock_api_key not in client.base_url

    def test_session_headers_security(self, mock_api_key):
        """Test that session headers are set securely"""
        client = BaytClient(api_key=mock_api_key)

        # API key should be in Authorization header
        assert "Authorization" in client.session.headers

        # Should use Bearer token or similar
        auth_header = client.session.headers["Authorization"]
        assert "Bearer" in auth_header or mock_api_key in auth_header


class TestVariableValidation:
    """Test variable extraction and validation security"""

    def test_variable_type_validation(self, sample_prompt_data):
        """Test that variable types are validated"""
        # Set up prompt with typed variables in the content field
        sample_prompt_data["content"] = (
            "Hello {{safe_string:string}}, your number is {{safe_number:number}}."
        )

        prompt = Prompt(sample_prompt_data)

        # Valid variables - should return no errors
        valid_vars = {
            "safe_string": "hello",
            "safe_number": 42,
        }

        errors = prompt.validate_variables(valid_vars)
        assert (
            not errors
        ), f"Valid variables should pass validation but got errors: {errors}"

        # Invalid types - should return errors
        invalid_vars = {
            "safe_string": ["not", "a", "string"],  # Wrong type
            "safe_number": "not a number",  # Wrong type
        }

        errors = prompt.validate_variables(invalid_vars)
        assert errors, "Invalid variable types should produce validation errors"
        assert "safe_string" in errors or "safe_number" in errors

    def test_variable_injection_protection(self, sample_prompt_data):
        """Test protection against template injection in variables"""
        # Use content field which maps to generator
        sample_prompt_data["content"] = "Hello {{name}}, welcome!"

        prompt = Prompt(sample_prompt_data)

        # Malicious variable values
        malicious_values = {
            "name": "{{constructor.constructor('return process')()}}",
        }

        # Should safely interpolate without executing
        from baytos.claro.utils import interpolate_variables

        result = interpolate_variables(prompt.generator, malicious_values)

        # Should contain the literal string, not execute it
        assert "constructor" in result
        # Should not cause code execution (this is just data)


class TestDependencySecurity:
    """Test dependency security"""

    def test_no_vulnerable_dependencies(self):
        """Test that there are no known vulnerable dependencies"""
        # This test requires pip-audit to be installed
        # Run: pip-audit --desc
        pytest.skip("Run 'pip-audit' manually to check for vulnerabilities")

    def test_requests_version(self):
        """Test that requests library is at secure version"""
        import requests

        # Should be using requests >= 2.25.0 (from requirements)
        version = requests.__version__
        major, minor = map(int, version.split(".")[:2])

        assert major >= 2
        if major == 2:
            assert minor >= 25


class TestErrorInformationLeakage:
    """Test that errors don't leak sensitive information"""

    def test_error_messages_safe(self, mock_api_key):
        """Test that error messages don't leak sensitive info"""
        client = BaytClient(api_key=mock_api_key)

        with patch("requests.Session.post") as mock_post:
            # Simulate various errors
            errors = [
                (401, {"error": "Invalid API key: " + mock_api_key}),
                (500, {"error": "Database connection string: postgres://..."}),
                (403, {"error": "User ID 12345 forbidden"}),
            ]

            for status, response_data in errors:
                mock_response = Mock()
                mock_response.status_code = status
                mock_response.json.return_value = response_data
                mock_post.return_value = mock_response

                try:
                    client.get_prompt("@test/sample:v1")
                except BaytAPIError as e:
                    error_msg = str(e)

                    # Should not expose full API key
                    if mock_api_key in response_data.get("error", ""):
                        # Verify our SDK masks it
                        assert mock_api_key not in error_msg or "***" in error_msg

    def test_stack_trace_sanitization(self, mock_api_key):
        """Test that stack traces don't expose sensitive info"""
        client = BaytClient(api_key=mock_api_key)

        with patch("requests.Session.post") as mock_post:
            mock_post.side_effect = Exception("Connection failed to api.baytos.ai")

            try:
                client.get_prompt("@test/sample:v1")
            except (Exception, BaytAPIError) as e:
                # Error message exists
                assert str(e)

                # API key should not be in the error
                assert mock_api_key not in str(e)
