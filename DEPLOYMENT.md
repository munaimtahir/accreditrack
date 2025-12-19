# AccrediFy VPS Deployment Guide

This guide provides detailed instructions for deploying AccrediFy to a VPS (Virtual Private Server).

## Prerequisites

- VPS with Ubuntu 20.04+ or similar Linux distribution
- Docker and Docker Compose installed
- At least 2GB of free disk space
- Root or sudo access
- Domain name or IP address (configured for: 172.104.187.212)

## Quick Deployment

### Automated Deployment (Recommended)

The fastest way to deploy AccrediFy is using the automated deployment script:

```bash
# Make the script executable
chmod +x deploy-to-vps.sh

# Run the deployment
./deploy-to-vps.sh
```

The script will automatically:
- ✅ Validate all prerequisites (Docker, Docker Compose, disk space)
- ✅ Set up environment variables
- ✅ Build the frontend
- ✅ Build and start all Docker containers
- ✅ Run database migrations
- ✅ Create admin user
- ✅ Perform health checks on all services
- ✅ Verify volumes and API configuration
- ✅ Test Gemini API integration
- ✅ Test frontend/backend connectivity
- ✅ Debug common issues

### Manual Deployment

If you prefer manual control or need to customize the deployment:

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

## Configuration

### Environment Variables

The `.env` file contains all configuration. Key variables:

```env
# Database
DB_NAME=accredify
DB_USER=accredify
DB_PASSWORD=your_secure_password

# Django
DJANGO_SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,172.104.187.212
CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1,http://172.104.187.212

# Gemini AI API
GEMINI_API_KEY=AIzaSyAvK-H204qOxbincL3UZaiU1f8bSglvULg
```

### VPS IP Configuration

The application is pre-configured for VPS IP: **172.104.187.212**

To change this, update in `.env`:
```env
ALLOWED_HOSTS=localhost,127.0.0.1,YOUR_VPS_IP
CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1,http://YOUR_VPS_IP
```

## Gemini API Configuration

### API Key
The Gemini API key is pre-configured:
```
AIzaSyAvK-H204qOxbincL3UZaiU1f8bSglvULg
```

### API Endpoint
```
https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent
```

### Model Used
- **gemini-2.0-flash-exp** - Latest Gemini 2.0 Flash model for fast and efficient AI responses

### AI Features Available
1. **Analyze Checklist** - `POST /api/analyze-checklist/`
2. **Categorize Indicators** - `POST /api/analyze-categorization/`
3. **Ask AI Assistant** - `POST /api/ask-assistant/`
4. **Generate Reports** - `POST /api/report-summary/`
5. **Convert Documents** - `POST /api/convert-document/`
6. **Compliance Guides** - `POST /api/compliance-guide/`
7. **Analyze Tasks** - `POST /api/analyze-tasks/`

## Docker Services

### Architecture
```
┌─────────────────┐
│   NGINX (80)    │ ← Public Entry Point
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼────┐ ┌──▼────────┐
│Frontend│ │  Backend  │
│ (React)│ │ (Django)  │
└────────┘ └─────┬─────┘
                 │
          ┌──────▼──────┐
          │ PostgreSQL  │
          └─────────────┘
```

### Services
1. **nginx** - Reverse proxy and static file server
   - Port: 80
   - Serves frontend and proxies API requests
   
2. **backend** - Django REST API
   - Port: 8000 (internal)
   - Gunicorn with 3 workers
   - Auto-restart on failure
   
3. **db** - PostgreSQL 16
   - Port: 5432 (internal)
   - Persistent volume for data

### Docker Volumes
- `db_data` - PostgreSQL database storage
- `backend_static` - Django static files
- `backend_media` - User uploaded media files

## Access Information

### URLs
- **Frontend**: http://172.104.187.212/
- **API Documentation**: http://172.104.187.212/api/docs/
- **Admin Panel**: http://172.104.187.212/admin/
- **API Root**: http://172.104.187.212/api/

### Default Credentials
```
Username: admin
Password: admin123
```

⚠️ **Important**: Change the default password immediately after first login!

