"""Tests for HTTP transport and credential extraction."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from nexus_mcp.dependencies import (
    InvalidCredentialsError,
    MissingCredentialsError,
    get_nexus_credentials,
)


class TestCredentialExtraction:
    """Tests for extracting credentials from HTTP headers."""

    def test_get_credentials_success(self) -> None:
        """Valid headers should return NexusCredentials."""
        mock_request = MagicMock()
        mock_request.headers = {
            "x-nexus-url": "https://nexus.example.com",
            "x-nexus-username": "testuser",
            "x-nexus-password": "testpass",
        }

        with patch(
            "nexus_mcp.dependencies.get_http_request", return_value=mock_request
        ):
            creds = get_nexus_credentials()

            assert creds.url == "https://nexus.example.com"
            assert creds.username == "testuser"
            assert creds.password == "testpass"
            assert creds.verify_ssl is True  # Default value

    def test_get_credentials_with_verify_ssl_false(self) -> None:
        """Valid headers with verify_ssl=false should return NexusCredentials."""
        mock_request = MagicMock()
        mock_request.headers = {
            "x-nexus-url": "https://nexus.example.com",
            "x-nexus-username": "testuser",
            "x-nexus-password": "testpass",
            "x-nexus-verify-ssl": "false",
        }

        with patch(
            "nexus_mcp.dependencies.get_http_request", return_value=mock_request
        ):
            creds = get_nexus_credentials()

            assert creds.url == "https://nexus.example.com"
            assert creds.username == "testuser"
            assert creds.password == "testpass"
            assert creds.verify_ssl is False

    def test_get_credentials_with_verify_ssl_variations(self) -> None:
        """Test various values for verify_ssl header."""
        test_cases = [
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("0", False),
            ("no", False),
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("anything", True),  # Any non-false value is treated as true
        ]

        for header_value, expected in test_cases:
            mock_request = MagicMock()
            mock_request.headers = {
                "x-nexus-url": "https://nexus.example.com",
                "x-nexus-username": "testuser",
                "x-nexus-password": "testpass",
                "x-nexus-verify-ssl": header_value,
            }

            with patch(
                "nexus_mcp.dependencies.get_http_request", return_value=mock_request
            ):
                creds = get_nexus_credentials()
                assert creds.verify_ssl is expected, f"Failed for header value: {header_value}"

    def test_get_credentials_missing_url(self) -> None:
        """Missing URL header should raise MissingCredentialsError."""
        mock_request = MagicMock()
        mock_request.headers = {
            "x-nexus-username": "testuser",
            "x-nexus-password": "testpass",
        }

        with patch(
            "nexus_mcp.dependencies.get_http_request", return_value=mock_request
        ):
            with pytest.raises(MissingCredentialsError) as exc_info:
                get_nexus_credentials()

            assert "X-Nexus-Url" in str(exc_info.value)

    def test_get_credentials_missing_username(self) -> None:
        """Missing username header should raise MissingCredentialsError."""
        mock_request = MagicMock()
        mock_request.headers = {
            "x-nexus-url": "https://nexus.example.com",
            "x-nexus-password": "testpass",
        }

        with patch(
            "nexus_mcp.dependencies.get_http_request", return_value=mock_request
        ):
            with pytest.raises(MissingCredentialsError) as exc_info:
                get_nexus_credentials()

            assert "X-Nexus-Username" in str(exc_info.value)

    def test_get_credentials_missing_password(self) -> None:
        """Missing password header should raise MissingCredentialsError."""
        mock_request = MagicMock()
        mock_request.headers = {
            "x-nexus-url": "https://nexus.example.com",
            "x-nexus-username": "testuser",
        }

        with patch(
            "nexus_mcp.dependencies.get_http_request", return_value=mock_request
        ):
            with pytest.raises(MissingCredentialsError) as exc_info:
                get_nexus_credentials()

            assert "X-Nexus-Password" in str(exc_info.value)

    def test_get_credentials_missing_all(self) -> None:
        """Missing all headers should list all missing headers."""
        mock_request = MagicMock()
        mock_request.headers = {}

        with patch(
            "nexus_mcp.dependencies.get_http_request", return_value=mock_request
        ):
            with pytest.raises(MissingCredentialsError) as exc_info:
                get_nexus_credentials()

            error_msg = str(exc_info.value)
            assert "X-Nexus-Url" in error_msg
            assert "X-Nexus-Username" in error_msg
            assert "X-Nexus-Password" in error_msg

    def test_get_credentials_invalid_url_no_scheme(self) -> None:
        """URL without scheme should raise InvalidCredentialsError."""
        mock_request = MagicMock()
        mock_request.headers = {
            "x-nexus-url": "nexus.example.com",
            "x-nexus-username": "testuser",
            "x-nexus-password": "testpass",
        }

        with patch(
            "nexus_mcp.dependencies.get_http_request", return_value=mock_request
        ):
            with pytest.raises(InvalidCredentialsError) as exc_info:
                get_nexus_credentials()

            assert "Invalid Nexus URL" in str(exc_info.value)

    def test_get_credentials_invalid_url_wrong_scheme(self) -> None:
        """URL with non-http scheme should raise InvalidCredentialsError."""
        mock_request = MagicMock()
        mock_request.headers = {
            "x-nexus-url": "ftp://nexus.example.com",
            "x-nexus-username": "testuser",
            "x-nexus-password": "testpass",
        }

        with patch(
            "nexus_mcp.dependencies.get_http_request", return_value=mock_request
        ):
            with pytest.raises(InvalidCredentialsError) as exc_info:
                get_nexus_credentials()

            assert "http or https" in str(exc_info.value)

    def test_get_credentials_http_url_accepted(self) -> None:
        """HTTP URL (not HTTPS) should be accepted."""
        mock_request = MagicMock()
        mock_request.headers = {
            "x-nexus-url": "http://nexus.local:8081",
            "x-nexus-username": "testuser",
            "x-nexus-password": "testpass",
        }

        with patch(
            "nexus_mcp.dependencies.get_http_request", return_value=mock_request
        ):
            creds = get_nexus_credentials()

            assert creds.url == "http://nexus.local:8081"

    def test_get_credentials_no_request(self) -> None:
        """No HTTP request (None) should raise MissingCredentialsError."""
        with patch("nexus_mcp.dependencies.get_http_request", return_value=None):
            with pytest.raises(MissingCredentialsError) as exc_info:
                get_nexus_credentials()

            # All headers should be listed as missing
            error_msg = str(exc_info.value)
            assert "X-Nexus-Url" in error_msg


class TestServerToolsWithMockedHeaders:
    """Tests for MCP tools using mocked HTTP headers."""

    @pytest.fixture
    def mock_valid_headers(self) -> Any:
        """Provide mock HTTP headers for tests."""
        mock_request = MagicMock()
        mock_request.headers = {
            "x-nexus-url": "https://nexus.example.com",
            "x-nexus-username": "testuser",
            "x-nexus-password": "testpass",
        }
        return mock_request

    def test_credentials_case_insensitive(self) -> None:
        """Headers should be case-insensitive (lowercase in Starlette)."""
        # Starlette normalizes headers to lowercase, so we test with lowercase
        mock_request = MagicMock()
        mock_request.headers = {
            "x-nexus-url": "https://nexus.example.com",
            "x-nexus-username": "testuser",
            "x-nexus-password": "testpass",
        }

        with patch(
            "nexus_mcp.dependencies.get_http_request", return_value=mock_request
        ):
            creds = get_nexus_credentials()
            assert creds.url == "https://nexus.example.com"
