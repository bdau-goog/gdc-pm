#!/bin/bash
# GDC-PM MCP server launcher — sources .env so GEMINI_API_KEY is available
# without the key ever appearing in cline_mcp_settings.json or git.
#
# The key lives ONLY in ~/gdc-pm/.env (gitignored):
#   echo "GEMINI_API_KEY=your-key-here" >> ~/gdc-pm/.env
#
# This script is what Cline registers as the MCP server command.

set -e

ENV_FILE="$(dirname "$0")/../.env"
if [ -f "$ENV_FILE" ]; then
    # shellcheck disable=SC1090
    set -a
    source "$ENV_FILE"
    set +a
fi

exec python3 "$(dirname "$0")/second_opinion_server.py"
