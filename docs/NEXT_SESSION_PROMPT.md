# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 9, 2026 (Session V — H2 Slug Flow Scenario Replay complete)
**git head:** `eb0936e` (1 commit this session)
**fault-trigger-ui image:** `sha256:a8cac759` (Session V — H2 Scenario Replay + Red Team Audit)
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
- field_intel: ~2–5 · rag_documents: 18 · telemetry_events: > 0
- inference-api models: `['esp_classifier', 'gas_lift_classifier', 'mud_pump_classifier', 'top_drive_classifier', ...]`

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

Also read: `docs/RED_TEAM_LEDGER.md` — trigger phrase "**red team**" re-runs the hostile-engineer audit at any checkpoint.

---

## STEP 3: Session W — Next Implementation Tasks

### ALL H1 AND H2 STEPS NOW COMPLETE ✅
H1 Decision Console (Sessions T + U) — done.
H2 Slug Flow Scenario Replay (Session V) — done and deployed.

### PRIORITY 1: H2 UX Polish (address remaining user feedback)
The following items were raised but deferred while physics and integrity issues were fixed first:

1. **Live-animating baseline feed:** On first page load, left-column charts should scroll in real-time with steady-state telemetry before any scenario is loaded. Currently both H1 and H2 charts are static on first visit. See SESSION V for details of what was planned.

2. **Decision console scrub-binding:** Verify that scrubbing backward on H2 correctly returns the SCADA view to the pre-alarm quiet slate. The watcher on `h2CursorIdx` should handle this since the SCADA view checks `h2CursorIdx < h2ReplayData.scada_hi_idx`.

3. **Cost explanation labels:** Embed concise source citations directly next to monetary values (e.g., `[WTX spot rig $14k/day × 3d · OEM motor]` appears on GDC cards but SCADA view outcome card needs the same treatment).

4. **SVG wellbore annotations:** Add explicit text labels inside the SVG for Pump Intake, API RP 11S submergence limit (H1 only), and reservoir perforations so the schematic is self-explanatory without verbal explanation.

### PRIORITY 2: RED_TEAM_LEDGER.md pending items
Three items remain in the Pending section of RED_TEAM_LEDGER.md:
- P-1: Verify `esp_health.ubj` slug_flow output (DONE — dips to 0.52, acknowledged honestly in UI)
- P-2: Source a citeable SPE reference for in-string slug loading pump vibration (candidate: SPE-174536 §3.4)
- P-3: Confirm ISA-18.2 H/HH alarm naming matches the standard exactly (ISA-18.2 Table 5.2: Warning → H → HH)

### PRIORITY 3: H3 Vizier Optimize Tab (if H2 polish is complete)
Per DEMO_MASTER.md §6: H3 tab already has the Vizier Pareto chart working. Next steps:
- Verify the Vizier API call from the new pod works (OPC/Vertex AI credentials)
- Add cost explanation cards matching the Claim Ledger

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
| `92%/94% confidence` literals in H1 verdict | ⏳ FIXING Session W Batch A | Fabricated HTML literals — no producer; replaced by Bayesian posterior in Batch B |
| `hs = 1.0000` fallback shown on confirmed-fault verdict | ⏳ FIXING Session W Batch B | Cursor past array bound hits '1.0000' fallback — contradicts confirmed-fault state |
| Well A-1 in sonic log modal vs A-3 everywhere else | ⏳ FIXING Session W Batch B | Display identity mismatch |
| Action-card outcome text: "pump integrity confirmed" | ⏳ FIXING Session W Batch A | We cannot assert this before a controlled restart test — RT-2; removing per HITL reframe |
| Shut-in framed as zero/no-cost option | ⏳ FIXING Session W Batch A | Deferred production + restart cost are real; framing was misleading |
| $ figures on operational cards (not behind ⓘ) | ⏳ FIXING Session W Batch A | ISA-101 operational consoles don't show dollar signs; move to info popups |

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
