# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 11, 2026 (Session AW — GPU discipline + H2 backend endpoint written)
**git head:** `b61d6f7` (feat(h2-backend): H2 scenario-replay endpoint — maintenance-provenance scenario, date anchors, static seed, Gemma fallback templates)
**fault-trigger-ui image:** `sha256:2fd95932...` (NOT YET DEPLOYED — code committed, build+push+deploy pending)
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected (dev default — GPU OFF):**
- 7 pods 1/1 Running + 3 prune CronJob Completed
- ollama deployment: **replicas=0** (pod absent — this is CORRECT and expected during dev)
- `ollama_online: False` — **this is NOT a problem**. Do NOT scale ollama up unless explicitly testing LLM output.
- field_intel: 5–6 · rag_docs: 18

**GPU discipline rule:** ollama is OFF by default. Scale up ONLY at an explicit LLM-test step:
  `./scripts/gpu-start.sh`   ← start (10–15 min, ~$0.65/hr begins)
  `./scripts/gpu-stop.sh`    ← stop immediately after test (billing stops ~10 min later)
The wrap-session checklist must confirm ollama is at 0 before closing.

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

## STEP 3: Session AW Completed — What Was Done

| Item | Status |
|---|---|
| GPU discipline: ollama scaled to 0, .clinerules + NEXT_SESSION_PROMPT updated | ✅ DONE — commit `3e4d5d7` |
| H2 backend endpoint `GET /api/h2/scenario-replay` — full implementation | ✅ COMMITTED `b61d6f7` — NOT YET DEPLOYED |
| H2 date anchors (`_H2_SCENARIO_DATE`, `_H2_WORKOVER_DATE`, `_H2_PRIOR_PULL_DATE`) at module level | ✅ in `b61d6f7` |
| H2 static doc helpers (`_build_h2_doc3`, `_build_h2_doc5`, `_H2_OEM_MATRIX_TEXT`) | ✅ in `b61d6f7` |
| `_seed_h2_static_docs_bg()` daemon thread (idempotent startup seed to field_intel) | ✅ in `b61d6f7` |
| N=80 steps / 8-week trajectory (efficiency↓ + vib↑ + amps elevated + temp slightly up) | ✅ in `b61d6f7` |
| `esp_health.ubj` sliding window health score + SCADA ISA-18.2 HI alarm (vib≥4.0 mm/s) | ✅ in `b61d6f7` |
| Gemma async doc generation (Doc 1 workover report + Doc 4 tour note) with fallback templates | ✅ in `b61d6f7` |
| Old slug-flow H2 stub (invalidated Session AR) fully replaced | ✅ in `b61d6f7` |

---

## STEP 4: Next Implementation Task

**H2 backend committed. Gate cleared. Next: deploy + smoke-test, then wireframe.**

### PRIORITY 1 (immediate): Deploy H2 backend endpoint

```bash
# From gdc-pm root:
docker build -t gcr.io/gdc-pm-v2/fault-trigger-ui:latest gke/fault-trigger-ui/
docker push gcr.io/gdc-pm-v2/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm

# Smoke-test (GPU down is correct — Gemma will use fallback template):
curl -s "http://gdc-pm.bdau.io/api/h2/scenario-replay" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print('scenario:', d.get('scenario'))
print('n:', d.get('n'))
print('doc_gen_mode:', d.get('doc_gen_mode'))
print('gdc_detect_idx:', d.get('gdc_detect_idx'))
print('scada_alarm_idx:', d.get('scada_alarm_idx'))
print('doc_reveals count:', len(d.get('doc_reveals',[])))
print('workover_vendor:', d.get('workover_vendor'))
print('health_ok:', d.get('health_ok'))
"
```

**Expected:** scenario=workover_fluid_incompatibility · n=80 · doc_gen_mode=FALLBACK_TEMPLATE (GPU down) · 5 doc_reveals · health_ok=True

### PRIORITY 2: H2 Briefing wireframe → sign-off → HTML (per §4.5 Briefing Pattern Spec)

Per hard constraint: **wireframe → sign-off → HTML**. No H2 HTML without user sign-off.

3 panels (from DEMO_MASTER §5):
- Panel 1: The Equipment (ESP + 4-sensor string callout + workover event 8 weeks ago)
- Panel 2: The Provenance Hook (timeline: workover → symptom onset → alarm today; 4 sensor tiles; doc stack preview)
- Panel 3: The Decision (GDC verdict card; action cards flush+reseal vs pump-pull; universal pattern close; CTA ▶ Run the Scenario)

### PRIORITY 3: H2 Scenario Replay UI

Same mechanics as H1. Dual-sensor Plotly chart (motor efficiency declining + vibration rising). SCADA View / GDC Advisor View. Sequential doc reveals (5 docs, staggered timing).

### PRIORITY 4 (if time): H1 Batch B date-templating remediation

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Briefing — all 6 panels | ✅ COMPLETE Session AQ | Deployed |
| H1 Scenario replay | ✅ WORKING | Deployed |
| H2 Briefing panels | ❌ NOT BUILT | Backend committed `b61d6f7`. Deploy + smoke-test → wireframe → sign-off → HTML. |
| H2 Scenario replay | ❌ NOT BUILT | After briefing panels |
| H2 backend endpoint | ⚠️ COMMITTED NOT DEPLOYED | `b61d6f7` — needs docker build+push+kubectl rollout |
| H3 copy — Vizier framing | ⚠️ NEEDS COPY FIX | H3 tab may still say "no cloud dependency" — Priority 4 |
| H1 static seed date-templating | ⚠️ NEEDS FIX | Sonic log, shift note, GOR lab have hardcoded dates. Batch B remediation. |
| MCP gdc-second-opinion | ✅ WORKING | gdc-pm/mcp/, gemini-3.5-flash, Vertex AI ADC, location=global, project=gdc-das-life-2026, max_output_tokens=8192 — upgraded Session AV |
| Ollama GPU pod | ✅ SCALED TO 0 | Session AW — GPU-discipline rule in effect. ollama_online=False is expected during dev. gpu-start.sh only at LLM-test steps. |
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
