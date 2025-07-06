# LiteCrew API Reference

## Base URL

**Production**: `https://api.litecrew.app/api/v1`  
**Local Development**: `http://localhost:8000/api/v1`

## Authentication

All API endpoints (except health check) require authentication via API key:

```http
X-API-Key: your-api-key-here
```

### Rate Limits
- **Without authentication**: 60 requests/minute
- **With authentication**: 600 requests/minute

## Endpoints

### Health Check

Check if the API is running and healthy.

```http
GET /health
```

**Response**
```json
{
  "status": "healthy",
  "version": "0.6.0",
  "environment": "production",
  "metrics": {
    "uptime": "2h 15m",
    "memory_usage": "17.2MB",
    "cpu_percent": "2.3",
    "active_crews": 5,
    "total_tasks": 127
  },
  "timestamp": "2025-07-06T20:15:00Z",
  "memory_mb": 17.2
}
```

### Crews

#### Create Crew

Create a new crew with agents and tasks.

```http
POST /crews
Content-Type: application/json
X-API-Key: your-api-key
```

**Request Body**
```json
{
  "name": "Research Crew",
  "description": "A crew for research and content creation",
  "agents": [
    {
      "role": "Researcher",
      "goal": "Find accurate information",
      "backstory": "Expert at research and analysis",
      "tools": ["search", "scrape"],
      "allow_delegation": true,
      "verbose": true,
      "max_iter": 5,
      "max_rpm": 60
    },
    {
      "role": "Writer",
      "goal": "Create engaging content",
      "backstory": "Professional content creator",
      "tools": ["write"],
      "allow_delegation": false
    }
  ],
  "tasks": [
    {
      "description": "Research AI frameworks performance",
      "agent_role": "Researcher",
      "expected_output": "Summary of benchmark results",
      "tools": ["search"],
      "async_execution": false,
      "context": []
    },
    {
      "description": "Write blog post about findings",
      "agent_role": "Writer",
      "expected_output": "Blog post draft",
      "context": [0],  // Uses output from first task
      "output_json": false,
      "output_dataclass": null
    }
  ],
  "process": "sequential",  // or "hierarchical"
  "verbose": true,
  "memory": true,
  "cache": true,
  "max_rpm": 100,
  "share_crew": false
}
```

**Response** (201 Created)
```json
{
  "crew_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Research Crew",
  "description": "A crew for research and content creation",
  "agents": [...],
  "tasks": [...],
  "process": "sequential",
  "created_at": "2025-07-06T20:15:00Z",
  "updated_at": null,
  "status": "created"
}
```

#### Get Crew

Retrieve details of a specific crew.

```http
GET /crews/{crew_id}
X-API-Key: your-api-key
```

**Response** (200 OK)
```json
{
  "crew_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Research Crew",
  "description": "A crew for research and content creation",
  "agents": [...],
  "tasks": [...],
  "process": "sequential",
  "created_at": "2025-07-06T20:15:00Z",
  "updated_at": "2025-07-06T20:30:00Z",
  "status": "idle",
  "executions": 3,
  "last_execution": "2025-07-06T20:30:00Z"
}
```

#### List Crews

Get all crews for the authenticated user.

```http
GET /crews
X-API-Key: your-api-key
```

**Query Parameters**
- `limit` (optional): Number of results per page (default: 20, max: 100)
- `offset` (optional): Number of results to skip (default: 0)
- `status` (optional): Filter by status (created, idle, running, completed, failed)

**Response** (200 OK)
```json
{
  "crews": [
    {
      "crew_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Research Crew",
      "description": "A crew for research and content creation",
      "process": "sequential",
      "created_at": "2025-07-06T20:15:00Z",
      "status": "idle",
      "agents_count": 2,
      "tasks_count": 2
    }
  ],
  "total": 15,
  "limit": 20,
  "offset": 0
}
```

#### Update Crew

Update crew configuration.

```http
PATCH /crews/{crew_id}
Content-Type: application/json
X-API-Key: your-api-key
```

