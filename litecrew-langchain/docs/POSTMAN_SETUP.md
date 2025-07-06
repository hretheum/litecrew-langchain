# Postman Configuration for LiteCrew API

## 1. API Key Authentication Setup

### Option A: Using Headers (Recommended)

1. **In Postman Collection/Request:**
   - Go to the "Headers" tab
   - Add a new header:
     - Key: `X-API-Key`
     - Value: `your-api-key-here`

2. **Using Postman Environment Variables (Best Practice):**
   - Create a new Environment in Postman
   - Add a variable:
     - Variable name: `api_key`
     - Initial value: `your-actual-api-key`
     - Current value: `your-actual-api-key`
   - In Headers, use: `{{api_key}}` as the value

### Option B: Using Authorization Tab

1. Go to the "Authorization" tab
2. Select "API Key" from the Type dropdown
3. Configure:
   - Key: `X-API-Key`
   - Value: `your-api-key-here`
   - Add to: `Header`

## 2. Postman Cloud Agent Configuration

Since you're using Postman Cloud Agent, ensure:

1. **For Local Development:**
   - API URL: `http://localhost:8000/api/v1/`
   - Cloud Agent must be running on the same machine

2. **For Production:**
   - API URL: `http://152.42.139.18/api/v1/`
   - No special Cloud Agent configuration needed

## 3. Complete Request Example

```json
// GET http://localhost:8000/api/v1/crews
// Headers:
{
  "X-API-Key": "test-key-123",
  "Content-Type": "application/json"
}
```

## 4. Testing Your Configuration

1. **Health Check (No Auth Required):**
   ```
   GET /api/v1/health
   ```
   Should return 200 OK without API key

2. **List Crews (Auth Required):**
   ```
   GET /api/v1/crews
   ```
   - Without API key: 401 Unauthorized
   - With valid API key: 200 OK

3. **Create Crew (Auth Required):**
   ```
   POST /api/v1/crews
   Content-Type: application/json
   X-API-Key: your-api-key

   {
     "name": "Test Crew",
     "description": "Test crew from Postman",
     "agents": [...],
     "tasks": [...]
   }
   ```

## 5. Postman Collection Setup

Create a collection with these pre-request scripts:

```javascript
// Collection-level Pre-request Script
pm.request.headers.add({
    key: 'X-API-Key',
    value: pm.environment.get('api_key')
});
```

## 6. Environment Variables

Create an environment with:
- `base_url`: `http://localhost:8000` (or production URL)
- `api_key`: `your-api-key-here`

Then use `{{base_url}}/api/v1/crews` in your requests.

## 7. Troubleshooting

### Common Issues:

1. **401 Unauthorized**
   - Check if API key is correctly set in headers
   - Verify the header name is exactly `X-API-Key` (case-sensitive)

2. **403 Forbidden**
   - API key is present but invalid
   - Check if the key matches one in `LITECREW_API_KEYS` environment variable

3. **Rate Limiting (429 Too Many Requests)**
   - You've exceeded 60 requests/minute (unauthenticated)
   - With valid API key: limit is 600 requests/minute

### Debug Headers

Enable Postman Console (View → Show Postman Console) to see actual headers being sent.

## 8. Example API Keys for Testing

For local development with our test environment:
- `test-key-123`
- `dev-key-456`

**Note:** Never commit real API keys to version control!