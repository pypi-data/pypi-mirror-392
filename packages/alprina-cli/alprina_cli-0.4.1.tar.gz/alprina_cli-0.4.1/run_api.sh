#!/bin/bash

# Alprina API Startup Script
# Runs the FastAPI server with proper configuration

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Starting Alprina API Server${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo -e "${YELLOW}⚠️  WARNING: DATABASE_URL not set${NC}"
    echo -e "${YELLOW}   Some endpoints will not work without a database${NC}"
    echo -e "${YELLOW}   Set it with: export DATABASE_URL='postgresql://...'${NC}\n"
else
    echo -e "${GREEN}✅ DATABASE_URL is configured${NC}\n"
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
# Prefer .venv over venv (newer Python version)
if [ -d ".venv" ]; then
    echo -e "${GREEN}✅ Activating virtual environment (.venv)...${NC}"
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo -e "${GREEN}✅ Activating virtual environment (venv)...${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠️  No virtual environment found${NC}"
    echo -e "${YELLOW}   Using system Python${NC}"
fi

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo -e "${YELLOW}⚠️  uvicorn not found, installing...${NC}"
    pip install uvicorn fastapi --quiet
fi

# Set Python path to include src directory
export PYTHONPATH="${SCRIPT_DIR}/src:${PYTHONPATH}"

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🚀 Starting API server on http://localhost:8000${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${BLUE}📋 Available endpoints:${NC}"
echo -e "   • Health check:    ${GREEN}http://localhost:8000/health${NC}"
echo -e "   • API docs:        ${GREEN}http://localhost:8000/docs${NC}"
echo -e "   • OpenAPI spec:    ${GREEN}http://localhost:8000/openapi.json${NC}\n"

echo -e "${YELLOW}Press CTRL+C to stop the server${NC}\n"

# Run uvicorn with proper module path
cd src

# Use the venv python explicitly (prefer .venv)
if [ -d "../.venv" ]; then
    ../.venv/bin/python -m uvicorn alprina_cli.api.main:app --reload --host 0.0.0.0 --port 8000
elif [ -d "../venv" ]; then
    ../venv/bin/python -m uvicorn alprina_cli.api.main:app --reload --host 0.0.0.0 --port 8000
else
    python -m uvicorn alprina_cli.api.main:app --reload --host 0.0.0.0 --port 8000
fi