**Request Body** (partial update)
```json
{
  "name": "Updated Research Crew",
  "description": "Updated description",
  "verbose": false
}
```

**Response** (200 OK)
Returns updated crew object.

#### Delete Crew

Delete a crew and all associated data.

```http
DELETE /crews/{crew_id}
X-API-Key: your-api-key
```

**Response** (204 No Content)

### Crew Execution

#### Execute Crew

Start crew execution with inputs.

```http
POST /crews/{crew_id}/execute
Content-Type: application/json
X-API-Key: your-api-key
```

**Request Body**
```json
{
  "inputs": {
    "topic": "LangChain vs CrewAI performance",
    "style": "technical blog post"
  },
  "async_execution": false,
  "webhook_url": "https://your-webhook.com/callback",
  "metadata": {
    "client_id": "web-app-123",
    "user": "john@example.com"
  }
}
```

**Response** (200 OK for sync, 202 Accepted for async)
```json
{
  "execution_id": "660e8400-e29b-41d4-a716-446655440001",
  "crew_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",  // or "running" for async
  "result": {
    "raw": "Final output text...",
    "tasks_output": [
      {
        "task_id": "task-1",
        "description": "Research AI frameworks performance",
        "raw": "Research findings...",
        "agent": "Researcher",
        "status": "completed",
        "created_at": "2025-07-06T20:15:00Z",
        "completed_at": "2025-07-06T20:16:30Z"
      }
    ],
    "token_usage": {
      "total_tokens": 2543,
      "prompt_tokens": 1823,
      "completion_tokens": 720,
      "successful_requests": 5
    }
  },
  "started_at": "2025-07-06T20:15:00Z",
  "completed_at": "2025-07-06T20:17:45Z",
  "duration": 165.23
}
```

#### Get Execution Status

Check status of an async execution.

```http
GET /executions/{execution_id}
X-API-Key: your-api-key
```

**Response** (200 OK)
Same as execute response.

#### Get Crew Executions

List all executions for a crew.

```http
GET /crews/{crew_id}/executions
X-API-Key: your-api-key
```

**Query Parameters**
- `limit` (optional): Number of results (default: 20)
- `offset` (optional): Skip results (default: 0)
- `status` (optional): Filter by status

**Response** (200 OK)
```json
{
  "executions": [
    {
      "execution_id": "660e8400-e29b-41d4-a716-446655440001",
      "status": "completed",
      "started_at": "2025-07-06T20:15:00Z",
      "completed_at": "2025-07-06T20:17:45Z",
      "duration": 165.23,
      "token_usage": {
        "total_tokens": 2543
      }
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

### Tasks

#### Submit Task

Submit a single task to a crew.

```http
POST /crews/{crew_id}/tasks
Content-Type: application/json
X-API-Key: your-api-key
```

**Request Body**
```json
{
  "description": "Analyze market trends for AI tools",
  "expected_output": "Market analysis report",
  "agent_role": "Researcher",
  "priority": "high",
  "tools": ["search", "analyze"],
  "context": ["previous-task-id"],
  "async_execution": true
}
```

**Response** (202 Accepted)
```json
{
  "task_id": "770e8400-e29b-41d4-a716-446655440002",
  "crew_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "accepted",
  "created_at": "2025-07-06T20:15:00Z"
}
```

#### Get Task Status

```http
GET /tasks/{task_id}
X-API-Key: your-api-key
```

**Response** (200 OK)
```json
{
  "task_id": "770e8400-e29b-41d4-a716-446655440002",
  "crew_id": "550e8400-e29b-41d4-a716-446655440000",
  "description": "Analyze market trends for AI tools",
  "status": "completed",
  "result": {
    "raw": "Market analysis shows...",
    "agent": "Researcher",
    "output_json": null,
    "token_usage": {
      "total_tokens": 523
    }
  },
  "created_at": "2025-07-06T20:15:00Z",
  "started_at": "2025-07-06T20:15:05Z",
  "completed_at": "2025-07-06T20:16:30Z"
}
```

### WebSocket

Real-time updates for crew execution.

```
ws://api.litecrew.app/ws/crews/{crew_id}
```

**Authentication**: Include API key as query parameter
```
ws://api.litecrew.app/ws/crews/{crew_id}?api_key=your-api-key
```

**Message Types**

Subscribe to execution:
```json
{
  "action": "subscribe",
  "execution_id": "660e8400-e29b-41d4-a716-446655440001"
}
```

Execution updates:
```json
{
  "type": "execution_started",
  "execution_id": "660e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2025-07-06T20:15:00Z"
}
```

```json
{
  "type": "task_completed",
  "task_id": "task-1",
  "task_description": "Research AI frameworks",
  "result_preview": "Research findings show...",
  "timestamp": "2025-07-06T20:16:30Z"
}
```

```json
{
  "type": "execution_completed",
  "execution_id": "660e8400-e29b-41d4-a716-446655440001",
  "duration": 165.23,
  "token_usage": {
    "total_tokens": 2543
  },
  "timestamp": "2025-07-06T20:17:45Z"
}
```

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "INVALID_API_KEY",
    "message": "The provided API key is invalid",
    "details": {
      "provided_key_prefix": "prod-44c8..."
    }
  },
  "request_id": "req_1234567890"
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| INVALID_API_KEY | 403 | API key is invalid |
| MISSING_API_KEY | 401 | No API key provided |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| RESOURCE_NOT_FOUND | 404 | Crew/task/execution not found |
| INVALID_REQUEST | 400 | Request validation failed |
| CREW_BUSY | 409 | Crew is already executing |
| INTERNAL_ERROR | 500 | Server error |
| LLM_ERROR | 502 | LLM provider error |
| TIMEOUT | 504 | Execution timeout |

## SDKs and Examples

### Python SDK

```python
from litecrew import LiteCrewClient

