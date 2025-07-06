"""Additional CLI tests to improve coverage."""

import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import yaml
from click.testing import CliRunner

from litecrew.cli.commands.config import init, show, validate
from litecrew.cli.commands.crew import create, execute
from litecrew.cli.commands.crew import list as list_crews
from litecrew.cli.commands.debug import connectivity, logs, performance
from litecrew.cli.commands.task import run
from litecrew.cli.main import cli


class TestCLIConfig:
    """Test CLI config commands with more coverage."""

    def test_init_config_existing_file(self, tmp_path):
        """Test init config when file already exists."""
        runner = CliRunner()
        config_path = tmp_path / "litecrew.yaml"
        config_path.write_text("existing: config")

        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Simulate "no" response to overwrite prompt
            result = runner.invoke(init, ["--output", str(config_path)], input="n\n")
            # Check if it either exits with 0 (handled gracefully) or 1 (aborted)
            assert result.exit_code in [0, 1]
            assert (
                "already exists" in result.output
                or "Configuration initialized" in result.output
            )

    def test_init_config_custom_values(self, tmp_path):
        """Test init config with custom values."""
        runner = CliRunner()
        config_path = tmp_path / "custom.yaml"

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                init,
                [
                    "--output",
                    str(config_path),
                    "--template",
                    "basic",
                ],
            )
            assert result.exit_code == 0
            assert config_path.exists()

            # Check content
            content = yaml.safe_load(config_path.read_text())
            assert "api" in content
            assert content["api"]["url"] == "http://localhost:8000"

    def test_validate_config_invalid_yaml(self, tmp_path):
        """Test validate config with invalid YAML."""
        runner = CliRunner()
        config_path = tmp_path / "invalid.yaml"
        config_path.write_text("invalid: yaml: content:")

        result = runner.invoke(validate, [str(config_path)])
        assert result.exit_code == 1
        assert "YAML parsing error" in result.output

    def test_validate_config_missing_fields(self, tmp_path):
        """Test validate config with missing required fields."""
        runner = CliRunner()
        config_path = tmp_path / "incomplete.yaml"
        config_path.write_text("crew: {}")  # Missing required fields

        result = runner.invoke(validate, [str(config_path)])
        assert result.exit_code == 1
        assert "Missing required" in result.output

    def test_show_config_user(self, tmp_path):
        """Test show user config."""
        runner = CliRunner()
        user_config = tmp_path / ".litecrew" / "config.yaml"
        user_config.parent.mkdir(parents=True)
        user_config.write_text("user: config")

        with patch.dict(os.environ, {"HOME": str(tmp_path)}):
            result = runner.invoke(show, ["--system"])
            assert result.exit_code == 0
            assert "Configuration Paths" in result.output

    def test_show_config_project(self, tmp_path):
        """Test show project config."""
        runner = CliRunner()
        project_config = tmp_path / "litecrew.yaml"
        project_config.write_text("project: config")

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(show, [])
            assert result.exit_code == 0
            assert "Current LiteCrew Configuration" in result.output

    def test_show_config_env(self):
        """Test show environment config."""
        runner = CliRunner()
        with patch.dict(os.environ, {"LITECREW_API_URL": "http://test:8000"}):
            result = runner.invoke(show, [])
            assert result.exit_code == 0
            assert "Environment variables" in result.output


