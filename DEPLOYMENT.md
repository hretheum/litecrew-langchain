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

### Sprawdzenie statusu:
```bash
docker compose ps
docker compose logs -f litecrewai
curl http://localhost:8000/health
```

### Metryki:
- Prometheus: http://DROPLET_IP:9090
- Application metrics: http://DROPLET_IP:8000/metrics

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