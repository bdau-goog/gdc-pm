# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 10, 2026 (Session AO — H1 narrative reframe deployed; Discern as default tab)
**git head:** `7e7af08` (fix(h1-narrative): reframe H1 as cited-evidence analyst — cut detection race, relabel tabs, Mining row removed, seizure→unplanned outcome, Discern as default tab)
**fault-trigger-ui image:** `sha256:b0e186376502e3296c6253f1559dcfcaa555e73728cbfa28b9508e844a6a2ae3` (Session AO)
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
- field_intel: 5-6 · rag_documents: 18 · telemetry_events: > 1,000,000

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Next Tasks — Batch 2 / H2 Briefing

### H1 is video-ready (Session AO ruling locked and deployed)

**H1 narrative spine is settled.** Three beats, no straw-man, no detection race:
1. SCADA alarm fires — AMBIGUOUS — standard policy = shut in (honest, defensible)
2. GDC L3 docs → cited verdict in seconds → confident, production-preserving action
3. Class of problems, not a one-off (Panels 4/5/6)

**Unblocked now (no content approval needed — code only):**

**Batch 2A — HP-HMI Color Full-Compliance Pass:**
Per ISA-101.01 §5: gray is normal, color = alarm only. Fix in ONE batched `replace_in_file`:
- GDC Recommended/Contraindicated card backgrounds → remove green/red tint (pure `var(--surf)`)
- Card borders → thin, ~30% opacity
- Zone-1 verdict box bg → near-black (`rgba(15,23,42,0.8)`), no green/orange tint
- Zone-1 headline color → wrap in small colored status pill; body = all `var(--text2)`

**Batch 2B — OEM Troubleshooting Guide modal (requires copy sign-off G1–G6 before code):**
Doc 3 in H1 evidence panel has NO click handler. Draft fictional-vendor content against G1–G6 gates for user review first.

**Sprint 3 — H2 Briefing (3 panels):**
- Panel 1: The Well (slug flow setup)
- Panel 2: Why It Looks Like a Failing Pump (vibration HI, but temp flat)
- Panel 3: STATE vs. CONTEXT exoneration (same 3-beat structure as H1)
Same architecture as H1 briefing (`h2BriefingMode`/`h2BriefingPanel` in Vue data, `<template v-else>` wrapper).

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| Financial Justification modal raw {{ }} | ✅ FIXED Session AJ | div balance net 0 |
| Panel 2 animated bars (infinite loop) | ✅ FIXED Session AL | h1P2Scrub scrubber |
| Panel 3 infinite bubble/drain loops | ✅ FIXED Session AL | opacity/scaleY scrubber-driven |
| Panel 1+4 flicker (color-emoji repaint) | ✅ FIXED Session AM | .h1-ok-dot + CSS squares |
| Panels 4/5/6 build shimmer (@keyframes) | ✅ FIXED Session AM | opacity-only, no transforms |
| Field Link (bandwidth claim) | ✅ REMOVED Session AM | wan-badge span deleted |
| ← Briefing re-entry button | ✅ ADDED Session AM | h1BriefingMode=true |
| ISA-101 card color scoping | ✅ FIXED Session AN | `.h1-card-green .h1-card-header` |
| SCADA leading-the-witness text | ✅ FIXED Session AN | Card A/B neutralized |
| H1 detection-race framing | ✅ RETIRED Session AO | Lead-time banner, "Smart SCADA", "PUMP SEIZED" removed |
| Tab default landing | ✅ FIXED Session AO | mainTab → 'horizon1'; How It Works → ⓘ Reference |
| Panel 6 Mining row | ✅ REMOVED Session AO | 3 rows remain: O&G / P&E / MFG |
| OEM Troubleshooting Guide no click handler | ⚠️ BATCH 2 | Doc 3 needs modal + content (G1–G6 gate) |
| STATE-vs-CONTEXT premise | ✅ LOCKED | Claim Ledger PREMISE row |
| SPE-174536 citation | ⚠️ UNVERIFIED | Using SPE-170776; 4.2 ft/s = representative |

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
