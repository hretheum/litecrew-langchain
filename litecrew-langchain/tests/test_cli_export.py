"""Tests for CLI export commands."""

import json
import tempfile
from unittest.mock import MagicMock, Mock, patch

import pytest
from click.testing import CliRunner

from litecrew.cli.commands.export import export_group


class TestCLIExport:
    """Test CLI export functionality."""

    def test_export_group_help(self):
        """Test export group help."""
        runner = CliRunner()
        result = runner.invoke(export_group, ["--help"])
        assert result.exit_code == 0
        assert "Export results and data in various formats" in result.output

    @patch("httpx.Client")
    def test_export_execution_success(self, mock_client):
        """Test successful execution export."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "execution_id": "test-123",
            "status": "completed",
            "result": "Test result",
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        mock_http_client = Mock()
        mock_http_client.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_http_client
        
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Test with context object
            ctx = {
                "api_url": "http://localhost:8000",
                "verbose": False
            }
            
            result = runner.invoke(
                export_group,
                ["execution", "test-123"],
                obj=ctx
            )
            
            assert result.exit_code == 0
            mock_http_client.get.assert_called_once()

    @patch("httpx.Client")
    def test_export_execution_not_found(self, mock_client):
        """Test execution not found error."""
        mock_response = Mock()
        mock_response.status_code = 404
        
        mock_http_client = Mock()
        mock_http_client.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_http_client
        
        runner = CliRunner()
        ctx = {
            "api_url": "http://localhost:8000",
            "verbose": False
        }
        
        result = runner.invoke(
            export_group,
            ["execution", "nonexistent"],
            obj=ctx
        )
        
        assert result.exit_code == 1
        assert "❌ Execution nonexistent not found" in result.output

    @patch("httpx.Client")
    def test_export_execution_server_error(self, mock_client):
        """Test server error handling."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        mock_http_client = Mock()
        mock_http_client.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_http_client
        
        runner = CliRunner()
        ctx = {
            "api_url": "http://localhost:8000",
            "verbose": False
        }
        
        result = runner.invoke(
            export_group,
            ["execution", "test-123"],
            obj=ctx
        )
        
        assert result.exit_code == 1

    @patch("httpx.Client")
    def test_export_execution_with_output_file(self, mock_client):
        """Test export to output file."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "execution_id": "test-123",
            "result": "Test result"
        }
        
        mock_http_client = Mock()
        mock_http_client.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_http_client
        
        runner = CliRunner()
        with runner.isolated_filesystem():
            ctx = {
                "api_url": "http://localhost:8000",
                "verbose": False
            }
            
            result = runner.invoke(
                export_group,
                ["execution", "test-123", "--output", "output.json"],
                obj=ctx
            )
            
            assert result.exit_code == 0

    @patch("httpx.Client")
    def test_export_execution_different_formats(self, mock_client):
        """Test export in different formats."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "execution_id": "test-123",
            "result": "Test result"
        }
        
        mock_http_client = Mock()
        mock_http_client.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_http_client
        
        runner = CliRunner()
        ctx = {
            "api_url": "http://localhost:8000",
            "verbose": False
        }
        
        formats = ["json", "yaml", "txt", "csv"]
        for fmt in formats:
            result = runner.invoke(
                export_group,
                ["execution", "test-123", "--format", fmt],
                obj=ctx
            )
            assert result.exit_code == 0

    @patch("httpx.Client")
    def test_export_execution_with_metadata(self, mock_client):
        """Test export with metadata flag."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "execution_id": "test-123",
            "result": "Test result",
            "metadata": {"key": "value"}
        }
        
        mock_http_client = Mock()
        mock_http_client.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_http_client
        
        runner = CliRunner()
        ctx = {
            "api_url": "http://localhost:8000",
            "verbose": False
        }
        
        result = runner.invoke(
            export_group,
            ["execution", "test-123", "--include-metadata"],
            obj=ctx
        )
        
        assert result.exit_code == 0

    @patch("httpx.Client")
    def test_export_execution_connection_error(self, mock_client):
        """Test connection error handling."""
        mock_client.side_effect = Exception("Connection failed")
        
        runner = CliRunner()
        ctx = {
            "api_url": "http://localhost:8000",
            "verbose": False
        }
        
        result = runner.invoke(
            export_group,
            ["execution", "test-123"],
            obj=ctx
        )
        
        assert result.exit_code == 1