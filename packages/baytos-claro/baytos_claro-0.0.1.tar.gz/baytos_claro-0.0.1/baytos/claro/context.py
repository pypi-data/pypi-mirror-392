"""
Context items for Bayt prompts (files and URLs)
"""

from typing import Dict, Any, Optional, Literal, cast


class ContextItem:
    """
    Represents a context item (file or URL) attached to a prompt.

    Context items provide additional information that can be included
    when using a prompt. They can be files or URLs.
    """

    def __init__(self, data: Dict[str, Any]):
        """
        Initialize a ContextItem from API response data.

        Args:
            data: Dictionary containing context item data from the API
        """
        self._data = data

    @property
    def id(self) -> str:
        """Context item ID"""
        return cast(str, self._data.get("id", ""))

    @property
    def type(self) -> Literal["url", "file"]:
        """Context item type (url or file)"""
        return cast(Literal["url", "file"], self._data.get("type", "url"))

    @property
    def label(self) -> Optional[str]:
        """Optional label for the context item"""
        return self._data.get("label")

    @property
    def created_at(self) -> Optional[int]:
        """Timestamp when the context item was created"""
        return self._data.get("createdAt")

    def is_file(self) -> bool:
        """Check if this context item is a file"""
        return self.type == "file"

    def is_url(self) -> bool:
        """Check if this context item is a URL"""
        return self.type == "url"

    @property
    def url(self) -> Optional[str]:
        """URL (only for URL-type context items)"""
        if self.type == "url":
            return self._data.get("url")
        return None

    @property
    def url_fetched_at(self) -> Optional[int]:
        """Timestamp when URL was last fetched (only for URL-type context items)"""
        if self.type == "url":
            return self._data.get("urlFetchedAt")
        return None

    @property
    def file_name(self) -> Optional[str]:
        """File name (only for file-type context items)"""
        if self.type == "file":
            return self._data.get("fileName")
        return None

    @property
    def file_size(self) -> Optional[int]:
        """File size in bytes (only for file-type context items)"""
        if self.type == "file":
            return self._data.get("fileSize")
        return None

    @property
    def mime_type(self) -> Optional[str]:
        """MIME type (only for file-type context items)"""
        if self.type == "file":
            return self._data.get("mimeType")
        return None

    def __repr__(self) -> str:
        """String representation of the context item"""
        if self.is_file():
            return f"<ContextItem type='file' name='{self.file_name}' size={self.file_size}>"
        else:
            return f"<ContextItem type='url' url='{self.url}'>"

    def __str__(self) -> str:
        """Human-readable string representation"""
        if self.label:
            return f"{self.label} ({self.type})"
        elif self.is_file():
            return self.file_name or "Untitled file"
        else:
            return self.url or "Untitled URL"

    def to_dict(self) -> Dict[str, Any]:
        """Get the full dictionary representation of the context item"""
        return self._data.copy()
