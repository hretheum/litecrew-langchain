# LiteCrewAI - Instrukcja Deployment

## 🔐 Konfiguracja GitLab CI/CD

### 1. Dodaj Deploy Key do GitLab

Przejdź do: Settings → Repository → Deploy Keys

**Nazwa**: LiteCrewAI Deployment
**Key**:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAy00Tas3vadpFrxeQcVe231fk/V5FrScrhjYgjZMa9v litecrewai@deployment
```
**Grant write permissions**: ✅ (dla auto-tagging)

### 2. Skonfiguruj CI/CD Variables

Przejdź do: Settings → CI/CD → Variables

Dodaj następujące zmienne:

| Variable | Value | Protected | Masked |
|----------|-------|-----------|---------|
| `DROPLET_IP` | `46.101.181.183` | ✅ | ❌ |
| `SSH_PRIVATE_KEY` | (zawartość ~/.ssh/deploy_key z droplet) | ✅ | ✅ |
| `BACKUP_ENCRYPTION_KEY` | (wygeneruj silne hasło) | ✅ | ✅ |

### 3. Pobierz klucz prywatny

Na lokalnej maszynie:
```bash
ssh -i ~/.ssh/id_rag litecrewai@46.101.181.183 "cat ~/.ssh/deploy_key"
```

Skopiuj całą zawartość (włącznie z BEGIN/END) do zmiennej `SSH_PRIVATE_KEY`.

### 4. Skonfiguruj Container Registry

Przejdź do: Settings → General → Visibility, project features → Container Registry

Włącz Container Registry: ✅

### 5. Schedule dla backupów

Przejdź do: CI/CD → Schedules → New Schedule

- **Description**: Daily Backup
- **Interval Pattern**: `0 3 * * *` (3:00 AM)
- **Target Branch**: main/master
- **Variables**: Możesz dodać dodatkowe

## 🚀 Deployment

### Automatyczny deployment:
1. Push do `main` lub `master`
2. Testy i build wykonają się automatycznie
3. Kliknij "Deploy" w pipeline dla manual deployment

### Ręczny deployment z CLI:
```bash
# Na lokalnej maszynie
git push origin main

# Na droplet
cd /opt/litecrewai
git pull
docker compose up -d --build
```

### Rollback:
W GitLab pipeline kliknij "Rollback" lub ręcznie:
```bash
cd /opt/litecrewai
docker compose down
tar -xzf backups/backup-YYYYMMDD-HHMMSS.tar.gz -C .
docker compose up -d
```

## 📊 Monitoring

### Deploy systemu monitorowania:
```bash
# Wykonaj lokalnie aby wdrożyć monitoring na droplet
./scripts/deploy_monitoring.sh
```

### Sprawdzenie statusu:
```bash
docker compose ps
docker compose logs -f litecrewai
curl http://localhost:8000/health
```

### Dashboard i metryki:
- Dashboard: http://46.101.181.183:8000/dashboard
- Health check: http://46.101.181.183:8000/health/detailed
- Prometheus metrics: http://46.101.181.183:8000/metrics

### Logi i raporty:
```bash
# Dashboard raport (generowany co godzinę)
ssh -i ~/.ssh/id_rag root@46.101.181.183 'cat /opt/litecrewai/logs/dashboard_report.txt'

# Sprawdź logi aplikacji
ssh -i ~/.ssh/id_rag root@46.101.181.183 'tail -f /opt/litecrewai/logs/app.log'

# Sprawdź błędy
ssh -i ~/.ssh/id_rag root@46.101.181.183 'tail -f /opt/litecrewai/logs/error.log'
```

### Walidacja systemów:
```bash
# Walidacja logowania
ssh -i ~/.ssh/id_rag root@46.101.181.183 '/opt/litecrewai/venv/bin/python /opt/litecrewai/masterplan/src/faza-0/validate_logging.py'

# Walidacja monitoringu
ssh -i ~/.ssh/id_rag root@46.101.181.183 '/opt/litecrewai/venv/bin/python /opt/litecrewai/masterplan/src/faza-0/validate_monitoring.py'
```

### Agregacja metryk:
```bash
# Status timera agregacji
ssh -i ~/.ssh/id_rag root@46.101.181.183 'sudo systemctl status litecrewai-metrics-aggregation.timer'

# Ręczna agregacja
ssh -i ~/.ssh/id_rag root@46.101.181.183 '/opt/litecrewai/venv/bin/python /opt/litecrewai/scripts/aggregate_metrics.py'
```

## 🔧 Troubleshooting

### Container nie startuje:
```bash
docker compose logs litecrewai
docker compose run --rm litecrewai bash
```

### Brak połączenia z Redis/Ollama:
```bash
# Test z kontenera
docker compose exec litecrewai curl http://host.docker.internal:11434
docker compose exec litecrewai redis-cli -h host.docker.internal ping
```

### Problemy z uprawnieniami:
```bash
sudo chown -R litecrewai:litecrewai /opt/litecrewai
chmod -R 755 /opt/litecrewai
```