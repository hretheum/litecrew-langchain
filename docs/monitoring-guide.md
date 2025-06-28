# LiteCrewAI Monitoring & Logging Guide

## 📊 Przegląd

System monitorowania LiteCrewAI składa się z:
- **Structured Logging**: JSON logi z correlation IDs
- **Metrics Storage**: SQLite z agregacją czasową
- **Real-time Dashboard**: FastAPI + htmx (bez JavaScript)
- **Alert System**: Konfigurowalne reguły alertów
- **Cost Tracking**: Śledzenie kosztów LLM

## 🚀 Deployment na DigitalOcean

### Automatyczny deploy
```bash
# Z lokalnej maszyny
cd /Users/hretheum/dev/bezrobocie/crewAI
./scripts/deploy_monitoring.sh
```

### Ręczna instalacja
```bash
# SSH do droplet
ssh -i ~/.ssh/id_rag root@46.101.181.183

# Instalacja logrotate
/opt/litecrewai/scripts/setup_logrotate.sh

# Instalacja metrics aggregation
/opt/litecrewai/scripts/setup_metrics_aggregation.sh

# Weryfikacja
/opt/litecrewai/masterplan/src/faza-0/validate_logging.py
/opt/litecrewai/masterplan/src/faza-0/validate_monitoring.py
```

## 📁 Struktura logów

Wszystkie logi znajdują się w `/opt/litecrewai/logs/`:

```
/opt/litecrewai/logs/
├── app.log          # Główny log aplikacji
├── api.log          # Requesty API
├── llm.log          # Wywołania LLM
├── error.log        # Tylko błędy (ERROR, CRITICAL)
├── dashboard_report.txt  # Raport godzinowy
└── validation_*.txt      # Wyniki walidacji
```

### Format logów (JSON)
```json
{
  "timestamp": "2024-01-20T15:30:45.123456",
  "level": "INFO",
  "logger": "app.main",
  "message": "Request processed",
  "module": "main",
  "function": "handle_request",
  "line": 123,
  "request_id": "req-123-456",
  "correlation_id": "corr-789",
  "extra_fields": {
    "user_id": "user-001",
    "duration_seconds": 0.123
  }
}
```

## 📈 Dashboard

### Dostęp
- URL: http://46.101.181.183:8000/dashboard
- Auto-refresh: co 5 sekund
- Brak JavaScript - działa wszędzie

### Widgety
1. **System Health**: CPU, RAM, Disk, Uptime
2. **Request Metrics**: RPS, latencja, trendy
3. **LLM Usage**: Tokeny, API calls, modele
4. **Cost Tracking**: Koszty bieżące i prognozy
5. **Active Alerts**: Aktywne alarmy
6. **Recent Errors**: Ostatnie błędy

### Generowanie raportów
```bash
# Raport lokalny
python scripts/log_dashboard.py --hours 24

# Raport na droplet
ssh -i ~/.ssh/id_rag root@46.101.181.183 \
  '/opt/litecrewai/venv/bin/python /opt/litecrewai/scripts/log_dashboard.py'
```

## 🚨 System alertów

### Domyślne reguły
- **high_cpu_usage**: CPU > 80% przez 5 minut
- **high_memory_usage**: RAM > 85% przez 5 minut
- **disk_space_critical**: Dysk > 90%
- **high_error_rate**: Error rate > 5% przez 2 minuty
- **slow_response_time**: Avg response > 2s przez 3 minuty
- **high_llm_costs**: Koszty > $1/godzinę

### Konfiguracja alertów (.env)
```bash
# Email alerts
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@example.com
SMTP_PASS=app-password
ALERT_EMAIL=admin@example.com

# Webhook alerts (Discord/Slack)
ALERT_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### Sprawdzanie alertów
```bash
# Ręczne sprawdzenie
python scripts/check_critical_errors.py

# Status alertów
curl http://46.101.181.183:8000/dashboard/alerts
```

## 📊 Metryki

### Prometheus endpoint
```bash
curl http://46.101.181.183:8000/metrics
```

### SQLite metrics database
```bash
# Lokalizacja
/opt/litecrewai/data/metrics.db

# Tabele
- metrics          # Surowe metryki
- metrics_1min     # Agregacja 1-minutowa
- metrics_5min     # Agregacja 5-minutowa  
- metrics_1hour    # Agregacja godzinowa
- alerts           # Historia alertów
```

### Agregacja metryk
```bash
# Status timera
sudo systemctl status litecrewai-metrics-aggregation.timer

# Ręczna agregacja
python scripts/aggregate_metrics.py
```

## 🔍 Troubleshooting

### Brak logów
```bash
# Sprawdź uprawnienia
ls -la /opt/litecrewai/logs/
sudo chown -R litecrewai:litecrewai /opt/litecrewai/logs/

# Sprawdź czy aplikacja działa
docker compose ps
docker compose logs litecrewai
```

### Dashboard nie działa
```bash
# Sprawdź czy app działa
curl http://localhost:8000/health

# Sprawdź logi
tail -f /opt/litecrewai/logs/error.log

# Restart aplikacji
docker compose restart litecrewai
```

### Metryki nie są zbierane
```bash
# Sprawdź bazę
ls -la /opt/litecrewai/data/metrics.db

# Test zapisu
python -c "from app.core.metrics_storage import MetricsStorage; s = MetricsStorage(); s.record_metric('test', 42)"

# Sprawdź timer
systemctl list-timers | grep litecrewai
```

### Alerty nie działają
```bash
# Test ręczny
python scripts/check_critical_errors.py

# Sprawdź konfigurację
grep ALERT /opt/litecrewai/.env

# Sprawdź logi
grep "alert" /opt/litecrewai/logs/app.log
```

## 🛠️ Maintenance

### Rotacja logów
- Automatyczna: codziennie o północy
- Kompresja: po 1 dniu
- Retencja: 30 dni dla zwykłych, 90 dni dla error.log

### Czyszczenie metryk
- Automatyczne: co 24h
- Raw metrics: 7 dni
- Agregowane: 28 dni
- Alerty: 30 dni (tylko rozwiązane)

### Backup
```bash
# Backup logów i metryk
tar -czf monitoring-backup-$(date +%Y%m%d).tar.gz \
  /opt/litecrewai/logs/ \
  /opt/litecrewai/data/metrics.db
```

## 📝 Użycie w kodzie

### Logger wrapper
```python
from app.core.logger_wrapper import LiteCrewAILogger

logger = LiteCrewAILogger("my_module")

# API request
logger.log_api_request(
    method="POST",
    path="/api/agents",
    status_code=201,
    duration=0.123,
    user_id="user-123"
)

# LLM call
logger.log_llm_call(
    provider="openai",
    model="gpt-3.5-turbo",
    prompt_tokens=150,
    completion_tokens=75,
    duration=1.234,
    cost=0.0045
)

# Performance tracking
with logger.performance("database_query"):
    # kod do zmierzenia
    pass

# Error logging
try:
    risky_operation()
except Exception as e:
    logger.log_error("Operation failed", exception=e)
```

### Metrics tracking
```python
from app.core.metrics import metrics_collector

# Track custom metric
metrics_collector.storage.record_metric(
    "custom.metric.name",
    42.0,
    {"label1": "value1"}
)
```