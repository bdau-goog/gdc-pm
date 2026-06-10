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

## STEP 3: NEXT TASK — H1 PANEL + SCENARIO REDESIGN (START IN PLAN MODE)

> **⚠️ H1 IS NOT DONE. Session AO relabeled text only. The detection race is still structurally present — two separate indices, two scrubber markers, two reveal times. The real work is next session.**

### Your locked thesis
There is a **class of SCADA-informed decisions that skew toward safety/asset-protection** and, in doing so, **cost money and lose production** (reflexive shut-ins, unnecessary conservatism). Better decisions — less outage, lower cost — are possible when **AI + RAG + active document monitoring + LLM is implemented sovereignly on GDC.** This reduces to one line:

> **Better informed = less cost, more uptime, more production.**

ESP unloading is **one worked example of the class — not the point itself.**

### Hard constraints (locked, non-negotiable)
1. **Remove ALL detection-lead over SCADA.** This is structural — not copy:
   - `app.py` ~L6113–6141: two indices (`gdc_detect_idx`, `scada_alarm_idx`, `lead_time_minutes`) → **collapse to a single shared alarm moment**
   - `index.html` scrubber: two markers → **one alarm marker**
   - `app.js` `_renderH1ReplayChart` annotations + `h1CursorIdx` watcher that reveals GDC at `gdc_detect_idx` vs SCADA at `scada_alarm_idx` → **both reveal at the same alarm index**
   - The ONLY post-alarm difference: **decision quality** (GDC adds fused context), never timing.
2. **Remove 'sand' from the narrative spine.** No sand-bridging, no "moderate-sand well" as the stakes-setter, no AR-trim, no sand decision matrix (Panel 5). Reframe as a **generic mature ESP**; describe the use-case as **a class of problems GDC solves**. Sand physics may live deep in ⓘ Reference but is out of the story.
3. **Remove the $150k catastrophe story.** No catastrophe number, no "PUMP SEIZED" / "UNPLANNED OUTCOME." Honest contrast: *production-deferring shut-in (lost uptime + restart cost)* vs. *informed production-preserving action (cheaper, more uptime)*. Quieter, defensible delta — no scary outlier.

### Guidance for my review (NOT a fixed spec — I propose a panel flow for your sign-off)
User's suggested arc to review and refine:
1. What is an ESP?
2. What is unloading?
3. What might cause unloading?
4. Why do they look the same (on the sensor)?
5. How do operators react today? — the *class of problems* beat: SCADA-informed default skews protective → production deferred, cost incurred
6. How GDC decides better — fuses context → production-preserving action → framed as uptime + cost only

**My job at session start:** read the current panel content, then **propose a refined 6-panel flow with content as ASCII wireframes/tables for user review** BEFORE any code.

### Build state to rework (do not rebuild from scratch)
- 6 briefing panels at `index.html` ~L368–908. **Panels 1, 3, 5** are sand-dependent → rework. **Panels 4** (STATE vs CONTEXT) and **6** (universal class, 3 rows) are reusable.
- Live scenario: `/api/h1/scenario-replay` (app.py ~L6060–6145) + `loadH1Scenario` / `_renderH1ReplayChart` / `h1CursorIdx` watcher (app.js) + console views (index.html ~L1074–1345). **This is where the detection race physically lives.**
- H2 has the same two-index pattern (app.py ~L6307–6350) — same fix applies there in a later session.

### Method
1. **PLAN MODE** — read current panel content; propose revised panel flow + content; get user sign-off
2. **Agree single-alarm interaction model** (one marker, both views reveal together, GDC adds context not lead-time)
3. **ACT** — backend (collapse indices) → briefing panels → scenario console → deploy with explicit digest → verify
4. **Update Claim Ledger** — retire detection-lead row and $150k row; surviving spine is STATE-vs-CONTEXT / better-informed-decision (PREMISE row SURVIVES)

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
