"""Integration tests for the _make_api_request_impl tool."""

import pytest
import json
import tempfile
import os
from openapi_navigator.server import _make_api_request_impl
from openapi_navigator.spec_manager import SpecManager


class TestApiRequestIntegration:
    """Integration tests for the _make_api_request_impl tool."""

    @pytest.mark.integration
    def test_real_api_get_request(self):
        """Test real GET request to httpbin.org."""
        result = _make_api_request_impl("https://httpbin.org/get")

        assert result["status_code"] == 200
        assert result["method"] == "GET"
        assert result["json"] is not None
        assert "url" in result["json"]
        assert result["url"] == "https://httpbin.org/get"
        assert result["elapsed_ms"] > 0
        assert len(result["headers"]) > 0  # Just ensure we have headers

    @pytest.mark.integration
    def test_real_api_post_request_with_json(self):
        """Test real POST request with JSON data to httpbin.org."""
        headers = {"Content-Type": "application/json"}
        data = '{"test": "data", "number": 42}'

        result = _make_api_request_impl(
            url="https://httpbin.org/post", method="POST", headers=headers, data=data
        )

        assert result["status_code"] == 200
        assert result["method"] == "POST"
        assert result["json"] is not None
        assert result["json"]["json"]["test"] == "data"
        assert result["json"]["json"]["number"] == 42
        assert result["json"]["headers"]["Content-Type"] == "application/json"

    @pytest.mark.integration
    def test_real_api_request_with_parameters(self):
        """Test real GET request with URL parameters to httpbin.org."""
        params = {"param1": "value1", "param2": "value2"}

        result = _make_api_request_impl(url="https://httpbin.org/get", params=params)

        assert result["status_code"] == 200
        assert result["json"] is not None
        assert result["json"]["args"]["param1"] == "value1"
        assert result["json"]["args"]["param2"] == "value2"

    @pytest.mark.integration
    def test_real_api_request_with_custom_headers(self):
        """Test real request with custom headers to httpbin.org."""
        headers = {
            "X-Custom-Header": "test-value",
            "User-Agent": "OpenAPI-Navigator-Test/1.0",
        }

        result = _make_api_request_impl(
            url="https://httpbin.org/headers", headers=headers
        )

        assert result["status_code"] == 200
        assert result["json"] is not None
        assert result["json"]["headers"]["X-Custom-Header"] == "test-value"
        assert result["json"]["headers"]["User-Agent"] == "OpenAPI-Navigator-Test/1.0"

    @pytest.mark.integration
    def test_real_api_different_methods(self):
        """Test different HTTP methods with httpbin.org."""
        methods = ["PUT", "PATCH", "DELETE"]

        for method in methods:
            result = _make_api_request_impl(
                url=f"https://httpbin.org/{method.lower()}", method=method
            )

            assert result["status_code"] == 200
            assert result["method"] == method
            assert result["json"] is not None

    @pytest.mark.integration
    def test_real_api_404_error(self):
        """Test handling of 404 error response."""
        result = _make_api_request_impl("https://httpbin.org/status/404")

        assert result["status_code"] == 404
        assert result["method"] == "GET"
        # Should not raise an exception, just return the error status

    @pytest.mark.integration
    def test_real_api_timeout_behavior(self):
        """Test timeout behavior with httpbin.org delay endpoint."""
        # Use a very short timeout to test timeout handling
        with pytest.raises(TimeoutError):
            _make_api_request_impl("https://httpbin.org/delay/5", timeout=1)

    @pytest.mark.integration
    def test_real_api_connection_error(self):
        """Test connection error with non-existent domain."""
        with pytest.raises(ConnectionError):
            _make_api_request_impl("https://nonexistent-domain-12345.com")

    @pytest.mark.integration
    def test_combined_workflow_spec_loading_and_api_requests(self, sample_openapi_spec):
        """Test combined workflow: load spec, explore endpoints, then make API requests."""
        manager = SpecManager()

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_openapi_spec, f, indent=2)
            temp_file = f.name

        try:
            # 1. Load and explore the OpenAPI spec
            manager.load_spec_from_file(temp_file, "pet-store")
            spec = manager.get_spec("pet-store")

            # 2. Explore available endpoints
            endpoints_result = spec.search_endpoints("")
            assert len(endpoints_result["endpoints"]) == 3

            # 3. Get base URL info from spec metadata
            metadata = spec.get_spec_metadata()
            assert metadata["title"] == "Sample Pet Store API"

            # 4. Make real API requests to test endpoints (using httpbin as a proxy)
            # Simulate what a user might do after exploring the spec

            # Test a GET request (like listing pets)
            get_result = _make_api_request_impl("https://httpbin.org/get")
            assert get_result["status_code"] == 200

            # Test a POST request (like creating a pet)
            post_data = '{"name": "Fluffy", "tag": "cat"}'
            post_result = _make_api_request_impl(
                url="https://httpbin.org/post",
                method="POST",
                headers={"Content-Type": "application/json"},
                data=post_data,
            )
            assert post_result["status_code"] == 200
            assert post_result["json"]["json"]["name"] == "Fluffy"

            # Test error handling
            error_result = _make_api_request_impl("https://httpbin.org/status/500")
            assert error_result["status_code"] == 500

            # Clean up spec
            manager.unload_spec("pet-store")

        finally:
            # Cleanup
            try:
                os.unlink(temp_file)
            except OSError:
                pass
