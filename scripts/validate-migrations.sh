#!/bin/bash
# Validate that Django migrations are up to date
set -e

cd "$(dirname "$0")/../backend"

echo "Checking for pending migrations..."

# Check if we can import Django (basic check)
python3 -c "import django" 2>/dev/null || {
    echo "Django not installed locally. This check will run in CI/CD."
    echo "To check locally, install dependencies: pip install -r requirements.txt"
    exit 0
}

# Check for pending migrations
python3 manage.py makemigrations --check --dry-run || {
    echo "ERROR: There are pending migrations!"
    echo "Run: python manage.py makemigrations"
    exit 1
}

echo "✅ No pending migrations"
