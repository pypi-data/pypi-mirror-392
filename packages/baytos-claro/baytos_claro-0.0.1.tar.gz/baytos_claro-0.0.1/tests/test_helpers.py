"""Test helpers and utilities for Bayt SDK tests

This module provides:
- PromptDataFactory: Centralized test data creation
- Assertion helpers: Reusable test assertions
"""

from typing import Dict, Any, List, Optional


class PromptDataFactory:
    """Factory for creating test prompt data structures

    Centralizes test data creation to eliminate duplication and make
    field name changes easier to manage.
    """

    @staticmethod
    def create_minimal(
        workspace_slug: str = "testuser",
        package_name: str = "test-prompt",
        version: str = "v1",
    ) -> Dict[str, Any]:
        """Create minimal valid prompt data"""
        return {
            "id": "prompt_123",
            "title": "Test Prompt",
            "content": "Test content",
            "category": "test",
            "workspaceSlug": workspace_slug,
            "packageName": package_name,
            "version": version,
        }

    @staticmethod
    def create_full(
        workspace_slug: str = "alice",
        package_name: str = "test-prompt",
        version: str = "v1",
        **overrides,
    ) -> Dict[str, Any]:
        """Create complete prompt data with all fields"""
        data = {
            "id": "prompt_123",
            "title": "Test Prompt",
            "content": "This is the main prompt content",
            "systemPrompt": "You are a helpful assistant",
            "critiquePrompt": "Evaluate the response",
            "description": "A test prompt for unit tests",
            "category": "testing",
            "workspaceSlug": workspace_slug,
            "packageName": package_name,
            "version": version,
            "tags": ["test", "sample"],
            "metadata": {"createdAt": 1234567890},
            "context": [],
        }
        data.update(overrides)
        return data

    @staticmethod
    def create_with_context(
        has_files: bool = True, has_urls: bool = True, **kwargs
    ) -> Dict[str, Any]:
        """Create prompt with context items (files and/or URLs)"""
        data = PromptDataFactory.create_full(**kwargs)
        context = []

        if has_urls:
            context.append(
                {
                    "id": "ctx_url_1",
                    "type": "url",
                    "label": "Documentation",
                    "url": "https://example.com/docs",
                    "createdAt": 1234567890,
                }
            )

        if has_files:
            context.append(
                {
                    "id": "ctx_2",
                    "type": "file",
                    "fileName": "report.pdf",
                    "fileSize": 1024000,
                    "mimeType": "application/pdf",
                    "createdAt": 1234567900,
                }
            )

        data["context"] = context
        return data

    @staticmethod
    def create_draft(
        workspace_slug: str = "alice", package_name: str = "draft-prompt", **kwargs
    ) -> Dict[str, Any]:
        """Create draft (v0) prompt data"""
        return PromptDataFactory.create_full(
            workspace_slug=workspace_slug,
            package_name=package_name,
            version="v0",
            is_draft=True,
            **kwargs,
        )

    @staticmethod
    def create_large(
        num_variables: int = 50, content_size: int = 100000, **kwargs
    ) -> Dict[str, Any]:
        """Create large prompt for performance testing"""
        # Create content with embedded variables
        vars_string = " ".join([f"{{{{var{i}}}}}" for i in range(num_variables)])
        padding_size = content_size - len(vars_string) - 1
        content_with_vars = vars_string + " " + ("G" * padding_size)

        return PromptDataFactory.create_full(
            package_name="large-prompt",
            content=content_with_vars,
            systemPrompt="S" * 50000,
            critiquePrompt="C" * 50000,
            description="A" * 10000,
            **kwargs,
        )

    @staticmethod
    def create_list_response(
        count: int = 2,
        workspace_slug: str = "testuser",
        has_more: bool = False,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create list prompts response"""
        prompts = [
            {
                "id": f"prompt{i}",
                "title": f"Prompt {i}",
                "packageName": f"prompt-{i}",
                "workspaceSlug": workspace_slug,
                "version": "v1",
                "category": "test",
                "tags": [],
                "metadata": {"createdAt": 1234567890 + i},
            }
            for i in range(1, count + 1)
        ]

        return {
            "prompts": prompts,
            "next_cursor": cursor,
            "hasMore": has_more,
            "cursor": cursor,  # Legacy field
        }


# Assertion Helpers


def assert_prompt_has_required_fields(prompt) -> None:
    """Assert prompt has all required fields with values

    Args:
        prompt: Prompt instance to check

    Raises:
        AssertionError: If any required field is missing or empty
    """
    assert prompt.id, "Prompt must have an id"
    assert prompt.title, "Prompt must have a title"
    assert prompt.namespace, "Prompt must have a namespace (workspaceSlug)"
    assert prompt.slug, "Prompt must have a slug (packageName)"
    assert isinstance(prompt.version, str), "Prompt version must be a string"


def assert_context_item_valid(item) -> None:
    """Assert context item has valid structure

    Args:
        item: ContextItem instance to check

    Raises:
        AssertionError: If context item is invalid
    """
    assert item.id, "Context item must have an id"
    assert item.type in (
        "url",
        "file",
    ), f"Context type must be 'url' or 'file', got {item.type}"

    if item.is_url():
        assert item.url, "URL context must have a url"
        assert item.url.startswith(
            ("http://", "https://")
        ), "URL must start with http:// or https://"

    if item.is_file():
        assert item.file_name, "File context must have a file_name"
        assert item.file_size is not None, "File context must have a file_size"
        assert item.file_size >= 0, "File size must be non-negative"
        assert item.mime_type, "File context must have a mime_type"


def assert_prompt_list_response_valid(response: Dict[str, Any]) -> None:
    """Assert list response has valid structure

    Args:
        response: List response dict to check

    Raises:
        AssertionError: If response structure is invalid
    """
    assert "prompts" in response, "Response must have 'prompts' field"
    assert isinstance(response["prompts"], list), "'prompts' must be a list"
    assert "hasMore" in response, "Response must have 'hasMore' field"
    assert isinstance(response["hasMore"], bool), "'hasMore' must be a boolean"
