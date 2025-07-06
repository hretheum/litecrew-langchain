"""Tests for the CLI commands."""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from litecrew.cli.main import cli


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_config_file():
    """Create temporary config file for testing."""
    config_data = {
        "api": {"url": "http://localhost:8000", "timeout": 30},
        "logging": {"level": "INFO"},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config_data, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def temp_crew_file():
    """Create temporary crew configuration file."""
    crew_data = {
        "name": "Test Crew",
        "description": "A test crew for CLI testing",
        "agents": [
            {
                "role": "Researcher",
                "goal": "Research topics",
                "backstory": "Expert researcher",
            }
        ],
        "tasks": [
            {
                "description": "Research AI trends",
                "agent_role": "Researcher",
                "expected_output": "Research summary",
            }
        ],
        "process": "sequential",
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(crew_data, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


class TestCLIBasics:
    """Test basic CLI functionality."""

    def test_cli_help(self, runner):
        """Test CLI help display."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "LiteCrew" in result.output
        assert "crew" in result.output
        assert "task" in result.output
        assert "export" in result.output
        assert "debug" in result.output
        assert "config" in result.output

    def test_cli_version(self, runner):
        """Test CLI version display."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_cli_with_config(self, runner, temp_config_file):
        """Test CLI with config file."""
        result = runner.invoke(
            cli, ["--config", temp_config_file, "--verbose", "--help"]
        )
        assert result.exit_code == 0
        assert "LiteCrew" in result.output


class TestStatusCommand:
    """Test status command."""

    @patch("httpx.Client")
    def test_status_success(self, mock_client, runner):
        """Test successful status check."""
        # Mock API responses
        mock_health_response = Mock()
        mock_health_response.status_code = 200
        mock_health_response.json.return_value = {
            "status": "healthy",
            "memory_mb": 25.5,
            "version": "1.0.0",
            "timestamp": "2025-01-01T00:00:00Z",
        }

        mock_crews_response = Mock()
        mock_crews_response.status_code = 200
        mock_crews_response.json.return_value = {
            "crews": [{"name": "test", "crew_id": "123"}]
        }

        mock_client_instance = Mock()
        mock_client_instance.get.side_effect = [
            mock_health_response,
            mock_crews_response,
        ]
        mock_client.return_value.__enter__.return_value = mock_client_instance

        start_time = time.perf_counter()
        result = runner.invoke(cli, ["status"])
        duration = (time.perf_counter() - start_time) * 1000

        assert result.exit_code == 0
        assert "API Server: Online" in result.output
        assert "Active Crews: 1" in result.output
        assert "Memory Usage: 25.5 MB" in result.output
        assert duration < 100  # Command execution <100ms

    @patch("httpx.Client")
    def test_status_api_offline(self, mock_client, runner):
        """Test status when API is offline."""
        mock_client.return_value.__enter__.side_effect = Exception("Connection refused")

        result = runner.invoke(cli, ["status"])
        assert result.exit_code == 1
        assert "Cannot connect to API server" in result.output


class TestBenchmarkCommand:
    """Test benchmark command."""

    @patch("httpx.Client")
    def test_benchmark_success(self, mock_client, runner):
        """Test successful benchmark run."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"memory_mb": 30.0}

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance

        start_time = time.perf_counter()
        result = runner.invoke(cli, ["benchmark"])
        duration = (time.perf_counter() - start_time) * 1000

        assert result.exit_code == 0
        assert "Benchmark Results" in result.output
        assert "Avg Latency" in result.output
        assert "Memory Usage" in result.output
        assert duration < 5000  # Benchmark should complete quickly


class TestCrewCommands:
    """Test crew management commands."""

    def test_crew_help(self, runner):
        """Test crew command help."""
        result = runner.invoke(cli, ["crew", "--help"])
        assert result.exit_code == 0
        assert "create" in result.output
        assert "list" in result.output
        assert "execute" in result.output
        assert "delete" in result.output
        assert "show" in result.output

    @patch("httpx.Client")
    def test_crew_create_dry_run(self, mock_client, runner, temp_crew_file):
        """Test crew creation with dry run."""
        result = runner.invoke(cli, ["crew", "create", temp_crew_file, "--dry-run"])
        assert result.exit_code == 0
        assert "Configuration is valid" in result.output
        assert "Test Crew" in result.output

        # Should not make API calls in dry run
        mock_client.assert_not_called()

    @patch("httpx.Client")
    def test_crew_create_success(self, mock_client, runner, temp_crew_file):
        """Test successful crew creation."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "crew_id": "test-123",
            "name": "Test Crew",
            "agents": [{"role": "Researcher"}],
            "tasks": [{"description": "Research AI trends"}],
        }

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance

        result = runner.invoke(cli, ["crew", "create", temp_crew_file])
        assert result.exit_code == 0
        assert "Crew 'Test Crew' created successfully" in result.output
        assert "test-123" in result.output

    @patch("httpx.Client")
    def test_crew_list_empty(self, mock_client, runner):
        """Test listing crews when none exist."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"crews": []}

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance

        result = runner.invoke(cli, ["crew", "list"])
        assert result.exit_code == 0
        assert "No crews found" in result.output

    @patch("httpx.Client")
    def test_crew_execute(self, mock_client, runner):
        """Test crew execution."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "execution_id": "exec-123",
            "status": "completed",
            "result": {"result": "Task completed successfully"},
        }

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance

        result = runner.invoke(cli, ["crew", "execute", "test-crew-id"])
        assert result.exit_code == 0
        assert "Execution completed" in result.output


class TestTaskCommands:
    """Test task management commands."""

    def test_task_help(self, runner):
        """Test task command help."""
        result = runner.invoke(cli, ["task", "--help"])
        assert result.exit_code == 0
        assert "run" in result.output
        assert "status" in result.output
        assert "list" in result.output

    @patch("httpx.Client")
    def test_task_run_success(self, mock_client, runner):
        """Test successful task submission."""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.json.return_value = {"task_id": "task-123", "status": "accepted"}

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance

        result = runner.invoke(
            cli,
            [
                "task",
                "run",
                "Test task description",
                "--crew-id",
                "test-crew",
                "--priority",
                "high",
            ],
        )
        assert result.exit_code == 0
        assert "Task submitted successfully" in result.output
        assert "task-123" in result.output

    def test_task_run_no_crew(self, runner):
        """Test task run without crew ID."""
        result = runner.invoke(cli, ["task", "run", "Test task"])
        assert result.exit_code == 1
        assert "No crew ID specified" in result.output


class TestExportCommands:
    """Test export commands."""

    def test_export_help(self, runner):
        """Test export command help."""
        result = runner.invoke(cli, ["export", "--help"])
        assert result.exit_code == 0
        assert "execution" in result.output
        assert "executions" in result.output
        assert "crews" in result.output
        assert "metrics" in result.output

    @patch("httpx.Client")
    def test_export_metrics(self, mock_client, runner):
        """Test metrics export."""
        mock_health_response = Mock()
        mock_health_response.status_code = 200
        mock_health_response.json.return_value = {
            "memory_mb": 25.0,
            "version": "1.0.0",
            "timestamp": "2025-01-01T00:00:00Z",
        }

        mock_crews_response = Mock()
        mock_crews_response.status_code = 200
        mock_crews_response.json.return_value = {"crews": []}

        mock_executions_response = Mock()
        mock_executions_response.status_code = 200
        mock_executions_response.json.return_value = {"executions": []}

        mock_client_instance = Mock()
        mock_client_instance.get.side_effect = [
            mock_health_response,
            mock_crews_response,
            mock_executions_response,
        ]
        mock_client.return_value.__enter__.return_value = mock_client_instance

        result = runner.invoke(cli, ["export", "metrics"])
        assert result.exit_code == 0
        assert "system" in result.output
        assert "usage" in result.output
        assert "memory_mb" in result.output


class TestDebugCommands:
    """Test debug commands."""

    def test_debug_help(self, runner):
        """Test debug command help."""
        result = runner.invoke(cli, ["debug", "--help"])
        assert result.exit_code == 0
        assert "logs" in result.output
        assert "connectivity" in result.output
        assert "trace" in result.output
        assert "performance" in result.output

    def test_debug_logs(self, runner):
        """Test debug logs command."""
        result = runner.invoke(cli, ["debug", "logs", "--tail", "5"])
        assert result.exit_code == 0
        assert "System Logs" in result.output

    @patch("httpx.Client")
    def test_debug_connectivity(self, mock_client, runner):
        """Test connectivity check."""
        mock_response = Mock()
        mock_response.status_code = 200

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance

        result = runner.invoke(cli, ["debug", "connectivity"])
        assert result.exit_code == 0
        assert "Testing LiteCrew Connectivity" in result.output
        assert "API Server" in result.output

    @patch("httpx.Client")
    def test_debug_performance(self, mock_client, runner):
        """Test performance analysis."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"memory_mb": 30.0}

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance

        result = runner.invoke(cli, ["debug", "performance"])
        assert result.exit_code == 0
        assert "Performance Analysis" in result.output
        assert "Performance Metrics" in result.output


class TestConfigCommands:
    """Test configuration commands."""

    def test_config_help(self, runner):
        """Test config command help."""
        result = runner.invoke(cli, ["config", "--help"])
        assert result.exit_code == 0
        assert "init" in result.output
        assert "validate" in result.output
        assert "show" in result.output
        assert "set" in result.output

    def test_config_init(self, runner):
        """Test config initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test-config.yaml"

            result = runner.invoke(
                cli,
                ["config", "init", "--output", str(config_path), "--template", "basic"],
            )

            assert result.exit_code == 0
            assert "Configuration initialized" in result.output
            assert config_path.exists()

            # Verify config content
            with open(config_path) as f:
                content = f.read()
                assert "api:" in content
                assert "url: http://localhost:8000" in content

    def test_config_validate_valid(self, runner, temp_config_file):
        """Test validation of valid config."""
        result = runner.invoke(cli, ["config", "validate", temp_config_file])
        assert result.exit_code == 0
        assert "Configuration is valid" in result.output

    def test_config_show_system(self, runner):
        """Test showing system configuration paths."""
        result = runner.invoke(cli, ["config", "show", "--system"])
        assert result.exit_code == 0
        assert "Configuration Paths" in result.output
        assert "User config" in result.output
        assert "System config" in result.output


class TestCLIPerformance:
    """Test CLI performance requirements."""

    def test_command_execution_speed(self, runner):
        """Test that commands execute quickly."""
        commands_to_test = [
            ["--help"],
            ["--version"],
            ["crew", "--help"],
            ["task", "--help"],
            ["export", "--help"],
            ["debug", "--help"],
            ["config", "--help"],
        ]

        for cmd in commands_to_test:
            start_time = time.perf_counter()
            result = runner.invoke(cli, cmd)
            duration = (time.perf_counter() - start_time) * 1000

            assert result.exit_code == 0
            assert duration < 100  # <100ms command execution

    def test_help_text_coverage(self, runner):
        """Test that all commands have help text."""
        # Test main help
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert len(result.output) > 100  # Substantial help text

        # Test subcommand help
        subcommands = ["crew", "task", "export", "debug", "config"]
        for subcmd in subcommands:
            result = runner.invoke(cli, [subcmd, "--help"])
            assert result.exit_code == 0
            assert len(result.output) > 50  # Help text exists
            assert subcmd in result.output.lower()  # Command name in help

    def test_error_handling(self, runner):
        """Test graceful error handling."""
        # Test invalid command
        result = runner.invoke(cli, ["invalid-command"])
        assert result.exit_code != 0

        # Test invalid option
        result = runner.invoke(cli, ["--invalid-option"])
        assert result.exit_code != 0

        # Test missing required argument
        result = runner.invoke(cli, ["crew", "create"])
        assert result.exit_code != 0

        # Test invalid file path
        result = runner.invoke(cli, ["crew", "create", "/nonexistent/file.yaml"])
        assert result.exit_code != 0


def test_cli_integration_workflow(runner, temp_crew_file):
    """Test a complete CLI workflow."""
    with patch("httpx.Client") as mock_client:
        # Mock successful API responses for a complete workflow
        mock_responses = {
            "health": Mock(
                status_code=200, json=lambda: {"status": "healthy", "memory_mb": 25}
            ),
            "crews": Mock(status_code=200, json=lambda: {"crews": []}),
            "create": Mock(
                status_code=201,
                json=lambda: {
                    "crew_id": "test-123",
                    "name": "Test Crew",
                    "agents": [],
                    "tasks": [],
                },
            ),
            "execute": Mock(
                status_code=200,
                json=lambda: {
                    "execution_id": "exec-123",
                    "status": "completed",
                    "result": {},
                },
            ),
        }

        def mock_request(*args, **kwargs):
            url = args[0] if args else kwargs.get("url", "")
            if "health" in url:
                return mock_responses["health"]
            elif "crews" in url and "execute" in url:
                return mock_responses["execute"]
            elif "crews" in url:
                if kwargs.get("json"):  # POST request
                    return mock_responses["create"]
                else:  # GET request
                    return mock_responses["crews"]
            return Mock(status_code=404)

        mock_client_instance = Mock()
        mock_client_instance.get.side_effect = mock_request
        mock_client_instance.post.side_effect = mock_request
        mock_client.return_value.__enter__.return_value = mock_client_instance

        # 1. Check status
        result = runner.invoke(cli, ["status"])
        assert result.exit_code == 0

        # 2. Create crew
        result = runner.invoke(cli, ["crew", "create", temp_crew_file])
        assert result.exit_code == 0
        assert "created successfully" in result.output

        # 3. List crews
        result = runner.invoke(cli, ["crew", "list"])
        assert result.exit_code == 0

        # 4. Execute crew (would require crew ID from step 2 in real scenario)
        # This is simplified for testing
        with patch("click.prompt", return_value="test-123"):
            result = runner.invoke(cli, ["crew", "execute", "test-123"])
            assert result.exit_code == 0
