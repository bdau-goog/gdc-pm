#!/usr/bin/env python3
"""
GDC-PM MCP Server — second_opinion tool + web_search stub

Exposes two tools to Cline:
  1. gemini_second_opinion(claim_or_plan) — runs the hostile-engineer red-team persona
     against a claim or scenario description using the Gemini API.
  2. gemini_search(query) — uses Gemini's grounding/search capability to fetch
     a cited answer to a factual question (API RP numbers, SPE references, etc.)

Setup (run once before starting the server):
  pip install --break-system-packages mcp google-genai

API key:
  Set GEMINI_API_KEY in ~/gdc-pm/.env BEFORE sourcing it:
    echo "GEMINI_API_KEY=your-key-here" >> ~/gdc-pm/.env
  The .env file is gitignored. The key never enters git or this chat.

Registration in Cline MCP settings (~/Library/Application Support/Code/User/globalStorage/
saoudrizwan.claude-dev/settings/cline_mcp_settings.json):

  {
    "mcpServers": {
      "gdc-second-opinion": {
        "command": "python3",
        "args": ["/home/brian/gdc-pm/mcp/second_opinion_server.py"],
        "env": {
          "GEMINI_API_KEY": "${GEMINI_API_KEY}"
        },
        "disabled": false,
        "autoApprove": ["gemini_second_opinion", "gemini_search"]
      }
    }
  }

  Note: Cline will inherit the env var from the shell that launched VS Code.
  Run `source ~/gdc-pm/.env` in the terminal that opens VS Code to ensure
  GEMINI_API_KEY is available to subprocesses.
"""

import os
import sys
import json
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

# ── Config ────────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"   # fast + grounding-capable; swap to 2.5-pro for deeper red-team

# ── MCP server setup ──────────────────────────────────────────────────────────
server = Server("gdc-second-opinion")


# ── Tool: gemini_second_opinion ───────────────────────────────────────────────
HOSTILE_PERSONA = """\
You are a 20-year production and ESP reliability engineer. You have personally run GE
SmartSignal, AVEVA PRiSM, and Aspen Mtell on ESP fleets in the Permian Basin. Your job
is to RED-TEAM the claim or scenario description below. Be blunt. Do not agree with
anything you cannot independently verify.

For each claim or scenario element:
1. Write the one-sentence hostile attack first.
2. Then assess: SURVIVES / SURVIVES-IF-REWORDED / FAILS
3. Give a one-line reason and cite a standard or failure mode if you know one.

End with: "WEAKEST LINK: [the sentence most likely to get the demo dismantled in 5 minutes]"
and "TOP 3 FIXES: [ordered list of the highest-leverage changes]."

Do not pad. Be the engineer who walks out if the physics is wrong.
"""

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="gemini_second_opinion",
            description=(
                "Run a hostile-engineer red-team on a claim, scenario, or narrative "
                "using Gemini. Returns SURVIVES/REWORD/FAILS verdicts per claim, "
                "a weakest-link identification, and top-3 fixes. "
                "Use before writing any wireframe or Claim Ledger row."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "claim_or_plan": {
                        "type": "string",
                        "description": "The claim, scenario description, or narrative to red-team. "
                                       "Include the full physics, cost figures, and value proposition."
                    }
                },
                "required": ["claim_or_plan"]
            }
        ),
        types.Tool(
            name="gemini_search",
            description=(
                "Ask Gemini a factual question with web grounding — returns a cited answer. "
                "Use for: API RP / SPE / IEC references, current rig rates, ESP gauge specs, "
                "APM platform capabilities, or any domain fact needed for the Claim Ledger."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The factual question to answer with citations."
                    }
                },
                "required": ["query"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if not GEMINI_API_KEY:
        return [types.TextContent(
            type="text",
            text="ERROR: GEMINI_API_KEY is not set. Add it to ~/gdc-pm/.env and restart VS Code."
        )]

    try:
        from google import genai
        from google.genai import types as gtypes
    except ImportError:
        return [types.TextContent(
            type="text",
            text="ERROR: google-genai not installed. Run: pip install --break-system-packages google-genai"
        )]

    client = genai.Client(api_key=GEMINI_API_KEY)

    if name == "gemini_second_opinion":
        user_text = arguments.get("claim_or_plan", "")
        prompt = f"{HOSTILE_PERSONA}\n\n===CLAIM/SCENARIO TO RED-TEAM===\n{user_text}"
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=gtypes.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=2048,
            )
        )
        return [types.TextContent(type="text", text=response.text)]

    elif name == "gemini_search":
        query = arguments.get("query", "")
        # Use grounding with Google Search for factual queries
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=f"Answer this factual question with citations (standards, papers, or OEM docs): {query}",
            config=gtypes.GenerateContentConfig(
                tools=[gtypes.Tool(google_search=gtypes.GoogleSearch())],
                temperature=0.1,
                max_output_tokens=1024,
            )
        )
        # Extract grounding metadata if available
        result = response.text
        if hasattr(response, 'candidates') and response.candidates:
            cand = response.candidates[0]
            if hasattr(cand, 'grounding_metadata') and cand.grounding_metadata:
                meta = cand.grounding_metadata
                if hasattr(meta, 'grounding_chunks') and meta.grounding_chunks:
                    sources = [
                        f"- {c.web.title} ({c.web.uri})"
                        for c in meta.grounding_chunks
                        if hasattr(c, 'web') and c.web
                    ]
                    if sources:
                        result += "\n\nSources:\n" + "\n".join(sources)
        return [types.TextContent(type="text", text=result)]

    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


# ── Entry point ───────────────────────────────────────────────────────────────
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
