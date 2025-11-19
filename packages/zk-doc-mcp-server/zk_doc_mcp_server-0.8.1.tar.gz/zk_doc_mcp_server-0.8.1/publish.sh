#!/bin/bash

# ZK Doc MCP Package Publisher
# Usage: ./publish.sh [test|prod]
#
# Parameters:
#   test - Publish to TestPyPI (https://test.pypi.org)
#   prod - Publish to PyPI (https://pypi.org)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check parameter
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Missing target parameter${NC}"
    echo "Usage: ./publish.sh [test|prod]"
    echo ""
    echo "Examples:"
    echo "  ./publish.sh test  # Publish to TestPyPI"
    echo "  ./publish.sh prod  # Publish to PyPI"
    exit 1
fi

TARGET=$1

# Set URL and token env var based on target
if [ "$TARGET" = "test" ]; then
    PUBLISH_URL="https://test.pypi.org/legacy/"
    TOKEN_ENV_VAR="TESTPYPI_TOKEN"
    DISPLAY_URL="TestPyPI (https://test.pypi.org)"
elif [ "$TARGET" = "prod" ]; then
    PUBLISH_URL="https://upload.pypi.org/legacy/"
    TOKEN_ENV_VAR="PYPI_TOKEN"
    DISPLAY_URL="PyPI (https://pypi.org)"
else
    echo -e "${RED}Error: Invalid target '${TARGET}'${NC}"
    echo "Valid options: test, prod"
    exit 1
fi

echo -e "${YELLOW}=== ZK Doc MCP Package Publisher ===${NC}"
echo -e "Target: ${DISPLAY_URL}"
echo ""

# Check if token is already set in environment
if [ -z "${!TOKEN_ENV_VAR}" ]; then
    echo -e "${YELLOW}API Token not found in \$${TOKEN_ENV_VAR}${NC}"
    echo ""

    if [ "$TARGET" = "test" ]; then
        echo "To get a TestPyPI token:"
        echo "1. Go to https://test.pypi.org/account/manage/tokens/"
        echo "2. Create a new API token"
        echo "3. Copy the token value (starts with 'pypi-')"
        echo ""
    else
        echo "To get a PyPI token:"
        echo "1. Go to https://pypi.org/account/manage/tokens/"
        echo "2. Create a new API token"
        echo "3. Copy the token value (starts with 'pypi-')"
        echo ""
    fi

    read -sp "Enter your API token: " TOKEN
    echo ""

    if [ -z "$TOKEN" ]; then
        echo -e "${RED}Error: Token cannot be empty${NC}"
        exit 1
    fi

    export "${TOKEN_ENV_VAR}=${TOKEN}"
else
    echo -e "${GREEN}API token found in \$${TOKEN_ENV_VAR}${NC}"
fi

# Verify dist directory exists
if [ ! -d "dist" ]; then
    echo -e "${RED}Error: dist/ directory not found${NC}"
    echo "Please run 'uv build' first to build the package"
    exit 1
fi

# Check if there are files to publish
DIST_FILES=$(find dist -type f \( -name "*.whl" -o -name "*.tar.gz" \) 2>/dev/null | wc -l)
if [ "$DIST_FILES" -eq 0 ]; then
    echo -e "${RED}Error: No distribution files found in dist/${NC}"
    echo "Please run 'uv build' first to build the package"
    exit 1
fi

echo -e "${YELLOW}Files to publish:${NC}"
ls -lh dist/ | grep -E "\.(whl|tar\.gz)$" | awk '{print "  " $9 " (" $5 ")"}'
echo ""

# First confirmation - review files
read -p "Continue with publishing to ${DISPLAY_URL}? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}Publishing cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}Publishing to ${DISPLAY_URL}...${NC}"
echo ""

# Publish using uv with the token
if ! uv publish --publish-url "$PUBLISH_URL" \
    --username "__token__" \
    --password "${!TOKEN_ENV_VAR}"; then
    echo ""
    echo -e "${RED}✗ Publishing failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Successfully published to ${DISPLAY_URL}${NC}"
echo ""

if [ "$TARGET" = "test" ]; then
    echo "View your package at:"
    echo "  https://test.pypi.org/project/zk-doc-mcp-server/"
    echo ""
    echo "To test installation:"
    echo "  uv pip install --index-url https://test.pypi.org/simple/ zk-doc-mcp-server"
else
    echo "View your package at:"
    echo "  https://pypi.org/project/zk-doc-mcp-server/"
    echo ""
    echo "To install:"
    echo "  uv pip install zk-doc-mcp-server"
fi