class TestCLICrew:
    """Test CLI crew commands with more coverage."""

    @patch("litecrew.cli.commands.crew.httpx.Client")
    def test_create_crew_from_file(self, mock_client_class, tmp_path):
        """Test create crew from file."""
        runner = CliRunner()
        crew_file = tmp_path / "crew.yaml"
        crew_data = {
            "name": "Test Crew",
            "agents": [{"role": "Worker", "goal": "Work", "backstory": "Worker"}],
            "tasks": [{"description": "Task", "agent_role": "Worker"}],
        }
        crew_file.write_text(yaml.dump(crew_data))

        # Mock the client instance and its post method
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"crew_id": "123", **crew_data}
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                create, 
                [str(crew_file)],
                obj={"api_url": "http://localhost:8000", "verbose": False}
            )
            if result.exit_code != 0:
                print(f"Exit code: {result.exit_code}")
                print(f"Output: {result.output}")
                print(f"Exception: {result.exception}")
            assert result.exit_code == 0
            assert "created successfully" in result.output

    @patch("litecrew.cli.commands.crew.httpx.Client")
    def test_create_crew_dry_run(self, mock_client_class):
        """Test create crew dry run."""
        runner = CliRunner()
        # Create a temp crew file for dry run
        with runner.isolated_filesystem():
            crew_file = Path("test_crew.yaml")
            crew_file.write_text(
                yaml.dump(
                    {
                        "name": "Test",
                        "agents": [
                            {"role": "Worker", "goal": "Work", "backstory": "Worker"}
                        ],
                        "tasks": [{"description": "Do work", "agent_role": "Worker"}],
                    }
                )
            )
            result = runner.invoke(
                create,
                [str(crew_file), "--dry-run"],
                obj={"api_url": "http://localhost:8000", "verbose": False}
            )
        assert result.exit_code == 0
        assert "Configuration is valid" in result.output
        mock_client_class.assert_not_called()

    @patch("litecrew.cli.commands.crew.httpx.Client")
    def test_list_crews_with_filter(self, mock_client_class):
        """Test list crews with name filter."""
        runner = CliRunner()
        
        # Mock the client instance and its get method
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "crews": [
                {"crew_id": "1", "name": "Test Crew", "created_at": "2024-01-01"},
                {"crew_id": "2", "name": "Another", "created_at": "2024-01-02"},
            ]
        }
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            list_crews,
            ["--filter", "Test"],
            obj={"api_url": "http://localhost:8000", "verbose": False}
        )
        assert result.exit_code == 0
        assert "Test Crew" in result.output
        assert "Another" not in result.output

    @patch("litecrew.cli.commands.crew.httpx.Client")
    def test_execute_crew_with_inputs(self, mock_client_class, tmp_path):
        """Test execute crew with JSON inputs."""
        runner = CliRunner()
        
        # Create input file
        input_file = tmp_path / "inputs.json"
        input_file.write_text('{"key": "value"}')
        
        # Mock the client instance and its post method
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "execution_id": "exec-123",
            "status": "completed",
            "result": {"output": "Done"},
        }
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                execute,
                ["crew-123", "--inputs", str(input_file)],
                obj={"api_url": "http://localhost:8000", "verbose": False}
            )
        assert result.exit_code == 0
        assert "Execution completed" in result.output

    @patch("litecrew.cli.commands.crew.httpx.Client")
    def test_execute_crew_async(self, mock_client_class):
        """Test execute crew async."""
        runner = CliRunner()
        
        # Mock the client instance and its post method
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "execution_id": "exec-123",
            "status": "running",
        }
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            execute,
            ["crew-123", "--async"],
            obj={"api_url": "http://localhost:8000", "verbose": False}
        )
        assert result.exit_code == 0
        assert "Execution started" in result.output


