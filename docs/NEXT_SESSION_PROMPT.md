# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 8, 2026 (Session L — H1 Comparative Detection Scenario deployed)
**git head:** `06dffe8` (feat(ui): Session L — Comparative Detection Scenario)
**fault-trigger-ui image:** `sha256:85803d58` (1/1 Running — Session L)
**inference-api image:** `sha256:d1194989` (1/1 Running — unchanged)
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected when healthy:**
- All 8 pods 1/1 Running · ollama replicas: 1
- ollama_online: True · model: gemma4:latest
- field_intel: ~2 · rag_documents: 18

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Next Implementation Task — Session M

### What was shipped in Session L (deployed, verified sha256:85803d58)

The H1 "Discern" tab was redesigned from first principles per the Session L spec:

1. **De-Gamification complete:** "Double-Blind Choice Game" → "Comparative Detection Scenario"; "Inject Unloading Anomaly" → "⚡ Ingest Pad Anomalies"; "Blind Gamble" → "Reactive Manual Intervention"; "Ready for Double-Blind Choice Game" → "Pad Alpha Surveillance Active".
2. **Pad Alpha 6-Well Surveillance Grid:** Interactive well cards (A-1 to A-6) with color-coded status (Alerting/Suppressed/Nominal). `⚡ Ingest Pad Anomalies` randomly picks the target well and flags two adjacent nuisance wells as suppressed.
3. **4 Stacked Plotly Sparkline Cards:** Replaced ISA-101 horizontal progress bars with `#h1-spark-psi`, `#h1-spark-amps`, `#h1-spark-temp`, `#h1-spark-vib` — each with a red dashed SCADA threshold line and a bold live digital readout annotation.
4. **Dual Resizable Splitters:** `.h1-splitter` (horizontal, between Left/Right columns, 25–75%) and `.h1-v-splitter` (vertical, chart height control, 80–320px). Both support double-click to reset to defaults.
5. **Departure Rate Toggle:** Standard (900s) / Accelerated (300s) shown in banner before injection.
6. **New Vue state:** `h1SelectedWell`, `h1TargetWell`, `h1NuisanceWells`, `h1RampSpeed`, `h1WellData`.

### Session M Tasks

**Priority 1 — Browser smoke-test of H1 Discern (user must run in browser):**
- Verify Pad Alpha grid renders correctly (6 cards, A-1 to A-6)
- Verify "⚡ Ingest Pad Anomalies" selects a random target well (red "Alerting") and two adjacent nuisance wells (amber "Suppressed")
- Verify nuisance suppression text appears below grid
- Verify 4 sparkline charts render with threshold lines and live readout annotations after injection
- Verify horizontal splitter drag and vertical sparkline height drag work
- Report any visual issues

**Priority 2 — app.py: nuisance well suppression backend support (if needed):**
- The nuisance wells currently show "Suppressed" in the UI based on frontend state only
- If the demo requires fetching a Daily Well Test log from AlloyDB to justify suppression, a small app.py endpoint `GET /api/nuisance-suppression/{asset_id}` returning a RAG card text can be added
- This is optional — the current frontend-only approach is defensible for the demo narrative

**Priority 3 — H2 Classify tab upgrade:**
- Per DEMO_MASTER.md §5: two-pane SCADA/GDC layout, surface slug flow narrative, $148,500 avoided false-positive story
- Reuse the sparkline card CSS pattern from H1 Left column

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 nuisance suppression | ⚠ Frontend only | GDC auto-dismiss shown as text; no RAG doc fetched. Acceptable for demo; can add backend if challenged. |
| H1 sparklines pre-injection | ⚠ Needs baseline data | `_renderH1Charts(d)` renders on first `forecast-data` poll; may show empty charts until first poll completes. |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
