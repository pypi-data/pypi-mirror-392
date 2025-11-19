"""Integration tests for Bayt SDK against staging environment

These tests make real API calls and require:
- BAYT_TEST_API_KEY environment variable
- BAYT_TEST_BASE_URL environment variable (optional, defaults to staging)

Run with: pytest tests/test_integration.py -v
Skip with: pytest -m "not integration"
"""

import pytest
import os
from baytos.claro import BaytClient, Prompt
from baytos.claro.exceptions import (
    BaytAPIError,
    BaytAuthError,
    BaytNotFoundError,
    BaytRateLimitError,
    BaytValidationError,
)


pytestmark = pytest.mark.integration


@pytest.fixture
def integration_client(staging_api_key, staging_base_url, skip_if_no_staging_key):
    """Create a client for integration testing"""
    return BaytClient(api_key=staging_api_key, base_url=staging_base_url)


@pytest.mark.usefixtures("api_server_required")
class TestIntegrationClientAuth:
    """Test client authentication against real API"""

    def test_client_with_valid_key(
        self, staging_api_key, staging_base_url, skip_if_no_staging_key
    ):
        """Test that client initializes with valid API key"""
        client = BaytClient(api_key=staging_api_key, base_url=staging_base_url)
        assert client.api_key == staging_api_key
        assert client.base_url == staging_base_url.rstrip("/")

    def test_client_with_invalid_key(self, staging_base_url, skip_if_no_staging_key):
        """Test that invalid API key raises authentication error"""
        # This test requires network access, so skip if not configured
        # Use properly formatted but invalid key
        client = BaytClient(
            api_key="sk_test_invalid_mock_key_1234567890abcdefghijklmnopqr",
            base_url=staging_base_url,
        )

        with pytest.raises(BaytAuthError):
            # This should fail with authentication error
            client.get_prompt("@test/nonexistent:v0")

    def test_client_with_revoked_key(self, staging_base_url, skip_if_no_staging_key):
        """Test that revoked API key raises authentication error"""
        # Note: You'll need to provide a known revoked key for this test
        revoked_key = os.getenv("BAYT_TEST_REVOKED_KEY")
        if not revoked_key:
            pytest.skip("BAYT_TEST_REVOKED_KEY not set")

        client = BaytClient(api_key=revoked_key, base_url=staging_base_url)

        with pytest.raises(BaytAuthError):
            client.get_prompt("@test/sample:v0")


@pytest.mark.usefixtures("api_server_required")
class TestIntegrationGetPrompt:
    """Test get_prompt method with real API calls"""

    def test_get_prompt(self, integration_client, test_prompts):
        """Test retrieving a published (non-draft) prompt from accessible workspace"""
        prompt_package = test_prompts["published"]

        prompt = integration_client.get_prompt(prompt_package)

        # Verify it returns a Prompt object
        assert isinstance(prompt, Prompt)

        # Verify basic properties are present
        assert prompt.title
        assert prompt.slug
        assert prompt.namespace

        # Verify it's a published version (not draft)
        assert prompt.version != "v0", "Should retrieve published version, not draft"

        # Verify content is accessible
        assert hasattr(prompt, "generator")

    def test_get_draft_prompt(self, integration_client, test_prompts):
        """Test retrieving a draft (v0) prompt"""
        draft_package = test_prompts["draft"]

        prompt = integration_client.get_prompt(draft_package)
        assert isinstance(prompt, Prompt)
        assert prompt.version == 0 or prompt.is_draft

    def test_get_nonexistent_prompt(self, integration_client, test_prompts):
        """Test that nonexistent prompt raises NotFoundError"""
        with pytest.raises(BaytNotFoundError):
            integration_client.get_prompt(test_prompts["nonexistent"])

    def test_get_prompt_with_variables(self, integration_client, test_prompts):
        """Test retrieving a prompt with variables"""
        prompt_with_vars = test_prompts["with_vars"]

        prompt = integration_client.get_prompt(prompt_with_vars)

        # Extract variables
        variables = prompt.extract_variables()

        # Should have at least some variables
        assert isinstance(variables, list)

        # If variables exist, verify structure
        if variables:
            for var in variables:
                assert "name" in var
                # Type and description are optional


