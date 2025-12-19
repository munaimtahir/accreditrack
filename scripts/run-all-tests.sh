#!/bin/bash
# Run all tests and validations
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "Running All Tests and Validations"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

test_step() {
    local name="$1"
    local command="$2"
    
    echo -n "Testing: $name... "
    if eval "$command" > /tmp/test_output.log 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        cat /tmp/test_output.log | head -20
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Test 1: Validate YAML syntax for GitHub Actions
test_step "GitHub Actions YAML syntax" \
    "python3 -c 'import yaml; [yaml.safe_load(open(f)) for f in [\".github/workflows/backend-tests.yml\", \".github/workflows/frontend-tests.yml\", \".github/workflows/docker-tests.yml\"]]'"

# Test 2: Validate frontend package.json
test_step "Frontend package.json" \
    "cd frontend && node -e 'JSON.parse(require(\"fs\").readFileSync(\"package.json\"))'"

# Test 3: Validate backend requirements.txt exists
test_step "Backend requirements.txt" \
    "test -f $PROJECT_ROOT/backend/requirements.txt"

# Test 4: Validate docker-compose.yml syntax (skip if docker not available)
if command -v docker >/dev/null 2>&1; then
    test_step "Docker Compose syntax" \
        "(test -f .env || (test -f .env.template && cp .env.template .env)) && (docker compose config > /dev/null 2>&1 || docker-compose config > /dev/null 2>&1)"
else
    echo -e "${YELLOW}Skipping: Docker Compose syntax (Docker not available)${NC}"
    PASSED=$((PASSED + 1))
fi

# Test 5: Validate Dockerfiles exist
test_step "Dockerfiles exist" \
    "test -f $PROJECT_ROOT/Dockerfile && test -f $PROJECT_ROOT/backend/Dockerfile && test -f $PROJECT_ROOT/frontend/Dockerfile"

# Test 6: Validate nginx config exists
test_step "Nginx configuration" \
    "test -f $PROJECT_ROOT/nginx/conf.d/default.conf"

# Test 7: Validate deployment scripts exist and are executable
test_step "Deployment scripts" \
    "test -x $PROJECT_ROOT/deploy-vps.sh"

# Test 8: Check for Python syntax errors in backend
test_step "Backend Python syntax" \
    "find $PROJECT_ROOT/backend -name '*.py' -not -path '*/migrations/*' -not -path '*/venv*/*' -exec python3 -m py_compile {} +"

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
