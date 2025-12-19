# AccrediFy Quick Start Guide

## TL;DR - One Command Deployment

```bash
chmod +x deploy-to-vps.sh && ./deploy-to-vps.sh
```

That's it! The script handles everything automatically.

## What Gets Deployed?

✅ **PostgreSQL 16** - Database with persistent storage
✅ **Django Backend** - REST API with Gunicorn (3 workers)
✅ **React Frontend** - Production-optimized build
✅ **Nginx** - Reverse proxy and static file server
✅ **Gemini AI** - AI-powered compliance analysis

## Access After Deployment

| Service | URL |
|---------|-----|
| **Frontend** | http://172.104.187.212/ |
| **API Docs** | http://172.104.187.212/api/docs/ |
| **Admin Panel** | http://172.104.187.212/admin/ |

**Default Login:**
- Username: `admin`
- Password: `admin123`

⚠️ Change the password immediately!

## Key Features

### AI-Powered Analysis (Gemini API)
- ✨ Analyze compliance checklists
- 📊 Categorize indicators automatically
- 💬 Ask compliance questions to AI assistant
- 📝 Generate compliance reports
- 📄 Convert documents between formats
- 📚 Get compliance guides
- 🎯 Analyze and optimize tasks

### API Endpoints
```bash
# Get JWT token
curl -X POST http://172.104.187.212/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Use AI assistant
curl -X POST http://172.104.187.212/api/ask-assistant/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"question": "What is PMDC compliance?"}'
```

## Quick Commands

```bash
# View logs
docker compose logs -f

# Restart services
docker compose restart

# Stop everything
docker compose down

# Start again
docker compose up -d
```

## Troubleshooting

### Services not starting?
```bash
docker compose logs
```

### Database issues?
```bash
docker compose exec db pg_isready -U accredify
```

### Frontend not loading?
```bash
docker compose restart nginx
```

## Need More Details?

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive documentation.