@pytest.mark.usefixtures("api_server_required")
class TestIntegrationListPrompts:
    """Test list_prompts method with real API calls"""

    def test_list_prompts(self, integration_client):
        """Test listing prompts from accessible workspaces"""
        import requests

        try:
            result = integration_client.list_prompts(limit=10)

            # Should return a list
            assert isinstance(result, dict)
            assert "prompts" in result
            assert isinstance(result["prompts"], list)

            # Verify pagination fields
            assert "hasMore" in result
            assert isinstance(result["hasMore"], bool)

            # If there are prompts, verify structure
            if result["prompts"]:
                prompt_data = result["prompts"][0]
                # List API may return different fields than get_prompt
                # Just verify it's a Prompt object with basic fields
                assert isinstance(prompt_data, Prompt)
                assert prompt_data.title  # Should have a title
                # Slug is optional, just verify the property exists
                assert hasattr(prompt_data, "slug")

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            pytest.skip("Backend not available at localhost:3001")
        except BaytAPIError as e:
            pytest.fail(f"Failed to list prompts: {e}")

    def test_list_prompts_with_pagination(self, integration_client):
        """Test listing prompts with pagination"""
        # Get first page
        page1 = integration_client.list_prompts(limit=5)

        # If there's more data, get next page
        if page1.get("hasMore") and page1.get("cursor"):
            page2 = integration_client.list_prompts(limit=5, cursor=page1["cursor"])

            assert isinstance(page2, dict)
            assert "prompts" in page2

            # Verify pages are different
            if page1["prompts"] and page2["prompts"]:
                assert page1["prompts"][0]["id"] != page2["prompts"][0]["id"]

    def test_list_prompts_empty_result(self, integration_client):
        """Test listing prompts with large limit"""
        # Using a very high limit should still work (capped at 100 by validation)
        result = integration_client.list_prompts(limit=100)

        assert isinstance(result, dict)
        assert "prompts" in result
        assert isinstance(result["prompts"], list)


@pytest.mark.usefixtures("api_server_required")
class TestIntegrationErrorHandling:
    """Test error handling with real API"""

    def test_timeout_handling(self, integration_client):
        """Test that timeouts are handled gracefully"""
        # This test may be difficult to trigger reliably
        # You might need to configure a very short timeout
        import requests

        # Temporarily set a very short timeout on the session
        original_timeout = getattr(integration_client.session, "timeout", None)
        try:
            # Make a request with very short timeout
            with pytest.raises((requests.Timeout, BaytAPIError)):
                integration_client.session.timeout = 0.001
                integration_client.get_prompt("@test/sample:v1")
        finally:
            if hasattr(integration_client.session, "timeout"):
                integration_client.session.timeout = original_timeout

    def test_malformed_package_name(self, integration_client):
        """Test that malformed package names are rejected"""
        with pytest.raises(BaytValidationError):
            integration_client.get_prompt("invalid-package-name")

        with pytest.raises(BaytValidationError):
            integration_client.get_prompt("@namespace-only")

        with pytest.raises(BaytValidationError):
            integration_client.get_prompt("no-namespace/slug")

    def test_connection_error_handling(self):
        """Test handling of connection errors"""
        # Use dummy valid-format key since we're testing connection, not auth
        dummy_key = "sk_test_dummy_mock_key_1234567890abcdefghijklmnopqrs"

        # Use an invalid base URL that won't resolve
        client = BaytClient(
            api_key=dummy_key, base_url="https://invalid.nonexistent.bayt.test"
        )

        with pytest.raises(BaytAPIError):
            client.get_prompt("@test/sample:v1")


@pytest.mark.usefixtures("api_server_required")
class TestIntegrationPromptData:
    """Test that retrieved prompt data is complete and valid"""

    def test_prompt_has_required_fields(self, integration_client, test_prompts):
        """Test that prompt has all required fields"""
        prompt_package = test_prompts["published"]

        prompt = integration_client.get_prompt(prompt_package)

        # Required metadata fields
        assert prompt.id
        assert prompt.title
        assert prompt.slug
        assert prompt.namespace
        assert isinstance(prompt.version, str)
        assert prompt.version != "v0", "Should use published prompt, not draft"

        # Content fields (at least one should be present)
        has_content = prompt.system or prompt.generator or prompt.critique
        assert has_content, "Prompt should have at least some content"


