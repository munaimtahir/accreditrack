# VPS Deployment Guide

This guide will help you deploy the AccrediTrack application on a VPS with multi-app support using Google Cloud public IP.

## Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Docker and Docker Compose installed
- Google Cloud VPS instance with public IP
- Domain name (optional, but recommended for SSL)

## Initial Server Setup

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and log back in for group changes to take effect
```

### 3. Configure Firewall

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp  # SSH
sudo ufw enable
```

## Deployment Steps

### 1. Clone Repository

```bash
cd /opt  # or your preferred directory
git clone <your-repository-url> accreditrack
cd accreditrack
```

### 2. Configure Environment Variables

#### Backend Configuration

```bash
cd backend
cp .env.production.example .env.production
nano .env.production
```

Update the following values:
- `SECRET_KEY`: Generate a secure secret key (use `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `ALLOWED_HOSTS`: Add your Google Cloud public IP (e.g., `34.123.45.67`)
- `DB_PASSWORD`: Set a strong database password
- `CORS_ALLOWED_ORIGINS`: Add your public IP with https (e.g., `https://34.123.45.67`)

#### Frontend Configuration

```bash
cd ../frontend
cp .env.production.example .env.production
nano .env.production
```

Update:
- `NEXT_PUBLIC_API_URL`: Set to `https://your-google-cloud-ip/api/v1` or your domain

### 3. Update Nginx Configuration

Edit `infra/nginx/conf.d/accreditrack.conf`:

```bash
cd ../infra/nginx/conf.d
nano accreditrack.conf
```

Replace `server_name _;` with your Google Cloud public IP or domain:
```nginx
server_name 34.123.45.67;  # Your Google Cloud IP
# OR
server_name yourdomain.com www.yourdomain.com;  # If using domain
```

### 4. Deploy Application

```bash
cd /opt/accreditrack/infra
chmod +x deploy.sh
./deploy.sh
```

Or manually:

```bash
docker-compose build
docker-compose up -d db
sleep 10
docker-compose run --rm backend python config/manage.py migrate
docker-compose run --rm backend python config/manage.py collectstatic --noinput
docker-compose up -d
```

### 5. Verify Deployment

```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs -f

# Test backend
curl http://your-google-cloud-ip/api/v1/

# Test frontend
curl http://your-google-cloud-ip/
```

## SSL Certificate Setup (Recommended)

### Using Let's Encrypt with Certbot

1. Install Certbot:

```bash
sudo apt install certbot python3-certbot-nginx
```

2. Update nginx config to temporarily allow HTTP for validation:

Edit `infra/nginx/conf.d/accreditrack.conf` and comment out the HTTPS redirect temporarily.

3. Obtain certificate:

```bash
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

4. Update nginx config with SSL paths:

```nginx
ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
```

5. Mount certificates in docker-compose.yml:

Add to nginx service volumes:
```yaml
- /etc/letsencrypt:/etc/letsencrypt:ro
```

6. Restart nginx:

```bash
docker-compose restart nginx
```

## Multi-App Deployment

This setup supports multiple applications on the same VPS. To add another app:

1. Create a new nginx config in `infra/nginx/conf.d/` for your new app
2. Add new services to `docker-compose.yml`
3. Use different ports internally and route via nginx based on domain/path

Example for second app:
```nginx
server {
    listen 443 ssl http2;
    server_name app2.yourdomain.com;
    # ... rest of config
}
```

## Maintenance Commands

### View Logs
```bash
docker-compose logs -f [service-name]
```

### Restart Services
```bash
docker-compose restart [service-name]
```

### Update Application
```bash
git pull
docker-compose build
docker-compose up -d
docker-compose run --rm backend python config/manage.py migrate
docker-compose run --rm backend python config/manage.py collectstatic --noinput
```

### Backup Database
```bash
mkdir -p backups
docker-compose exec db pg_dump -U accreditrack accreditrack | gzip > backups/backup_$(date +%Y%m%d).sql.gz
```

### Restore Database
```bash
# Decompress the backup first
gunzip backup_20240101_120000.sql.gz
# Then restore
docker-compose exec -T db psql -U accreditrack accreditrack < backup_20240101_120000.sql
```

### Stop Services
```bash
docker-compose down
```

### Stop and Remove Volumes (⚠️ Deletes Data)
```bash
docker-compose down -v
```

## Troubleshooting

### Services won't start
```bash
docker-compose logs [service-name]
docker-compose ps
```

### Database connection issues
- Check `DB_HOST` in `.env.production` is set to `db`
- Verify database service is running: `docker-compose ps db`
- Check database logs: `docker-compose logs db`

### Nginx 502 errors
- Check backend is running: `docker-compose ps backend`
- Check backend logs: `docker-compose logs backend`
- Verify nginx config: `docker-compose exec nginx nginx -t`

### Static files not loading
- Run collectstatic: `docker-compose run --rm backend python config/manage.py collectstatic --noinput`
- Check volume mounts in docker-compose.yml
- Verify nginx static file paths

## Security Considerations

1. **Change default passwords** in `.env.production`
2. **Use strong SECRET_KEY** for Django
3. **Enable SSL/HTTPS** for production
4. **Keep system updated**: `sudo apt update && sudo apt upgrade`
5. **Configure firewall** properly
6. **Use SSH keys** instead of passwords
7. **Regular backups** of database
8. **Monitor logs** for suspicious activity

## Google Cloud Specific Notes

1. **Firewall Rules**: Ensure Google Cloud firewall allows traffic on ports 80 and 443
2. **Static IP**: Reserve a static IP in Google Cloud Console
3. **Health Checks**: Configure load balancer health checks if using multiple instances
4. **Monitoring**: Set up Google Cloud monitoring for your instance

## Support

For issues or questions, check:
- Application logs: `docker-compose logs`
- System logs: `journalctl -u docker`
- Google Cloud Console for instance status
