# Quick Start Deployment Guide

## Prerequisites Checklist

- [ ] Google Cloud VPS instance running Ubuntu 20.04+
- [ ] Public IP address from Google Cloud
- [ ] Docker and Docker Compose installed
- [ ] Firewall configured (ports 80, 443, 22)

## 5-Minute Setup

### 1. On Your VPS Server

```bash
# Clone repository
cd /opt
git clone <your-repo-url> accreditrack
cd accreditrack/infra
```

### 2. Configure Environment

```bash
# Backend
cd ../backend
cp .env.production.example .env.production
nano .env.production
# Update: SECRET_KEY, ALLOWED_HOSTS (add your Google Cloud IP), DB_PASSWORD

# Frontend
cd ../frontend
cp .env.production.example .env.production
nano .env.production
# Update: NEXT_PUBLIC_API_BASE_URL (use your Google Cloud IP)
```

### 3. Update Nginx Config

```bash
cd ../infra/nginx/conf.d
nano accreditrack.conf
# Replace server_name _; with your Google Cloud IP
```

### 4. Deploy

```bash
cd /opt/accreditrack/infra
./deploy.sh
```

### 5. Access Your App

Open browser: `http://your-google-cloud-ip`

## Important Notes

- Replace `your-google-cloud-ip` with your actual Google Cloud public IP
- For HTTPS, see full README.md for SSL certificate setup
- Default database credentials are in `.env.production` - change them!

## Common Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Update application
./update.sh

# Backup database
./backup.sh
```
