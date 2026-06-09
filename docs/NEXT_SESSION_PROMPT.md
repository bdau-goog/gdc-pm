# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 9, 2026 (Session AA — MODEL_FOUNDATIONS precision conflict resolved)
**git head:** `58190e2` (docs: Session AA — reconcile MODEL_FOUNDATIONS precision conflict)
**fault-trigger-ui image:** `sha256:5b608508` (Session Z Batch E — no code changes this session)
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
- field_intel: ≥1 (hitl_action rows from Batch D) · rag_documents: 18 · telemetry_events: > 1,000,000
- inference-api models: `['esp_classifier', 'gas_lift_classifier', 'mud_pump_classifier', 'top_drive_classifier', ...]`

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

Also read: `docs/RED_TEAM_LEDGER.md` — trigger phrase "**red team**" re-runs the hostile-engineer audit.

---

## STEP 3: Session Z completed Batch D + Batch E — Next Tasks

### Session Z Batch D COMPLETE ✅
- `/api/h1/remediation-record` endpoint live — writes `doc_type='remediation_record'`, `lbl_type='hitl_action'` to `field_intel`
- `get_rag_context_and_adjusted_rul()` excludes `hitl_action` rows (`AND lbl_type != 'hitl_action'`)
- `executeH1Shutdown()` and `approveH1VFD()` wired in `app.js` to POST remediation record

### Session Z Batch E COMPLETE ✅
- **SCADA pre-alarm sensor tiles:** Live PIP/Amps/Temp/Vib tiles (green nominal state) now shown on SCADA tab BEFORE alarm fires — same data as GDC tab. Symmetric presentation, ISA-101 compliant.
- **Taller wellbore SVG (Zone 3):** Container 12%→15%. viewBox 0 0 40 210 → 0 0 44 250. Added surface Christmas tree (X-MAS block at top), 4 perforation pairs, formation/reservoir block at bottom (~9,800 ft MD). Depth tick marks at 3k/6k ft.
- **SVG document icons:** Replaced plain 📄 emoji with distinct inline SVG badges: waveform acoustic trace (sonic log/shift note), bar chart GOR trend (separator lab report), open book (OEM guide). Each has distinct color (green/blue/purple) + label text.

### NEXT TASKS (Session AA — confirm with user)
1. **MODEL_FOUNDATIONS precision conflict** — ✅ RESOLVED this session. `MODEL_FOUNDATIONS.md` updated to document June 9 Session S retrain results (gas_lock P=0.995, slug_flow P=0.993, RMSE=0.00179). The 0.815 figure in §9 is now correctly labeled as v1 historical failure. Integrity item closed.
2. **H3 Optimize tab review:** Check if Vertex AI Vizier endpoint is still live and returning real trials. Smoke-test the full H3 flow. `vizier_optimize()` integrity violation still open (`esp_thermal.ubj` not built — hardcoded polynomial still running).
3. **Any presenter walkthrough gaps** — user to identify.

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Scenario Replay physics | ✅ FIXED Session S | psi_final 400–600 PSI, temp 245–265°F, vib 4.5–6.5, lead ~5–15 min |
| Smart SCADA alarm logic | ✅ FIXED Session S | 3-rule ISA-18.2/API RP 11S — fires step 79/120 (~T=20min) |
| `esp_health.ubj` / `esp_classifier.ubj` | ✅ FIXED Session S | RMSE=0.00179, gas_lock P=0.995, all gates pass |
| CLAIM_LEDGER.md H1 ranges | ✅ FIXED Session V | Was wrong (875-1100 PSI) — reconciled to actual FAULT_PROFILES (400-600 PSI) |
| H2 physics mechanism | ✅ FIXED Session V | Cut 'surface shock transmission'; corrected to in-string multiphase slug loading |
| H2 Classify tab | ✅ NEW Session V | Full Scenario Replay layout: dual chart, scrubber, ISA-101 SCADA, GDC 3-zone, shared SVG wellbore |
| `92%/94% confidence` literals | ✅ FIXED Session X Batch B | Replaced with live `_bayes_discriminate()` posterior — 99.6% on fluid_drawdown |
| Bayesian discrimination confidence not wired | ✅ FIXED Session X Batch B | `_bayes_discriminate()` live; evidence table shows F1–F4 LR chain |
| Scrub-reactive GDC verdict reset | ✅ FIXED Session Y Batch C | Back-scrub before gdc_detect_idx resets all revealed state |
| Transport controls locked after remediation | ✅ FIXED Session Y Batch C | Buttons + scrubber disabled on h1Resolved/h1Seized/h2Resolved/h2PullOutcome |
| H2 classifier_ok verified live | ✅ VERIFIED Session Y | curl confirms classifier_ok:true — inference-api running real esp_classifier.ubj |
| Remediation writes to field_intel | ✅ FIXED Session Z Batch D | `/api/h1/remediation-record` live; lbl_type='hitl_action' excluded from discrimination RAG |
| SCADA pre-alarm sensor tiles | ✅ NEW Session Z Batch E | Live PIP/Amps/Temp/Vib tiles (green) on SCADA tab before alarm fires |
| Wellbore SVG taller + X-MAS tree + formation | ✅ NEW Session Z Batch E | Zone 3: 15% wide, viewBox 250 tall, surface tree, depth ticks, formation block |
| SVG document icons | ✅ NEW Session Z Batch E | Distinct inline SVG badges (sonic waveform, GOR bar chart, OEM book) replace 📄 emoji |
| MODEL_FOUNDATIONS vs SESSION_LOG precision conflict | ✅ FIXED Session AA | MODEL_FOUNDATIONS.md updated — v2 results (P=0.995, all gates pass) documented in §6/§8/§9 addendum. 0.815 retained in §9 as correct v1 historical record. |

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
- `app.py` ~6,400 lines, `index.html` ~2,760 lines, `app.js` ~2,300 lines — always grep for line numbers first
- H2 uses inference-api (not local esp_classifier.bst) — local .bst is 4-class without slug_flow
