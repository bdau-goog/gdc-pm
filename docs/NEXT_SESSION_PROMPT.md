# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 10, 2026 (Session AL — Panel 2+3 scrubber rebuild complete)
**git head:** `bc5edd7` (feat(sprint-ak): Panel 2+3 scrubber rebuild)
**fault-trigger-ui image:** `sha256:ca4c110c37e9e7e0030f0577656c6115a0a1f6ff830132115168b7b0961ea10b` (Session AL)
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

**Expected when healthy:**
- All 8 pods 1/1 Running · ollama replicas: 1
- ollama_online: True · model: gemma4:latest
- field_intel: 5 · rag_documents: 18 · telemetry_events: > 1,000,000

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Next Task — Sprint 3 H2 Briefing (3 Panels)

Panels 1–6 of H1 Briefing are all ship-ready (Panels 2+3 fixed this session). Next task is Sprint 3: H2 Briefing.

### H2 Briefing — 3 Panels
Architecture: `h2BriefingMode: true` + `h2BriefingPanel: 1` in Vue data, `<template v-else>` wrapper around existing H2 scenario replay. Same pattern as H1 briefing.

| Panel | Title | Key Message |
|---|---|---|
| 1 | What is Slug Flow? | Gas-liquid slugs in surface flowline transmit mechanical shocks → vibration rises, temp FLAT |
| 2 | Why It Looks Like a Failing Pump | SCADA sees vib alarm → conservative operator orders $150k pump pull |
| 3 | STATE vs. CONTEXT Exoneration | Temp flatness + choke log + separator test = pump healthy. Surface truck roll $1,500 |

**Files to edit (same 3-file pattern as H1):**
- `gke/fault-trigger-ui/static/app.js` — add `h2BriefingMode`, `h2BriefingPanel` to Vue data
- `gke/fault-trigger-ui/index.html` — H2 Briefing markup (ONE batched call)
- No styles.css changes needed (reuse H1 briefing CSS classes)

**Token discipline:** `index.html` is ~3,210 lines. Grep for line numbers first. Batch all index.html changes into ONE `replace_in_file` call.

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| Financial Justification modal raw {{ }} | ✅ FIXED Session AJ | div balance net 0 |
| Panel 2 animated bars (infinite loop) | ✅ FIXED Session AL | h1P2Scrub scrubber — green→amber, short=worse |
| Panel 3 wellbore SVG size | ✅ FIXED Session AL | max-height:148px → 280px |
| Panel 3 infinite bubble/drain loops | ✅ FIXED Session AL | opacity/scaleY scrubber-driven |
| STATE-vs-CONTEXT premise | ✅ LOCKED | Claim Ledger PREMISE row |
| SPE-174536 citation | ⚠️ UNVERIFIED | Using SPE-170776; 4.2 ft/s = representative |
| Panels 1, 2, 3, 4, 5, 6 | ✅ SHIP-READY | All 6 H1 Briefing panels approved |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — use `node scripts/ui_smoke.mjs` or `curl`
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- **Deploy with explicit digest** — `kubectl rollout restart` with `:latest` does NOT pull from registry
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,400 lines, `index.html` ~3,210 lines, `app.js` ~2,300 lines — grep for line numbers first
- H2 uses inference-api (not local esp_classifier.bst)
