#!/bin/bash
set -e

# Alprina CLI Installation Script
# Usage: curl -fsSL https://api.alprina.com/install.sh | sh

BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${CYAN}${BOLD}"
echo "╔═══════════════════════════════════════╗"
echo "║     Alprina CLI Installation          ║"
echo "║   AI-Powered Security for Developers  ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

# Check if Python 3.10+ is installed
echo -e "${BOLD}Checking system requirements...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed.${NC}"
    echo ""
    echo "Please install Python 3.10 or higher:"
    echo "  • macOS: brew install python@3.10"
    echo "  • Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  • Fedora/RHEL: sudo dnf install python3 python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo -e "${RED}❌ Python 3.10+ is required (found Python $PYTHON_VERSION)${NC}"
    echo ""
    echo "Please upgrade Python:"
    echo "  • macOS: brew install python@3.10"
    echo "  • Ubuntu/Debian: sudo apt install python3.10"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Check if pipx is installed, if not install it
if ! command -v pipx &> /dev/null; then
    echo -e "${YELLOW}⚠ pipx not found. Installing pipx...${NC}"
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath

    # Add pipx to PATH for current session
    export PATH="$HOME/.local/bin:$PATH"

    if ! command -v pipx &> /dev/null; then
        echo -e "${RED}❌ Failed to install pipx${NC}"
        echo ""
        echo "Please install pipx manually:"
        echo "  python3 -m pip install --user pipx"
        echo "  python3 -m pipx ensurepath"
        exit 1
    fi

    echo -e "${GREEN}✓ pipx installed${NC}"
    echo -e "${YELLOW}⚠ Please restart your terminal or run: source ~/.bashrc (or ~/.zshrc)${NC}"
else
    echo -e "${GREEN}✓ pipx found${NC}"
fi

# Install/Upgrade Alprina CLI
echo ""
echo -e "${BOLD}Installing Alprina CLI...${NC}"

if pipx list | grep -q "alprina-cli"; then
    echo "Upgrading existing installation..."
    pipx upgrade alprina-cli
else
    echo "Installing Alprina CLI..."
    pipx install alprina-cli
fi

echo ""
echo -e "${GREEN}${BOLD}✓ Alprina CLI installed successfully!${NC}"
echo ""
echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}${BOLD}         Getting Started with Alprina      ${NC}"
echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BOLD}Step 1: Sign up & Subscribe${NC}"
echo -e "  Visit: ${CYAN}https://www.alprina.com/pricing${NC}"
echo -e "  Plans: Developer (\$39/mo), Pro (\$49/mo), Team (\$99/mo)"
echo -e "  💰 Save 2 months with annual billing!"
echo ""
echo -e "${BOLD}Step 2: Authenticate${NC}"
echo -e "  Run: ${GREEN}alprina auth login${NC}"
echo -e "  This will open your browser to authorize the CLI"
echo ""
echo -e "${BOLD}Step 3: Start Scanning${NC}"
echo -e "  Run: ${GREEN}alprina scan${NC}"
echo -e "  Start securing your code with AI-powered analysis"
echo ""
echo -e "${YELLOW}${BOLD}⚠ Important:${NC} ${YELLOW}You need an active subscription to use Alprina CLI${NC}"
echo -e "${YELLOW}  Visit https://www.alprina.com/pricing to get started${NC}"
echo ""
echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${CYAN}Need help? Visit https://docs.alprina.com${NC}"
echo -e "${CYAN}Questions? Join our Discord: https://discord.gg/alprina${NC}"
echo ""

# Try to show version (might need PATH refresh)
if command -v alprina &> /dev/null; then
    VERSION=$(alprina --version 2>/dev/null | grep -oP 'version \K[0-9.]+' || echo "unknown")
    echo -e "${GREEN}Installed version: ${BOLD}$VERSION${NC}"
else
    echo -e "${YELLOW}⚠ Please restart your terminal to use 'alprina' command${NC}"
fi
