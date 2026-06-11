# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 11, 2026 (Session AY — H2 Briefing 3-panel deployed)
**git head:** `7673efd` (feat(h2-briefing): 3-panel H2 Briefing — Maintenance Provenance)
**fault-trigger-ui image:** `sha256:de369a364855624d78d499c0d9373024d738e0ce1508c44fbd19cb0d6619f4f9`
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
- field_intel: **9–12** (H2 static seeds: oem_manual + pull_record + well_history seeded at startup) · rag_docs: 18

**Actual at session-AY close:** 6 pods Running · ollama=0 · ollama_online=False · field_intel=11 · rag_docs=18 ✅

**GPU discipline rule:** OFF by default.
  `./scripts/gpu-start.sh`  ← start only at explicit LLM-test step (~$0.65/hr begins)
  `./scripts/gpu-stop.sh`   ← stop immediately after (always paired)

**⚠️ REGISTRY NOTE:** The cluster uses **Artifact Registry**, NOT gcr.io.
Correct push/deploy path:
```bash
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest gke/fault-trigger-ui/
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
# Get digest from push output, then:
kubectl set image deployment/fault-trigger-ui -n gdc-pm \
  fault-trigger-ui=us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui@sha256:<digest>
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm
```

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat /home/brian/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Next Implementation Tasks (in order)

### PRIORITY 1 — H2 Scenario Replay UI

H2 Briefing (3 panels) is now DEPLOYED. Next: the scenario replay UI.
Same mechanics as H1. Per DEMO_MASTER §5:

- Dual-sensor Plotly chart: Motor efficiency (declining, amber) + Vibration (rising, purple)
- SCADA View: quiet pre-alarm → degradation banner ("Mechanical degradation — investigation recommended") → action cards: (A) Pump-pull investigation / (B) Continue monitoring
- GDC Advisor View: 3-zone layout:
  - Zone 1: "Elastomer seal degradation — NOT bearing wear"
  - Zone 2 left: action card (flush+reseal ~$8k–$15k est.) vs averted (pump pull ~$70k–$100k)
  - Zone 2 right: 5 staggered doc reveals — Workover completion report [DYNAMIC] → OEM matrix (+2s) → Pull record (+3.5s) → Shift note [DYNAMIC] (+5s) → Well history (+6.5s)
- The existing `/api/h2/scenario-replay` endpoint already returns the correct payload
- Note: the existing H2 scenario replay UI uses OLD slug-flow GDC wording — must update Zone 1 verdict copy to use workover-fluid-incompatibility language

**Gate: write HTML without additional sign-off — this is already approved in DEMO_MASTER §5.**

### PRIORITY 2 — H3 Briefing panels (3 panels, replace toggle info panel)

H3 currently has a toggle "ⓘ Physics & Logic" inline panel at index.html ~line 2011. Needs proper 3-panel briefing per §4.5.

### PRIORITY 3 — H3 copy fix

H3 may still display "no cloud dependency" → must read "no public-cloud dependency for the decision."

### PRIORITY 4 — H1 Batch B date-templating

Sonic log, shift note, GOR lab report in field_intel have hardcoded 2025 dates.

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Briefing — all 6 panels | ✅ DEPLOYED | Session AQ |
| H1 Scenario replay | ✅ DEPLOYED | Session AP |
| H2 backend endpoint | ✅ DEPLOYED | `sha256:cd46caa8` — session AX |
| H2 Briefing panels (3 panels) | ✅ DEPLOYED | `7673efd` — session AY |
| H2 "protector fill oil" terminology | ✅ DEPLOYED | `306ef60` |
| Ariel JGP temperature limits | ✅ DEPLOYED | `2d0035a` |
| H2 Scenario replay UI | ❌ NOT BUILT | PRIORITY 1 — existing UI has old slug-flow copy |
| H3 Briefing panels | ❌ NOT BUILT | Toggle info panel exists (~line 2011) but doesn't meet §4.5 spec |
| H3 copy — "no cloud dependency" | ⚠️ NEEDS FIX | 1–2 lines in index.html |
| H1 static seed date-templating | ⚠️ NEEDS FIX | Hardcoded 2025 dates (Batch B) |
| Ollama GPU pod | ✅ AT 0 | GPU-discipline rule in effect. False is correct. |
| MCP gdc-second-opinion | ✅ WORKING | gemini-2.5-flash, Vertex AI ADC, gdc-pm-v2 |
| H2-C1 flush+reseal ~$8k–$15k | ⚠️ 🔴 NEEDS-EXPERT | Soft range only — labeled as estimate on screen |
| SPE papers cited (SPE-174536, SPE-170776) | ⚠️ UNVERIFIED | Not yet pulled and confirmed — do not cite as hard facts |
| 51% ESP failures = operational factors | ✅ ATTRIBUTED | 2014 SPE Artificial Lift Conference survey (Gemini-verified) |
| BH Centrilift pricing in financial justifications | ⚠️ ESTIMATES | Behind ⓘ Justify click; labeled "2024 list price" — defensible as illustrative |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No `browser_action` (SSH remote, no browser)
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,800 lines · `index.html` ~3,200 lines · `app.js` ~2,300 lines — grep first, targeted reads only
- **Wireframes → sign-off → HTML** (never write HTML without sign-off) — exception: H2 scenario replay is pre-approved in DEMO_MASTER §5
- **No build/push/deploy without user walkthrough and verification**
- Gemini tools (gemini_search, gemini_second_opinion) on autoApprove — use freely for fact-checking
- **Ask inline questions — no option lists** (ask_followup_question options array causes display issues)
- **Keep text before tool calls short** — large text blocks may not render in VS Code interface
- **Deploy sequence:** `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status` (use Artifact Registry, NOT gcr.io)
