# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 9, 2026 (Session X — Batch B integrity fixes deployed)
**git head:** `5767ccf` (feat(integrity): Session X Batch B)
**fault-trigger-ui image:** `sha256:18155185` (Session X Batch B — Bayesian posterior + de-smoking-gun + GOR modal)
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Five Commands First

```bash
source .env && echo "PROJECT=$GOOGLE_CLOUD_PROJECT KUBECONFIG=$KUBECONFIG"
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents; SELECT COUNT(*) FROM telemetry_events;"
```

**Verification (Command 5 — inference model audit):**
```bash
kubectl exec -n gdc-pm deployment/fault-trigger-ui -- python3 -c "import urllib.request, json; print(list(json.loads(urllib.request.urlopen('http://inference-api:8080/model-info').read().decode())['models'].keys()))"
```

**Expected when healthy:**
- Workspace: `PROJECT=gdc-pm-v2` · `KUBECONFIG=/home/brian/gdc-pm/.kubeconfig`
- All 8 pods 1/1 Running · ollama replicas: 1
- ollama_online: True · model: gemma4:latest
- field_intel: ~2–5 · rag_documents: 18 · telemetry_events: > 1,000,000
- inference-api models: `['esp_classifier', 'gas_lift_classifier', 'mud_pump_classifier', 'top_drive_classifier', ...]`

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

Also read: `docs/RED_TEAM_LEDGER.md` — trigger phrase "**red team**" re-runs the hostile-engineer audit.

---

## STEP 3: Session X was Batch B — Next Tasks Are Batch C

### Session X Batch B COMPLETE ✅
RT-1…RT-10 all addressed. Key deliverables:
- `_bayes_discriminate()` live in app.py — naive-Bayes log-odds (Good 1950 / Fagan 1975), returns `bayes_pct: 99.6` on fluid_drawdown
- Sonic log de-smoking-gunned: 240 ft submergence (within limits at 06:00), no diagnosis/shutdown orders in document body
- GOR provenance moved to new `Separator Lab Report` modal (Permian Fluid Analytics)
- All Well A-1 references → A-3 (sonic log, shift note modals)
- `Baker Hughes SONiK™` → `Permian Acoustic Services (SONiX-2)`
- `Baker Hughes ESP` → `Permian ESP Operational Manual`
- Health score fallback: `Math.min(h1CursorIdx, h1ReplayData.health_score.length-1)` — no more 1.0000 on confirmed-fault
- Expandable Bayesian evidence table in GDC Advisor Zone 1 (toggle button)
- Smoke test: 12/12 assertions, 0 console errors ✅

### NEXT: Batch C (scoped, in priority order)
1. **Scrub-reactive GDC (#4):** GDC verdict resets when cursor scrubs back before `gdc_detect_idx` — currently stays revealed permanently even if scrubber goes back to T+0. Fix: add `h1ShowEvidenceTable=false` reset in `h1Reset()` + clear `h1RagRevealed` when cursor moves back before `gdc_detect_idx` in the `h1CursorIdx` watcher.
2. **Lock transport/scrubber after remediation:** Once an action card is clicked (resolved or seized), disable the Play/scrub controls so operator can't rewind and replay the decision. Prevents confusing state where resolved=true but cursor at T+0 shows pre-fault sensors.
3. **H2 live slug_flow_prob verification:** Confirm `slug_flow_prob` in the H2 chart is from the inference-api (not the fallback sigmoid). Check the `classifier_ok` field returned by `/api/h2/scenario-replay`.

### PRIORITY 4: Batch D–E (after Batch C deployed + verified)
- **Batch D:** Remediation writes a record to `field_intel` (RT-7 scoped: `doc_type='remediation_record'`, excluded from discrimination RAG)
- **Batch E:** Taller wellbore SVG + telemetry in both SCADA+GDC views + self-drawn SVG doc artifacts

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Scenario Replay physics | ✅ FIXED Session S | psi_final 400–600 PSI, temp 245–265°F, vib 4.5–6.5, lead ~5–15 min |
| Smart SCADA alarm logic | ✅ FIXED Session S | 3-rule ISA-18.2/API RP 11S — fires step 79/120 (~T=20min) |
| `esp_health.ubj` / `esp_classifier.ubj` | ✅ FIXED Session S | RMSE=0.00179, gas_lock P=0.995, all gates pass |
| CLAIM_LEDGER.md H1 ranges | ✅ FIXED Session V | Was wrong (875-1100 PSI) — reconciled to actual FAULT_PROFILES (400-600 PSI) |
| H2 physics mechanism | ✅ FIXED Session V | Cut 'surface shock transmission'; corrected to in-string multiphase slug loading at pump intake |
| simulator.py slug_flow vib | ✅ FIXED Session V | Now 4.0–6.5 mm/s (was 2.7) — matches FAULT_PROFILES and training data |
| H2 Classify tab | ✅ NEW Session V | Full Scenario Replay layout: dual chart, scrubber, ISA-101 SCADA, GDC 3-zone, shared SVG wellbore |
| `92%/94% confidence` literals | ✅ FIXED Session X Batch B | Replaced with live `_bayes_discriminate()` posterior — 99.6% on fluid_drawdown |
| `hs = 1.0000` fallback past array bound | ✅ FIXED Session X Batch B | Clamped to `Math.min(h1CursorIdx, health_score.length-1)` |
| Well A-1 in sonic log modal vs A-3 everywhere else | ✅ FIXED Session X Batch B | All Well A-1 → A-3 in modals |
| `Baker Hughes SONiK™` trademark in sonic log | ✅ FIXED Session X Batch B | → `Permian Acoustic Services (SONiX-2)` |
| Sonic log "smoking gun" (diagnosis + shutdown in body) | ✅ FIXED Session X Batch B | Survey now measurements-only (240 ft, within limits). GDC verdict carries synthesis. |
| GOR in sonic log (wrong provenance) | ✅ FIXED Session X Batch B | GOR moved to new Separator Lab Report modal (Permian Fluid Analytics) |
| Bayesian discrimination confidence not wired | ✅ FIXED Session X Batch B | `_bayes_discriminate()` live; evidence table shows F1–F4 LR chain |
| Action-card HITL reframe | ✅ FIXED Session W Batch A | "Awaiting field confirmation · pump condition assessed on controlled restart" |
| Shut-in framed as zero-cost | ✅ FIXED Session W Batch A | Now: "Deferred production + restart costs apply (see ⓘ)" |
| Scrub-reactive GDC (resets on back-scrub) | ⏳ BATCH C | Verdict persists if cursor scrubs back before gdc_detect_idx |
| Transport controls after remediation | ⏳ BATCH C | Scrubber still enabled after action card clicked |
| MODEL_FOUNDATIONS vs SESSION_LOG precision conflict | ⏳ OPEN | SESSION_LOG says P=0.995 pass; MODEL_FOUNDATIONS says 0.815 fail not committed — reconcile before any accuracy % ships |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — use `node scripts/ui_smoke.mjs` instead
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
- Gas Lock and Fluid Drawdown have IDENTICAL sensor trajectories — this is the H1 premise
- Physics panel `<` chars in text content: safe only as `< ` (space after) — never `<digit`
- `app.py` ~6,300 lines, `index.html` ~2,650 lines, `app.js` ~2,225 lines — always grep for line numbers first
- H2 uses inference-api (not local esp_classifier.bst) — local .bst is 4-class without slug_flow
