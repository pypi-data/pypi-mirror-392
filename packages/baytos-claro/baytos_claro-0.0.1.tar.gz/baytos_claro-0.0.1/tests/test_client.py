"""Tests for the Bayt client"""

import os
import pytest
from unittest.mock import Mock, patch
import requests

from baytos.claro import BaytClient, Prompt
from baytos.claro.exceptions import (
    BaytAPIError,
    BaytAuthError,
    BaytNotFoundError,
    BaytRateLimitError,
    BaytValidationError,
)


class TestBaytClient:
    """Test BaytClient class"""

    def test_init_with_api_key(self):
        """Test client initialization with API key"""
        client = BaytClient(
            api_key="sk_test_mock_client_key_1234567890abcdefghijklmnopqrst"
        )
        assert (
            client.api_key == "sk_test_mock_client_key_1234567890abcdefghijklmnopqrst"
        )
        assert client.base_url == "https://api.baytos.ai"

    def test_init_with_env_var(self):
        """Test client initialization with environment variable"""
        with patch.dict(
            os.environ,
            {"BAYT_API_KEY": "sk_test_mock_dev_key_1234567890abcdefghijklmnopqrstuv"},
        ):
            client = BaytClient()
            assert (
                client.api_key
                == "sk_test_mock_dev_key_1234567890abcdefghijklmnopqrstuv"
            )

    def test_init_without_api_key(self):
        """Test client initialization without API key raises error"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API key is required"):
                BaytClient()

    def test_init_with_invalid_api_key(self):
        """Test client initialization with invalid API key format"""
        with pytest.raises(ValueError, match="Invalid API key format"):
            BaytClient(api_key="invalid_key")

    def test_custom_base_url(self):
        """Test client with custom base URL"""
        client = BaytClient(
            api_key="sk_test_mock_client_key_1234567890abcdefghijklmnopqrst",
            base_url="https://api.bayt.dev/",
        )
        assert client.base_url == "https://api.bayt.dev"  # Trailing slash removed

    @patch("requests.Session.post")
    def test_get_prompt_success(self, mock_post):
        """Test successful prompt retrieval"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "prompt_123",
            "title": "Test Prompt",
            "content": "Main content",
            "systemPrompt": "System prompt",
            "critiquePrompt": "Critique prompt",
            "description": "Description",
            "category": "testing",
            "workspaceSlug": "alice",
            "packageName": "test-prompt",
            "version": "v1",
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = BaytClient(
            api_key="sk_test_mock_client_key_1234567890abcdefghijklmnopqrst"
        )
        prompt = client.get_prompt("@alice/test-prompt:v1")

        assert isinstance(prompt, Prompt)
        assert prompt.title == "Test Prompt"
        assert prompt.namespace == "alice"
        assert prompt.slug == "test-prompt"

        # Verify request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.baytos.ai/v1/prompts/get"
        assert kwargs["json"] == {"package_name": "@alice/test-prompt:v1"}
        assert kwargs["timeout"] == 30

    @patch("requests.Session.post")
    def test_get_prompt_invalid_package_name(self, mock_post):
        """Test get_prompt with invalid package name"""
        client = BaytClient(
            api_key="sk_test_mock_client_key_1234567890abcdefghijklmnopqrst"
        )

        with pytest.raises(BaytValidationError, match="Invalid package name format"):
            client.get_prompt("invalid-package-name")

        # Should not make API call
        mock_post.assert_not_called()

    @patch("requests.Session.post")
    def test_get_prompt_auth_error(self, mock_post):
        """Test get_prompt with authentication error"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_post.return_value = mock_response

        client = BaytClient(
            api_key="sk_test_mock_client_key_1234567890abcdefghijklmnopqrst"
        )

        with pytest.raises(BaytAuthError, match="Invalid API key"):
            client.get_prompt("@alice/test-prompt:v1")

    @patch("requests.Session.post")
    def test_get_prompt_forbidden(self, mock_post):
        """Test get_prompt with forbidden error"""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_post.return_value = mock_response

        client = BaytClient(
            api_key="sk_test_mock_client_key_1234567890abcdefghijklmnopqrst"
        )

        with pytest.raises(BaytAuthError, match="Insufficient permissions"):
            client.get_prompt("@alice/test-prompt:v1")

    @patch("requests.Session.post")
    def test_get_prompt_not_found(self, mock_post):
        """Test get_prompt with not found error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = '{"error": "Prompt not found"}'
        mock_response.json.return_value = {"error": "Prompt not found"}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_post.return_value = mock_response

        client = BaytClient(
            api_key="sk_test_mock_client_key_1234567890abcdefghijklmnopqrst"
        )

        with pytest.raises(BaytNotFoundError, match="Prompt not found"):
            client.get_prompt("@alice/missing:v1")

    @patch("requests.Session.post")
    def test_get_prompt_rate_limit(self, mock_post):
        """Test get_prompt with rate limit error (no retries)"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_post.return_value = mock_response

        # Disable retries for fast test
        client = BaytClient(
            api_key="sk_test_mock_client_key_1234567890abcdefghijklmnopqrst",
            max_retries=0,
        )

        with pytest.raises(BaytRateLimitError, match="rate limit exceeded"):
            client.get_prompt("@alice/test-prompt:v1")

    @patch("requests.Session.post")
    @patch("time.sleep")  # Mock sleep to make test fast
    def test_get_prompt_rate_limit_with_retry_success(self, mock_sleep, mock_post):
        """Test that rate limit retries work and eventually succeed"""
        call_count = 0

        def mock_response_generator(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            mock_resp = Mock()
            if call_count <= 2:
                # First 2 calls return 429
                mock_resp.status_code = 429
                mock_resp.headers = {"Retry-After": "1"}
            else:
                # Third call succeeds
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "id": "test123",
                    "title": "Test Prompt",
                    "content": "Test content",
                    "systemPrompt": "System",
                    "critiquePrompt": "Critique",
                }
                mock_resp.raise_for_status.return_value = None

            return mock_resp

        mock_post.side_effect = mock_response_generator

        client = BaytClient(
            api_key="sk_test_mock_client_key_1234567890abcdefghijklmnopqrst",
            max_retries=3,
        )

        # Should succeed after retries
        prompt = client.get_prompt("@alice/test:v1")
        assert prompt.title == "Test Prompt"
        assert call_count == 3  # Verify it retried

        # Verify sleep was called for retries
        assert mock_sleep.call_count == 2  # Slept twice before success

    @patch("requests.Session.post")
    def test_get_prompt_timeout(self, mock_post):
        """Test get_prompt with timeout"""
        mock_post.side_effect = requests.exceptions.Timeout()

        client = BaytClient(
            api_key="sk_test_mock_client_key_1234567890abcdefghijklmnopqrst"
        )

        with pytest.raises(BaytAPIError, match="Request timed out"):
            client.get_prompt("@alice/test-prompt:v1")

    @patch("requests.Session.post")
    def test_get_prompt_connection_error(self, mock_post):
        """Test get_prompt with connection error"""
        mock_post.side_effect = requests.exceptions.ConnectionError()

        client = BaytClient(
            api_key="sk_test_mock_client_key_1234567890abcdefghijklmnopqrst"
        )

        with pytest.raises(BaytAPIError, match="Failed to connect"):
            client.get_prompt("@alice/test-prompt:v1")

    @patch("requests.Session.get")
    def test_list_prompts_success(self, mock_get):
        """Test successful prompt listing"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "prompts": [
                {
                    "id": "prompt_1",
                    "title": "Prompt 1",
                    "content": "Content 1",
                    "category": "test",
                    "workspaceSlug": "alice",
                    "packageName": "prompt-1",
                },
                {
                    "id": "prompt_2",
                    "title": "Prompt 2",
                    "content": "Content 2",
                    "category": "test",
                    "workspaceSlug": "alice",
                    "packageName": "prompt-2",
                },
            ],
            "cursor": "next_cursor",
            "hasMore": True,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = BaytClient(
            api_key="sk_test_mock_key_abc123_1234567890abcdefghijklmnopqrs"
        )
        result = client.list_prompts(limit=10, cursor="prev_cursor")

        assert len(result["prompts"]) == 2
        assert all(isinstance(p, Prompt) for p in result["prompts"])
        assert result["cursor"] == "next_cursor"
        assert result["hasMore"] is True

        # Verify request
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == "https://api.baytos.ai/v1/prompts"
        assert kwargs["params"] == {"limit": 10, "cursor": "prev_cursor"}

    def test_list_prompts_invalid_limit(self):
        """Test list_prompts with invalid limit"""
        client = BaytClient(
            api_key="sk_test_mock_key_abc123_1234567890abcdefghijklmnopqrs"
        )

        with pytest.raises(
            BaytValidationError, match="Limit must be between 1 and 100"
        ):
            client.list_prompts(limit=0)

        with pytest.raises(
            BaytValidationError, match="Limit must be between 1 and 100"
        ):
            client.list_prompts(limit=101)
