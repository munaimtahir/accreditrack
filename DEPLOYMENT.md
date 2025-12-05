# Deployment Overview

This application is configured for multi-app deployment on a VPS using Docker Compose and Nginx as a reverse proxy.

## Architecture

```
Internet → Nginx (Port 80/443) → Frontend (Next.js) + Backend (Django/Gunicorn)
                                    ↓
                                 PostgreSQL Database
```

## Key Features

- **Multi-app Support**: Nginx configuration allows multiple applications on the same VPS
- **Production Ready**: Gunicorn for Django, optimized Next.js build
- **Security**: HTTPS support, security headers, CORS configuration
- **Scalable**: Docker Compose makes it easy to scale services
- **Google Cloud Compatible**: Configured for Google Cloud VPS public IP

## Quick Links

- [Full Deployment Guide](./infra/README.md)
- [Quick Start Guide](./infra/QUICK_START.md)
- [Deployment Scripts](./infra/)

## File Structure

```
infra/
├── docker-compose.yml          # Production Docker Compose configuration
├── deploy.sh                   # Initial deployment script
├── update.sh                   # Update application script
├── backup.sh                   # Database backup script
├── generate-secret-key.sh      # Generate Django secret key
├── README.md                   # Full deployment documentation
├── QUICK_START.md              # Quick start guide
└── nginx/
    ├── nginx.conf              # Main Nginx configuration
    └── conf.d/
        └── accreditrack.conf   # Application-specific Nginx config
```

## Environment Variables

### Backend (.env.production)
- `SECRET_KEY`: Django secret key (use generate-secret-key.sh)
- `ALLOWED_HOSTS`: Comma-separated list including your Google Cloud IP
- `DB_PASSWORD`: Strong database password
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed origins
- `SECURE_SSL_REDIRECT`: Set to True when SSL is configured

### Frontend (.env.production)
- `NEXT_PUBLIC_API_URL`: Full API URL (e.g., https://your-ip/api/v1)

## Deployment Steps Summary

1. **Server Setup**: Install Docker, configure firewall
2. **Clone Repository**: Get code on server
3. **Configure Environment**: Set up .env.production files
4. **Update Nginx Config**: Add your Google Cloud IP
5. **Deploy**: Run `./deploy.sh`

## Multi-App Deployment

To add another application:

1. Create new nginx config in `infra/nginx/conf.d/`
2. Add new services to `docker-compose.yml`
3. Use different server_name or paths in nginx config
4. Restart nginx: `docker-compose restart nginx`

## Maintenance

- **Update**: `./update.sh`
- **Backup**: `./backup.sh`
- **Logs**: `docker-compose logs -f [service]`
- **Restart**: `docker-compose restart [service]`

## Support

For detailed instructions, see [infra/README.md](./infra/README.md)
