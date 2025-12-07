# Security Guide

This document outlines security best practices, secrets management, and credential rotation procedures for AccrediTrack.

## Secrets Management

### Overview

AccrediTrack uses environment variables for all sensitive configuration. **Never commit `.env.production` files to the repository.** Only `.env.example` and `.env.production.example` files should be committed.

### Environment Files

- **Development**: Use `.env` files (gitignored)
- **Production**: Use `.env.production` files (gitignored)
- **Examples**: `.env.example` and `.env.production.example` (committed to repo)

### Required Environment Variables

#### Backend (`backend/.env.production`)

```bash
# Django Settings
SECRET_KEY=<generate-using-generate-secret-key.sh>
DEBUG=False
ALLOWED_HOSTS=your-ip,localhost,127.0.0.1

# Database Configuration
DB_NAME=accreditrack
DB_USER=accreditrack
DB_PASSWORD=<strong-random-password>
DB_HOST=db
DB_PORT=5432

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://your-ip,https://your-domain.com

# Security Settings
SECURE_SSL_REDIRECT=True  # Set to True when SSL is configured
```

#### Frontend (`frontend/.env.production`)

```bash
NEXT_PUBLIC_API_URL=https://your-ip/api/v1
```

### Generating Secrets

#### Django Secret Key

Use the provided script:

```bash
cd infra
./generate-secret-key.sh
```

Or manually:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### Database Password

Generate a strong random password:

```bash
openssl rand -base64 32
```

Or use a password manager to generate a secure password.

### Setting Up Environment Files

1. **Copy example files**:
   ```bash
   cp backend/.env.production.example backend/.env.production
   cp frontend/.env.production.example frontend/.env.production
   ```

2. **Update values**:
   - Generate and set `SECRET_KEY`
   - Set strong `DB_PASSWORD`
   - Update `ALLOWED_HOSTS` with your server IP/domain
   - Update `CORS_ALLOWED_ORIGINS` with your frontend URL
   - Update `NEXT_PUBLIC_API_URL` in frontend `.env.production`

3. **Verify files are gitignored**:
   ```bash
   git status
   # .env.production files should NOT appear
   ```

## Credential Rotation

### When to Rotate Credentials

Rotate credentials immediately if:
- Credentials have been exposed in Git history
- Credentials have been shared insecurely
- A security breach is suspected
- As part of regular security maintenance (recommended: every 90 days)

### Rotation Procedure

#### 1. Rotate Django SECRET_KEY

**⚠️ WARNING**: Changing SECRET_KEY will invalidate all existing sessions and password reset tokens.

1. Generate new secret key:
   ```bash
   cd infra
   ./generate-secret-key.sh
   ```

2. Update `backend/.env.production`:
   ```bash
   SECRET_KEY=<new-secret-key>
   ```

3. Restart backend service:
   ```bash
   cd infra
   docker compose restart backend
   ```

4. **Notify users**: All users will need to log in again.

#### 2. Rotate Database Password

1. Generate new password:
   ```bash
   openssl rand -base64 32
   ```

2. Update database password in PostgreSQL:
   ```bash
   docker compose exec db psql -U accreditrack -d accreditrack -c "ALTER USER accreditrack WITH PASSWORD 'new-password';"
   ```

3. Update `backend/.env.production`:
   ```bash
   DB_PASSWORD=<new-password>
   ```

4. Update `infra/docker-compose.yml` environment variable (if using):
   ```yaml
   POSTGRES_PASSWORD: <new-password>
   ```

5. Restart services:
   ```bash
   docker compose restart db backend
   ```

#### 3. Rotate JWT Signing Key

The JWT signing key uses the Django `SECRET_KEY`. Rotating `SECRET_KEY` (step 1) automatically rotates JWT keys. All existing tokens will be invalidated.

### Post-Rotation Checklist

- [ ] All services restarted successfully
- [ ] Application is accessible
- [ ] Users can log in
- [ ] Database connections working
- [ ] No errors in logs
- [ ] Old credentials removed from any documentation or notes

## Removing Exposed Credentials from Git History

If credentials were accidentally committed:

### Option 1: Using git filter-repo (Recommended)

```bash
# Install git-filter-repo if not installed
pip install git-filter-repo

# Remove .env.production files from history
git filter-repo --path backend/.env.production --invert-paths
git filter-repo --path frontend/.env.production --invert-paths

# Force push (coordinate with team)
git push origin --force --all
```

### Option 2: Using BFG Repo-Cleaner

```bash
# Download BFG from https://rtyley.github.io/bfg-repo-cleaner/

# Remove files
java -jar bfg.jar --delete-files .env.production

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

**⚠️ Important**: After cleaning history:
1. Rotate ALL exposed credentials immediately
2. Notify all team members to re-clone the repository
3. Update any CI/CD systems that may have cached credentials

## Docker Secrets (Alternative Approach)

For production deployments, consider using Docker secrets:

1. Create secrets:
   ```bash
   echo "your-secret-key" | docker secret create django_secret_key -
   echo "your-db-password" | docker secret create db_password -
   ```

2. Update `docker-compose.yml` to use secrets:
   ```yaml
   services:
     backend:
       secrets:
         - django_secret_key
       environment:
         SECRET_KEY_FILE: /run/secrets/django_secret_key
   secrets:
     django_secret_key:
       external: true
   ```

3. Update Django settings to read from secret files if needed.

## Cloud Secrets Management

For cloud deployments, consider using:

- **AWS**: AWS Secrets Manager or Parameter Store
- **Google Cloud**: Secret Manager
- **Azure**: Key Vault
- **HashiCorp Vault**: Self-hosted or cloud-managed

### Example: Google Cloud Secret Manager

```bash
# Create secrets
gcloud secrets create django-secret-key --data-file=- <<< "your-secret-key"
gcloud secrets create db-password --data-file=- <<< "your-password"

# Grant access
gcloud secrets add-iam-policy-binding django-secret-key \
  --member="serviceAccount:your-sa@project.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Security Best Practices

1. **Never commit secrets**: Always use `.gitignore` and example files
2. **Use strong passwords**: Minimum 32 characters, mix of characters
3. **Rotate regularly**: Every 90 days for production credentials
4. **Limit access**: Only grant access to secrets to those who need them
5. **Monitor access**: Log and audit secret access
6. **Use secrets management services**: For production, prefer managed services
7. **Encrypt at rest**: Ensure database and backups are encrypted
8. **Use HTTPS**: Always use SSL/TLS in production
9. **Keep dependencies updated**: Regularly update packages for security patches
10. **Regular audits**: Review and audit access logs regularly

## Incident Response

If credentials are exposed:

1. **Immediately rotate** all exposed credentials
2. **Remove from Git history** (see above)
3. **Review access logs** for unauthorized access
4. **Notify affected users** if necessary
5. **Document the incident** and lessons learned
6. **Update procedures** to prevent recurrence

## Additional Resources

- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [12-Factor App: Config](https://12factor.net/config)
