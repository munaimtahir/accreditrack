# AccrediFy Deployment Guide

## Quick Start

Deploy AccrediFy with a single command:

```bash
./deploy.sh
```

That's it! The script will:
- ✅ Validate all prerequisites
- ✅ Set up environment configuration
- ✅ Build frontend application
- ✅ Deploy Docker containers
- ✅ Run database migrations
- ✅ Create admin user
- ✅ Perform health checks

## Prerequisites

Before running the deployment script, ensure you have:

1. **Docker** (version 20.10 or higher)
   - Install: https://docs.docker.com/get-docker/

2. **Docker Compose** (version 2.0 or higher)
   - Usually included with Docker Desktop
   - Install separately: https://docs.docker.com/compose/install/

3. **Node.js and npm** (optional, for local frontend build)
   - Install: https://nodejs.org/
   - Note: Frontend can be built inside Docker if Node.js is not available

4. **At least 2GB free disk space**

5. **Internet connection** (for downloading dependencies)

## Configuration

### Environment Variables

The script uses the following environment variables (all optional):

- `VPS_IP`: Your server's IP address (default: `172.104.187.212`)
- `GEMINI_API_KEY`: Your Gemini AI API key (required for AI features)

**IMPORTANT**: For security, set `GEMINI_API_KEY` via environment variable:

```bash
export VPS_IP="your.server.ip"
export GEMINI_API_KEY="your-api-key"  # DO NOT commit this to git
./deploy.sh
```

If `GEMINI_API_KEY` is not set, AI features will not work.

### .env File

On first run, the script creates a `.env` file with:
- Randomly generated database password
- Randomly generated Django secret key
- Configured Gemini API key
- VPS IP addresses for CORS and allowed hosts

The `.env` file is preserved across deployments.

## Access URLs

After successful deployment:

### Local Access
- **Frontend**: http://localhost/
- **API Root**: http://localhost/api/
- **API Documentation**: http://localhost/api/docs/
- **Admin Panel**: http://localhost/admin/

### VPS Access (replace with your IP)
- **Frontend**: http://YOUR_VPS_IP/
- **API Root**: http://YOUR_VPS_IP/api/
- **API Documentation**: http://YOUR_VPS_IP/api/docs/
- **Admin Panel**: http://YOUR_VPS_IP/admin/

## Default Credentials

⚠️ **CRITICAL SECURITY WARNING** ⚠️

The deployment creates a default admin account with **PUBLICLY KNOWN** credentials:

```
Username: admin
Password: admin123
```

🚨 **YOU MUST CHANGE THIS PASSWORD IMMEDIATELY AFTER FIRST LOGIN!** 🚨

These credentials are documented publicly and should be considered compromised. Failure to change them immediately exposes your application to unauthorized access.

To change the password:
1. Log in with the default credentials
2. Go to Admin Panel → Users → admin
3. Change password immediately

Or via command line:
```bash
docker compose exec backend python manage.py changepassword admin
```

