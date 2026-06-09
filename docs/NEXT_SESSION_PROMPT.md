# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 9, 2026 (Session W — Batch A integrity fixes deployed)
**git head:** `d9d86af` (2 commits this session)
**fault-trigger-ui image:** `sha256:b0ebc20d` (Session W Batch A — HITL reframe + strip $ + remove fake % + H1_METHODOLOGY.md)
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
- field_intel: ~2–5 · rag_documents: 18 · telemetry_events: > 1,000,000 (healthy accumulation)
- inference-api models: `['esp_classifier', 'gas_lift_classifier', 'mud_pump_classifier', 'top_drive_classifier', ...]`

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

Also read: `docs/RED_TEAM_LEDGER.md` — trigger phrase "**red team**" re-runs the hostile-engineer audit at any checkpoint.

---

## STEP 3: Session W — Next Implementation Tasks

### Session W Batch A COMPLETE ✅
All three integrity violations (RT-1 fake %, RT-2 pump-integrity claim, RT-8 shut-in cost) — fixed, deployed, live-verified. H1_METHODOLOGY.md written.

### NEXT: Session W Batch B (truth-critical documents)
1. **RT-3 — De-smoking-gun the sonic log:** Survey body = measurements only (no diagnosis/action). At 06:00 it shows fluid level declining but WITHIN LIMITS (e.g., ~240 ft → not yet alarm-worthy alone). The "decisive" 150-ft value is the LIVE reading during the demo window. Move "VFD CONTRAINDICATED / emergency shutdown" wording to GDC verdict only.
2. **RT-4 — GOR provenance:** Move GOR evidence to a separate Separator/Lab doc; survey keeps fluid level + casing pressure + free-gas only.
3. **RT-5 — Well A-1 → A-3:** Sonic log modal title currently says "Well A-1" — fix to A-3.
4. **RT-2 — `hs = 1.0000` binding:** GDC verdict shows 1.0000 when cursor past array bound on confirmed-fault state — fix the fallback.
5. **Document Realism Gate G1–G6 applied to all 3 H1 docs + 3 H2 docs** — fictional vendor (no "Baker Hughes SONiK™"), G3 "no smoking gun" test, G5 physics consistency.
6. **Bayesian confidence wiring (_bayes_discriminate):** Add `_bayes_discriminate(findings)` to app.py; wire live posterior to H1 Zone 1 verdict headline; add expandable evidence table. Replace "L3 context fused" placeholder with real posterior.
7. **H2 live `slug_flow_prob`:** Already bound in the UI; verify it's live (not hardcoded).
8. **RED_TEAM_LEDGER.md:** Append RT-1…RT-10 rows (not yet done this session — deferred to Batch B).

### PRIORITY 3: Batch C–E (after Batch B deployed + verified)
- **Batch C:** #4 scrub-reactive GDC (resets on back-scrub) + lock transport/scrubber after remediation chosen
- **Batch D:** #3 remediation writes a record to `field_intel` (RT-7 scoped: `doc_type='remediation_record'`, excluded from discrimination RAG)
- **Batch E:** #1 taller wellbore + #5 telemetry in both SCADA+GDC views + #8 self-drawn SVG doc artifacts

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
| esp_classifier.bst (4-class) | ✅ NOTED Session V | Local .bst has no slug_flow class; H2 uses inference-api esp_classifier.ubj (5-class) via async httpx |
| RED_TEAM_LEDGER.md | ✅ NEW Session V | Trigger: "red team" → re-runs hostile-engineer audit |
| H2 live baseline feed | ⏳ DEFERRED | Charts are static on first visit; live-scroll not yet implemented |
| `92%/94% confidence` literals in H1 verdict | ✅ FIXED Session W Batch A | Removed; replaced with "L3 context fused" placeholder pending Bayesian wiring (Batch B) |
| `hs = 1.0000` fallback on confirmed-fault verdict | ⏳ FIXING Session W Batch B | Cursor past array bound hits '1.0000' fallback — contradicts confirmed-fault state |
| Well A-1 in sonic log modal vs A-3 everywhere else | ⏳ FIXING Session W Batch B | Display identity mismatch |
| Action-card outcome text: "pump integrity confirmed" | ✅ FIXED Session W Batch A | Replaced: "Awaiting field confirmation · pump condition assessed on controlled restart" |
| Shut-in framed as zero/no-cost option | ✅ FIXED Session W Batch A | Now: "Deferred production + restart costs apply (see ⓘ)" |
| $ figures on operational cards | ✅ FIXED Session W Batch A | Stripped from all cards/outcomes/toasts; kept only in ⓘ Physics & Logic panel |
| "Baker Hughes SONiK™" in sonic log modal | ⏳ FIXING Session W Batch B | RT-3: real company + invented product name → fictional vendor per G1 gate |
| Sonic log "smoking gun" (diagnosis + shutdown order in doc body) | ⏳ FIXING Session W Batch B | RT-3: doc body should be measurements only; GDC verdict carries the synthesis |
| Bayesian discrimination confidence not yet wired | ⏳ Session W Batch B | "L3 context fused" is a placeholder; real posterior from _bayes_discriminate() coming |
| MODEL_FOUNDATIONS vs SESSION_LOG precision conflict | ⏳ OPEN | SESSION_LOG says P=0.995 pass; MODEL_FOUNDATIONS says 0.815 fail not committed — must reconcile before any accuracy % ships |

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
- `app.py` ~6,180 lines, `index.html` ~2,545 lines, `app.js` ~2,180 lines — always grep for line numbers first
- H2 uses inference-api (not local esp_classifier.bst) — local .bst is 4-class without slug_flow
