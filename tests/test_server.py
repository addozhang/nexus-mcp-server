"""Tests for server configuration and argument parsing."""

import os
from unittest.mock import patch

import pytest


class TestArgumentParsing:
    """Tests for command line argument parsing."""

    def test_default_transport_sse(self) -> None:
        """Default transport mode should be sse."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("sys.argv", ["nexus-mcp"]):
                with patch("nexus_mcp.server.mcp.run") as mock_run:
                    from nexus_mcp.server import run_server

                    run_server()

                    mock_run.assert_called_once()
                    call_kwargs = mock_run.call_args[1]
                    assert call_kwargs["transport"] == "sse"
                    assert call_kwargs["host"] == "0.0.0.0"
                    assert call_kwargs["port"] == 8000

    def test_cli_transport_sse(self) -> None:
        """CLI argument --transport sse should work."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("sys.argv", ["nexus-mcp", "--transport", "sse"]):
                with patch("nexus_mcp.server.mcp.run") as mock_run:
                    from nexus_mcp.server import run_server

                    run_server()

                    mock_run.assert_called_once()
                    call_kwargs = mock_run.call_args[1]
                    assert call_kwargs["transport"] == "sse"

    def test_cli_transport_streamable_http(self) -> None:
        """CLI argument --transport streamable-http should work."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("sys.argv", ["nexus-mcp", "--transport", "streamable-http"]):
                with patch("nexus_mcp.server.mcp.run") as mock_run:
                    from nexus_mcp.server import run_server

                    run_server()

                    mock_run.assert_called_once()
                    call_kwargs = mock_run.call_args[1]
                    assert call_kwargs["transport"] == "streamable-http"

    def test_env_var_transport_sse(self) -> None:
        """Environment variable NEXUS_MCP_TRANSPORT=sse should work."""
        with patch.dict(os.environ, {"NEXUS_MCP_TRANSPORT": "sse"}):
            with patch("sys.argv", ["nexus-mcp"]):
                with patch("nexus_mcp.server.mcp.run") as mock_run:
                    from nexus_mcp.server import run_server

                    run_server()

                    mock_run.assert_called_once()
                    call_kwargs = mock_run.call_args[1]
                    assert call_kwargs["transport"] == "sse"

    def test_env_var_transport_streamable_http(self) -> None:
        """Environment variable NEXUS_MCP_TRANSPORT=streamable-http should work."""
        with patch.dict(os.environ, {"NEXUS_MCP_TRANSPORT": "streamable-http"}):
            with patch("sys.argv", ["nexus-mcp"]):
                with patch("nexus_mcp.server.mcp.run") as mock_run:
                    from nexus_mcp.server import run_server

                    run_server()

                    mock_run.assert_called_once()
                    call_kwargs = mock_run.call_args[1]
                    assert call_kwargs["transport"] == "streamable-http"

    def test_cli_overrides_env_var_transport(self) -> None:
        """CLI argument should override environment variable for transport."""
        with patch.dict(os.environ, {"NEXUS_MCP_TRANSPORT": "streamable-http"}):
            with patch("sys.argv", ["nexus-mcp", "--transport", "sse"]):
                with patch("nexus_mcp.server.mcp.run") as mock_run:
                    from nexus_mcp.server import run_server

                    run_server()

                    mock_run.assert_called_once()
                    call_kwargs = mock_run.call_args[1]
                    assert call_kwargs["transport"] == "sse"

    def test_invalid_transport_rejected(self) -> None:
        """Invalid transport mode should be rejected by argparse."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("sys.argv", ["nexus-mcp", "--transport", "invalid"]):
                with pytest.raises(SystemExit) as exc_info:
                    from nexus_mcp.server import run_server

                    run_server()

                # argparse exits with code 2 for invalid arguments
                assert exc_info.value.code == 2

    def test_port_default(self) -> None:
        """Default port should be 8000."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("sys.argv", ["nexus-mcp"]):
                with patch("nexus_mcp.server.mcp.run") as mock_run:
                    from nexus_mcp.server import run_server

                    run_server()

                    mock_run.assert_called_once()
                    call_kwargs = mock_run.call_args[1]
                    assert call_kwargs["port"] == 8000

    def test_port_cli_argument(self) -> None:
        """CLI argument --port should set custom port."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("sys.argv", ["nexus-mcp", "--port", "9000"]):
                with patch("nexus_mcp.server.mcp.run") as mock_run:
                    from nexus_mcp.server import run_server

                    run_server()

                    mock_run.assert_called_once()
                    call_kwargs = mock_run.call_args[1]
                    assert call_kwargs["port"] == 9000

    def test_port_env_var(self) -> None:
        """Environment variable NEXUS_MCP_PORT should set port."""
        with patch.dict(os.environ, {"NEXUS_MCP_PORT": "9000"}):
            with patch("sys.argv", ["nexus-mcp"]):
                with patch("nexus_mcp.server.mcp.run") as mock_run:
                    from nexus_mcp.server import run_server

                    run_server()

                    mock_run.assert_called_once()
                    call_kwargs = mock_run.call_args[1]
                    assert call_kwargs["port"] == 9000

    def test_cli_overrides_env_var_port(self) -> None:
        """CLI argument should override environment variable for port."""
        with patch.dict(os.environ, {"NEXUS_MCP_PORT": "9000"}):
            with patch("sys.argv", ["nexus-mcp", "--port", "8080"]):
                with patch("nexus_mcp.server.mcp.run") as mock_run:
                    from nexus_mcp.server import run_server

                    run_server()

                    mock_run.assert_called_once()
                    call_kwargs = mock_run.call_args[1]
                    assert call_kwargs["port"] == 8080

    def test_host_default(self) -> None:
        """Default host should be 0.0.0.0."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("sys.argv", ["nexus-mcp"]):
                with patch("nexus_mcp.server.mcp.run") as mock_run:
                    from nexus_mcp.server import run_server

                    run_server()

                    mock_run.assert_called_once()
                    call_kwargs = mock_run.call_args[1]
                    assert call_kwargs["host"] == "0.0.0.0"

    def test_host_cli_argument(self) -> None:
        """CLI argument --host should set custom host."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("sys.argv", ["nexus-mcp", "--host", "127.0.0.1"]):
                with patch("nexus_mcp.server.mcp.run") as mock_run:
                    from nexus_mcp.server import run_server

                    run_server()

                    mock_run.assert_called_once()
                    call_kwargs = mock_run.call_args[1]
                    assert call_kwargs["host"] == "127.0.0.1"

    def test_host_env_var(self) -> None:
        """Environment variable NEXUS_MCP_HOST should set host."""
        with patch.dict(os.environ, {"NEXUS_MCP_HOST": "127.0.0.1"}):
            with patch("sys.argv", ["nexus-mcp"]):
                with patch("nexus_mcp.server.mcp.run") as mock_run:
                    from nexus_mcp.server import run_server

                    run_server()

                    mock_run.assert_called_once()
                    call_kwargs = mock_run.call_args[1]
                    assert call_kwargs["host"] == "127.0.0.1"

    def test_cli_overrides_env_var_host(self) -> None:
        """CLI argument should override environment variable for host."""
        with patch.dict(os.environ, {"NEXUS_MCP_HOST": "127.0.0.1"}):
            with patch("sys.argv", ["nexus-mcp", "--host", "0.0.0.0"]):
                with patch("nexus_mcp.server.mcp.run") as mock_run:
                    from nexus_mcp.server import run_server

                    run_server()

                    mock_run.assert_called_once()
                    call_kwargs = mock_run.call_args[1]
                    assert call_kwargs["host"] == "0.0.0.0"

    def test_all_parameters_together(self) -> None:
        """All parameters should work together."""
        with patch.dict(os.environ, {}, clear=True):
            with patch(
                "sys.argv",
                [
                    "nexus-mcp",
                    "--transport",
                    "streamable-http",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "9000",
                ],
            ):
                with patch("nexus_mcp.server.mcp.run") as mock_run:
                    from nexus_mcp.server import run_server

                    run_server()

                    mock_run.assert_called_once()
                    call_kwargs = mock_run.call_args[1]
                    assert call_kwargs["transport"] == "streamable-http"
                    assert call_kwargs["host"] == "127.0.0.1"
                    assert call_kwargs["port"] == 9000

    def test_env_vars_all_parameters(self) -> None:
        """All environment variables should work together."""
        with patch.dict(
            os.environ,
            {
                "NEXUS_MCP_TRANSPORT": "streamable-http",
                "NEXUS_MCP_HOST": "127.0.0.1",
                "NEXUS_MCP_PORT": "9000",
            },
        ):
            with patch("sys.argv", ["nexus-mcp"]):
                with patch("nexus_mcp.server.mcp.run") as mock_run:
                    from nexus_mcp.server import run_server

                    run_server()

                    mock_run.assert_called_once()
                    call_kwargs = mock_run.call_args[1]
                    assert call_kwargs["transport"] == "streamable-http"
                    assert call_kwargs["host"] == "127.0.0.1"
                    assert call_kwargs["port"] == 9000
