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

Auth: Vertex AI + Application Default Credentials (ADC) — same as Cline Plan Mode.
  No API key needed. Requires active ADC:
    gcloud auth application-default login --no-browser
    gcloud auth application-default set-quota-project gdc-das-life-2026
  Project: gdc-das-life-2026 | Location: global | Model: gemini-3.5-flash

Registration in Cline MCP settings:
  {
    "mcpServers": {
      "gdc-second-opinion": {
        "command": "python3",
        "args": ["/home/brian/gdc-pm/mcp/second_opinion_server.py"],
        "disabled": false,
        "autoApprove": ["gemini_second_opinion", "gemini_search"]
      }
    }
  }

  Note: No env vars needed — uses ADC from the shell that launched VS Code.
  If calls fail with auth errors: gcloud auth application-default login --no-browser
"""

import os
import sys
import json
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

# ── Config ────────────────────────────────────────────────────────────────────
# Auth: Vertex AI + ADC (same path as Cline) — project gdc-das-life-2026
# No API key needed. Requires: gcloud auth application-default login
VERTEX_PROJECT = "gdc-das-life-2026"
VERTEX_LOCATION = "global"
GEMINI_MODEL = "gemini-3.5-flash"   # upgraded Session AV — faster + better than 2.5-flash

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
    try:
        from google import genai
        from google.genai import types as gtypes
    except ImportError:
        return [types.TextContent(
            type="text",
            text="ERROR: google-genai not installed. Run: pip install --break-system-packages google-genai"
        )]

    client = genai.Client(vertexai=True, project=VERTEX_PROJECT, location=VERTEX_LOCATION)

    if name == "gemini_second_opinion":
        user_text = arguments.get("claim_or_plan", "")
        prompt = f"{HOSTILE_PERSONA}\n\n===CLAIM/SCENARIO TO RED-TEAM===\n{user_text}"
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=gtypes.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=8192,  # thinking model needs headroom
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
                max_output_tokens=4096,  # thinking model needs headroom
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
