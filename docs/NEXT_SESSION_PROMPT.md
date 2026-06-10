# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 10, 2026 (Session AQ — H1 Briefing Batch 2 deployed)
**git head:** `71b68b3` (fix(h1-briefing-batch2): P1 remove sand-stakes row + move callout top, P2 strip dev-leak, P3 soften drawdown footer, P5 replace sand matrix with How Operators Decide Today)
**fault-trigger-ui image:** `sha256:2fd95932a9b8ae9ca0eb6c961cf9a031b264a97ad69705fb8197a05999414a9a` (Session AQ)
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

## STEP 3: NEXT TASK — H1 Briefing Batch 3 + H2 Briefing (Sprint 3)

> **✅ Session AQ completed Batch 2:** All 4 briefing panel reworks deployed and verified live.
> P1: sand-stakes row removed, callout moved to top; P2: dev-leak stripped; P3: drawdown footer softened;
> P5: sand matrix replaced with "How Operators Decide Today" two-column layout.

### Remaining H1 work (Batch 3):
1. **OEM Troubleshooting Guide (Doc 3)** — no click handler. Needs modal + G1–G6-gated content. Low priority — gate on user direction.

### Next major work — H2 Briefing (Sprint 3):
3 animated panels, same architecture as H1 briefing (`h2BriefingMode`/`h2BriefingPanel` in Vue data, `<template v-else>` wrapper around existing H2 scenario replay):

#### Panel 1 — What is Slug Flow?
- Surface slugs → cyclic vibration at pump intake
- Animated: slug pulses in production tubing, PDG gauge showing cyclic PIP

#### Panel 2 — Why It Looks Like a Failing Pump
- Vibration rising (alarming STATE) — SCADA HI fires
- "The sensor shows the pattern. It doesn't tell you what's driving it."

#### Panel 3 — STATE vs. CONTEXT (the exoneration)
- STATE: vibration rising + **flat motor temp** → "something changed, but not at the motor"
- CONTEXT cards reveal: choke log (3 adjustments) · separator test (1.8 bbl slugs) · shift note ("pumping rough but temp normal")
- "The documents say: do NOT pull. $1,500 surface adjustment vs. $150k false alarm."
- `[▶ Run the Scenario]` CTA

### Method:
1. Read current H2 scenario header in index.html (`grep -n "h2BriefingMode\|tab-horizon2\|Classify"`)
2. Propose panel wireframes for user review
3. Get sign-off BEFORE writing HTML
4. Batch all changes into ONE `replace_in_file` call on index.html

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
| H1 detection-race framing | ✅ FIXED Session AP | Single alarm_idx, both views reveal together |
| H1 Bayes posterior overconfidence | ✅ FIXED Session AP | 99.6% → 93.1% (LRs 3/2/1.6/1.4) |
| H1 contraindicated card + seizure path | ✅ REMOVED Session AP | drawdown both cards → shut-in |
| Tab default landing | ✅ FIXED Session AO | mainTab → 'horizon1'; How It Works → ⓘ Reference |
| Panel 6 Mining row | ✅ REMOVED Session AO | 3 rows remain: O&G / P&E / MFG |
| Panel 1 sand-stakes row ($150k on setup) | ✅ FIXED Session AQ | Row removed; callout moved to top |
| Panel 2 dev-leak line + detection race text | ✅ FIXED Session AQ | Stripped "Sprint 2b–2e" + "GDC detects before SCADA" |
| Panel 3 drawdown footer ($150k seizure) | ✅ FIXED Session AQ | Softened to "riskier" + "shut-in is correct" |
| Panel 5 sand matrix → "How Operators Decide" | ✅ FIXED Session AQ | Full replacement; two-column layout |
| OEM Troubleshooting Guide no click handler | ⚠️ BATCH 3 | Doc 3 needs modal + content (G1–G6 gate) |
| STATE-vs-CONTEXT premise | ✅ LOCKED | Claim Ledger PREMISE row |
| SPE-174536 citation (on-screen in GDC verdict) | ⚠️ UNVERIFIED | Still on screen in Zone-1 drawdown text — OK in ⓘ Reference, flag for removal from main verdict |
| SPE-174536 citation in override modal | ⚠️ NOTE | Override modal still references SPE-174536; modal is low-visibility path now |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — use `node scripts/ui_smoke.mjs` or `curl`
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- **Deploy with explicit digest** — `kubectl rollout restart` with `:latest` does NOT pull from registry
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,400 lines, `index.html` ~3,200 lines, `app.js` ~2,300 lines — grep for line numbers first
- H2 uses inference-api (not local esp_classifier.bst)
