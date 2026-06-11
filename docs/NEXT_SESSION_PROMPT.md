# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 11, 2026 (Session AR — H2 scenario invalidated, docs-only session, MCP setup queued)
**git head:** to be set after commit
**fault-trigger-ui image:** `sha256:2fd95932a9b8ae9ca0eb6c961cf9a031b264a97ad69705fb8197a05999414a9a` (unchanged — no code deployed this session)
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected:** 8 pods 1/1 · ollama_online: True · gemma4:latest · field_intel: 5-6 · rag_docs: 18

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY — especially §5 H2 INVALIDATED notice + §3 L1/L2/L3 stack)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: NEXT SESSION — Two Bounded Tasks (in order)

### Task 1 — Stand up web-search + Gemini second-opinion MCP server (~15 min)
The MCP server closes the in-session citation gap that caused H2 to drift undetected.
- Tool: `web_search` (Brave Search API — free tier) + `gemini_second_opinion` (Gemini API — free tier user has)
- Both in one MCP server. User to have **Gemini API key** (Google AI Studio) ready.
- Brave Search key optional; Gemini-only is acceptable for the red-team function.
- After: verify both tools return results in-session.

### Task 2 — Lock the new H2 scenario (frac-hit / offset-well interference)
Sequence — DO NOT SKIP or COMBINE steps:
1. **Hostile-engineer red-team** (in-persona, me, via MCP) on the frac-hit candidate. 4 survival-test pass/fail written out explicitly.
2. If SURVIVES: write full H2 scenario spec (asset, trigger, docs, action, $ contrast) + CLAIM_LEDGER rows.
3. Confirm H1/H2 doc-overlap differentiation (H1 uses offset-frac report as a corroborating doc; H2 makes the frac event the CAUSE — must be clearly distinct on screen).
4. User approves spec, then Act mode to build.

**Do NOT write any H2 wireframe or HTML until Steps 1–3 are done and approved.**

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Briefing — all 6 panels | ✅ COMPLETE Session AQ | Deployed |
| H2 Briefing panels | ❌ INVALIDATED Session AR | Slug-flow scenario fails H2-9/H2-10/H2-11/H2-12. New scenario (frac-hit) must be validated before build. |
| H3 Briefing panels | ⚠️ QUEUED SPRINT 4 | Not started. H3 is sovereign-edge-optimization story, NOT L3 context-fusion — do not market as the moat. |
| H2 scenario — slug flow | ❌ INVALIDATED | Telemetric signature; APM reads it; false-dichotomy cost; documents don't carry load |
| H2 scenario — frac-hit | ⚠️ CANDIDATE | Passes 4 survival-test criteria structurally; pending dual-AI validation via MCP |
| Vib units (H2 + H1) | ⚠️ INTEGRITY FINDING | Downhole ESP gauges report in **g** (0–5 g), not mm/s (surface ISO-10816 convention). H1 shows "0.41 in/s". Fix when rebuilding H2 scenario. |
| ISA-18.2 alarm level framing | ⚠️ INTEGRITY FINDING | Standard governs alarm management/rationalization, NOT trip levels. Say "OEM limits, rationalized per ISA-18.2". |
| 90% classifier confidence display | ⚠️ INTEGRITY FINDING | Single softmax number = overfit theater to this audience. Replace with evidence-chain + citation in new H2 build. |
| H3 Class H temp label | ✅ FIXED Session AE (app) / FIXED Session AR (DEMO_MASTER §6) | 280°F is derated operating setpoint, not Class H limit (Class H = 356°F / 180°C per IEC 60085) |
| DEMO_MASTER.md | ✅ UPDATED Session AR | §5 H2 invalidated + 4 survival tests; §6 temp label fixed; Scenario Gate + In-Session Red-Team rules added |
| RED_TEAM_LEDGER.md | ✅ UPDATED Session AR | H2-9..12 + H2-C1..C3 added; process finding recorded |
| .clinerules | ✅ UPDATED Session AR | Scenario Validation Gate + In-Session Red-Team Discipline sections added |
| Video Script | ⚠️ SPRINT 5 | docs/VIDEO_SCRIPT.md does not exist |
| web-search + Gemini MCP | ⚠️ TASK 1 NEXT SESSION | Not set up. Closes in-session citation + dual-model cross-check gap. |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — do NOT use `browser_action`
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,400 lines · `index.html` ~3,200 lines · `app.js` ~2,300 lines — grep first, read targeted sections only
- **Wireframes → sign-off → HTML** (never write HTML without sign-off)
- **Scenario gate: 4 survival tests must pass before any wireframe or code**
- **In-session red-team (hostile-engineer persona) mandatory before any new claim ships**
- H2 uses inference-api (not local esp_classifier.bst)
