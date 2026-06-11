# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 11, 2026 (Session AV — H2 synthetic documents approved, DEMO_MASTER §5 physics fix)
**git head:** `dea71be` (docs(session-av): H2 synthetic docs approved + DEMO_MASTER physics fix + CLAIM_LEDGER H2-P1/D1/D2)
**fault-trigger-ui image:** `sha256:2fd95932...` (unchanged — no app code deployed this session)
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

## STEP 2: MCP Server (verify before use)

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

---

## STEP 3: Session AV Completed — What Was Done

| Item | Status |
|---|---|
| All 5 H2 synthetic documents drafted, G1–G6 gated, Gemini red-teamed | ✅ DONE |
| `docs/H2_SYNTHETIC_DOCS.md` — full approved spec (Gemma templates + Python date anchors) | ✅ DONE |
| DEMO_MASTER §5 physics fix — bearing wear IS real (APM right symptom, wrong root cause) | ✅ DONE |
| CLAIM_LEDGER H2-P1 updated + H2-D1 + H2-D2 rows added | ✅ DONE |
| Date-templating architecture approved for ALL H1/H2/H3 static seeds | ✅ DONE |
| Commit `dea71be` on `feature-trio-clean` | ✅ DONE |

**Key finding this session:** The H2 physics was corrected — APM CORRECTLY identifies bearing wear (amps elevated, vibration rising), but cannot determine WHY (root cause = incompatible workover fluid → seal degradation → well fluid ingress → bearing contamination). This makes the APM moat claim STRONGER: not "APM misidentifies the symptom" but "APM gets the symptom right and recommends the wrong, expensive fix." All 4 Scenario Survival Tests still pass.

---

## STEP 4: Next Implementation Task

**All 5 H2 documents approved. Gate is cleared. BUILD H2 backend + UI.**

### PRIORITY 1: H2 Backend Endpoint (`GET /api/h2/scenario-replay`)

Per DEMO_MASTER §5 Screen Architecture and docs/H2_SYNTHETIC_DOCS.md:

**Python date anchor setup** (add to app.py startup, near existing H2 seeding logic):
```python
from datetime import datetime, timedelta
SCENARIO_DATE   = datetime.now()
WORKOVER_DATE   = SCENARIO_DATE - timedelta(weeks=8)
PRIOR_PULL_DATE = WORKOVER_DATE - timedelta(weeks=78)
def _fmt_date(dt): return dt.strftime("%B %d, %Y")
```

**Static seed docs at startup** (seed to field_intel using above anchors):
- Doc 2: OEM matrix — seed once, no dates
- Doc 3: Prior pull record — Python f-string with PRIOR_PULL_DATE
- Doc 5: Well history — Python f-string with 7 algorithmically-distributed SCADA events

**Per-run dynamic generation** (in endpoint handler):
- Doc 1: Call Gemma with workover completion report template + randomized params
- Doc 4: Call Gemma with tour note template + randomized params
- Return both in `doc_reveals[]` payload

**Endpoint returns:**
```json
{
  "efficiency": [...],    // motor efficiency %, declining over N steps
  "vib": [...],           // vibration mm/s, rising over N steps
  "t_min": [...],         // time axis in weeks post-workover
  "health_score": [...],  // esp_health.ubj output per window
  "gdc_detect_idx": N,    // first index where health_score < 0.65
  "scada_alarm_idx": N,   // index where vib or amps crosses SCADA threshold
  "gdc_verdict": "...",   // Gemma-generated verdict string
  "doc_reveals": [...]    // 5 document objects, staggered timing
}
```

**SCADA alarm rule for H2:** vibration threshold cross (amps elevated is secondary). SCADA sees "mechanical degradation" but no root cause.

### PRIORITY 2: H2 Briefing UI (3 panels, per §4.5 Briefing Pattern Spec)

Per constraint: **wireframe → sign-off → HTML**. Do not write HTML without sign-off.

- Panel 1: The Equipment (ESP + 4-sensor string callout + workover event 8 weeks ago)
- Panel 2: The Provenance Hook (timeline: workover → symptom onset → alarm today; 4 sensor tiles; doc stack preview)
- Panel 3: The Decision (GDC verdict card; action cards flush+reseal vs pump-pull; universal pattern close; CTA ▶ Run the Scenario)

### PRIORITY 3: H2 Scenario Replay UI

Same mechanics as H1. Dual-sensor Plotly chart (motor efficiency declining + vibration rising). SCADA View / GDC Advisor View. Sequential doc reveals (5 docs, staggered timing).

### PRIORITY 4 (if time): H1 Batch B remediation

Apply Python date-templating to H1 static seed documents (sonic log, shift note, GOR lab report). Also fix remaining G1/G2/G3 issues on those documents (see DEMO_MASTER §8).

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Briefing — all 6 panels | ✅ COMPLETE Session AQ | Deployed |
| H1 Scenario replay | ✅ WORKING | Deployed |
| H2 Briefing panels | ❌ NOT BUILT | Documents approved Session AV. Backend endpoint + UI = next task. |
| H2 Scenario replay | ❌ NOT BUILT | After briefing panels |
| H3 copy — Vizier framing | ⚠️ NEEDS COPY FIX | H3 tab may still say "no cloud dependency" — Priority 4 |
| H1 static seed date-templating | ⚠️ NEEDS FIX | Sonic log, shift note, GOR lab have hardcoded dates. Batch B remediation. |
| MCP gdc-second-opinion | ✅ WORKING | ~/mcp/, gemini-2.5-flash, gdc-pm-v2, timeout=120000 |
| DEMO_MASTER §5 | ✅ UPDATED Session AV | APM right symptom, wrong root cause (physics corrected) |
| docs/H2_SYNTHETIC_DOCS.md | ✅ CREATED Session AV | All 5 docs approved, G1-G6 pass, Gemini SURVIVES |
| CLAIM_LEDGER H2 rows | ✅ UPDATED Session AV | H2-P1 physics fix + H2-D1 + H2-D2 added |
| H2-C1 flush+reseal ~$8k–$15k | ⚠️ 🔴 NEEDS-EXPERT | No hard public figure. Display as soft range only. |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — do NOT use `browser_action`
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,400 lines · `index.html` ~3,200 lines · `app.js` ~2,300 lines — grep first, read targeted sections only
- **Wireframes → sign-off → HTML** (never write HTML without sign-off)
- **No H2 HTML until wireframe approved** (documents are approved; wireframe still needed)
- **No build/push/deploy without user walkthrough and verification**
- Gemini tools (gemini_search, gemini_second_opinion) on autoApprove — use freely for fact-checking
- **Ask inline questions — no option lists** (ask_followup_question options array causes display issues)
- **Keep text before tool calls short** — large text blocks between tool calls may not render in VS Code interface
