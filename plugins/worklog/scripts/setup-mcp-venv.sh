#!/bin/bash
# setup-mcp-venv.sh - Set up Python venv for worklog MCP server
#
# Usage: ./setup-mcp-venv.sh [--venv-path PATH]
#
# This script:
# 1. Detects suitable Python using detect-python-env.sh
# 2. Creates a venv at the specified path (or default location)
# 3. Installs MCP dependencies
# 4. Outputs the Python path for .mcp.json configuration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"
MCP_DIR="$PLUGIN_DIR/mcp"

# Default venv location
DEFAULT_VENV_PATH="$MCP_DIR/.venv"

# Parse arguments
VENV_PATH="$DEFAULT_VENV_PATH"
while [[ $# -gt 0 ]]; do
    case $1 in
        --venv-path)
            VENV_PATH="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--venv-path PATH]"
            echo ""
            echo "Options:"
            echo "  --venv-path PATH  Path for the virtual environment"
            echo "                    Default: $DEFAULT_VENV_PATH"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Worklog MCP Server Setup${NC}"
echo "=========================="
echo ""

# Source the detection script
source "$SCRIPT_DIR/detect-python-env.sh"

if [[ "$PYTHON_OK" != "yes" ]]; then
    echo -e "${RED}Error: No suitable Python found${NC}"
    echo ""
    echo "Please install Python 3.10+ first:"
    echo "  $PYTHON_RECOMMENDATION"
    exit 1
fi

echo -e "${GREEN}Using Python:${NC} $PYTHON_CMD ($PYTHON_VERSION via $PYTHON_SOURCE)"
echo ""

# Create venv
echo -e "${BLUE}Creating virtual environment...${NC}"
if [[ -d "$VENV_PATH" ]]; then
    echo -e "${YELLOW}Warning: venv already exists at $VENV_PATH${NC}"
    read -p "Remove and recreate? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$VENV_PATH"
    else
        echo "Using existing venv"
    fi
fi

if [[ ! -d "$VENV_PATH" ]]; then
    "$PYTHON_CMD" -m venv "$VENV_PATH"
    echo -e "${GREEN}Created venv at: $VENV_PATH${NC}"
fi

# Activate and install dependencies
echo ""
echo -e "${BLUE}Installing dependencies...${NC}"
source "$VENV_PATH/bin/activate"

# Upgrade pip first
pip install --upgrade pip --quiet

# Install MCP server dependencies
if [[ -f "$MCP_DIR/pyproject.toml" ]]; then
    pip install -e "$MCP_DIR" --quiet
elif [[ -f "$MCP_DIR/requirements.txt" ]]; then
    pip install -r "$MCP_DIR/requirements.txt" --quiet
else
    # Fallback: install known dependencies
    pip install fastmcp aiosqlite --quiet
fi

echo -e "${GREEN}Dependencies installed${NC}"

# Deactivate
deactivate

# Output configuration
VENV_PYTHON="$VENV_PATH/bin/python"

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "Virtual environment: $VENV_PATH"
echo "Python executable:   $VENV_PYTHON"
echo ""
echo -e "${BLUE}For .mcp.json configuration, use:${NC}"
echo "{"
echo "  \"mcpServers\": {"
echo "    \"worklog\": {"
echo "      \"type\": \"stdio\","
echo "      \"command\": \"$VENV_PYTHON\","
echo "      \"args\": [\"-m\", \"worklog_mcp\"],"
echo "      \"env\": {"
echo "        \"WORKLOG_DB\": \"/path/to/worklog.db\""
echo "      }"
echo "    }"
echo "  }"
echo "}"
echo ""

# Write out the path for other scripts to use
echo "$VENV_PYTHON" > "$MCP_DIR/.python-path"
echo -e "${GREEN}Python path saved to: $MCP_DIR/.python-path${NC}"
