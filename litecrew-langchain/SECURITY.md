# 🔒 LiteCrewAI Security Guidelines

## 🚨 Krytyczne zasady bezpieczeństwa

### 1. Zarządzanie sekretami

#### ❌ NIGDY nie rób tego:
```python
# ŹLEE - hardcoded credentials
API_KEY = "sk-EXAMPLE_DO_NOT_USE_THIS_KEY"
DATABASE_URL = "postgresql://user:password@localhost/db"
SECRET_KEY = "my-secret-key"

# ŹLEE - defaults w kodzie
username = os.getenv("USERNAME", "admin")  # NIE!
password = os.getenv("PASSWORD", "changeme")  # NIE!
```

#### ✅ ZAWSZE rób tak:
```python
# DOBRZE - wymuszaj zmienne środowiskowe
API_KEY = os.environ["OPENAI_API_KEY"]  # Crashuje jeśli brak
DATABASE_URL = os.environ["DATABASE_URL"]

# DOBRZE - lub sprawdzaj i informuj
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
```

### 2. Plik .env

#### Struktura .env (NIGDY nie commituj!):
```bash
# .env
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...

# Database
DATABASE_URL=sqlite:///opt/litecrewai/data/litecrewai.db
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=use-a-long-random-string-here
JWT_SECRET=another-long-random-string
METRICS_USERNAME=custom_admin_name
METRICS_PASSWORD=very_secure_password_here

# Monitoring
SENTRY_DSN=https://...@sentry.io/...
```

#### .env.example (TO commituj):
```bash
# .env.example
# API Keys
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GROQ_API_KEY=your-groq-api-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/litecrewai
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=generate-secure-random-string
JWT_SECRET=generate-another-secure-string
METRICS_USERNAME=change-this-username
METRICS_PASSWORD=use-strong-password

# Monitoring
SENTRY_DSN=optional-sentry-dsn
```

### 3. Walidacja wejścia

#### Dla zmiennych środowiskowych:
```python
import re
import ipaddress

def validate_ip(ip_string):
    """Validate IP address format"""
    try:
        ipaddress.ip_address(ip_string)
        return True
    except ValueError:
        return False

def validate_api_key(key):
    """Validate API key format"""
    # OpenAI format
    if key.startswith("sk-") and len(key) > 20:
        return True
    # Anthropic format
    if key.startswith("sk-ant-") and len(key) > 20:
        return True
    return False

# Użycie
DROPLET_IP = os.environ.get("DROPLET_IP")
if not validate_ip(DROPLET_IP):
    raise ValueError(f"Invalid IP address: {DROPLET_IP}")
```

#### Dla danych użytkownika:
```python
from pydantic import BaseModel, validator
import bleach

class UserInput(BaseModel):
    name: str
    description: str
    
    @validator('name')
    def validate_name(cls, v):
        # Tylko litery, cyfry, myślniki
        if not re.match(r'^[a-zA-Z0-9-_]+$', v):
            raise ValueError('Invalid name format')
        return v
    
    @validator('description')
    def sanitize_description(cls, v):
        # Usuń potencjalnie niebezpieczne HTML
        return bleach.clean(v, tags=[], strip=True)
```

### 4. Autentykacja i autoryzacja

#### WebSocket z autentykacją:
```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    # Weryfikuj token PRZED akceptacją połączenia
    user = await verify_jwt_token(token)
    if not user:
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    await websocket.accept()
    # ... reszta logiki
```

#### API z kluczami:
```python
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    # Sprawdź w bazie/cache
    if not await is_valid_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return api_key
```

### 5. Bezpieczne połączenia z bazą danych

```python
# Używaj SSL/TLS dla produkcji
DATABASE_URL = "postgresql://user:pass@host:5432/db?sslmode=require"

# Connection pooling z timeoutami
from sqlalchemy.pool import NullPool

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Lub QueuePool z limitem
    connect_args={
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000"  # 30s timeout
    }
)
```

### 6. Rate limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/agents")
@limiter.limit("10 per minute")  # Stricter dla resource-intensive
async def create_agent():
    pass
```

### 7. Security headers

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# CORS - tylko trusted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.litecrewai.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["litecrewai.com", "*.litecrewai.com"]
)

# Security headers
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### 8. Logging bez sekretów

```python
import logging
from typing import Any

class SecureFormatter(logging.Formatter):
    """Formatter that removes secrets from logs"""
    
    SENSITIVE_KEYS = {
        'password', 'secret', 'token', 'api_key', 
        'authorization', 'cookie', 'session'
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # Redact sensitive data
        if hasattr(record, 'args'):
            record.args = self._redact_dict(record.args)
        return super().format(record)
    
    def _redact_dict(self, obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                k: '***REDACTED***' if k.lower() in self.SENSITIVE_KEYS else self._redact_dict(v)
                for k, v in obj.items()
            }
        return obj
```

### 9. Bezpieczne generowanie tokenów

```python
import secrets
import string

def generate_secure_token(length=32):
    """Generate cryptographically secure random token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_api_key():
    """Generate API key with prefix"""
    prefix = "lc_"  # LiteCrewAI prefix
    token = generate_secure_token(40)
    return f"{prefix}{token}"
```

### 10. Dockerowe best practices

```dockerfile
# Dockerfile
# Nie używaj root
RUN useradd -m -u 1000 litecrewai
USER litecrewai

# Nie expose'uj niepotrzebnych portów
EXPOSE 8000

# Używaj secrets podczas buildu
# docker build --secret id=api_key,src=.env ...
RUN --mount=type=secret,id=api_key \
    API_KEY=$(cat /run/secrets/api_key) && \
    # użyj klucza tylko podczas buildu
```

## 🔍 Checklist bezpieczeństwa

Przed każdym deploymentem sprawdź:

- [ ] Brak hardcoded secrets w kodzie
- [ ] Wszystkie API endpoints wymagają autentykacji
- [ ] Rate limiting jest włączony
- [ ] Logi nie zawierają wrażliwych danych
- [ ] .env jest w .gitignore
- [ ] Wszystkie dependencies są aktualne
- [ ] Security headers są ustawione
- [ ] HTTPS/TLS jest wymuszony
- [ ] Backup bazy danych jest szyfrowany
- [ ] Monitoring wykrywa nietypową aktywność

## 🚨 Incident response

W przypadku wycieku klucza API:
1. Natychmiast revoke stary klucz
2. Wygeneruj nowy klucz
3. Zaktualizuj wszystkie instancje
4. Sprawdź logi w poszukiwaniu nadużyć
5. Powiadom affected users jeśli potrzeba

## 📞 Kontakt bezpieczeństwa

Security issues: security@litecrewai.com (lub utwórz dedykowany email)

---

**Pamiętaj**: Bezpieczeństwo to proces, nie produkt. Regularnie przeglądaj i aktualizuj te zasady.