# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 11, 2026 (Session AX — H2 deploy + domain terminology fixes)
**git head:** `2d0035a` (fix(ariel-temps): correct Ariel JGP discharge temperature references)
**fault-trigger-ui image:** `sha256:cd46caa8c960e503f78174250604ad319617b4ccca856d7c3f052f89d6b539ee`
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

**Actual at session-AX close:** 6 pods Running · ollama=0 · ollama_online=False · field_intel=11 · rag_docs=18 ✅

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

### PRIORITY 1 — H2 Briefing wireframe sign-off → HTML

The wireframe was designed this session but the user did not sign off before wrap.
3 panels, simplified structure (doc stack removed from Panel 2 — overtelling):

- **Panel 1:** The asset (ESP-ALPHA-3) + workover context callout
  - Right callout: *"8 weeks ago: fresh motor, new pump, startup normal. Expected 12–18 months of run life."* (NOT "something went wrong" — that's Panel 3's reveal)
- **Panel 2:** Timeline (workover → 3-week onset → alarm) + 4 sensor tiles + APM conclusion only
  - No document stack preview — documents first appear in the scenario replay
  - Closing line: *"Bearing wear. Pull the pump." — APM makes the statistically correct call.*
- **Panel 3:** GDC verdict + action cards (~$8k–$15k est. vs ~$70k–$100k) + universal pattern + CTA
  - Key subtitle: *"The completion report says what fluid was used. The OEM manual says that fluid destroys Buna-N seals. GDC connected them. No sensor, no human, no APM system had done that yet."*

**Gate: wireframe → your sign-off → HTML. Ask the user to confirm Panel 1/2/3 copy before writing code.**

### PRIORITY 2 — H2 Scenario Replay UI

Same mechanics as H1. Dual-sensor Plotly (efficiency↓ amber + vib↑ purple). SCADA View / GDC Advisor View. 5 staggered doc reveals.

### PRIORITY 3 — H3 Briefing panels (3 panels, replace toggle info panel)

H3 currently has a toggle "ⓘ Physics & Logic" inline panel at index.html ~line 2011. Needs proper 3-panel briefing per §4.5.

### PRIORITY 4 — H3 copy fix

H3 may still display "no cloud dependency" → must read "no public-cloud dependency for the decision."

### PRIORITY 5 — H1 Batch B date-templating

Sonic log, shift note, GOR lab report in field_intel have hardcoded 2025 dates.

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Briefing — all 6 panels | ✅ DEPLOYED | Session AQ |
| H1 Scenario replay | ✅ DEPLOYED | Session AP |
| H2 backend endpoint | ✅ DEPLOYED | `sha256:cd46caa8` — session AX |
| H2 "protector fill oil" terminology | ✅ DEPLOYED | `306ef60` — was "hydraulic fluid" (wrong) |
| Ariel JGP temperature limits | ✅ DEPLOYED | `2d0035a` — was "250°F design limit" (doesn't exist); now 330°F guideline / 350°F shutdown |
| H2 Briefing panels | ❌ NOT BUILT | Wireframe designed but not signed off — PRIORITY 1 |
| H2 Scenario replay UI | ❌ NOT BUILT | After briefing panels |
| H3 Briefing panels | ❌ NOT BUILT | Toggle info panel exists (~line 2011) but doesn't meet §4.5 spec |
| H3 copy — "no cloud dependency" | ⚠️ NEEDS FIX | 1–2 lines in index.html |
| H1 static seed date-templating | ⚠️ NEEDS FIX | Hardcoded 2025 dates (Batch B) |
| Ollama GPU pod | ✅ AT 0 | GPU-discipline rule in effect. False is correct. |
| MCP gdc-second-opinion | ✅ WORKING | gemini-2.5-flash, Vertex AI ADC, gdc-pm-v2 |
| H2-C1 flush+reseal ~$8k–$15k | ⚠️ 🔴 NEEDS-EXPERT | Soft range only — no hard public source |
| SPE papers cited (SPE-174536, SPE-170776) | ⚠️ UNVERIFIED | Not yet pulled and confirmed — do not cite as hard facts |
| BH Centrilift pricing in financial justifications | ⚠️ ESTIMATES | Behind ⓘ Justify click; labeled "2024 list price" — defensible as illustrative |
| Ariel fin-fan PM interval "6 months" | ⚠️ PLAUSIBLE | Gemini confirms 6-month intervals exist in Ariel manuals; specific fin-fan assignment unconfirmed |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No `browser_action` (SSH remote, no browser)
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,800 lines · `index.html` ~3,200 lines · `app.js` ~2,300 lines — grep first, targeted reads only
- **Wireframes → sign-off → HTML** (never write HTML without sign-off)
- **No build/push/deploy without user walkthrough and verification**
- Gemini tools (gemini_search, gemini_second_opinion) on autoApprove — use freely for fact-checking
- **Ask inline questions — no option lists** (ask_followup_question options array causes display issues)
- **Keep text before tool calls short** — large text blocks may not render in VS Code interface
- **Deploy sequence:** `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status` (use Artifact Registry, NOT gcr.io)