# Initialize client
client = LiteCrewClient(
    api_key="your-api-key",
    base_url="https://api.litecrew.app"
)

# Create crew
crew = client.create_crew(
    name="My Crew",
    agents=[...],
    tasks=[...]
)

# Execute crew
result = client.execute_crew(
    crew_id=crew.id,
    inputs={"topic": "AI trends"}
)

print(result.raw)
```

### cURL Examples

```bash
# Create crew
curl -X POST https://api.litecrew.app/api/v1/crews \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d @crew.json

# Execute crew
curl -X POST https://api.litecrew.app/api/v1/crews/{crew_id}/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"inputs": {"topic": "AI trends"}}'

# Get execution result
curl https://api.litecrew.app/api/v1/executions/{execution_id} \
  -H "X-API-Key: your-api-key"
```

### JavaScript/TypeScript

```typescript
const response = await fetch('https://api.litecrew.app/api/v1/crews', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-api-key'
  },
  body: JSON.stringify({
    name: 'My Crew',
    agents: [...],
    tasks: [...]
  })
});

const crew = await response.json();
```

## Webhooks

Configure webhooks to receive execution updates:

```json
{
  "webhook_url": "https://your-app.com/webhook/litecrew",
  "events": ["execution.started", "execution.completed", "task.completed"]
}
```

Webhook payload:
```json
{
  "event": "execution.completed",
  "execution_id": "660e8400-e29b-41d4-a716-446655440001",
  "crew_id": "550e8400-e29b-41d4-a716-446655440000",
  "result": {...},
  "timestamp": "2025-07-06T20:17:45Z",
  "signature": "sha256=..."
}
```

Verify webhook signature:
```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

## Best Practices

1. **Rate Limiting**: Implement exponential backoff for 429 errors
2. **Async Execution**: Use async for long-running crews
3. **Webhooks**: Use webhooks instead of polling for status
4. **Error Handling**: Always handle LLM_ERROR and TIMEOUT
5. **Caching**: Cache crew configurations to reduce API calls
6. **Monitoring**: Use execution IDs for debugging and support

## Support

- **API Status**: https://status.litecrew.app
- **Documentation**: https://api.litecrew.app/docs
- **Issues**: https://gitlab.com/eof3/litecrewai/issues
- **Email**: api-support@litecrew.app