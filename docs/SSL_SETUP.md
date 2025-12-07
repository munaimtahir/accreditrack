# SSL Certificate Setup Guide

This guide covers setting up SSL/TLS certificates for AccrediTrack using Let's Encrypt.

## Prerequisites

- Domain name pointing to your server IP
- Port 80 and 443 open in firewall
- Docker and Docker Compose installed
- Nginx configured (already done)

## Option 1: Let's Encrypt with Certbot (Recommended)

### Step 1: Install Certbot

On your server:

```bash
sudo apt-get update
sudo apt-get install certbot
```

### Step 2: Obtain Certificate

```bash
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com
```

Certificates will be stored in `/etc/letsencrypt/live/your-domain.com/`

### Step 3: Update Docker Compose

Update `infra/docker-compose.yml` to mount certificates:

```yaml
nginx:
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    - ./nginx/conf.d:/etc/nginx/conf.d:ro
    - /etc/letsencrypt:/etc/letsencrypt:ro  # Add this line
    - backend_static:/var/www/static:ro
    - backend_media:/var/www/media:ro
```

### Step 4: Update Nginx Configuration

Update `infra/nginx/conf.d/accreditrack.conf`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Rest of your configuration...
}
```

### Step 5: Update Environment Variables

Update `backend/.env.production`:

```bash
SECURE_SSL_REDIRECT=True
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

Update `frontend/.env.production`:

```bash
NEXT_PUBLIC_API_URL=https://your-domain.com/api/v1
```

### Step 6: Restart Services

```bash
cd infra
docker compose restart nginx
docker compose restart backend frontend
```

### Step 7: Set Up Auto-Renewal

Create a renewal script `infra/renew-ssl.sh`:

```bash
#!/bin/bash
certbot renew --quiet --post-hook "docker compose -f /path/to/infra/docker-compose.yml restart nginx"
```

Add to crontab:

```bash
sudo crontab -e
# Add this line:
0 3 * * * /path/to/infra/renew-ssl.sh
```

## Option 2: Certbot in Docker Container

### Step 1: Add Certbot Service to docker-compose.yml

```yaml
certbot:
  image: certbot/certbot
  volumes:
    - ./nginx/conf.d:/etc/nginx/conf.d:ro
    - certbot-data:/etc/letsencrypt
    - certbot-www:/var/www/certbot
  command: certonly --webroot --webroot-path=/var/www/certbot --email your-email@example.com --agree-tos --no-eff-email -d your-domain.com

volumes:
  certbot-data:
  certbot-www:
```

### Step 2: Update Nginx for ACME Challenge

Add to nginx config:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$host$request_uri;
    }
}
```

### Step 3: Obtain Certificate

```bash
docker compose run --rm certbot
```

### Step 4: Update Nginx SSL Configuration

Same as Option 1, Step 4.

## Option 3: Self-Signed Certificate (Development Only)

⚠️ **Warning**: Self-signed certificates are for development only. Browsers will show security warnings.

### Generate Self-Signed Certificate

```bash
mkdir -p infra/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout infra/nginx/ssl/nginx-selfsigned.key \
  -out infra/nginx/ssl/nginx-selfsigned.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"
```

### Update Nginx Configuration

```nginx
ssl_certificate /etc/nginx/ssl/nginx-selfsigned.crt;
ssl_certificate_key /etc/nginx/ssl/nginx-selfsigned.key;
```

## Testing SSL Configuration

### Check Certificate

```bash
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

### Test SSL Labs

Visit: https://www.ssllabs.com/ssltest/analyze.html?d=your-domain.com

### Verify HTTPS Redirect

```bash
curl -I http://your-domain.com
# Should return 301 redirect to https://
```

## Troubleshooting

### Certificate Not Found

- Verify certificate path in nginx config
- Check file permissions: `sudo chmod 644 /etc/letsencrypt/live/your-domain.com/*.pem`
- Ensure nginx container has read access

### Mixed Content Warnings

- Ensure all API calls use HTTPS
- Check `NEXT_PUBLIC_API_URL` uses `https://`
- Verify `CORS_ALLOWED_ORIGINS` uses HTTPS

### Certificate Renewal Fails

- Check certbot logs: `sudo certbot certificates`
- Verify domain DNS still points to server
- Ensure port 80 is accessible for renewal

### Nginx Won't Start

- Check nginx config: `docker compose exec nginx nginx -t`
- Verify SSL certificate files exist
- Check nginx logs: `docker compose logs nginx`

## Security Headers

After SSL is configured, ensure these headers are set (already in Django settings):

- `Strict-Transport-Security` (HSTS)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`

## Additional Resources

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Certbot Documentation](https://certbot.eff.org/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [SSL Labs SSL Test](https://www.ssllabs.com/ssltest/)
