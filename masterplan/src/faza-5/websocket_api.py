# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Subscribe to events
    async def forward_events(event_name: str, data: dict):
        await websocket.send_json({
            "type": event_name,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    EventBus.subscribe("agent.*", forward_events)
    EventBus.subscribe("task.*", forward_events)
    EventBus.subscribe("metrics.*", forward_events)
    
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(30)
            await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        # Unsubscribe when disconnected
        EventBus.unsubscribe("agent.*", forward_events)
        EventBus.unsubscribe("task.*", forward_events)
        EventBus.unsubscribe("metrics.*", forward_events)