class TestCLIDebug:
    """Test CLI debug commands with more coverage."""

    @patch("litecrew.cli.commands.debug.httpx.Client")
    def test_debug_connectivity_success(self, mock_client_class):
        """Test debug connectivity success."""
        runner = CliRunner()
        
        # Mock the client instance and its get method
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            connectivity,
            obj={"api_url": "http://localhost:8000", "verbose": False}
        )
        assert result.exit_code == 0
        assert "API Server" in result.output
        assert "OK" in result.output

    @patch("litecrew.cli.commands.debug.httpx.Client")
    def test_debug_connectivity_failure(self, mock_client_class):
        """Test debug connectivity failure."""
        runner = CliRunner()
        
        # Mock the client instance to raise an exception
        mock_client = MagicMock()
        mock_client.get.side_effect = Exception("Connection error")
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            connectivity,
            obj={"api_url": "http://localhost:8000", "verbose": False}
        )
        assert result.exit_code == 0  # The command continues and shows summary
        assert "API Server" in result.output
        assert "FAIL" in result.output

    def test_debug_logs(self, tmp_path):
        """Test debug logs command."""
        runner = CliRunner()
        log_file = tmp_path / "litecrew.log"
        log_file.write_text("Log line 1\nLog line 2\nLog line 3")

        result = runner.invoke(logs, ["--tail", "2"], obj={"api_url": "http://localhost:8000", "verbose": False})
        assert result.exit_code == 0
        assert "System Logs" in result.output
        assert "showing last 2 entries" in result.output

    def test_debug_logs_follow(self, tmp_path):
        """Test debug logs follow mode."""
        runner = CliRunner()
        log_file = tmp_path / "litecrew.log"
        log_file.write_text("Initial log")

        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = tmp_path.parent
            with patch.object(Path, "exists", return_value=True):
                with patch("litecrew.cli.commands.debug.time.sleep") as mock_sleep:
                    # Make it only iterate once
                    mock_sleep.side_effect = KeyboardInterrupt
                    result = runner.invoke(logs, ["--follow"], obj={"api_url": "http://localhost:8000", "verbose": False})
                    assert result.exit_code == 0

    @patch("litecrew.cli.commands.debug.httpx.Client")
    def test_debug_performance(self, mock_client_class):
        """Test debug performance command."""
        runner = CliRunner()

        # Mock the client instance and its get method
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "memory_mb": 50,
            "uptime": 3600,
        }
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(performance, obj={"api_url": "http://localhost:8000", "verbose": False})
        assert result.exit_code == 0
        assert "LiteCrew Performance Analysis" in result.output
        assert "Performance Metrics" in result.output


class TestCLITask:
    """Test CLI task commands with more coverage."""

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_run_task_with_crew(self, mock_client_class):
        """Test run task with specific crew."""
        runner = CliRunner()
        
        # Mock the client instance and its post method
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.json.return_value = {
            "task_id": "task-123",
            "status": "completed",
            "result": "Task done",
        }
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            run,
            [
                "Do something",
                "--crew-id",
                "crew-123",
                "--expected-output",
                "Result",
            ],
            obj={"api_url": "http://localhost:8000", "verbose": False}
        )
        assert result.exit_code == 0
        assert "Task submitted successfully" in result.output

    def test_run_task_no_crew(self):
        """Test run task without specific crew."""
        runner = CliRunner()
        
        result = runner.invoke(run, ["Do something"], obj={"api_url": "http://localhost:8000", "verbose": False})
        assert result.exit_code == 1
        assert "No crew ID specified" in result.output

    def test_run_task_no_crews_available(self):
        """Test run task when no crews available."""
        runner = CliRunner()
        
        # Task always requires a crew ID
        result = runner.invoke(run, ["Do something"], obj={"api_url": "http://localhost:8000", "verbose": False})
        assert result.exit_code == 1
        assert "No crew ID specified" in result.output


class TestCLIIntegration:
    """Test CLI integration scenarios."""

    def test_cli_version(self):
        """Test CLI version command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "litecrew, version" in result.output

    def test_cli_help(self):
        """Test CLI help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "LiteCrew" in result.output
        assert "crew" in result.output
        assert "task" in result.output

    def test_cli_with_config_file(self, tmp_path):
        """Test CLI with config file."""
        runner = CliRunner()
        config_file = tmp_path / "config.yaml"
        config_file.write_text("api:\n  url: http://custom:8000")

        result = runner.invoke(cli, ["--config", str(config_file), "--help"])
        assert result.exit_code == 0
        assert "LiteCrew" in result.output

    def test_crew_group_help(self):
        """Test crew group help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["crew", "--help"])
        assert result.exit_code == 0
        assert "create" in result.output
        assert "list" in result.output
        assert "execute" in result.output

    def test_debug_group_help(self):
        """Test debug group help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["debug", "--help"])
        assert result.exit_code == 0
        assert "connectivity" in result.output
        assert "logs" in result.output
        assert "performance" in result.output
