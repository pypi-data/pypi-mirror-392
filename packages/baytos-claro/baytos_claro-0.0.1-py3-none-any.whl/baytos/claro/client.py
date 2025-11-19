"""
Main client for interacting with the Bayt API
"""

import os
import time
from typing import Optional, Dict, Any, Callable, cast
import requests
from urllib.parse import urljoin

from .models import Prompt
from .exceptions import (
    BaytAPIError,
    BaytAuthError,
    BaytNotFoundError,
    BaytRateLimitError,
    BaytValidationError,
)
from .utils import parse_package_name, validate_api_key, mask_api_key


class BaytClient:
    """
    Client for interacting with the Bayt API.

    Example:
        >>> client = BaytClient(api_key="b_prod_xxxx_...")
        >>> prompt = client.get_prompt("@bijou/team-analysis:v0")
        >>> print(prompt.title)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.baytos.ai",
        max_retries: int = 3,
    ):
        """
        Initialize the Bayt client.

        Args:
            api_key: Bayt API key. If not provided, will look for BAYT_API_KEY environment variable
            base_url: Base URL for the API (default: https://api.baytos.ai)
            max_retries: Maximum number of retries for rate-limited requests (default: 3)

        Raises:
            ValueError: If no API key is provided and BAYT_API_KEY is not set
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.environ.get("BAYT_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Pass it as a parameter or set BAYT_API_KEY environment variable"
            )

        # Validate API key format
        if not validate_api_key(self.api_key):
            raise ValueError(
                "Invalid API key format. Expected WorkOS API key starting with 'sk_'"
            )

        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries

        # Set up session with default headers
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "bayt-python/1.0.0",
                "Accept": "application/json",
            }
        )

    def _make_request_with_retry(
        self, request_func: Callable[[], requests.Response]
    ) -> requests.Response:
        """
        Make an HTTP request with automatic retry on rate limit (429).

        Implements exponential backoff: 1s, 2s, 4s, 8s, etc.
        Respects Retry-After header if provided by the server.

        Args:
            request_func: A callable that makes the HTTP request

        Returns:
            The successful response

        Raises:
            BaytRateLimitError: If all retries are exhausted
            Other exceptions: Passed through from request_func
        """
        for attempt in range(self.max_retries + 1):
            try:
                response = request_func()

                # If we get a 429, retry with backoff
                if response.status_code == 429:
                    if attempt == self.max_retries:
                        # Out of retries
                        raise BaytRateLimitError(
                            f"API rate limit exceeded. Max retries ({self.max_retries}) exhausted."
                        )

                    # Calculate backoff time
                    # Safely get Retry-After header (handle missing headers or mock objects)
                    retry_after = None
                    if hasattr(response, "headers") and isinstance(
                        response.headers, dict
                    ):
                        retry_after = response.headers.get("Retry-After")

                    # Validate it's a numeric string before using
                    if (
                        retry_after
                        and isinstance(retry_after, str)
                        and retry_after.isdigit()
                    ):
                        # Server specified retry time in seconds
                        wait_time = int(retry_after)
                    else:
                        # Exponential backoff: 1s, 2s, 4s, 8s...
                        wait_time = 2**attempt

                    # Wait before retrying
                    time.sleep(wait_time)
                    continue

                # Not a 429, return the response for normal error handling
                return response

            except requests.exceptions.RequestException:
                # Network errors, timeouts, etc - don't retry, let caller handle
                raise

        # Should not reach here, but just in case
        raise BaytRateLimitError("API rate limit exceeded. Max retries exhausted.")

    def get_prompt(self, package_name: str) -> Prompt:
        """
        Fetch a prompt by its package name.

        Args:
            package_name: Package identifier (e.g., "@bijou/team-analysis:v0")

        Returns:
            Prompt object with content, system, critique, and metadata

        Raises:
            BaytValidationError: If the package name format is invalid
            BaytAuthError: If authentication fails
            BaytNotFoundError: If the prompt is not found
            BaytRateLimitError: If rate limit is exceeded
            BaytAPIError: For other API errors
        """
        # Validate package name format
        parsed = parse_package_name(package_name)
        if not parsed:
            raise BaytValidationError(
                f"Invalid package name format: {package_name}. "
                f"Expected format: @namespace/slug:version"
            )

        # Make API request to get the prompt
        url = urljoin(self.base_url, "/v1/prompts/get")
        payload = {"package_name": package_name}

        try:
            # Make request with automatic retry on rate limit
            response = self._make_request_with_retry(
                lambda: self.session.post(url, json=payload, timeout=30)
            )
            response.raise_for_status()

            data = response.json()
            return Prompt(data)

        except requests.exceptions.HTTPError as e:
            # Handle specific HTTP errors
            if e.response.status_code == 401:
                raise BaytAuthError("Invalid API key or authentication failed")
            elif e.response.status_code == 403:
                raise BaytAuthError("Insufficient permissions to access this resource")
            elif e.response.status_code == 404:
                error_data = e.response.json() if e.response.text else {}
                error_msg = error_data.get("error", f"Prompt not found: {package_name}")
                raise BaytNotFoundError(error_msg)
            else:
                # Generic API error (429 is handled by retry logic)
                error_data = e.response.json() if e.response.text else {}
                error_msg = error_data.get("error", str(e))
                raise BaytAPIError(f"API request failed: {error_msg}")

        except requests.exceptions.Timeout:
            raise BaytAPIError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise BaytAPIError("Failed to connect to Bayt API")
        except requests.exceptions.RequestException as e:
            raise BaytAPIError(f"Network error: {e}")
        except ValueError as e:
            # JSON parsing error
            raise BaytAPIError(f"Invalid response from API: {e}")

    def list_prompts(
        self, limit: int = 20, cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List prompts accessible to the authenticated user.

        Args:
            limit: Maximum number of prompts to return (1-100, default 20)
            cursor: Pagination cursor from previous response

        Returns:
            Dictionary with prompts, cursor, and hasMore fields

        Raises:
            BaytAuthError: If authentication fails
            BaytRateLimitError: If rate limit is exceeded
            BaytAPIError: For other API errors
        """
        # Validate limit
        if not 1 <= limit <= 100:
            raise BaytValidationError("Limit must be between 1 and 100")

        # Make API request
        url = urljoin(self.base_url, "/v1/prompts")
        params: Dict[str, Any] = {
            "limit": limit,
        }

        if cursor:
            params["cursor"] = cursor

        try:
            # Make request with automatic retry on rate limit
            response = self._make_request_with_retry(
                lambda: self.session.get(url, params=params, timeout=30)
            )
            response.raise_for_status()

            data = cast(Dict[str, Any], response.json())

            # Convert prompt data to Prompt objects
            if "prompts" in data:
                data["prompts"] = [Prompt(p) for p in data["prompts"]]

            return data

        except requests.exceptions.HTTPError as e:
            # Handle specific HTTP errors
            if e.response.status_code == 401:
                raise BaytAuthError("Invalid API key or authentication failed")
            elif e.response.status_code == 403:
                raise BaytAuthError("Insufficient permissions")
            else:
                # Generic API error (429 is handled by retry logic)
                error_data = e.response.json() if e.response.text else {}
                error_msg = error_data.get("error", str(e))
                raise BaytAPIError(f"API request failed: {error_msg}")

        except requests.exceptions.Timeout:
            raise BaytAPIError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise BaytAPIError("Failed to connect to Bayt API")
        except requests.exceptions.RequestException as e:
            raise BaytAPIError(f"Network error: {e}")
        except ValueError as e:
            # JSON parsing error
            raise BaytAPIError(f"Invalid response from API: {e}")

    def get_context_download_url(self, context_id: str) -> Dict[str, Any]:
        """
        Get a signed download URL for a context file.

        Args:
            context_id: The context item ID from prompt.context

        Returns:
            Dictionary with 'url' (signed download URL) and 'expiresIn' (seconds until expiry)

        Raises:
            BaytAuthError: If authentication fails
            BaytNotFoundError: If the context item is not found
            BaytValidationError: If the context item is not a file type
            BaytAPIError: For other API errors
        """
        url = urljoin(self.base_url, "/api/v1/prompts/context/download-url")
        params = {"contextId": context_id}

        try:
            response = self._make_request_with_retry(
                lambda: self.session.get(url, params=params, timeout=30)
            )
            response.raise_for_status()

            data = cast(Dict[str, Any], response.json())
            return data

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise BaytAuthError("Invalid API key or authentication failed")
            elif e.response.status_code == 403:
                raise BaytAuthError(
                    "Access denied: You don't have permission to access this context"
                )
            elif e.response.status_code == 404:
                error_data = e.response.json() if e.response.text else {}
                error_msg = error_data.get("error", f"Context not found: {context_id}")
                raise BaytNotFoundError(error_msg)
            elif e.response.status_code == 400:
                error_data = e.response.json() if e.response.text else {}
                error_msg = error_data.get("error", "Bad request")
                raise BaytValidationError(error_msg)
            else:
                error_data = e.response.json() if e.response.text else {}
                error_msg = error_data.get("error", str(e))
                raise BaytAPIError(f"API request failed: {error_msg}")

        except requests.exceptions.Timeout:
            raise BaytAPIError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise BaytAPIError("Failed to connect to Bayt API")
        except requests.exceptions.RequestException as e:
            raise BaytAPIError(f"Network error: {e}")
        except ValueError as e:
            raise BaytAPIError(f"Invalid response from API: {e}")

    def download_context_file(self, context_id: str) -> bytes:
        """
        Download a context file and return its content as bytes.

        This method first gets a signed download URL, then downloads the file.
        The file content is returned in memory - the caller decides whether to save it.

        Args:
            context_id: The context item ID from prompt.context

        Returns:
            File content as bytes

        Raises:
            BaytAuthError: If authentication fails
            BaytNotFoundError: If the context item is not found
            BaytValidationError: If the context item is not a file type
            BaytAPIError: For other API errors

        Example:
            >>> prompt = client.get_prompt("@team/prompt:v1")
            >>> files = prompt.get_file_contexts()
            >>> if files:
            ...     content = client.download_context_file(files[0].id)
            ...     # Do something with bytes in memory
            ...     # Or save to disk if needed:
            ...     with open(files[0].file_name, 'wb') as f:
            ...         f.write(content)
        """
        # Get signed download URL
        url_data = self.get_context_download_url(context_id)
        download_url = url_data.get("url")

        if not download_url:
            raise BaytAPIError("No download URL returned from API")

        try:
            # Download the file (no auth header needed - URL is pre-signed)
            response = requests.get(download_url, timeout=60)
            response.raise_for_status()

            return response.content

        except requests.exceptions.HTTPError as e:
            raise BaytAPIError(f"Failed to download file: {e}")
        except requests.exceptions.Timeout:
            raise BaytAPIError("File download timed out")
        except requests.exceptions.ConnectionError:
            raise BaytAPIError("Failed to connect to file storage")
        except requests.exceptions.RequestException as e:
            raise BaytAPIError(f"Network error during file download: {e}")

    def __repr__(self) -> str:
        """String representation of the client."""
        masked_key = mask_api_key(self.api_key or "")
        return f"<BaytClient base_url='{self.base_url}' api_key='{masked_key}'>"
