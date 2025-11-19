"""Tests for data models"""

import pytest
from baytos.claro.models import Prompt
from .test_helpers import (
    PromptDataFactory,
    assert_prompt_has_required_fields,
    assert_context_item_valid,
)


class TestPromptModel:
    """Test Prompt model"""

    @pytest.fixture
    def sample_prompt_data(self):
        """Sample prompt data from API"""
        return PromptDataFactory.create_full(
            workspace_slug="alice", package_name="test-prompt"
        )

    def test_property_access(self, sample_prompt_data):
        """Test accessing prompt properties"""
        prompt = Prompt(sample_prompt_data)

        assert prompt.id == "prompt_123"
        assert prompt.title == "Test Prompt"
        assert prompt.content == "This is the main prompt content"
        assert prompt.generator == "This is the main prompt content"  # Alias
        assert prompt.system == "You are a helpful assistant"
        assert prompt.critique == "Evaluate the response"
        assert prompt.description == "A test prompt for unit tests"
        assert prompt.category == "testing"
        assert prompt.namespace == "alice"
        assert prompt.slug == "test-prompt"
        assert prompt.version == "v1"

    def test_dictionary_access(self, sample_prompt_data):
        """Test dictionary-style access"""
        prompt = Prompt(sample_prompt_data)

        assert prompt["title"] == "Test Prompt"
        assert prompt["content"] == "This is the main prompt content"
        assert prompt.get("title") == "Test Prompt"
        assert prompt.get("missing_field") is None
        assert prompt.get("missing_field", "default") == "default"

    def test_dictionary_methods(self, sample_prompt_data):
        """Test dictionary methods"""
        prompt = Prompt(sample_prompt_data)

        keys = prompt.keys()
        assert "title" in keys
        assert "content" in keys
        assert len(keys) == len(sample_prompt_data)

        values = prompt.values()
        assert "Test Prompt" in values

        items = prompt.items()
        assert ("title", "Test Prompt") in items

    def test_missing_fields(self):
        """Test handling of missing fields"""
        minimal_data = PromptDataFactory.create_minimal(
            workspace_slug="alice", package_name="minimal"
        )

        prompt = Prompt(minimal_data)

        assert prompt.system == ""
        assert prompt.critique == ""
        assert prompt.description is None
        assert prompt.version == "v1"  # Default version from factory

    def test_package_name(self, sample_prompt_data):
        """Test package name generation"""
        prompt = Prompt(sample_prompt_data)
        assert prompt.package_name == "@alice/test-prompt:v1"

    def test_has_methods(self, sample_prompt_data):
        """Test has_system_prompt and has_critique_prompt methods"""
        prompt = Prompt(sample_prompt_data)
        assert prompt.has_system_prompt() is True
        assert prompt.has_critique_prompt() is True

        # Test without prompts
        minimal_data = sample_prompt_data.copy()
        minimal_data["systemPrompt"] = ""
        minimal_data["critiquePrompt"] = ""

        minimal_prompt = Prompt(minimal_data)
        assert minimal_prompt.has_system_prompt() is False
        assert minimal_prompt.has_critique_prompt() is False

    def test_string_representations(self, sample_prompt_data):
        """Test __str__ and __repr__ methods"""
        prompt = Prompt(sample_prompt_data)

        assert str(prompt) == "Test Prompt"
        assert repr(prompt) == "<Prompt 'Test Prompt' @alice/test-prompt:v1>"

    def test_to_dict(self, sample_prompt_data):
        """Test to_dict method"""
        prompt = Prompt(sample_prompt_data)
        data = prompt.to_dict()

        assert data == sample_prompt_data
        # Ensure it's a copy
        data["title"] = "Modified"
        assert prompt.title == "Test Prompt"

    def test_context_property_empty(self, sample_prompt_data):
        """Test context property with no context items"""
        prompt = Prompt(sample_prompt_data)

        assert prompt.context == []
        assert prompt.has_context() is False

    def test_context_property_with_items(self):
        """Test context property with mixed context items"""
        data = PromptDataFactory.create_with_context(
            workspace_slug="alice", package_name="test", has_files=True, has_urls=True
        )

        prompt = Prompt(data)

        assert len(prompt.context) == 2
        assert prompt.has_context() is True

        # Check that context items are ContextItem objects
        from baytos.claro.context import ContextItem

        assert all(isinstance(item, ContextItem) for item in prompt.context)

        # Verify individual items
        assert prompt.context[0].type == "url"
        assert prompt.context[0].url == "https://example.com/docs"
        assert prompt.context[1].type == "file"
        assert prompt.context[1].file_name == "report.pdf"

    def test_get_file_contexts(self):
        """Test get_file_contexts method"""
        data = PromptDataFactory.create_with_context(
            workspace_slug="alice", package_name="test", has_files=True, has_urls=True
        )

        prompt = Prompt(data)
        files = prompt.get_file_contexts()

        assert len(files) == 1
        assert all(item.is_file() for item in files)
        assert files[0].file_name == "report.pdf"

    def test_get_url_contexts(self):
        """Test get_url_contexts method"""
        data = PromptDataFactory.create_with_context(
            workspace_slug="alice", package_name="test", has_files=True, has_urls=True
        )

        prompt = Prompt(data)
        urls = prompt.get_url_contexts()

        assert len(urls) == 1
        assert all(item.is_url() for item in urls)
        assert urls[0].url == "https://example.com/docs"

    def test_get_contexts_empty(self, sample_prompt_data):
        """Test get_file_contexts and get_url_contexts on prompt with no context"""
        prompt = Prompt(sample_prompt_data)

        assert prompt.get_file_contexts() == []
        assert prompt.get_url_contexts() == []
