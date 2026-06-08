# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 8, 2026 (Session K — tab nav labels fixed, deployed)
**git head:** `e8838af` (fix(ui): Session K — header nav tab labels Detect→Discern, Discern→Classify)
**fault-trigger-ui image:** `sha256:d66b61e6` (1/1 Running — Session K)
**inference-api image:** `sha256:d1194989` (1/1 Running — unchanged)
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
source .env && kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
source .env && kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
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

## STEP 3: Next Implementation Task — Session L

### What Was Completed in Sessions J + K

- **Session J:** Complete H1 "Discern" tab clean-slate rewrite — Double-Blind Choice Game fully deployed (`sha256:2fe914a6`)
- **Session K:** Header nav tab labels corrected: "Detect" → "Discern" (H1), "Discern" → "Classify" (H2) (`sha256:d66b61e6`)

### Current State of the Live Demo

**Header Nav:** `How It Works | Discern | Classify | Optimize` ✅ (correct per DEMO_MASTER §7)

**H1 Discern Tab:** Complete Double-Blind Choice Game deployed and working:
- Single inject button, random 50/50 Gas Lock / Fluid Drawdown
- Left 40%: telemetry column + dual-axis PIP/Amps trend chart
- Right 60%: SCADA View (blind gamble) + GDC Advisor (RAG card, wellbore twin, verdict, override modal)
- Field log modals (Shift Note + Sonic Log)
- Status banner double-blind until h1RagRevealed = true

**H2 Classify Tab:** Functional but uses old layout (no SCADA/GDC split pane, no narrative).

**H3 Optimize Tab:** Complete — Vizier Bayesian optimization, working.

### Next Tasks (in priority order)

**Task L-1 — Browser smoke-test of the full H1 Discern demo flow**
Since no browser is available on this SSH remote, ask the user to:
1. Navigate to `http://gdc-pm.bdau.io`
2. Click the **Discern** tab
3. Click ⚡ Inject Unloading Anomaly
4. Verify: (a) status banner shows "UNLOADING ANOMALY ACTIVE — FAULT TYPE UNKNOWN" until ~2s; (b) switching to GDC Advisor shows "⏳ Retrieving…" then the RAG card; (c) click the RAG card → field log modal opens; (d) try VFD trim from GDC tab during Drawdown → override modal fires
5. Report any visual issues back so they can be fixed

**Task L-2 — H2 "Classify" tab upgrade** (from DEMO_MASTER §5)
The current H2 tab shows the old layout (3 cards + 2 charts + truck roll). Per DEMO_MASTER.md §5, the Classify tab needs:
- Same two-pane structure: Left 40% shared telemetry, Right 60% SCADA vs GDC console
- SCADA View: "⚠ VIBRATION ALARM — Possible ESP bearing failure"  ($150k false positive risk)
- GDC Advisor: RAG retrieval reveals surface slug flow (OEM guide + separator test), verdict "PUMP IS HEALTHY — surface issue", dispatch truck roll ($1,500)
- This is a clean redesign of lines 716–850 in index.html + minor app.js additions

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| All H1 Discern features | ✅ Live | Session J deployed, Session K labels fixed |
| H2 Classify layout | ⚠ Old | Functional but lacks SCADA/GDC split narrative |
| H3 Optimize | ✅ Complete | No changes needed |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- Batch all edits to same file in ONE `replace_in_file` call
- ALL kubectl/gcloud commands require `source .env &&` prefix
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
