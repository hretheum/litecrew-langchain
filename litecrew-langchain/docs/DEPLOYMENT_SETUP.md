# LiteCrew Deployment Setup Guide

## GitLab CI/CD Variables Configuration

Aby pipeline deployment działał poprawnie, musisz skonfigurować następujące zmienne w GitLab:

### 1. Przejdź do Settings → CI/CD → Variables

### 2. Dodaj następujące zmienne:

#### Wymagane zmienne dla deployment:

1. **DROPLET_IP** (Required)
   - Type: Variable
   - Value: IP twojego droplet'a na Digital Ocean
   - Protected: Yes
   - Masked: Yes

2. **SSH_PRIVATE_KEY** (Required)
   - Type: Variable
   - Value: Klucz prywatny SSH do połączenia z droplet'em
   - Protected: Yes
   - Masked: No (klucze SSH nie mogą być maskowane)
   - Format: Cały klucz włącznie z `-----BEGIN OPENSSH PRIVATE KEY-----` i `-----END OPENSSH PRIVATE KEY-----`

3. **CI_REGISTRY** (Usually auto-set by GitLab)
   - Value: registry.gitlab.com

4. **CI_REGISTRY_USER** (Usually auto-set by GitLab)
   - Value: gitlab-ci-token

5. **CI_REGISTRY_PASSWORD** (Usually auto-set by GitLab)
   - Value: [Automatically provided by GitLab]

#### Zmienne dla aplikacji (używane w docker-compose):

6. **DB_PASSWORD** (Required)
   - Type: Variable
   - Value: Silne hasło dla PostgreSQL
   - Protected: Yes
   - Masked: Yes

7. **OPENAI_API_KEY** (Optional)
   - Type: Variable
   - Value: Twój klucz API OpenAI
   - Protected: Yes
   - Masked: Yes

8. **ANTHROPIC_API_KEY** (Optional)
   - Type: Variable
   - Value: Twój klucz API Anthropic
   - Protected: Yes
   - Masked: Yes

9. **GROQ_API_KEY** (Optional)
   - Type: Variable
   - Value: Twój klucz API Groq
   - Protected: Yes
   - Masked: Yes

10. **SECRET_KEY** (Required)
    - Type: Variable
    - Value: Losowy secret key dla aplikacji (min. 32 znaki)
    - Protected: Yes
    - Masked: Yes

11. **JWT_SECRET** (Required)
    - Type: Variable
    - Value: Losowy secret dla JWT (min. 32 znaki)
    - Protected: Yes
    - Masked: Yes

## Przygotowanie Droplet'a

### 1. Utwórz użytkownika dla deployment:
```bash
# Na droplet jako root:
adduser litecrewai
usermod -aG docker litecrewai
su - litecrewai
```

### 2. Skonfiguruj SSH na porcie 2222:
```bash
# Edytuj /etc/ssh/sshd_config
sudo nano /etc/ssh/sshd_config

# Dodaj lub zmień:
Port 2222

# Restart SSH
sudo systemctl restart sshd
```

### 3. Dodaj klucz publiczny:
```bash
# Jako litecrewai user:
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "YOUR_PUBLIC_KEY" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 4. Zainstaluj Docker i Docker Compose:
```bash
# Instrukcje dla Ubuntu/Debian:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker litecrewai

# Docker Compose
sudo apt-get install docker-compose-plugin
```

### 5. Przygotuj katalogi:
```bash
sudo mkdir -p /opt/litecrewai/litecrew-langchain
sudo chown -R litecrewai:litecrewai /opt/litecrewai
```

### 6. Skonfiguruj firewall:
```bash
# Otwórz porty
sudo ufw allow 2222/tcp  # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # API (opcjonalnie)
```

## Testowanie połączenia

Z lokalnej maszyny:
```bash
ssh -p 2222 litecrewai@YOUR_DROPLET_IP
```

## Troubleshooting

### Problem: ssh-keyscan fails
1. Sprawdź czy DROPLET_IP jest ustawione w GitLab CI/CD Variables
2. Sprawdź czy SSH nasłuchuje na porcie 2222
3. Sprawdź firewall na droplet

### Problem: Docker login fails
1. Sprawdź czy użytkownik litecrewai jest w grupie docker
2. Sprawdź czy CI_REGISTRY_PASSWORD jest poprawnie przekazywane

### Problem: Permission denied
1. Sprawdź uprawnienia do katalogu /opt/litecrewai
2. Sprawdź czy klucz SSH jest poprawny

## Pierwsze uruchomienie

Po skonfigurowaniu wszystkich zmiennych:
1. Push do branch'a `master` lub `develop`
2. W GitLab przejdź do CI/CD → Pipelines
3. Dla deployment do produkcji - kliknij manual job "deploy"
4. Monitoruj logi dla błędów