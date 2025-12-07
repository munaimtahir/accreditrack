# 🚀 One-Click Deployment Guide

## Quick Start

Your production deployment is **100% ready**. Just run:

```bash
cd infra
./deploy-one-click.sh
```

That's it! The script will:
- ✅ Check all prerequisites (Docker, Docker Compose)
- ✅ Validate environment configuration
- ✅ Build all Docker images
- ✅ Start database and wait for it to be ready
- ✅ Run migrations automatically
- ✅ Collect static files
- ✅ Start all services (backend, frontend, nginx)
- ✅ Verify everything is running

## What's Already Configured

### ✅ Production Secrets
- **Location**: `infra/secrets/`
- **Backend**: `backend.env` - Django settings with secure SECRET_KEY, database passwords, allowed hosts
- **Frontend**: `frontend.env` - Next.js API URL configuration

### ✅ Secure Values Generated
- Django SECRET_KEY: `5fbv&1sh_!&10k)wlqa@i^a!7%^-uecy$v8&e^zwbqz%7j@$4a`
- Database Password: `OQXDXwq29vxo/mFidP8mLN9i3P/xZcK+0FEcg/girzA=`
- All production-ready values configured

### ✅ IP Address Configuration
- **Current IP**: `34.123.45.67` (example - update with your actual server IP)
- **Allowed Hosts**: Configured in `backend.env`
- **CORS Origins**: Configured for the production IP
- **API URL**: Configured in `frontend.env`

## Updating Your Production IP

If your server IP is different from `34.123.45.67`, update these files:

### 1. `infra/secrets/backend.env`
```bash
ALLOWED_HOSTS=YOUR_ACTUAL_IP,localhost,127.0.0.1,accreditrack.com,www.accreditrack.com
CORS_ALLOWED_ORIGINS=http://YOUR_ACTUAL_IP,https://YOUR_ACTUAL_IP,http://accreditrack.com,https://accreditrack.com
```

### 2. `infra/secrets/frontend.env`
```bash
NEXT_PUBLIC_API_URL=http://YOUR_ACTUAL_IP/api/v1
```

### 3. `infra/nginx/conf.d/accreditrack.conf`
Update the `server_name` directive (line 15) if using a domain name.

## Deployment Commands

### Full Deployment (One-Click)
```bash
cd infra
./deploy-one-click.sh
```

### Standard Deployment
```bash
cd infra
./deploy.sh
```

### Manual Docker Compose
```bash
cd infra
docker compose up -d --build
```

## Service Management

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

### Stop Services
```bash
docker compose down
```

### Restart Services
```bash
docker compose restart
```

### Check Status
```bash
docker compose ps
```

## Access Points

After deployment, your application will be available at:

- **Frontend**: `http://34.123.45.67`
- **API**: `http://34.123.45.67/api/v1`
- **Health Check**: `http://34.123.45.67/api/v1/health/`
- **Admin Panel**: `http://34.123.45.67/api/v1/admin/` (if superuser created)

## Database Management

### Create Superuser
```bash
docker compose exec backend python config/manage.py createsuperuser
```

### Run Migrations
```bash
docker compose exec backend python config/manage.py migrate
```

### Access Database Shell
```bash
docker compose exec db psql -U accreditrack -d accreditrack
```

## Troubleshooting

### Services Not Starting
```bash
# Check logs
docker compose logs

# Check service status
docker compose ps

# Restart specific service
docker compose restart backend
```

### Database Connection Issues
```bash
# Check database logs
docker compose logs db

# Verify database is ready
docker compose exec db pg_isready -U accreditrack
```

### Port Already in Use
If ports 80 or 443 are already in use, update `infra/docker-compose.yml`:
```yaml
nginx:
  ports:
    - "8080:80"  # Change 80 to 8080
    - "8443:443" # Change 443 to 8443
```

## Production Checklist

- [x] Environment files created with secure values
- [x] Docker Compose configured
- [x] Deployment scripts ready
- [x] Nginx reverse proxy configured
- [x] Health checks enabled
- [ ] Update IP address in env files (if different)
- [ ] Configure domain name (if using)
- [ ] Set up SSL certificates (for HTTPS)
- [ ] Create superuser account
- [ ] Configure firewall rules (allow ports 80, 443)

## Next Steps

1. **Update IP Address**: Edit `infra/secrets/backend.env` and `infra/secrets/frontend.env` with your actual server IP
2. **Run Deployment**: Execute `./deploy-one-click.sh`
3. **Create Admin User**: Run `docker compose exec backend python config/manage.py createsuperuser`
4. **Access Application**: Open `http://YOUR_IP` in browser

## Security Notes

⚠️ **Important**: 
- The secrets directory is gitignored and contains production credentials
- Never commit `infra/secrets/` to version control
- Keep backups of your secrets in a secure location
- Rotate passwords periodically

---

**Ready to deploy?** Just run `./deploy-one-click.sh`! 🚀
