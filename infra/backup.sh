#!/bin/bash

set -e

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

echo "💾 Creating database backup..."

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Backup database
docker compose exec -T db pg_dump -U "${DB_USER:-accreditrack}" "${DB_NAME:-accreditrack}" > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

echo "✅ Backup created: ${BACKUP_FILE}.gz"
echo "📊 Backup size: $(du -h ${BACKUP_FILE}.gz | cut -f1)"
