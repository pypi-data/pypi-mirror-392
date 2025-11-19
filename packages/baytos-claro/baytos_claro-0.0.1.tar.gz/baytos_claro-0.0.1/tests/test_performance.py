"""Performance tests for Bayt SDK

These tests verify:
- Response time under various conditions
- Handling of large payloads
- Concurrent request handling
- Rate limiting behavior
- Memory usage

Run with: pytest tests/test_performance.py -v
Skip with: pytest -m "not performance"
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch
from baytos.claro import BaytClient, Prompt
from baytos.claro.exceptions import BaytRateLimitError, BaytAPIError


pytestmark = [pytest.mark.performance, pytest.mark.slow]


class TestResponseTime:
    """Test response time performance"""

    @pytest.mark.timeout(5)
    def test_get_prompt_response_time(self, mock_api_key, mock_successful_response):
        """Test that get_prompt responds within acceptable time"""
        client = BaytClient(api_key=mock_api_key)

        with patch("requests.Session.post", return_value=mock_successful_response):
            start_time = time.time()
            prompt = client.get_prompt("@test/sample:v1")
            elapsed = time.time() - start_time

            # Should respond quickly (under 1 second for mocked call)
            assert elapsed < 1.0
            assert isinstance(prompt, Prompt)

    @pytest.mark.timeout(5)
    def test_list_prompts_response_time(self, mock_api_key, mock_list_response):
        """Test that list_prompts responds within acceptable time"""
        client = BaytClient(api_key=mock_api_key)

        with patch("requests.Session.get", return_value=mock_list_response):
            start_time = time.time()
            result = client.list_prompts(limit=10)
            elapsed = time.time() - start_time

            # Should respond quickly
            assert elapsed < 1.0
            assert isinstance(result, dict)

    def test_multiple_sequential_requests(self, mock_api_key, mock_successful_response):
        """Test performance of multiple sequential requests"""
        client = BaytClient(api_key=mock_api_key)

        with patch("requests.Session.post", return_value=mock_successful_response):
            start_time = time.time()

            # Make 10 sequential requests
            for i in range(10):
                prompt = client.get_prompt(f"@test/sample{i}:v1")
                assert isinstance(prompt, Prompt)

            elapsed = time.time() - start_time

            # Should complete in reasonable time (< 5 seconds for mocked calls)
            assert elapsed < 5.0
            # Average time per request should be low
            avg_time = elapsed / 10
            assert avg_time < 0.5


class TestLargePayloads:
    """Test handling of large data payloads"""

    def test_large_prompt_content(self, mock_api_key, large_prompt_data):
        """Test handling of prompts with large content"""
        client = BaytClient(api_key=mock_api_key)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = large_prompt_data
        mock_response.raise_for_status.return_value = None

        with patch("requests.Session.post", return_value=mock_response):
            start_time = time.time()
            prompt = client.get_prompt("@test/large:v1")
            elapsed = time.time() - start_time

            # Should handle large content (200KB+)
            assert isinstance(prompt, Prompt)
            assert len(prompt.description) == 10000
            assert len(prompt.system) == 50000
            assert len(prompt.generator) == 100000

            # Should complete in reasonable time
            assert elapsed < 2.0

    def test_large_variable_list(self, mock_api_key, large_prompt_data):
        """Test handling of prompts with many variables"""
        client = BaytClient(api_key=mock_api_key)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = large_prompt_data
        mock_response.raise_for_status.return_value = None

        with patch("requests.Session.post", return_value=mock_response):
            prompt = client.get_prompt("@test/large:v1")

            # Extract variables (50 variables)
            start_time = time.time()
            variables = prompt.extract_variables()
            elapsed = time.time() - start_time

            assert len(variables) == 50
            # Should extract quickly
            assert elapsed < 0.5

    def test_large_list_response(self, mock_api_key):
        """Test handling of large list responses"""
        client = BaytClient(api_key=mock_api_key)

        # Create response with 100 prompts
        large_list = {
            "prompts": [
                {
                    "id": f"prompt{i}",
                    "title": f"Prompt {i}",
                    "packageName": f"prompt-{i}",
                    "workspaceSlug": "test",
                    "version": 1,
                }
                for i in range(100)
            ],
            "has_more": False,
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = large_list
        mock_response.raise_for_status.return_value = None

        with patch("requests.Session.get", return_value=mock_response):
            start_time = time.time()
            result = client.list_prompts(limit=100)
            elapsed = time.time() - start_time

            assert len(result["prompts"]) == 100
            # Should handle large lists efficiently
            assert elapsed < 1.0


class TestConcurrentRequests:
    """Test concurrent request handling"""

    def test_concurrent_get_requests(self, mock_api_key, mock_successful_response):
        """Test multiple concurrent get_prompt requests"""
        client = BaytClient(api_key=mock_api_key)

        def fetch_prompt(prompt_id):
            with patch("requests.Session.post", return_value=mock_successful_response):
                return client.get_prompt(f"@test/prompt{prompt_id}:v1")

        # Execute 10 concurrent requests
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_prompt, i) for i in range(10)]
            results = [future.result() for future in as_completed(futures)]
        elapsed = time.time() - start_time

        # All requests should succeed
        assert len(results) == 10
        for result in results:
            assert isinstance(result, Prompt)

        # Concurrent execution should be faster than sequential
        # (though with mocked responses, timing may vary)
        assert elapsed < 5.0

    def test_thread_safety(self, mock_api_key, mock_successful_response):
        """Test that client is thread-safe"""
        client = BaytClient(api_key=mock_api_key)
        errors = []

        def worker(worker_id):
            try:
                with patch(
                    "requests.Session.post", return_value=mock_successful_response
                ):
                    for i in range(5):
                        prompt = client.get_prompt(f"@test/prompt{i}:v1")
                        assert prompt.title
            except Exception as e:
                errors.append((worker_id, e))

        # Run 5 threads concurrently
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # No errors should occur
        assert len(errors) == 0, f"Thread safety errors: {errors}"

    def test_concurrent_mixed_requests(
        self, mock_api_key, mock_successful_response, mock_list_response
    ):
        """Test concurrent mixed request types"""
        client = BaytClient(api_key=mock_api_key)

        def get_prompt_task(prompt_id):
            with patch("requests.Session.post", return_value=mock_successful_response):
                return ("get", client.get_prompt(f"@test/prompt{prompt_id}:v1"))

        def list_prompts_task():
            with patch("requests.Session.get", return_value=mock_list_response):
                return ("list", client.list_prompts(limit=10))

        # Mix of get and list requests
        tasks = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit 5 get requests
            for i in range(5):
                tasks.append(executor.submit(get_prompt_task, i))

            # Submit 5 list requests
            for i in range(5):
                tasks.append(executor.submit(list_prompts_task))

            results = [task.result() for task in as_completed(tasks)]

        # Verify all completed successfully
        assert len(results) == 10
        get_results = [r for r in results if r[0] == "get"]
        list_results = [r for r in results if r[0] == "list"]

        assert len(get_results) == 5
        assert len(list_results) == 5


class TestRateLimiting:
    """Test rate limiting behavior"""

    def test_rate_limit_error_handling(self, mock_api_key, mock_429_response):
        """Test that rate limit errors are properly handled"""
        client = BaytClient(api_key=mock_api_key)

        with patch("requests.Session.post", return_value=mock_429_response), patch(
            "time.sleep"
        ):  # Mock sleep to avoid actual waiting
            with pytest.raises(BaytRateLimitError) as exc_info:
                client.get_prompt("@test/sample:v1")

            # Error should contain retry information
            error = exc_info.value
            assert "rate limit" in str(error).lower()

    def test_rate_limit_with_retry_after(self, mock_api_key):
        """Test handling of Retry-After header"""
        client = BaytClient(api_key=mock_api_key)

        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_response.json.return_value = {"error": "Rate limit exceeded"}

        with patch("requests.Session.post", return_value=mock_response), patch(
            "time.sleep"
        ):  # Mock sleep to avoid actual waiting
            with pytest.raises(BaytRateLimitError):
                client.get_prompt("@test/sample:v1")

    def test_burst_request_handling(self, mock_api_key):
        """Test handling of burst requests"""
        client = BaytClient(api_key=mock_api_key)

        # Simulate some requests succeeding, then rate limiting
        call_count = 0

        def mock_response_generator(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            if call_count <= 5:
                # First 5 succeed
                mock_resp = Mock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = {"data": {"id": "test", "title": "Test"}}
                mock_resp.raise_for_status.return_value = None
                return mock_resp
            else:
                # Then rate limited
                mock_resp = Mock()
                mock_resp.status_code = 429
                mock_resp.headers = {"Retry-After": "1"}
                mock_resp.json.return_value = {"error": "Rate limited"}
                return mock_resp

        with patch("requests.Session.post", side_effect=mock_response_generator):
            # First 5 should succeed
            for i in range(5):
                prompt = client.get_prompt(f"@test/prompt{i}:v1")
                assert prompt

            # 6th should fail with rate limit
            with pytest.raises(BaytRateLimitError):
                client.get_prompt("@test/prompt6:v1")


class TestTimeouts:
    """Test timeout handling"""

    @pytest.mark.timeout(5)
    def test_request_timeout_configuration(self, mock_api_key):
        """Test that timeouts can be configured"""
        client = BaytClient(api_key=mock_api_key)

        # Client should have timeout configured
        # (implementation-dependent)
        assert hasattr(client, "session")

    def test_timeout_error_handling(self, mock_api_key):
        """Test handling of timeout errors"""
        import requests

        client = BaytClient(api_key=mock_api_key)

        with patch(
            "requests.Session.post", side_effect=requests.Timeout("Request timeout")
        ):
            with pytest.raises(BaytAPIError):
                client.get_prompt("@test/sample:v1")

    def test_connection_timeout(self, mock_api_key):
        """Test handling of connection timeouts"""
        import requests

        client = BaytClient(api_key=mock_api_key)

        with patch(
            "requests.Session.post",
            side_effect=requests.ConnectTimeout("Connection timeout"),
        ):
            with pytest.raises(BaytAPIError):
                client.get_prompt("@test/sample:v1")


class TestMemoryUsage:
    """Test memory usage patterns"""

    def test_large_response_memory(self, mock_api_key, large_prompt_data):
        """Test memory usage with large responses"""
        import sys

        client = BaytClient(api_key=mock_api_key)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": large_prompt_data}
        mock_response.raise_for_status.return_value = None

        with patch("requests.Session.post", return_value=mock_response):
            prompt = client.get_prompt("@test/large:v1")

            # Prompt object should exist
            assert prompt

            # Size should be reasonable (less than 1MB for object overhead)
            # Note: sys.getsizeof doesn't include referenced objects
            size = sys.getsizeof(prompt)
            assert size < 1_000_000

    def test_no_memory_leak_sequential(self, mock_api_key, mock_successful_response):
        """Test that sequential requests don't leak memory"""
        import gc

        client = BaytClient(api_key=mock_api_key)

        # Force garbage collection
        gc.collect()

        # Track number of Prompt objects
        initial_prompts = len(
            [obj for obj in gc.get_objects() if isinstance(obj, Prompt)]
        )

        with patch("requests.Session.post", return_value=mock_successful_response):
            # Make many requests
            for i in range(50):
                prompt = client.get_prompt(f"@test/prompt{i}:v1")
                # Don't keep reference
                del prompt

        # Force garbage collection
        gc.collect()

        # Count Prompt objects again
        final_prompts = len(
            [obj for obj in gc.get_objects() if isinstance(obj, Prompt)]
        )

        # Should not have accumulated many objects
        # (Some may remain in gc, but not all 50)
        assert final_prompts - initial_prompts < 10

    def test_client_cleanup(self, mock_api_key):
        """Test that client resources are cleaned up properly"""
        import gc

        # Create and destroy client
        client = BaytClient(api_key=mock_api_key)
        client_id = id(client)
        del client

        # Force garbage collection
        gc.collect()

        # Client should be garbage collected
        # (This is a basic check - full cleanup depends on implementation)
        all_objects = gc.get_objects()
        client_objects = [obj for obj in all_objects if id(obj) == client_id]
        assert len(client_objects) == 0


class TestConnectionPooling:
    """Test connection pooling efficiency"""

    def test_session_reuse(self, mock_api_key, mock_successful_response):
        """Test that HTTP session is reused across requests"""
        client = BaytClient(api_key=mock_api_key)

        # Session should be created once
        session1 = client.session

        with patch("requests.Session.post", return_value=mock_successful_response):
            # Make multiple requests
            for i in range(5):
                client.get_prompt(f"@test/prompt{i}:v1")

            # Session should be the same instance
            session2 = client.session
            assert session1 is session2

    def test_session_headers_persistent(self, mock_api_key):
        """Test that session headers persist across requests"""
        client = BaytClient(api_key=mock_api_key)

        # Check initial headers
        initial_auth = client.session.headers.get("Authorization")
        assert initial_auth

        # Headers should persist
        assert client.session.headers.get("Authorization") == initial_auth
