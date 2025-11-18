# Tunnel System

## Клиент: установка и запуск

### Установка (рекомендуется)

Самый простой способ — установка из PyPI:

```bash
pip install tunnel-client
```

После каждого изменения в `client/` пакет автоматически публикуется в PyPI.

### Запуск клиента

```bash
tunnel-client --port <port>
```

Пример:
```bash
tunnel-client --port 3000
```

Сервер по умолчанию: `wss://tunnel.tunneloon.online` (можно переопределить через `--server`)

### Альтернативные способы установки

**Из исходников (для разработки):**
```bash
pip install .
# или в editable-режиме
pip install -e .
```

**Из артефакта (wheel):**
1. После пуша в `main/master` с изменениями в `client/` скачайте wheel из артефактов job `build_client`
2. Установите:
   ```bash
   pip install dist/tunnel_client-*.whl
   ```

## Сервер: деплой в Docker

### Автоматический деплой

При каждом изменении в `server_/` или `shared/`:
1. Автоматически собирается Docker образ
2. Образ пушится в GitLab Container Registry
3. Автоматически деплоится на сервер (перезапускается контейнер)

**Требуется настройка:**
- GitLab CI/CD Variables: `SSH_PRIVATE_KEY`, `SSH_USER`, `SERVER_HOST`
- На сервере должны быть созданы директории: `/opt/tunnel-server/{config.yaml,data,certs}`

### Ручной запуск контейнера
```bash
docker run -d \
  --name tunnel-server \
  --restart unless-stopped \
  --network host \
  -v /opt/tunnel-server/config.yaml:/app/config.yaml:ro \
  -v /opt/tunnel-server/certs:/app/certs:ro \
  -v /opt/tunnel-server/data:/app/data \
  -e SERVER_CONFIG=/app/config.yaml \
  registry.gitlab.com/YOUR_PROJECT/server:latest
```

## CI/CD (GitLab)

### Автоматические процессы:

**При изменении `server_/` или `shared/`:**
- `build_server_image` — сборка Docker образа
- `deploy_server_docker` — автоматический деплой на сервер

**При изменении `client/`, `shared/`, `setup.py` или `MANIFEST.in`:**
- `build_client` — автоматическое обновление версии (формат: YY.MM.DD.patch) → сборка wheel + sdist (артефакты)
- `publish_client_pypi` — автоматическая публикация в PyPI

**Версионирование:**
- Версия автоматически обновляется в CI при изменениях клиента
- Формат: `YY.MM.DD.patch` (например, `24.11.14.1`)
- При изменениях в тот же день увеличивается patch номер
- При изменениях в новый день patch сбрасывается до 1

### Переменные для деплоя сервера
Задайте в GitLab → Settings → CI/CD → Variables:
- `SSH_PRIVATE_KEY` — приватный ключ для SSH
- `SSH_USER` — пользователь на сервере
- `SERVER_HOST` — адрес сервера
- (опц.) `SERVER_CONFIG_REMOTE`, `SERVER_CERTS_REMOTE`, `SERVER_DATA_REMOTE`, `SERVER_CONTAINER_NAME`, `SERVER_PORT_HTTP`, `SSH_PORT`

### Переменные для публикации в PyPI
Задайте в GitLab → Settings → CI/CD → Variables:
- `PYPI_USERNAME` — должно быть `__token__` (буквально так)
- `PYPI_PASSWORD` — ваш PyPI API token (создайте на https://pypi.org/manage/account/token/)

## Разработка
```bash
make install-dev       # инструменты разработки (ruff, black, mypy, build)
make pre-commit-install
make lint              # ruff
make fmt               # black
make build-client      # сборка пакета клиента
```
