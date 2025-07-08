"""Tests for CLI task commands."""

from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from litecrew.cli.commands.task import task_group


class TestTaskRun:
    """Test task run command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_context(self):
        """Mock CLI context."""
        return {"api_url": "http://localhost:8000", "verbose": False}

    def test_run_no_crew_id(self, runner):
        """Test running task without crew ID."""
        with runner.isolated_filesystem():
            result = runner.invoke(
                task_group,
                ["run", "Test task"],
                obj={"api_url": "http://localhost:8000", "verbose": False},
            )

        assert result.exit_code == 1
        assert "❌ No crew ID specified" in result.output
        assert "Hint: Run 'litecrew crew list'" in result.output

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_run_success(self, mock_client_class, runner):
        """Test successful task submission."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.json.return_value = {"task_id": "task-123"}

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["run", "Test task description", "--crew-id", "crew-123"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 0
        assert "🚀 Submitting task to crew crew-123" in result.output
        assert "✅ Task submitted successfully" in result.output
        assert "task-123" in result.output

        # Verify API call
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert "crews/crew-123/tasks" in call_args[0][0]
        assert call_args[1]["json"]["description"] == "Test task description"
        assert call_args[1]["json"]["priority"] == "medium"

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_run_with_options(self, mock_client_class, runner):
        """Test task submission with all options."""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.json.return_value = {"task_id": "task-456"}

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            [
                "run",
                "Complex task",
                "--crew-id",
                "crew-456",
                "--expected-output",
                "Detailed report",
                "--priority",
                "high",
            ],
            obj={"api_url": "http://localhost:8000", "verbose": True},
        )

        assert result.exit_code == 0
        assert "📋 Task Details:" in result.output
        assert "Priority: high" in result.output
        assert "Expected Output: Detailed report" in result.output

        # Verify API call data
        call_args = mock_client.post.call_args
        json_data = call_args[1]["json"]
        assert json_data["description"] == "Complex task"
        assert json_data["expected_output"] == "Detailed report"
        assert json_data["priority"] == "high"

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_run_crew_not_found(self, mock_client_class, runner):
        """Test task submission with non-existent crew."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Crew not found"}

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["run", "Test task", "--crew-id", "nonexistent"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 1
        assert "❌ Crew nonexistent not found" in result.output

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_run_api_error(self, mock_client_class, runner):
        """Test task submission with API error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"detail": "Internal server error"}
        mock_response.text = '{"detail": "Internal server error"}'

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["run", "Test task", "--crew-id", "crew-123"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 1
        assert "❌ Failed to submit task" in result.output
        assert "Internal server error" in result.output

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_run_api_error_no_json(self, mock_client_class, runner):
        """Test task submission with API error and no JSON response."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_response.text = ""

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["run", "Test task", "--crew-id", "crew-123"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 1
        assert "❌ Failed to submit task" in result.output
        assert "Unknown error" in result.output

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_run_network_error(self, mock_client_class, runner):
        """Test task submission with network error."""
        mock_client = Mock()
        mock_client.post.side_effect = Exception("Connection failed")
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["run", "Test task", "--crew-id", "crew-123"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 1
        assert "❌ Error: Connection failed" in result.output

    def test_run_default_expected_output(self, runner):
        """Test that default expected output is used."""
        with patch("litecrew.cli.commands.task.httpx.Client") as mock_client_class:
            mock_response = Mock()
            mock_response.status_code = 202
            mock_response.json.return_value = {"task_id": "task-789"}

            mock_client = Mock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__enter__.return_value = mock_client

            result = runner.invoke(
                task_group,
                ["run", "Test task", "--crew-id", "crew-123"],
                obj={"api_url": "http://localhost:8000", "verbose": False},
            )

            # Check that default expected output was used
            call_args = mock_client.post.call_args
            assert call_args[1]["json"]["expected_output"] == "Task result"


class TestTaskStatus:
    """Test task status command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_status_simple(self, mock_client_class, runner):
        """Test simple status check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "task_id": "task-123",
            "status": "completed",
            "description": "Test task description",
            "priority": "medium",
            "created_at": "2025-01-01T00:00:00Z",
        }

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["status", "task-123"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 0
        assert "📋 Task task-123 Status: ✅ COMPLETED" in result.output
        assert "Description: Test task description" in result.output
        assert "Priority: medium" in result.output

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_status_verbose(self, mock_client_class, runner):
        """Test verbose status check."""
        task_data = {
            "task_id": "task-123",
            "status": "completed",
            "description": "Test task",
            "priority": "high",
            "created_at": "2025-01-01T00:00:00Z",
            "result": "Task completed successfully",
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = task_data

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["status", "task-123"],
            obj={"api_url": "http://localhost:8000", "verbose": True},
        )

        assert result.exit_code == 0
        assert "📝 Task Details:" in result.output
        # Should contain the full JSON output
        assert '"task_id": "task-123"' in result.output
        assert '"result": "Task completed successfully"' in result.output

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_status_different_states(self, mock_client_class, runner):
        """Test status display for different task states."""
        status_cases = [
            ("completed", "✅ COMPLETED"),
            ("failed", "❌ FAILED"),
            ("running", "⏳ RUNNING"),
            ("in_progress", "⏳ IN_PROGRESS"),
            ("pending", "🔄 PENDING"),
        ]

        for status, expected_display in status_cases:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "task_id": "task-123",
                "status": status,
                "description": "Test task",
                "priority": "medium",
                "created_at": "2025-01-01T00:00:00Z",
            }

            mock_client = Mock()
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__enter__.return_value = mock_client

            result = runner.invoke(
                task_group,
                ["status", "task-123"],
                obj={"api_url": "http://localhost:8000", "verbose": False},
            )

            assert result.exit_code == 0
            assert expected_display in result.output

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_status_not_found(self, mock_client_class, runner):
        """Test status check for non-existent task."""
        mock_response = Mock()
        mock_response.status_code = 404

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["status", "nonexistent"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 1
        assert "❌ Task nonexistent not found" in result.output

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_status_api_error(self, mock_client_class, runner):
        """Test status check with API error."""
        mock_response = Mock()
        mock_response.status_code = 500

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["status", "task-123"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 1
        assert "❌ Failed to fetch task: HTTP 500" in result.output

    @patch("litecrew.cli.commands.task.time.sleep")
    @patch("litecrew.cli.commands.task.time.time")
    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_status_wait_completion(
        self, mock_client_class, mock_time, mock_sleep, runner
    ):
        """Test waiting for task completion."""
        # Mock time progression
        time_values = [0, 1, 2, 3, 4]  # Simulate 4 seconds passing
        mock_time.side_effect = time_values

        # First few calls return running, then final status call returns completed
        responses = []
        for status in [
            "running",
            "running",
            "completed",
            "completed",
        ]:  # Added extra for final call
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "task_id": "task-123",
                "status": status,
                "description": "Test task",
                "priority": "medium",
                "created_at": "2025-01-01T00:00:00Z",
            }
            responses.append(mock_response)

        mock_client = Mock()
        mock_client.get.side_effect = responses
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["status", "task-123", "--wait", "--timeout", "300"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 0
        assert "⏳ Waiting for task task-123 completion" in result.output
        assert "Status: running..." in result.output
        assert "✅ COMPLETED" in result.output

        # Should have called sleep between polls
        assert mock_sleep.call_count >= 1

    @patch("litecrew.cli.commands.task.time.sleep")
    @patch("litecrew.cli.commands.task.time.time")
    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_status_wait_timeout(
        self, mock_client_class, mock_time, mock_sleep, runner
    ):
        """Test waiting for task with timeout."""
        # Mock time progression beyond timeout
        mock_time.side_effect = [0, 100, 200, 350]  # Exceeds 300s timeout

        # Always return running status
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "task_id": "task-123",
            "status": "running",
            "description": "Test task",
            "priority": "medium",
        }

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["status", "task-123", "--wait", "--timeout", "300"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 0
        assert "⏱️ Timeout waiting for task completion" in result.output
        assert "⏳ RUNNING" in result.output  # Final status

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_status_wait_task_not_found_during_wait(self, mock_client_class, runner):
        """Test waiting when task is not found during polling."""
        mock_response = Mock()
        mock_response.status_code = 404

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["status", "nonexistent", "--wait"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 1
        assert "❌ Task nonexistent not found" in result.output

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_status_wait_api_error_during_wait(self, mock_client_class, runner):
        """Test waiting when API error occurs during polling."""
        mock_response = Mock()
        mock_response.status_code = 500

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["status", "task-123", "--wait"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 1
        assert "❌ Failed to check status: HTTP 500" in result.output

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_status_network_error(self, mock_client_class, runner):
        """Test status check with network error."""
        mock_client = Mock()
        mock_client.get.side_effect = Exception("Network error")
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["status", "task-123"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 1
        assert "❌ Error: Network error" in result.output


class TestTaskList:
    """Test task list command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def sample_tasks(self):
        """Sample task data."""
        return {
            "tasks": [
                {
                    "task_id": "task-123-long-id",
                    "description": "This is a very long task description that should be truncated",
                    "status": "completed",
                    "priority": "high",
                    "crew_id": "crew-1",
                },
                {
                    "task_id": "task-456",
                    "description": "Short task",
                    "status": "failed",
                    "priority": "medium",
                    "crew_id": "crew-2",
                },
                {
                    "task_id": "task-789",
                    "description": "Running task",
                    "status": "running",
                    "priority": "low",
                    "crew_id": "crew-1",
                },
            ]
        }

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_list_tasks(self, mock_client_class, runner, sample_tasks):
        """Test listing all tasks."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_tasks

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["list"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 0
        assert "📋 Found 3 task(s):" in result.output
        assert "task-123" in result.output  # Truncated ID
        assert "✅" in result.output  # Completed icon
        assert "❌" in result.output  # Failed icon
        assert "⏳" in result.output  # Running icon
        assert (
            "This is a very long task description tha..." in result.output
        )  # Truncated desc

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_list_tasks_filter_by_crew(self, mock_client_class, runner, sample_tasks):
        """Test listing tasks filtered by crew ID."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_tasks

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["list", "--crew-id", "crew-1"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 0
        assert "📋 Found 2 task(s):" in result.output  # Should filter to 2 tasks
        assert "task-123" in result.output
        assert "task-789" in result.output
        assert "task-456" not in result.output  # Should be filtered out

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_list_tasks_filter_by_status(self, mock_client_class, runner, sample_tasks):
        """Test listing tasks filtered by status."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_tasks

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["list", "--status", "completed"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 0
        assert "📋 Found 1 task(s):" in result.output  # Should filter to 1 task
        assert "task-123" in result.output
        assert "✅" in result.output  # Completed icon

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_list_tasks_limit(self, mock_client_class, runner, sample_tasks):
        """Test listing tasks with limit."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_tasks

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["list", "--limit", "2"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 0
        assert "📋 Found 2 task(s):" in result.output  # Should limit to 2 tasks
        # Should show first 2 tasks
        assert "task-123" in result.output
        assert "task-456" in result.output

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_list_tasks_empty(self, mock_client_class, runner):
        """Test listing when no tasks exist."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"tasks": []}

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["list"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 0
        assert "📋 No tasks found" in result.output

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_list_tasks_api_error(self, mock_client_class, runner):
        """Test listing tasks with API error."""
        mock_response = Mock()
        mock_response.status_code = 500

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["list"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 1
        assert "❌ Failed to fetch tasks" in result.output

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_list_tasks_network_error(self, mock_client_class, runner):
        """Test listing tasks with network error."""
        mock_client = Mock()
        mock_client.get.side_effect = Exception("Connection failed")
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["list"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 1
        assert "❌ Error: Connection failed" in result.output

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_list_tasks_combined_filters(self, mock_client_class, runner, sample_tasks):
        """Test listing tasks with multiple filters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_tasks

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["list", "--crew-id", "crew-1", "--status", "running", "--limit", "1"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 0
        assert "📋 Found 1 task(s):" in result.output
        assert "task-789" in result.output  # Only running task in crew-1
        assert "⏳" in result.output

    @patch("litecrew.cli.commands.task.httpx.Client")
    def test_list_tasks_missing_fields(self, mock_client_class, runner):
        """Test listing tasks with missing fields in response."""
        tasks_with_missing_fields = {
            "tasks": [
                {
                    "task_id": "task-incomplete",
                    # Missing description, status, priority, crew_id
                }
            ]
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = tasks_with_missing_fields

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = runner.invoke(
            task_group,
            ["list"],
            obj={"api_url": "http://localhost:8000", "verbose": False},
        )

        assert result.exit_code == 0
        assert "task-inc" in result.output  # Truncated ID
        assert "No description" in result.output
        assert "unknown" in result.output  # Default values
        assert "🔄" in result.output  # Default status icon


class TestTaskGroup:
    """Test task command group."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def test_task_group_help(self, runner):
        """Test task group help."""
        result = runner.invoke(task_group, ["--help"])

        assert result.exit_code == 0
        assert "Run and manage individual tasks." in result.output
        assert "run" in result.output
        assert "status" in result.output
        assert "list" in result.output

    def test_run_command_help(self, runner):
        """Test run command help."""
        result = runner.invoke(task_group, ["run", "--help"])

        assert result.exit_code == 0
        assert "Run a single task." in result.output
        assert "--crew-id" in result.output
        assert "--expected-output" in result.output
        assert "--priority" in result.output

    def test_status_command_help(self, runner):
        """Test status command help."""
        result = runner.invoke(task_group, ["status", "--help"])

        assert result.exit_code == 0
        assert "Check task status." in result.output
        assert "--wait" in result.output
        assert "--timeout" in result.output

    def test_list_command_help(self, runner):
        """Test list command help."""
        result = runner.invoke(task_group, ["list", "--help"])

        assert result.exit_code == 0
        assert "List tasks." in result.output
        assert "--crew-id" in result.output
        assert "--status" in result.output
        assert "--limit" in result.output
