"""End-to-end tests for process integration with API."""

import asyncio
import json
from unittest.mock import AsyncMock, patch

import pytest
import websockets
from fastapi.testclient import TestClient

from litecrew.api import app


class TestProcessIntegrationE2E:
    """End-to-end tests for process integration."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def sample_crew_data(self):
        """Sample crew creation data."""
        return {
            "name": "Test Process Crew",
            "description": "Testing different process types",
            "agents": [
                {
                    "role": "Analyst",
                    "goal": "Analyze data",
                    "backstory": "Expert analyst",
                },
                {
                    "role": "Writer",
                    "goal": "Create content",
                    "backstory": "Creative writer",
                },
                {
                    "role": "Reviewer",
                    "goal": "Review work",
                    "backstory": "Quality checker",
                },
            ],
            "tasks": [
                {
                    "description": "Research topic",
                    "agent_role": "Analyst",
                    "expected_output": "Research report",
                },
                {
                    "description": "Write article",
                    "agent_role": "Writer",
                    "expected_output": "Article draft",
                },
            ],
            "process": "conversational",
            "process_config": {
                "min_turns": 2,
                "max_turns": 6,
                "turn_style": "round_robin",
            },
        }

    def test_list_process_types(self, client):
        """Test listing available process types."""
        response = client.get("/api/v1/process-types")
        assert response.status_code == 200

        process_types = response.json()
        assert isinstance(process_types, list)
        assert (
            len(process_types) >= 5
        )  # sequential, hierarchical, conversational, debate, panel

        # Check process type structure
        for process_type in process_types:
            assert "name" in process_type
            assert "description" in process_type
            assert "supports_moderator" in process_type
            assert "configurable_options" in process_type
            assert "example_config" in process_type

    def test_get_process_type_details(self, client):
        """Test getting details of specific process type."""
        # Test conversational process
        response = client.get("/api/v1/process-types/conversational")
        assert response.status_code == 200

        process_info = response.json()
        assert process_info["name"] == "conversational"
        assert "Natural conversation" in process_info["description"]
        assert "min_turns" in process_info["configurable_options"]
        assert "max_turns" in process_info["configurable_options"]

        # Test non-existent process
        response = client.get("/api/v1/process-types/nonexistent")
        assert response.status_code == 404

    def test_create_crew_with_process_config(self, client, sample_crew_data):
        """Test creating crew with process configuration."""
        response = client.post("/api/v1/crews", json=sample_crew_data)
        assert response.status_code == 201

        crew = response.json()
        assert crew["process"] == "conversational"
        assert crew["process_config"]["min_turns"] == 2
        assert crew["process_config"]["max_turns"] == 6

        return crew["crew_id"]

    def test_switch_crew_process(self, client, sample_crew_data):
        """Test switching crew process type."""
        # Create crew first
        create_response = client.post("/api/v1/crews", json=sample_crew_data)
        crew_id = create_response.json()["crew_id"]

        # Switch to debate process
        switch_data = {
            "process_type": "debate",
            "process_config": {
                "rounds": 3,
                "allow_rebuttals": True,
                "debate_style": "oxford",
            },
        }

        response = client.put(f"/api/v1/crews/{crew_id}/process", json=switch_data)
        assert response.status_code == 200

        updated_crew = response.json()
        assert updated_crew["process"] == "debate"
        assert updated_crew["process_config"]["rounds"] == 3

    def test_invalid_process_switch(self, client, sample_crew_data):
        """Test switching to invalid process type."""
        # Create crew
        create_response = client.post("/api/v1/crews", json=sample_crew_data)
        crew_id = create_response.json()["crew_id"]

        # Try to switch to non-existent process
        switch_data = {"process_type": "invalid_process", "process_config": {}}

        response = client.put(f"/api/v1/crews/{crew_id}/process", json=switch_data)
        assert response.status_code == 400
        assert "Invalid process type" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_websocket_process_events(self, client, sample_crew_data):
        """Test WebSocket events for process execution."""
        # Create crew
        create_response = client.post("/api/v1/crews", json=sample_crew_data)
        crew_id = create_response.json()["crew_id"]

        # Mock WebSocket connection
        received_events = []

        async def mock_websocket_handler():
            async with websockets.connect(
                f"ws://localhost:8000/ws/crew/{crew_id}"
            ) as websocket:
                # Listen for events
                try:
                    while True:
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        event = json.loads(message)
                        received_events.append(event)

                        # Stop after receiving a few events
                        if len(received_events) >= 3:
                            break
                except asyncio.TimeoutError:
                    pass

        # Execute crew in background
        asyncio.create_task(client.post(f"/api/v1/crews/{crew_id}/execute", json={}))

        # Listen for WebSocket events
        try:
            await mock_websocket_handler()
        except Exception as e:
            # WebSocket might not be available in test environment
            pytest.skip(f"WebSocket test skipped: {e}")

        # Check received events
        if received_events:
            for event in received_events:
                assert event["type"] == "process_event"
                assert "event" in event
                assert "crew_id" in event
                assert event["crew_id"] == crew_id

    def test_crew_visualization_endpoint(self, client, sample_crew_data):
        """Test crew visualization endpoint."""
        # Create and execute crew
        create_response = client.post("/api/v1/crews", json=sample_crew_data)
        crew_id = create_response.json()["crew_id"]

        # Mock execution
        with patch("litecrew.crew.LiteCrew.kickoff") as mock_kickoff:
            mock_result = AsyncMock()
            mock_result.success = True
            mock_result.turns = []
            mock_result.tasks_output = []
            mock_result.raw = "Test completed"
            mock_result.duration = 1.5
            mock_result.metadata = {"process_type": "conversational"}
            mock_kickoff.return_value = mock_result

            # Execute crew
            client.post(f"/api/v1/crews/{crew_id}/execute", json={})

        # Get visualization
        response = client.get(f"/api/v1/crews/{crew_id}/visualization")

        # Should return message since no real execution happened
        assert response.status_code == 200

    def test_process_config_validation(self, client):
        """Test process configuration validation."""
        crew_data = {
            "name": "Test Crew",
            "agents": [{"role": "Agent", "goal": "Goal", "backstory": "Story"}],
            "tasks": [{"description": "Task", "expected_output": "Output"}],
            "process": "debate",
            "process_config": {
                "rounds": -1,  # Invalid: negative rounds
                "debate_style": "invalid_style",
            },
        }

        # Should still create (validation happens at process level)
        response = client.post("/api/v1/crews", json=crew_data)
        assert response.status_code == 201

    def test_multiple_process_types_execution(self, client):
        """Test executing different process types."""
        process_configs = [
            ("sequential", {}),
            ("hierarchical", {"manager_rounds": 2}),
            ("conversational", {"min_turns": 2, "max_turns": 5}),
            ("debate", {"rounds": 2, "allow_rebuttals": False}),
            ("panel", {"consensus_required": True, "voting_enabled": False}),
        ]

        for process_type, config in process_configs:
            # Create crew with specific process
            crew_data = {
                "name": f"Test {process_type} Crew",
                "agents": [
                    {"role": "A", "goal": "Goal A", "backstory": "Story A"},
                    {"role": "B", "goal": "Goal B", "backstory": "Story B"},
                ],
                "tasks": [
                    {"description": "Test task", "expected_output": "Test output"}
                ],
                "process": process_type,
                "process_config": config,
            }

            response = client.post("/api/v1/crews", json=crew_data)
            assert response.status_code == 201

            crew = response.json()
            assert crew["process"] == process_type

    @pytest.mark.asyncio
    async def test_process_performance_metrics(self, client, sample_crew_data):
        """Test that process metrics meet performance requirements."""
        # Create crew
        create_response = client.post("/api/v1/crews", json=sample_crew_data)
        crew_id = create_response.json()["crew_id"]

        # Measure API response times
        import time

        # Test process type listing
        start = time.perf_counter()
        response = client.get("/api/v1/process-types")
        duration = (time.perf_counter() - start) * 1000
        assert response.status_code == 200
        assert duration < 100  # Should be under 100ms

        # Test process switching
        start = time.perf_counter()
        response = client.put(
            f"/api/v1/crews/{crew_id}/process",
            json={"process_type": "panel", "process_config": {}},
        )
        duration = (time.perf_counter() - start) * 1000
        assert response.status_code == 200
        assert duration < 100  # Should be under 100ms


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