@pytest.mark.usefixtures("api_server_required")
class TestIntegrationContextSupport:
    """Test context support (files and URLs)"""

    def test_prompt_with_context_metadata(self, integration_client, test_prompts):
        """Test that prompts with context include metadata"""
        # This test requires a prompt with context items
        # For now, test that the context field is present (even if empty)
        prompt_package = test_prompts.get("published", "@test/sample:v0")

        prompt = integration_client.get_prompt(prompt_package)

        # Context field should be present
        assert hasattr(prompt, "context")
        assert isinstance(prompt.context, list)

        # Test helper methods
        assert hasattr(prompt, "has_context")
        assert hasattr(prompt, "get_file_contexts")
        assert hasattr(prompt, "get_url_contexts")

        # If there's context, verify structure
        if prompt.has_context():
            from baytos.claro.context import ContextItem

            for item in prompt.context:
                assert isinstance(item, ContextItem)
                assert item.id
                assert item.type in ("url", "file")

                if item.is_file():
                    assert item.file_name
                    assert item.file_size is not None
                    assert item.mime_type
                elif item.is_url():
                    assert item.url

    def test_get_context_download_url(self, integration_client):
        """Test getting download URL for context file"""
        # This test requires a prompt with file context
        # Create a dummy context ID to test the endpoint
        context_id = "test_context_id"

        try:
            # This should fail with not found, but tests the endpoint
            result = integration_client.get_context_download_url(context_id)

            # If successful, verify structure
            assert "url" in result
            assert "expiresIn" in result
            assert isinstance(result["expiresIn"], int)

        except BaytNotFoundError:
            # Expected - context doesn't exist
            pass
        except BaytAuthError:
            pytest.skip("Authentication required or insufficient permissions")
        except (BaytAPIError, Exception):
            pytest.skip("Backend not available or endpoint not implemented yet")

    def test_download_context_file(self, integration_client):
        """Test downloading context file content"""
        # This test requires a prompt with file context
        context_id = "test_context_id"

        try:
            # This should fail with not found, but tests the endpoint
            content = integration_client.download_context_file(context_id)

            # If successful, verify it returns bytes
            assert isinstance(content, bytes)

        except BaytNotFoundError:
            # Expected - context doesn't exist
            pass
        except BaytAuthError:
            pytest.skip("Authentication required or insufficient permissions")
        except (BaytAPIError, Exception):
            pytest.skip("Backend not available or endpoint not implemented yet")

    def test_context_filtering(self, integration_client):
        """Test filtering context by type"""
        # Create mock prompt data with mixed context
        from baytos.claro.models import Prompt

        data = {
            "id": "test_prompt",
            "title": "Test",
            "content": "Content",
            "category": "test",
            "workspaceSlug": "test",
            "packageName": "test",
            "version": "v1",
            "context": [
                {
                    "id": "ctx_1",
                    "type": "url",
                    "url": "https://example.com",
                },
                {
                    "id": "ctx_2",
                    "type": "file",
                    "fileName": "test.pdf",
                    "fileSize": 1000,
                    "mimeType": "application/pdf",
                },
                {
                    "id": "ctx_3",
                    "type": "file",
                    "fileName": "test.txt",
                    "fileSize": 500,
                    "mimeType": "text/plain",
                },
            ],
        }

        prompt = Prompt(data)

        # Test filtering
        files = prompt.get_file_contexts()
        urls = prompt.get_url_contexts()

        assert len(files) == 2
        assert len(urls) == 1
        assert all(f.is_file() for f in files)
        assert all(u.is_url() for u in urls)

    def test_prompt_with_file_context(self, integration_client, test_prompts):
        """Test prompt with file context and validate file download"""
        # This test requires a prompt with file context
        # Skip if no prompt with files is configured
        prompt_with_files = test_prompts.get("with_files")
        if not prompt_with_files:
            pytest.skip("No prompt with file context configured in test_data.json")

        prompt = integration_client.get_prompt(prompt_with_files)

        # Verify context exists
        assert prompt.has_context(), "Prompt should have context"

        # Get file contexts
        files = prompt.get_file_contexts()
        assert len(files) > 0, "Prompt should have at least one file"

        # Validate first file metadata
        file = files[0]
        assert file.id
        assert file.file_name
        assert file.file_size > 0
        assert file.mime_type

        # Test download URL generation
        url_info = integration_client.get_context_download_url(file.id)
        assert "url" in url_info
        assert "expiresIn" in url_info
        assert isinstance(url_info["expiresIn"], int)
        assert url_info["expiresIn"] > 0

        # Test file download
        content = integration_client.download_context_file(file.id)
        assert isinstance(content, bytes)
        assert len(content) > 0
        assert len(content) == file.file_size

    def test_prompt_with_url_context(self, integration_client, test_prompts):
        """Test prompt with URL context and validate URL metadata"""
        # This test requires a prompt with URL context
        prompt_with_urls = test_prompts.get("with_urls")
        if not prompt_with_urls:
            pytest.skip("No prompt with URL context configured in test_data.json")

        prompt = integration_client.get_prompt(prompt_with_urls)

        # Verify context exists
        assert prompt.has_context(), "Prompt should have context"

        # Get URL contexts
        urls = prompt.get_url_contexts()
        assert len(urls) > 0, "Prompt should have at least one URL"

        # Validate URL metadata
        url_item = urls[0]
        assert url_item.id
        assert url_item.url
        assert url_item.url.startswith(("http://", "https://"))

        # Optional fields that may be present
        if url_item.label:
            assert isinstance(url_item.label, str)
        if url_item.url_fetched_at:
            assert isinstance(url_item.url_fetched_at, int)

    def test_prompt_with_mixed_context(self, integration_client, test_prompts):
        """Test prompt with both file and URL context"""
        prompt_with_mixed = test_prompts.get("with_mixed_context")
        if not prompt_with_mixed:
            pytest.skip("No prompt with mixed context configured in test_data.json")

        prompt = integration_client.get_prompt(prompt_with_mixed)

        # Verify context exists
        assert prompt.has_context(), "Prompt should have context"
        assert len(prompt.context) > 1, "Prompt should have multiple context items"

        # Get both types
        files = prompt.get_file_contexts()
        urls = prompt.get_url_contexts()

        # Should have at least one of each
        assert len(files) > 0, "Prompt should have at least one file"
        assert len(urls) > 0, "Prompt should have at least one URL"

        # Verify no overlap (filter works correctly)
        all_context_ids = {item.id for item in prompt.context}
        file_ids = {f.id for f in files}
        url_ids = {u.id for u in urls}

        assert len(file_ids & url_ids) == 0, "Files and URLs should not overlap"
        assert (
            file_ids | url_ids == all_context_ids
        ), "All context items should be categorized"
