# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 11, 2026 (Session AS)
**git head:** `62741f6` (last commit — MCP + docs; no app code this session)
**fault-trigger-ui image:** `sha256:2fd95932...` (unchanged)
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

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: MCP Server Status (verify before use)

MCP server lives at `~/mcp/` (cross-project, outside all git repos).

**Quick verify:**
```bash
python3 -c "
from google import genai
from google.genai import types as gtypes
client = genai.Client(vertexai=True, project='gdc-pm-v2', location='us-central1')
r = client.models.generate_content(model='gemini-2.5-flash', contents='Reply: OK',
    config=gtypes.GenerateContentConfig(max_output_tokens=8192))
print(r.text)
"
```

**If "Reauthentication needed":**
```bash
gcloud auth application-default login --no-browser
gcloud auth application-default set-quota-project gdc-pm-v2
# Then: Ctrl+Shift+P → Developer: Reload Window
```

**MCP config:** `~/mcp/second_opinion_server.py` · `~/mcp/start.sh` · Cline settings: `timeout: 120000`
**Model:** `gemini-2.5-flash` · **Project:** `gdc-pm-v2` · **Full responses:** `/tmp/mcp-results/`

---

## STEP 4: NEXT SESSION — H2 Scenario

### Strategic finding (Session AS)
We over-conceded L2 in prior sessions. The full GDC value is the **sovereign AI stack (L1+L2+L3)**, not L3 alone:
- L2 (ML models trained on YOUR fleet data, running locally) is genuinely better than cloud APM for sovereignty-constrained operators
- L3 (Gemma + pgvector RAG document fusion) is the new categorical moat
- Trying to prove L3 alone carries the moat → weak scenarios (slug flow, frac hit all failed T1)

### H2 candidate: Maintenance-provenance (wrong-fluid fill / non-spec workover)
- Asset: ESP in a Permian well
- Event: During workover, pump was filled with an incompatible fluid (documented only in the workover completion report)
- Sensor: Vibration increasing + efficiency dropping → APM routes to "bearing wear → pull pump ($80k)"
- GDC: Reads workover completion report + OEM fluid compatibility matrix → reclassifies as elastomer degradation from wrong fill → correct action: acid wash + correct fluid refill ($8k)
- Cross-industry: wrong lube (manufacturing), wrong coolant (power), wrong hydraulic fluid (aviation MRO) — same structure

**4 survival tests (to run next session):**
1. Discrete event: ✅ Wrong fluid fill during specific workover
2. Categorically off-sensor: ✅ Fill record is in workover completion report only
3. APM mis-routes: Likely ✅ (bearing wear and elastomer degradation produce similar vibration/efficiency patterns)
4. Common and material: Likely ✅ (51% of ESP failures = human factors per 2014 SPE AI Conf survey; SPE 185275-MS, 194398-MS, 144562-MS)

**Next session sequence (DO NOT SKIP):**
1. Run 4 survival tests explicitly (in-persona + `gemini_second_opinion` MCP call)
2. Read full file from `/tmp/mcp-results/` for complete response
3. If SURVIVES: write H2 spec + Claim Ledger rows
4. User approval → Act mode → build

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Briefing — all 6 panels | ✅ COMPLETE Session AQ | Deployed |
| H2 Briefing panels | ❌ INVALIDATED Session AR / AS | Frac-hit scenario FAILS T1. New candidate: maintenance-provenance. Pending survival tests. |
| H3 Briefing panels | ⚠️ QUEUED SPRINT 4 | Not started |
| MCP gdc-second-opinion | ✅ WORKING Session AS | ~/mcp/, gemini-2.5-flash, gdc-pm-v2, timeout=120000, file-save |
| Vib units (H2 + H1) | ⚠️ INTEGRITY FINDING | Downhole ESP: g (0–5 g), not mm/s. Fix when rebuilding H2. |
| ISA-18.2 alarm framing | ⚠️ INTEGRITY FINDING | Governs alarm management, NOT trip levels. Say "OEM limits, rationalized per ISA-18.2". |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,400 lines · `index.html` ~3,200 lines · `app.js` ~2,300 lines — grep first
- **Wireframes → sign-off → HTML** (never write HTML without sign-off)
- **Scenario gate: 4 survival tests must pass before any wireframe or code**
- H2 uses inference-api (not local esp_classifier.bst)