## Useful Commands

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f nginx
docker compose logs -f db
```

### Restart Services
```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart backend
```

### Stop Services
```bash
docker compose down
```

### Rebuild and Restart
```bash
docker compose up -d --build
```

### Check Service Status
```bash
docker compose ps
```

### Access Backend Shell
```bash
docker compose exec backend python manage.py shell
```

### Run Database Migrations
```bash
docker compose exec backend python manage.py migrate
```

### Create Additional Superuser
```bash
docker compose exec backend python manage.py createsuperuser
```

## Troubleshooting

### Services Not Starting

1. **Check logs**:
   ```bash
   docker compose logs
   ```

2. **Check service status**:
   ```bash
   docker compose ps
   ```

3. **Restart services**:
   ```bash
   docker compose restart
   ```

### Backend Container Restarting

The script automatically fixes the healthcheck issue by using `/api/` endpoint instead of `/admin/`. If you still see restart loops:

1. Check backend logs:
   ```bash
   docker compose logs backend
   ```

2. Verify database connection:
   ```bash
   docker compose exec backend python manage.py check --database default
   ```

3. Check environment variables:
   ```bash
   docker compose exec backend env | grep DB_
   ```

### Port Already in Use

If port 80 is already in use:

1. Stop the conflicting service
2. Or modify `docker-compose.yml` to use a different port:
   ```yaml
   nginx:
     ports:
       - "8080:80"  # Change 80 to 8080 or any available port
   ```

### Database Issues

1. **Reset database** (WARNING: deletes all data):
   ```bash
   docker compose down -v
   ./deploy.sh
   ```

2. **Backup database**:
   ```bash
   docker compose exec db pg_dump -U accredify accredify > backup.sql
   ```

3. **Restore database**:
   ```bash
   cat backup.sql | docker compose exec -T db psql -U accredify accredify
   ```

### Frontend Not Loading

1. Check nginx logs:
   ```bash
   docker compose logs nginx
   ```

2. Verify frontend is built:
   ```bash
   docker compose exec frontend ls -la /usr/share/nginx/html/
   ```

3. Rebuild frontend:
   ```bash
   cd frontend
   npm run build
   cd ..
   docker compose restart nginx
   ```

## Security Recommendations

### For Production Deployment

1. **Change default credentials immediately**
   ```bash
   docker compose exec backend python manage.py changepassword admin
   ```

2. **Update .env file with strong passwords**
   - Generate secure `DB_PASSWORD`
   - Generate secure `DJANGO_SECRET_KEY`
   - Update `GEMINI_API_KEY` if needed

3. **Set DEBUG=False** (already set by default)
   - Verify in `.env`: `DEBUG=False`

4. **Configure HTTPS** (recommended)
   - Set up SSL certificate (Let's Encrypt recommended)
   - Configure nginx for HTTPS
   - Update CORS settings for HTTPS URLs

5. **Restrict ALLOWED_HOSTS**
   - Remove unnecessary hosts from `.env`
   - Keep only your domain and VPS IP

6. **Enable firewall**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

## Updates and Maintenance

### Update Application

```bash
git pull origin main
./deploy.sh
```

### Update Docker Images

```bash
docker compose pull
docker compose up -d
```

### Cleanup Old Images

```bash
docker system prune -a
```

## Support

For issues and questions:
1. Check the deployment log file: `deployment_YYYYMMDD_HHMMSS.log`
2. Review Docker logs: `docker compose logs`
3. Check the project repository for documentation
4. Create an issue on GitHub

## Architecture

The deployment consists of 4 services:

1. **db**: PostgreSQL 16 database
2. **backend**: Django REST Framework API (Python 3.11)
3. **frontend**: React application (served by nginx)
4. **nginx**: Reverse proxy and static file server

All services communicate via a private Docker network (`app-network`).

## Backup and Recovery

### Backup Script

Create a backup script:

```bash
#!/bin/bash
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup database
docker compose exec -T db pg_dump -U accredify accredify > "$BACKUP_DIR/database.sql"

# Backup media files
docker compose cp backend:/app/media "$BACKUP_DIR/"

# Backup .env
cp .env "$BACKUP_DIR/"

echo "Backup completed: $BACKUP_DIR"
```

### Recovery

```bash
# Restore database
cat backup_dir/database.sql | docker compose exec -T db psql -U accredify accredify

# Restore media files
docker compose cp backup_dir/media backend:/app/

# Restore .env
cp backup_dir/.env .
```

## Performance Tuning

### For High Traffic

1. **Increase Gunicorn workers** in `docker-compose.yml`:
   ```yaml
   command: >
     sh -c "python manage.py migrate &&
            python manage.py collectstatic --noinput &&
            gunicorn accredify_backend.wsgi:application --bind 0.0.0.0:8000 --workers 5 --timeout 120"
   ```

2. **Add database connection pooling**

3. **Configure nginx caching**

4. **Use CDN for static files**

## License

See LICENSE file in the project root.
