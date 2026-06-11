# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 11, 2026 (Session AW — GPU discipline + H2 backend endpoint committed)
**git head:** `a1f60a0` (docs(session-aw): update NEXT_SESSION_PROMPT — H2 backend committed, deploy pending)
**fault-trigger-ui image:** `sha256:2fd95932...` (NOT DEPLOYED — code committed `b61d6f7`, build+push+deploy is PRIORITY 1)
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
- 6 pods 1/1 Running + 3 prune CronJob Completed (ollama pod ABSENT — correct)
- ollama replicas: **0** · `ollama_online: False` — NOT a problem. Do NOT scale up.
- field_intel: 5–6 · rag_docs: 18

**Actual at session-AW close:** 6 pods Running · ollama=0 · ollama_online=False · field_intel=6 · rag_docs=18 ✅

**GPU discipline rule:** OFF by default.
  `./scripts/gpu-start.sh`  ← start only at explicit LLM-test step (~$0.65/hr begins)
  `./scripts/gpu-stop.sh`   ← stop immediately after (always paired)

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat /home/brian/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Next Implementation Tasks (in order)

### PRIORITY 1 — Deploy H2 backend (code is committed, not yet live)

```bash
docker build -t gcr.io/gdc-pm-v2/fault-trigger-ui:latest gke/fault-trigger-ui/
docker push gcr.io/gdc-pm-v2/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm
```

**Smoke-test (GPU down → expect FALLBACK_TEMPLATE):**
```bash
curl -s "http://gdc-pm.bdau.io/api/h2/scenario-replay" | python3 -c "
import sys,json; d=json.load(sys.stdin)
print('scenario:', d.get('scenario'))
print('n:', d.get('n'))
print('doc_gen_mode:', d.get('doc_gen_mode'))
print('gdc_detect_idx:', d.get('gdc_detect_idx'))
print('scada_alarm_idx:', d.get('scada_alarm_idx'))
print('doc_reveals:', len(d.get('doc_reveals',[])))
print('health_ok:', d.get('health_ok'))
"
```
**Expected:** scenario=workover_fluid_incompatibility · n=80 · doc_gen_mode=FALLBACK_TEMPLATE · 5 doc_reveals · health_ok=True

### PRIORITY 2 — H2 Briefing wireframe → sign-off → HTML

3 panels per DEMO_MASTER §5 + §4.5 Briefing Pattern Spec:
- Panel 1: The Equipment (ESP + 4-sensor string + workover callout 8 weeks ago)
- Panel 2: The Provenance Hook (workover→onset→alarm timeline; 4 sensor tiles; doc stack preview)
- Panel 3: The Decision (GDC verdict; flush+reseal vs pump-pull cards; universal pattern close; ▶ Run the Scenario)

**Hard constraint: wireframe → sign-off → HTML. No HTML without approval.**

### PRIORITY 3 — H2 Scenario Replay UI

Same mechanics as H1. Dual-sensor Plotly (efficiency↓ amber + vib↑ purple). SCADA View / GDC Advisor View. 5 staggered doc reveals.

### PRIORITY 4 — H3 Briefing panels (3 panels, replace toggle info panel)

H3 currently has a toggle "ⓘ Physics & Logic" inline panel at index.html line 2011. This does NOT meet §4.5 spec. Needs a proper 3-panel briefing:
- Panel 1: The Opportunity (oil price spike + ESP fleet + VFD headroom)
- Panel 2: The Tradeoff (Hz vs temp vs RUL; why manual fails; safety constraint)
- Panel 3: The Optimization (Vizier GP Bandit; edge-cloud hybrid; CTA ▶ Run the Optimization)

**Same wireframe → sign-off → HTML gate applies.**

### PRIORITY 5 — H3 copy fix

H3 tab may still display "no cloud dependency" → must read "no public-cloud dependency for the decision" per DEMO_MASTER §6 locked language.

### PRIORITY 6 — H1 Batch B date-templating

Sonic log, shift note, GOR lab report in field_intel have hardcoded 2025 dates. Apply same Python date-anchor pattern as H2 static seeds.

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Briefing — all 6 panels | ✅ DEPLOYED | Session AQ |
| H1 Scenario replay | ✅ DEPLOYED | Session AP |
| H2 backend endpoint | ⚠️ COMMITTED NOT DEPLOYED | `b61d6f7` — PRIORITY 1 |
| H2 Briefing panels | ❌ NOT BUILT | After deploy + smoke-test |
| H2 Scenario replay UI | ❌ NOT BUILT | After briefing panels |
| H3 Briefing panels | ❌ NOT BUILT | Toggle info panel exists (line 2011) but doesn't meet §4.5 spec |
| H3 copy — "no cloud dependency" | ⚠️ NEEDS FIX | 1–2 lines in index.html |
| H1 static seed date-templating | ⚠️ NEEDS FIX | Hardcoded 2025 dates (Batch B) |
| Ollama GPU pod | ✅ AT 0 | GPU-discipline rule in effect. False is correct. |
| MCP gdc-second-opinion | ✅ WORKING | gemini-2.5-flash, Vertex AI ADC, gdc-pm-v2 |
| H2-C1 flush+reseal ~$8k–$15k | ⚠️ 🔴 NEEDS-EXPERT | Soft range only — no hard public source |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — do NOT use `browser_action`
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,800 lines · `index.html` ~3,200 lines · `app.js` ~2,300 lines — grep first, targeted reads only
- **Wireframes → sign-off → HTML** (never write HTML without sign-off)
- **No build/push/deploy without user walkthrough and verification**
- Gemini tools (gemini_search, gemini_second_opinion) on autoApprove — use freely for fact-checking
- **Ask inline questions — no option lists** (ask_followup_question options array causes display issues)
- **Keep text before tool calls short** — large text blocks may not render in VS Code interface
