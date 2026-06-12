#!/bin/bash
# Enable MCP gdc-second-opinion (Vertex AI Gemini) — resumes billing
# Usage: ./scripts/mcp-enable.sh
# After running: restart Cline's MCP connection (MCP icon in Cline sidebar → reconnect)
# Disable again: ./scripts/mcp-disable.sh
#
# ⚠️  WARNING: Vertex AI charges apply immediately on enable.
#     gemma-2.5-flash calls with Search grounding = ~$0.10–$0.30 per call.
#     Use sparingly. Disable immediately when done.

set -euo pipefail

MCP_SETTINGS="$HOME/.vscode-server/data/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"

if [ -f "$MCP_SETTINGS" ]; then
    jq '.mcpServers["gdc-second-opinion"].disabled = false' "$MCP_SETTINGS" > /tmp/mcp_tmp.json \
        && mv /tmp/mcp_tmp.json "$MCP_SETTINGS"
    echo "✅ MCP gdc-second-opinion ENABLED in Cline settings"
else
    echo "ERROR: $MCP_SETTINGS not found — check path"
    exit 1
fi

echo ""
echo "⚠️  Vertex AI billing is now ACTIVE."
echo "   → In Cline sidebar: click MCP icon → gdc-second-opinion → Reconnect"
echo "   → Run ./scripts/mcp-disable.sh when finished to stop billing"
