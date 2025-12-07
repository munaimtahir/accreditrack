# Database Migrations Guide

This guide covers database migration procedures for AccrediTrack.

## Overview

Django migrations are automatically run during deployment via the `deploy.sh` and `update.sh` scripts. This document provides additional information for manual migration management and rollback procedures.

## Automatic Migrations

### During Deployment

The `infra/deploy.sh` script automatically runs migrations:

```bash
docker compose run --rm backend python config/manage.py migrate
```

### During Updates

The `infra/update.sh` script also runs migrations before restarting services.

## Manual Migration Commands

### Create Migrations

```bash
# From project root
cd backend
python config/manage.py makemigrations

# For specific app
python config/manage.py makemigrations accounts
```

### Apply Migrations

```bash
# Apply all pending migrations
docker compose run --rm backend python config/manage.py migrate

# Apply migrations for specific app
docker compose run --rm backend python config/manage.py migrate accounts

# Show migration status
docker compose run --rm backend python config/manage.py showmigrations
```

### Rollback Migrations

```bash
# Rollback last migration
docker compose run --rm backend python config/manage.py migrate accounts zero

# Rollback to specific migration
docker compose run --rm backend python config/manage.py migrate accounts 0001_initial

# Rollback all migrations for an app
docker compose run --rm backend python config/manage.py migrate accounts zero
```

## Zero-Downtime Migration Strategy

### For Non-Breaking Changes

1. **Add new fields as nullable**:
   ```python
   new_field = models.CharField(max_length=100, null=True, blank=True)
   ```

2. **Deploy and migrate**:
   ```bash
   ./infra/update.sh
   ```

3. **Populate data** (if needed):
   ```bash
   docker compose run --rm backend python config/manage.py shell
   # Run data migration script
   ```

4. **Make field required** (in next deployment):
   ```python
   new_field = models.CharField(max_length=100)
   ```

### For Breaking Changes

1. **Create backward-compatible migration**:
   - Add new fields/columns alongside old ones
   - Update application code to use new fields
   - Deploy and migrate

2. **Data migration**:
   - Copy data from old to new fields
   - Verify data integrity

3. **Remove old fields** (in subsequent deployment):
   - Remove old columns/fields
   - Update code to remove references

## Migration Best Practices

1. **Test migrations locally first**:
   ```bash
   # Create test database
   docker compose up -d db
   docker compose run --rm backend python config/manage.py migrate
   ```

2. **Review migration files** before committing:
   - Check for data loss risks
   - Verify field types and constraints
   - Ensure indexes are created for foreign keys

3. **Backup before major migrations**:
   ```bash
   ./infra/backup.sh
   ```

4. **Run migrations during low-traffic periods** when possible

5. **Monitor application logs** during migration:
   ```bash
   docker compose logs -f backend
   ```

## Troubleshooting

### Migration Conflicts

If migrations conflict:

1. **Check migration status**:
   ```bash
   docker compose run --rm backend python config/manage.py showmigrations
   ```

2. **Resolve conflicts**:
   - Merge migration files if needed
   - Or reset migrations (development only):
     ```bash
     # WARNING: Only in development!
     docker compose run --rm backend python config/manage.py migrate accounts zero
     docker compose run --rm backend python config/manage.py migrate
     ```

### Migration Fails

1. **Check database connection**:
   ```bash
   docker compose exec db psql -U accreditrack -d accreditrack -c "SELECT 1;"
   ```

2. **Check migration file syntax**:
   ```bash
   docker compose run --rm backend python config/manage.py check
   ```

3. **Review error logs**:
   ```bash
   docker compose logs backend
   ```

4. **Rollback if necessary**:
   ```bash
   docker compose run --rm backend python config/manage.py migrate accounts <previous_migration>
   ```

### Database Lock Issues

If migrations hang due to database locks:

1. **Check for long-running queries**:
   ```bash
   docker compose exec db psql -U accreditrack -d accreditrack -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
   ```

2. **Kill blocking queries** (if safe):
   ```bash
   docker compose exec db psql -U accreditrack -d accreditrack -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'active' AND pid != pg_backend_pid();"
   ```

## Data Migrations

For complex data migrations, create a management command:

```python
# backend/accounts/management/commands/migrate_user_data.py
from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Migrate user data'

    def handle(self, *args, **options):
        # Migration logic here
        pass
```

Run with:
```bash
docker compose run --rm backend python config/manage.py migrate_user_data
```

## Migration Checklist

Before deploying migrations to production:

- [ ] Migrations tested in development/staging
- [ ] Database backup created
- [ ] Migration files reviewed
- [ ] Data migration scripts tested (if applicable)
- [ ] Rollback procedure documented
- [ ] Deployment scheduled during low-traffic period
- [ ] Monitoring in place
- [ ] Team notified of deployment

## Additional Resources

- [Django Migrations Documentation](https://docs.djangoproject.com/en/stable/topics/migrations/)
- [Zero-Downtime Deployments](https://www.postgresql.org/docs/current/ddl-alter.html)
