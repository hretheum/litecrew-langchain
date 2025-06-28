# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    # Verify authentication before accepting connection
    try:
        # TODO: Implement your token verification logic here
        # user = await verify_jwt_token(token)
        # if not user:
        #     await websocket.close(code=1008, reason="Unauthorized")
        #     return
        
        # For now, check if token is provided and not empty
        if not token or len(token) < 10:
            await websocket.close(code=1008, reason="Invalid token")
            return
            
    except Exception:
        await websocket.close(code=1008, reason="Authentication failed")
        return
    
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