#!/bin/bash
# Validate frontend build
set -e

cd "$(dirname "$0")/../frontend"

echo "Validating frontend configuration..."

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "ERROR: package.json not found"
    exit 1
fi

# Check if node_modules exists (optional)
if [ ! -d "node_modules" ]; then
    echo "WARNING: node_modules not found. Run 'npm install' first."
fi

# Validate package.json syntax
node -e "JSON.parse(require('fs').readFileSync('package.json'))" || {
    echo "ERROR: Invalid package.json"
    exit 1
}

echo "✅ Frontend configuration valid"
