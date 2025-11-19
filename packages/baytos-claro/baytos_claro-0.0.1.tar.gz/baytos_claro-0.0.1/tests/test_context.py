"""Unit tests for ContextItem class"""

import pytest
from baytos.claro.context import ContextItem


class TestContextItem:
    """Test ContextItem initialization and properties"""

    def test_url_context_creation(self):
        """Test creating a URL-type context item"""
        data = {
            "id": "ctx_123",
            "type": "url",
            "label": "Documentation",
            "url": "https://example.com/docs",
            "urlFetchedAt": 1234567890,
            "createdAt": 1234567800,
        }

        context = ContextItem(data)

        assert context.id == "ctx_123"
        assert context.type == "url"
        assert context.label == "Documentation"
        assert context.url == "https://example.com/docs"
        assert context.url_fetched_at == 1234567890
        assert context.created_at == 1234567800

    def test_file_context_creation(self):
        """Test creating a file-type context item"""
        data = {
            "id": "ctx_456",
            "type": "file",
            "label": "Report",
            "fileName": "report.pdf",
            "fileSize": 1024000,
            "mimeType": "application/pdf",
            "createdAt": 1234567900,
        }

        context = ContextItem(data)

        assert context.id == "ctx_456"
        assert context.type == "file"
        assert context.label == "Report"
        assert context.file_name == "report.pdf"
        assert context.file_size == 1024000
        assert context.mime_type == "application/pdf"
        assert context.created_at == 1234567900

    def test_is_file_method(self):
        """Test is_file() method"""
        url_context = ContextItem({"type": "url"})
        file_context = ContextItem({"type": "file"})

        assert not url_context.is_file()
        assert file_context.is_file()

    def test_is_url_method(self):
        """Test is_url() method"""
        url_context = ContextItem({"type": "url"})
        file_context = ContextItem({"type": "file"})

        assert url_context.is_url()
        assert not file_context.is_url()

    def test_file_properties_on_url_context(self):
        """Test that file properties return None for URL contexts"""
        url_context = ContextItem(
            {
                "type": "url",
                "url": "https://example.com",
            }
        )

        assert url_context.file_name is None
        assert url_context.file_size is None
        assert url_context.mime_type is None

    def test_url_properties_on_file_context(self):
        """Test that URL properties return None for file contexts"""
        file_context = ContextItem(
            {
                "type": "file",
                "fileName": "test.txt",
            }
        )

        assert file_context.url is None
        assert file_context.url_fetched_at is None

    def test_optional_label(self):
        """Test that label is optional"""
        context = ContextItem(
            {
                "type": "url",
                "url": "https://example.com",
            }
        )

        assert context.label is None

    def test_str_with_label(self):
        """Test string representation with label"""
        context = ContextItem(
            {
                "type": "file",
                "label": "My Document",
                "fileName": "doc.pdf",
            }
        )

        assert str(context) == "My Document (file)"

    def test_str_file_without_label(self):
        """Test string representation of file without label"""
        context = ContextItem(
            {
                "type": "file",
                "fileName": "report.pdf",
            }
        )

        assert str(context) == "report.pdf"

    def test_str_url_without_label(self):
        """Test string representation of URL without label"""
        context = ContextItem(
            {
                "type": "url",
                "url": "https://example.com/page",
            }
        )

        assert str(context) == "https://example.com/page"

    def test_repr_file(self):
        """Test repr for file context"""
        context = ContextItem(
            {
                "type": "file",
                "fileName": "test.txt",
                "fileSize": 1024,
            }
        )

        assert repr(context) == "<ContextItem type='file' name='test.txt' size=1024>"

    def test_repr_url(self):
        """Test repr for URL context"""
        context = ContextItem(
            {
                "type": "url",
                "url": "https://example.com",
            }
        )

        assert repr(context) == "<ContextItem type='url' url='https://example.com'>"

    def test_to_dict(self):
        """Test to_dict() method"""
        data = {
            "id": "ctx_789",
            "type": "file",
            "fileName": "data.csv",
            "fileSize": 2048,
            "mimeType": "text/csv",
        }

        context = ContextItem(data)
        result = context.to_dict()

        assert result == data
        assert result is not data  # Should be a copy

    def test_missing_fields_default_to_empty(self):
        """Test that missing fields have sensible defaults"""
        context = ContextItem({})

        assert context.id == ""
        assert context.type == "url"  # Default type
        assert context.label is None
        assert context.created_at is None


class TestContextItemIntegration:
    """Test ContextItem in realistic scenarios"""

    def test_file_context_full_workflow(self):
        """Test typical file context workflow"""
        data = {
            "id": "ctx_file_001",
            "type": "file",
            "label": "User Manual",
            "fileName": "manual.pdf",
            "fileSize": 5242880,  # 5MB
            "mimeType": "application/pdf",
            "createdAt": 1234567890,
        }

        context = ContextItem(data)

        # Type checking
        assert context.is_file()
        assert not context.is_url()

        # Metadata access
        assert context.label == "User Manual"
        assert context.file_name == "manual.pdf"
        assert context.file_size == 5242880
        assert context.mime_type == "application/pdf"

        # String representations
        assert "file" in repr(context)
        assert "User Manual" in str(context)

    def test_url_context_full_workflow(self):
        """Test typical URL context workflow"""
        data = {
            "id": "ctx_url_001",
            "type": "url",
            "label": "API Documentation",
            "url": "https://docs.example.com/api",
            "urlFetchedAt": 1234567890,
            "createdAt": 1234567800,
        }

        context = ContextItem(data)

        # Type checking
        assert context.is_url()
        assert not context.is_file()

        # Metadata access
        assert context.label == "API Documentation"
        assert context.url == "https://docs.example.com/api"
        assert context.url_fetched_at == 1234567890

        # String representations
        assert "url" in repr(context)
        assert "API Documentation" in str(context)

    def test_minimal_url_context(self):
        """Test URL context with only required fields"""
        data = {
            "id": "ctx_min",
            "type": "url",
            "url": "https://example.com",
        }

        context = ContextItem(data)

        assert context.id == "ctx_min"
        assert context.type == "url"
        assert context.url == "https://example.com"
        assert context.label is None
        assert context.url_fetched_at is None

    def test_minimal_file_context(self):
        """Test file context with only required fields"""
        data = {
            "id": "ctx_min_file",
            "type": "file",
            "fileName": "file.txt",
            "fileSize": 100,
            "mimeType": "text/plain",
        }

        context = ContextItem(data)

        assert context.id == "ctx_min_file"
        assert context.type == "file"
        assert context.file_name == "file.txt"
        assert context.file_size == 100
        assert context.mime_type == "text/plain"
        assert context.label is None
