# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 10, 2026 (Session AM — Stage A flicker fixes + Field Link removal + briefing re-entry)
**git head:** `97f008c` (fix(stage-a): flicker fixes + Field Link removal + briefing re-entry button)
**fault-trigger-ui image:** `sha256:153a7f9b27caef9ee8f4f8cfc87a9b28789f7cdcab75e1b2fab2af71360832a9` (Session AM)
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

## STEP 3: Next Task — Stage B + Stage C (H1 Briefing Content Rework)

### Open Items from Session AM Review

**Open rulings needed before any Stage B code:**
1. **"GDC detects before SCADA" claim** — strip from briefing entirely? (my rec: yes — rest on L3 moat). Affects Panel 2 Key Insight line AND the live scenario lead-time marker.
2. **Field Link** — REMOVED this session. ✅

### Stage B — Content Reworks (Panels 1, 2, 3, 6, 7)
Deck now proposed as **7 panels** (new "Options" panel between P3 and old P4):

| # | Title | Change |
|---|---|---|
| 1 | This Well | Rebalance: lead with ESP characteristics, sand demoted to a property |
| 2 | An Unloading Event Is a Critical ESP Failure | Retitle from question→stakes; remove "detects before SCADA" (pending ruling) |
| 3 | One Signature, Two Causes | Wider wellbores; multi-stage pump schematic; gas bubbles at pump intake; depth cues; remove inline actions |
| 4 (NEW) | Responding to an Unloading Event | VFD trim vs Shut-in: mechanism, cost, when each is used |
| 5 | Why Knowing the Cause Is Critical | Reframe: sand = stakes-setter; simplify 2x2; reword bottom line |
| 6 | STATE vs. CONTEXT | Spell out "Pump Intake Pressure"; emoji already fixed (this session) |
| 7 | This Pattern Is Universal | Single CTA (inline one removed); rephrase close (gap is universal → AI closes it → at the edge) |

**Token discipline:** `index.html` is ~3,210 lines. Grep for line numbers first. Batch all index.html changes into ONE `replace_in_file` call per panel set.

### Stage C — Panel 5 2×2 redesign + new Panel 4 build
After Stage B panels are approved visually.

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| Financial Justification modal raw {{ }} | ✅ FIXED Session AJ | div balance net 0 |
| Panel 2 animated bars (infinite loop) | ✅ FIXED Session AL | h1P2Scrub scrubber |
| Panel 3 infinite bubble/drain loops | ✅ FIXED Session AL | opacity/scaleY scrubber-driven |
| Panel 1+4 flicker (color-emoji repaint) | ✅ FIXED Session AM | .h1-ok-dot + CSS squares |
| Panels 4/5/6 build shimmer (@keyframes) | ✅ FIXED Session AM | opacity-only, no transforms |
| Field Link (bandwidth claim, DEMO_MASTER §9) | ✅ REMOVED Session AM | wan-badge span deleted |
| ← Briefing re-entry button | ✅ ADDED Session AM | h1BriefingMode=true |
| STATE-vs-CONTEXT premise | ✅ LOCKED | Claim Ledger PREMISE row |
| SPE-174536 citation | ⚠️ UNVERIFIED | Using SPE-170776; 4.2 ft/s = representative |
| "GDC detects before SCADA" in Panel 2 + scenario | ⚠️ PENDING RULING | My rec: strip from briefing; keep as model output in scenario only |
| Panel 1 vertical space + lead-in copy | ⚠️ STAGE B | Too sparse; dives into VFD/sand too early |
| Panel kicker copy (Setup/Event/Hook/Moat/etc.) | ⚠️ DEFERRED | Simple pass after structure lands |

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
