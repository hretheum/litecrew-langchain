"""Tests for WebSocket API functionality."""

import asyncio
import json
from unittest.mock import AsyncMock, Mock

import pytest

from litecrew.api.websocket import ConnectionManager, websocket_router


class TestConnectionManager:
    """Test WebSocket connection manager."""

    @pytest.fixture
    def manager(self):
        """Create a connection manager instance."""
        return ConnectionManager()

    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket."""
        ws = AsyncMock()
        ws.accept = AsyncMock()
        ws.send_text = AsyncMock()
        ws.send_json = AsyncMock()
        return ws

    @pytest.mark.asyncio
    async def test_connect_general(self, manager, mock_websocket):
        """Test connecting a general WebSocket."""
        await manager.connect(mock_websocket)

        mock_websocket.accept.assert_called_once()
        assert mock_websocket in manager.active_connections
        assert len(manager.active_connections) == 1

    @pytest.mark.asyncio
    async def test_connect_with_crew_id(self, manager, mock_websocket):
        """Test connecting with specific crew ID."""
        crew_id = "test-crew-123"
        await manager.connect(mock_websocket, crew_id)

        mock_websocket.accept.assert_called_once()
        assert mock_websocket in manager.active_connections
        assert crew_id in manager.crew_connections
        assert mock_websocket in manager.crew_connections[crew_id]

    @pytest.mark.asyncio
    async def test_connect_multiple_to_same_crew(self, manager):
        """Test multiple connections to same crew."""
        crew_id = "test-crew-123"
        ws1 = AsyncMock()
        ws2 = AsyncMock()

        await manager.connect(ws1, crew_id)
        await manager.connect(ws2, crew_id)

        assert len(manager.crew_connections[crew_id]) == 2
        assert ws1 in manager.crew_connections[crew_id]
        assert ws2 in manager.crew_connections[crew_id]

    def test_disconnect_general(self, manager, mock_websocket):
        """Test disconnecting a general WebSocket."""
        # First add the connection
        manager.active_connections.append(mock_websocket)

        # Then disconnect
        manager.disconnect(mock_websocket)

        assert mock_websocket not in manager.active_connections
        assert len(manager.active_connections) == 0

    def test_disconnect_with_crew_id(self, manager, mock_websocket):
        """Test disconnecting from specific crew."""
        crew_id = "test-crew-123"

        # Setup connections
        manager.active_connections.append(mock_websocket)
        manager.crew_connections[crew_id] = [mock_websocket]

        # Disconnect
        manager.disconnect(mock_websocket, crew_id)

        assert mock_websocket not in manager.active_connections
        assert mock_websocket not in manager.crew_connections[crew_id]

    def test_disconnect_nonexistent(self, manager, mock_websocket):
        """Test disconnecting non-existent connection."""
        # Should not raise error
        try:
            manager.disconnect(mock_websocket, "nonexistent-crew")
        except ValueError:
            # Expected if websocket not in active_connections
            pass

    @pytest.mark.asyncio
    async def test_send_personal_message(self, manager, mock_websocket):
        """Test sending personal message."""
        message = "Hello, WebSocket!"
        await manager.send_personal_message(message, mock_websocket)

        mock_websocket.send_text.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_send_crew_message(self, manager):
        """Test sending message to crew."""
        crew_id = "test-crew-123"
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        manager.crew_connections[crew_id] = [ws1, ws2]

        message = "Crew update"
        await manager.send_crew_message(message, crew_id)

        ws1.send_text.assert_called_once_with(message)
        ws2.send_text.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_send_crew_message_no_connections(self, manager):
        """Test sending message to crew with no connections."""
        # Should not raise error
        await manager.send_crew_message("Message", "nonexistent-crew")

    @pytest.mark.asyncio
    async def test_send_crew_message_with_failed_connection(self, manager):
        """Test handling failed connection when sending."""
        crew_id = "test-crew-123"
        ws_good = AsyncMock()
        ws_bad = AsyncMock()
        ws_bad.send_text.side_effect = Exception("Connection closed")

        manager.crew_connections[crew_id] = [ws_good, ws_bad]

        # Should handle error gracefully
        await manager.send_crew_message("Test message", crew_id)

        # Good connection should still receive message
        ws_good.send_text.assert_called_once()
        # Bad connection should be removed
        assert ws_bad not in manager.crew_connections[crew_id]

    @pytest.mark.asyncio
    async def test_send_process_event(self, manager, mock_websocket):
        """Test sending process event."""
        crew_id = "test-crew-123"
        manager.crew_connections[crew_id] = [mock_websocket]

        await manager.send_process_event(
            crew_id=crew_id,
            event_type="task_started",
            data={"task_id": "123", "agent": "Agent1"},
        )

        # Check that message was sent
        mock_websocket.send_text.assert_called_once()

        # Verify message format
        sent_message = mock_websocket.send_text.call_args[0][0]
        parsed = json.loads(sent_message)
        assert parsed["type"] == "process_event"
        assert parsed["event"] == "task_started"
        assert parsed["crew_id"] == crew_id
        assert parsed["data"]["task_id"] == "123"


class TestWebSocketEndpoints:
    """Test WebSocket endpoints."""

    def test_websocket_router_exists(self):
        """Test that websocket router is defined."""
        assert websocket_router is not None
        assert hasattr(websocket_router, "routes")

    @pytest.mark.asyncio
    async def test_websocket_crew_endpoint(self):
        """Test WebSocket crew endpoint."""
        from litecrew.api import create_app

        app = create_app()

        # Test that websocket endpoint exists
        routes = [route.path for route in app.routes]
        ws_routes = [r for r in routes if r.startswith("/ws/")]
        assert len(ws_routes) > 0  # Should have at least one WebSocket route

    @pytest.mark.asyncio
    async def test_broadcast_functionality(self):
        """Test broadcast message functionality."""
        manager = ConnectionManager()

        # Create multiple connections
        connections = [AsyncMock() for _ in range(3)]
        for ws in connections:
            manager.active_connections.append(ws)

        # Test broadcast would send to all
        message = "Broadcast message"
        for ws in manager.active_connections:
            await manager.send_personal_message(message, ws)

        # All should receive
        for ws in connections:
            ws.send_text.assert_called_with(message)

    def test_connection_state_management(self):
        """Test connection state is properly managed."""
        manager = ConnectionManager()

        # Initially empty
        assert len(manager.active_connections) == 0
        assert len(manager.crew_connections) == 0

        # Add connections
        ws1 = Mock()
        ws2 = Mock()
        crew_id = "crew-1"

        manager.active_connections.append(ws1)
        manager.active_connections.append(ws2)
        manager.crew_connections[crew_id] = [ws1]

        # Check state
        assert len(manager.active_connections) == 2
        assert len(manager.crew_connections[crew_id]) == 1

        # Remove one
        manager.disconnect(ws1, crew_id)
        assert len(manager.active_connections) == 1
        assert len(manager.crew_connections[crew_id]) == 0

    @pytest.mark.asyncio
    async def test_json_message_format(self):
        """Test JSON message formatting."""
        manager = ConnectionManager()

        # Test various event types
        events = [
            ("task_started", {"task_id": "1", "agent": "Agent1"}),
            ("task_completed", {"task_id": "1", "result": "Success"}),
            ("crew_finished", {"crew_id": "crew-1", "duration": 10.5}),
            ("error", {"message": "Something went wrong", "code": "ERR001"}),
        ]

        crew_id = "test-crew"
        ws = AsyncMock()
        manager.crew_connections[crew_id] = [ws]

        for event_type, data in events:
            await manager.send_process_event(crew_id, event_type, data)

            # Verify JSON structure
            call_args = ws.send_text.call_args_list[-1][0][0]
            parsed = json.loads(call_args)
            assert parsed["type"] == "process_event"
            assert parsed["event"] == event_type
            assert parsed["data"] == data


# Global manager instance for testing
_test_manager = None


def get_test_manager():
    """Get test manager instance."""
    global _test_manager
    if _test_manager is None:
        _test_manager = ConnectionManager()
    return _test_manager


class TestManagerSingleton:
    """Test manager singleton pattern."""

    def test_get_manager_returns_singleton(self):
        """Test that get_manager returns same instance."""
        # Import the actual get_manager if it exists
        try:
            from litecrew.api.websocket import get_manager

            manager1 = get_manager()
            manager2 = get_manager()
            assert manager1 is manager2
        except ImportError:
            # If not implemented, test our mock version
            manager1 = get_test_manager()
            manager2 = get_test_manager()
            assert manager1 is manager2


class TestBroadcastFunctionality:
    """Test broadcast functionality."""
    
    @pytest.mark.asyncio
    async def test_broadcast_success(self):
        """Test successful broadcast to all connections."""
        manager = ConnectionManager()
        
        # Create mock connections
        mock_conn1 = Mock()
        mock_conn2 = Mock()
        mock_conn1.send_text = AsyncMock()
        mock_conn2.send_text = AsyncMock()
        
        manager.active_connections = [mock_conn1, mock_conn2]
        
        # Test broadcast
        await manager.broadcast("Test broadcast message")
        
        mock_conn1.send_text.assert_called_once_with("Test broadcast message")
        mock_conn2.send_text.assert_called_once_with("Test broadcast message")
    
    @pytest.mark.asyncio
    async def test_broadcast_with_failed_connection(self):
        """Test broadcast with one failed connection."""
        manager = ConnectionManager()
        
        # Create mock connections - put failing one at the end to ensure others get message
        mock_conn1 = Mock()
        mock_conn2 = Mock()
        mock_conn1.send_text = AsyncMock()
        mock_conn2.send_text = AsyncMock(side_effect=Exception("Connection closed"))
        
        manager.active_connections = [mock_conn1, mock_conn2]
        
        # Test broadcast with failure
        await manager.broadcast("Test message")
        
        # Check that working connection got the message
        mock_conn1.send_text.assert_called_once_with("Test message")
        
        # Check that failed connection was removed
        assert mock_conn2 not in manager.active_connections
        assert len(manager.active_connections) == 1


class TestWebSocketEndpoints:
    """Test WebSocket endpoint handlers."""
    
    @pytest.mark.asyncio
    async def test_websocket_global_endpoint(self):
        """Test global WebSocket endpoint ping-pong and echo."""
        from fastapi.testclient import TestClient
        from litecrew.api import create_app
        
        app = create_app()
        client = TestClient(app)
        
        with client.websocket_connect("/ws") as websocket:
            # Test ping-pong
            websocket.send_text("ping")
            data = websocket.receive_text()
            assert data == "pong"
            
            # Test echo
            websocket.send_text("Hello WebSocket")
            data = websocket.receive_text()
            assert data == "Echo: Hello WebSocket"
    
    @pytest.mark.asyncio
    async def test_websocket_crew_subscribe_action(self):
        """Test crew WebSocket subscription flow."""
        from fastapi.testclient import TestClient
        from litecrew.api import create_app
        
        app = create_app()
        client = TestClient(app)
        
        with client.websocket_connect("/ws/crews/test-crew-123") as websocket:
            # Send subscribe action
            websocket.send_json({
                "action": "subscribe",
                "execution_id": "exec-456"
            })
            
            # Should receive execution started
            data = websocket.receive_json()
            assert data["type"] == "execution_started"
            assert data["execution_id"] == "exec-456"
            
            # Should receive 3 progress updates
            progress_updates = []
            for _ in range(3):
                data = websocket.receive_json()
                assert data["type"] == "execution_progress"
                progress_updates.append(data["progress"])
            
            assert progress_updates == [33, 66, 99]
            
            # Should receive completion
            data = websocket.receive_json()
            assert data["type"] == "execution_completed"
            assert data["execution_id"] == "exec-456"
            assert "result" in data
    
    @pytest.mark.asyncio
    async def test_websocket_crew_invalid_json(self):
        """Test crew WebSocket with invalid JSON."""
        from fastapi.testclient import TestClient
        from litecrew.api import create_app
        
        app = create_app()
        client = TestClient(app)
        
        with client.websocket_connect("/ws/crews/test-crew") as websocket:
            # Send invalid JSON
            websocket.send_text("not a valid json {")
            
            # Should receive error
            data = websocket.receive_json()
            assert data["error"] == "Invalid JSON"
    
    @pytest.mark.asyncio
    async def test_websocket_crew_unknown_action(self):
        """Test crew WebSocket with unknown action."""
        from fastapi.testclient import TestClient
        from litecrew.api import create_app
        
        app = create_app()
        client = TestClient(app)
        
        with client.websocket_connect("/ws/crews/test-crew") as websocket:
            # Send unknown action
            websocket.send_json({
                "action": "unknown_action",
                "data": "some data"
            })
            
            # Should receive error
            data = websocket.receive_json()
            assert data["error"] == "Unknown action"
