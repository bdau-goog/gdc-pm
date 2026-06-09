# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 9, 2026 (Session Z — Batch D remediation audit loop deployed)
**git head:** `58fc8ac` (feat(integrity): Batch D — remediation writes to field_intel via /api/h1/remediation-record)
**fault-trigger-ui image:** `sha256:bacd3718` (Session Z Batch D — HITL audit loop)
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

## STEP 3: Session Z completed Batch D — Next Tasks Are Batch E

### Session Z Batch D COMPLETE ✅
Remediation HITL audit loop. Key deliverables:
- **`/api/h1/remediation-record` endpoint (app.py):** New POST endpoint writes `doc_type='remediation_record'`, `lbl_type='hitl_action'` rows to `field_intel`. `RemediationRecordRequest` Pydantic schema: `asset_id`, `fault_type`, `action_label`, `headline`, `detail`.
- **RAG exclusion (app.py):** `get_rag_context_and_adjusted_rul()` dynamic query now includes `AND lbl_type != 'hitl_action'` — operator actions are written to the audit log but cannot contaminate pre-diagnosis RAG context.
- **Frontend wired (app.js):** `executeH1Shutdown()` and `approveH1VFD()` both POST to the new endpoint on execution. Shut-in path writes `action_label='emergency_shutin'` with elapsed T+Xmin in detail. VFD-trim-during-drawdown seize path writes `action_label='vfd_trim_contraindicated'` documenting the failure event.
- **Verified live:** `curl → {"status":"ok",...}` · AlloyDB confirms row `id=73411, lbl_type='hitl_action'` written correctly.

### NEXT: Batch E (scoped, in priority order)
1. **Taller wellbore SVG + telemetry in both SCADA+GDC views:** SVG Zone 3 wellbore should be taller (current proportions feel cramped). Both the SCADA and GDC tabs should show the live sensor readout tiles (PIP/Amps/Temp/Vib values at cursor position) — currently only GDC tab shows them.
2. **Self-drawn SVG document artifacts:** Replace the plain text doc cards with small inline SVG sketches (sonic log trace, pressure histogram, shift note icon) to make the document stack more visually compelling.

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
| Scrub-reactive GDC verdict reset | ✅ FIXED Session Y Batch C | Back-scrub before gdc_detect_idx resets all revealed state |
| Transport controls locked after remediation | ✅ FIXED Session Y Batch C | Buttons + scrubber disabled on h1Resolved/h1Seized/h2Resolved/h2PullOutcome |
| H2 classifier_ok verified live | ✅ VERIFIED Session Y | curl confirms classifier_ok:true — inference-api running real esp_classifier.ubj |
| Remediation writes to field_intel | ✅ FIXED Session Z Batch D | `/api/h1/remediation-record` live; lbl_type='hitl_action' excluded from discrimination RAG |
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
- `app.py` ~6,400 lines, `index.html` ~2,683 lines, `app.js` ~2,300 lines — always grep for line numbers first
- H2 uses inference-api (not local esp_classifier.bst) — local .bst is 4-class without slug_flow
