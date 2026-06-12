#!/bin/bash
# Disable MCP gdc-second-opinion (Vertex AI Gemini) — stops billing immediately
# Usage: ./scripts/mcp-disable.sh
# Re-enable: ./scripts/mcp-enable.sh (then restart Cline MCP connection)

set -euo pipefail

MCP_SETTINGS="$HOME/.vscode-server/data/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"

# Kill running server process if active
if pkill -f second_opinion_server.py 2>/dev/null; then
    echo "✓ second_opinion_server.py process stopped"
else
    echo "  second_opinion_server.py was not running"
fi

# Set disabled=true in Cline MCP settings
if [ -f "$MCP_SETTINGS" ]; then
    jq '.mcpServers["gdc-second-opinion"].disabled = true' "$MCP_SETTINGS" > /tmp/mcp_tmp.json \
        && mv /tmp/mcp_tmp.json "$MCP_SETTINGS"
    echo "✓ MCP gdc-second-opinion DISABLED in Cline settings"
else
    echo "ERROR: $MCP_SETTINGS not found — check path"
    exit 1
fi

echo ""
echo "⛔ Vertex AI / Gemini billing stopped. gemini_search and gemini_second_opinion"
echo "   will not respond until you run ./scripts/mcp-enable.sh"
