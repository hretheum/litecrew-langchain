"""WebSocket handlers for real-time updates."""

import asyncio
import json
from typing import Dict, List, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


# Connection manager
class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []
        self.crew_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, crew_id: Optional[str] = None) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        if crew_id:
            if crew_id not in self.crew_connections:
                self.crew_connections[crew_id] = []
            self.crew_connections[crew_id].append(websocket)

    def disconnect(self, websocket: WebSocket, crew_id: Optional[str] = None) -> None:
        self.active_connections.remove(websocket)
        if crew_id and crew_id in self.crew_connections:
            if websocket in self.crew_connections[crew_id]:
                self.crew_connections[crew_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        await websocket.send_text(message)

    async def send_crew_message(self, message: str, crew_id: str) -> None:
        if crew_id in self.crew_connections:
            for connection in self.crew_connections[crew_id]:
                try:
                    await connection.send_text(message)
                except Exception:
                    pass

    async def broadcast(self, message: str) -> None:
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Global WebSocket endpoint."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await manager.send_personal_message("pong", websocket)
            else:
                await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/ws/crews/{crew_id}")
async def crew_websocket_endpoint(websocket: WebSocket, crew_id: str) -> None:
    """Crew-specific WebSocket endpoint."""
    await manager.connect(websocket, crew_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)

                if message.get("action") == "subscribe":
                    execution_id = message.get("execution_id")
                    # Send mock execution updates
                    await manager.send_personal_message(
                        json.dumps(
                            {
                                "type": "execution_started",
                                "execution_id": execution_id,
                                "timestamp": "2025-07-03T00:00:00Z",
                            }
                        ),
                        websocket,
                    )

                    # Simulate progress updates
                    for i in range(3):
                        await asyncio.sleep(0.1)
                        await manager.send_personal_message(
                            json.dumps(
                                {
                                    "type": "execution_progress",
                                    "execution_id": execution_id,
                                    "progress": (i + 1) * 33,
                                    "message": f"Step {i + 1} completed",
                                }
                            ),
                            websocket,
                        )

                    await manager.send_personal_message(
                        json.dumps(
                            {
                                "type": "execution_completed",
                                "execution_id": execution_id,
                                "result": "Task completed successfully",
                            }
                        ),
                        websocket,
                    )
                else:
                    await manager.send_personal_message(
                        json.dumps({"error": "Unknown action"}), websocket
                    )
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    json.dumps({"error": "Invalid JSON"}), websocket
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket, crew_id)


websocket_router = router
