"""WebSocket callbacks for process events."""

from datetime import datetime
from typing import Any, Dict, Optional

from litecrew.processes import ProcessConfig

from .websocket import manager


class WebSocketProcessCallback:
    """Callback handler that sends process events via WebSocket."""

    def __init__(self, crew_id: str):
        self.crew_id = crew_id

    def on_event(self, event_type: str, data: Any) -> None:
        """Handle process events and send via WebSocket."""
        # Convert data to serializable format
        serializable_data = self._make_serializable(data)

        # Map internal events to user-friendly events
        event_mapping = {
            "task_start": "task_started",
            "task_complete": "task_completed",
            "task_progress": "task_progress",
            "panel_topic_start": "panel_discussion_started",
            "panel_topic_complete": "panel_discussion_completed",
            "debate_start": "debate_round_started",
            "debate_complete": "debate_round_completed",
        }

        user_event = event_mapping.get(event_type, event_type)

        # Send via WebSocket
        import asyncio

        asyncio.create_task(
            manager.send_process_event(
                self.crew_id,
                user_event,
                {"timestamp": datetime.utcnow().isoformat(), "data": serializable_data},
            )
        )

    def _make_serializable(self, data: Any) -> Any:
        """Convert data to JSON-serializable format."""
        if isinstance(data, dict):
            return {k: self._make_serializable(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return [self._make_serializable(item) for item in data]
        elif hasattr(data, "__dict__"):
            # Handle objects with attributes
            return {
                "type": data.__class__.__name__,
                "attributes": self._make_serializable(
                    {k: v for k, v in data.__dict__.items() if not k.startswith("_")}
                ),
            }
        elif isinstance(data, (str, int, float, bool, type(None))):
            return data
        else:
            return str(data)


def create_process_config_with_websocket(
    crew_id: str, base_config: Optional[Dict[str, Any]] = None
) -> ProcessConfig:
    """Create process config with WebSocket callback."""
    config_dict = (base_config or {}).copy()

    # Create callback
    ws_callback = WebSocketProcessCallback(crew_id)

    # Add to callbacks list
    callbacks = config_dict.get("callbacks", [])
    callbacks.append(ws_callback)
    config_dict["callbacks"] = callbacks

    # Create ProcessConfig
    config_fields = {"verbose", "max_iterations", "timeout", "callbacks", "metadata"}
    process_config_dict = {k: v for k, v in config_dict.items() if k in config_fields}

    return ProcessConfig(**process_config_dict)