## Common Commands

### Service Management
```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Restart services
docker compose restart

# View status
docker compose ps

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f nginx
docker compose logs -f db
```

### Database Management
```bash
# Run migrations
docker compose exec backend python manage.py migrate

# Create superuser
docker compose exec backend python manage.py createsuperuser

# Django shell
docker compose exec backend python manage.py shell

# Backup database
docker compose exec db pg_dump -U accredify accredify > backup.sql

# Restore database
cat backup.sql | docker compose exec -T db psql -U accredify accredify
```

### Maintenance
```bash
# Collect static files
docker compose exec backend python manage.py collectstatic --noinput

# Clear cache (if implemented)
docker compose exec backend python manage.py clear_cache

# Check system status
docker compose exec backend python manage.py check
```

## Troubleshooting

### Service Health Checks

The deployment script includes automatic health checks. You can manually verify:

```bash
# Check all services
docker compose ps

# Check backend health
curl http://localhost/admin/

# Check API
curl http://localhost/api/

# Check Gemini API integration
TOKEN=$(curl -s -X POST http://localhost/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])")

curl -X POST http://localhost/api/ask-assistant/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"question": "What is compliance?"}'
```

### Common Issues

#### 1. Services Not Starting
```bash
# Check logs
docker compose logs

# Check disk space
df -h

# Restart Docker
sudo systemctl restart docker
```

#### 2. Database Connection Issues
```bash
# Check database logs
docker compose logs db

# Verify database is healthy
docker compose exec db pg_isready -U accredify
```

#### 3. Frontend Not Loading
```bash
# Rebuild frontend
cd frontend && npm run build && cd ..

# Restart nginx
docker compose restart nginx
```

#### 4. API Not Responding
```bash
# Check backend logs
docker compose logs backend

# Restart backend
docker compose restart backend
```

#### 5. Gemini API Errors
```bash
# Verify API key is set
docker compose exec backend env | grep GEMINI_API_KEY

# Check backend logs for API errors
docker compose logs backend | grep -i gemini
```

### Debug Mode

To enable debug mode (not recommended for production):

```bash
# Edit .env
DEBUG=True

# Restart services
docker compose restart
```

## Security Best Practices

1. **Change Default Credentials**
   ```bash
   docker compose exec backend python manage.py changepassword admin
   ```

2. **Use Strong Passwords**
   - Update `DB_PASSWORD` in `.env`
   - Generate new `DJANGO_SECRET_KEY`

3. **Enable HTTPS**
   - Install SSL certificates (Let's Encrypt)
   - Update nginx configuration
   - Update CORS settings

4. **Regular Updates**
   ```bash
   # Pull latest changes
   git pull

   # Rebuild containers
   docker compose up --build -d
   ```

5. **Backup Strategy**
   - Regular database backups
   - Volume snapshots
   - Configuration backups

## Monitoring

### Log Files
```bash
# Real-time logs
docker compose logs -f

# Export logs
docker compose logs > logs.txt

# Logs for specific time period
docker compose logs --since 1h
```

### Resource Usage
```bash
# Container stats
docker stats

# Disk usage
docker system df

# Volume sizes
docker volume ls
```

## Scaling

### Increase Backend Workers
Edit `docker-compose.yml`:
```yaml
backend:
  command: >
    sh -c "python manage.py migrate &&
           python manage.py collectstatic --noinput &&
           gunicorn accredify_backend.wsgi:application --bind 0.0.0.0:8000 --workers 5 --timeout 120"
```

### Add More Resources
```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
```

## Backup and Restore

### Automatic Backup Script
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker compose exec -T db pg_dump -U accredify accredify > backup_$DATE.sql
tar czf backup_$DATE.tar.gz backup_$DATE.sql
```

### Restore from Backup
```bash
cat backup.sql | docker compose exec -T db psql -U accredify accredify
```

## Support

For issues, questions, or contributions:
- Check logs: `docker compose logs`
- Review documentation: `README.md`
- Open an issue on the repository

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Gemini API Documentation](https://ai.google.dev/docs)
