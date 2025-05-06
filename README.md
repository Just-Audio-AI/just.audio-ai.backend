
# Production Deployment Guide

This guide describes how to deploy the full-stack application (frontend + backend + workers) to a VPS using Docker Compose and Docker Hub images.

## 📦 Requirements

- VPS with Docker & Docker Compose (preferably NOT via Snap)
- Docker Hub account with pushed images:
  - `saidmagomedov/frontend-app:latest`
  - `saidmagomedov/backend-app:latest`
  - `saidmagomedov/backend-worker:latest`
- Open ports `80` (for frontend) and optionally `443` (for HTTPS)

---

## 📁 Files needed on the VPS

Only copy the following files to your VPS:
- `docker-compose.prod.yml`
- `.env.prod` (never commit this to Git!)

Structure example:

```
/home/app/
├── docker-compose.prod.yml
└── .env.prod
```

---

## 🔐 .env.prod format

Example content:

```env
DATABASE_URL=postgres://postgres:password@db:5432/app_db
REDIS_URL=redis://redis:6379/0
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Optional AI keys
WISPER_AI_BASE_URL=https://api.lemonfox.ai/v1/audio/transcriptions
WISPER_AI_AUTH_TOKEN=
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4.1-nano
BASE_URL="your-ip:8000"
```

---

## 🚀 Deployment Steps

### 1. Connect to your VPS

```bash
ssh root@your-vps-ip
```

### 2. Move into app directory

```bash
mkdir -p /home/app
cd /home/app
```

### 3. Create `.env.prod` file (if not already copied)

```bash
nano .env.prod
# Paste your variables
```

### 4. Pull images

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml pull
```

> 🛑 If you see `permission denied` for .env — it's likely caused by Docker installed via Snap.  
> 💡 Either avoid using `--env-file`, or reinstall Docker via APT for proper `.env` support.

### 5. Start services

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
```

---

## ⚙️ Architecture Overview

- `frontend` (nginx) — serves static files + proxies `/api` to backend
- `app` — FastAPI with 2 replicas
- `worker` — Celery workers with 2 replicas
- `db`, `redis`, `minio` — internal only, not exposed to host
- All services communicate via internal Docker network `appnet`

---

## 🧪 Debugging

- View logs:  
  ```bash
  docker compose logs -f
  ```

- Restart specific service:  
  ```bash
  docker compose restart app
  ```

- Access database shell (optional):  
  ```bash
  docker exec -it postgres psql -U postgres -d app_db
  ```

---

## 🔐 (Optional) Enable HTTPS

Install Certbot on VPS (host-level) and configure reverse proxy or SSL termination if needed:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

Then add to crontab for renewal:
```bash
0 0 * * * certbot renew --quiet
```

---

## 🧼 Cleanup

- Stop all containers:
  ```bash
  docker compose down
  ```

- Remove unused images:
  ```bash
  docker image prune -af
  ```

---

## 📝 Notes

- If you're using Apple Silicon (Mac M1/M2), build images for `linux/amd64`:
  ```bash
  docker buildx build --platform linux/amd64 ... --push
  ```

- Do **not expose** internal ports (5432, 6379, etc.) unless necessary — rely on internal networking.

---

## ✅ Done

Your full-stack app is now live and running in production. 🎉
