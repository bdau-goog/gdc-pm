# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 10, 2026 (Session AI — Sprint 2c+2d+2e ✅ H1 Briefing ALL 6 Panels deployed)
**git head:** `a8c5d27` (feat(sprint2e): H1 Briefing Panel 6 — This Pattern Is Universal)
**fault-trigger-ui image:** `sha256:ca6cea662e39501e9f19e21112f2a2a2eb3416abbf2298cec0d1f74f4e56e3e9` (Session AI — Sprint 2e deployed)
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

## STEP 2: Read DEMO_MASTER.md + SPRINT_PLAN.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md    # Full spec — Session AF rewrite
cat ~/gdc-pm/docs/SPRINT_PLAN.md    # Sprint breakdown + panel specs
```

---

## STEP 3: Session AI COMPLETE ✅ — H1 Briefing DONE (all 6 panels) — Next Task is Sprint 3

### Session AI Summary
Sprints 2c, 2d, AND 2e complete this session. **The H1 Briefing is now fully built (all 6 panels).**

- **Sprint 2c** (commit `52baa53`): Panel 4 — STATE vs. CONTEXT
- **Sprint 2d** (commit `db26131`): Panel 5 — Why Sand Changes Everything (2×2 decision matrix)
- **Sprint 2e** (commit `a8c5d27`): Panel 6 — This Pattern Is Universal. 4-row animated industry table slides in row by row via `h1-p6-rowin` (translateX -16px→0, 0.5s ease-out, `both` fill): Row 1 O&G/ESP (delay 0.3s, blue border) → Row 2 P&E/Transformer (delay 1.2s, purple border) → Row 3 MFG/Factory motor (delay 2.1s, amber border) → Row 4 MINING/Haul truck (delay 3.0s, yellow border). Each row: industry badge | STATE column (sensor readings) | → arrow | CONTEXT column (document types). Closing quote at 3.8s: *"This is not an oilfield trick. It is the structural gap in every industrial AI deployment."* + *"GDC: the AI goes to the data."* Run the Scenario CTA button at 4.3s (inline in panel + footer). Dot 6 upgraded from static cosmetic to reactive Vue-bound. Next `< 5` → `< 6`. Run the Scenario `===5` → `===6`. Hint text: 6-case ternary. All HTML entities (&#x2192; &#x2191; &#x2193; etc.) to avoid any emoji/Unicode parse issues. Deployed `sha256:ca6cea662`.

**Deployment note (permanent):** `kubectl rollout restart` with `:latest` does NOT pull new images (GKE node cache). Always use:
```bash
kubectl set image deployment/fault-trigger-ui -n gdc-pm \
  fault-trigger-ui=us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui@sha256:<digest>
```

### NEXT TASK — Sprint 3: H2 Briefing (3 Panels)
**File:** `gke/fault-trigger-ui/index.html` (ONE batched replace_in_file call per sub-sprint)
**Spec:** `docs/SPRINT_PLAN.md §Sprint 3` and `DEMO_MASTER.md §5`

H2 Briefing follows the same pattern as H1 (h2BriefingMode / h2BriefingPanel). 3 panels:

**Panel 1 — What is Slug Flow?**
- Surface slugs → cyclic vibration at pump intake
- Animated: slug pulses in production tubing, PDG gauge showing cyclic PIP

**Panel 2 — Why It Looks Like a Failing Pump**
- Vibration rising (alarming STATE) — SCADA HI fires
- "The sensor shows the pattern. It doesn't tell you what's driving it."

**Panel 3 — STATE vs. CONTEXT (the exoneration)**
- STATE: vibration rising + flat motor temp → "something changed, but not at the motor"
- CONTEXT cards reveal: choke log (3 adjustments) · separator test (1.8 bbl slugs) · shift note ("pumping rough but temp normal")
- "The documents say: do NOT pull. $1,500 surface adjustment vs. $150k false alarm."
- `[▶ Run the Scenario]` CTA

**Implementation:** Add `h2BriefingMode: true` + `h2BriefingPanel: 1` to Vue data in app.js. Wrap existing H2 scenario replay in `<template v-else>`. Insert briefing `<div v-if="h2BriefingMode">` before it.

**Note on Financial Justification modal:** Pre-existing bug (confirmed present since before Session AI work — div balance -21 unchanged). Not blocking briefing demo. Investigate in a separate session.

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| "200 GB/day for 38 wells" (info panel) | ✅ FIXED Session AG | Deleted; replaced with sovereignty framing |
| "VSAT round-trip 15–25 minutes" (info panel) | ✅ FIXED Session AG | Deleted |
| "E-House on the well pad" deployment framing | ✅ FIXED Session AG | Replaced with RTOC / sovereign data center |
| "No cloud dependency for the decision" tagline | ✅ FIXED Session AG | Replaced with "No public-cloud dependency — sovereign, outage-immune" |
| NERC-CIP cited for upstream O&G | ✅ FIXED Session AG | Scoped to P&E BES only in all occurrences |
| All Session AE RT fixes | ✅ FIXED Session AE | 280°F, IEC 60085, scada_rule_fired, lead-time banner |
| STATE-vs-CONTEXT premise | ✅ LOCKED DEMO_MASTER §3 | Claim Ledger PREMISE row added |
| Sand/shut-in physics | ✅ LOCKED DEMO_MASTER §4.1 + P5-A/B/C | Scoped: moderate-sand well · AR-trim |
| SPE-174536 citation | ⚠️ UNVERIFIED | Replaced with SPE-170776 in Claim Ledger P4; 4.2 ft/s = representative, not a constant |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — use `node scripts/ui_smoke.mjs` instead
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- **Deploy with explicit digest** — `kubectl rollout restart` with `:latest` does NOT pull from registry on this cluster (node cache). Always use `kubectl set image ... @sha256:<digest>`
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,400 lines, `index.html` ~2,827 lines, `app.js` ~2,300 lines — always grep for line numbers first
- H2 uses inference-api (not local esp_classifier.bst) — local .bst is 4-class without slug_flow
- Gas Lock / Drawdown STATE identical on intake-only wells — premise is now "decision window ambiguity" not "physically impossible forever"
