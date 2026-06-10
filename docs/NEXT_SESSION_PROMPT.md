# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 10, 2026 (Session AI — Sprint 2c ✅ H1 Briefing Panel 4 deployed)
**git head:** `52baa53` (feat(sprint2c): H1 Briefing Panel 4 — STATE vs. CONTEXT animated two-column reveal)
**fault-trigger-ui image:** `sha256:6a52012088427e3693bc9027050370461940d5ff020fe87e293ce4dac9d5bbf9` (Session AI — Sprint 2c deployed)
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

## STEP 3: Session AI COMPLETE ✅ — Next Task is Sprint 2d

### Session AI Summary
Sprint 2c complete this session.

- **Sprint 2c** (commit `52baa53`): H1 Briefing Panel 4 — "STATE vs. CONTEXT". Full-screen two-column animated reveal: LEFT = blue STATE column (header "STATE", 4 sensor tiles: PIP 612 PSI↓, AMPS 34.2 A↓, WINDING TEMP 246°F, VIBRATION 0.41 in/s, staggered `h1-p4-state-row` fade-in at 0.1/0.4/0.7/1.0/1.3s delays), RIGHT = amber CONTEXT column (header "CONTEXT", 4 document cards appearing one by one: WORKOVER RECORD→GOR TREND→OFFSET FRAC REPORT→SHIFT NOTE, `h1-p4-ctx-card` fade-in at 1.6/2.2/2.8/3.4/4.0s delays). Full-width bottom quote: *"You cannot instrument your way out of a context gap."* Dot 4 upgraded from static cosmetic to reactive Vue-bound (same 8px as dots 1-3). Next button: `< 3` → `< 4`. Run the Scenario: `===3` → `===4`. Hint text extended to 4-case ternary. CSS: `@keyframes h1-p4-fadein` + `.h1-p4-state-row` + `.h1-p4-ctx-card` (animation-fill-mode:both for proper pre/post state). Deployed `sha256:6a52012088427e3693bc9027050370461940d5ff020fe87e293ce4dac9d5bbf9`.

**Deployment note (permanent):** `kubectl rollout restart` with `:latest` does NOT pull new images (GKE node cache). Always use:
```bash
kubectl set image deployment/fault-trigger-ui -n gdc-pm \
  fault-trigger-ui=us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui@sha256:<digest>
```

### NEXT TASK — Sprint 2d: H1 Briefing — Panel 5 (Sand Stakes / Decision Matrix)
**File:** `gke/fault-trigger-ui/index.html` (ONE batched replace_in_file call)
**Spec:** `docs/SPRINT_PLAN.md §Sprint 2d` and `DEMO_MASTER.md §4`

Panel 5 — *Why Sand Makes the Stakes Asymmetric* — 2×2 animated decision matrix:
- **Scope badge visible:** "moderate-sand well · AR-trim"
- **2×2 cell-by-cell reveal:** Trim + Gas Lock (✅ ~$2,500) → Trim + Drawdown (❌ $150k seizure, animated sand packing) → Shut-in + Gas Lock (⚠️ deferred production) → Shut-in + Drawdown (✅ recoverable)
- Bottom quote: "Blind to the cause, trim risks seizure. Shut-in is safe in both — the rational default."
- Sub-quote: "The context that removes the blindness is in the documents. GDC reads them in seconds."
- Navigation: [← Back] [Next →] (advances to panel 6)
- Progress dot 5 activates when at panel 5
- Extend Next: `< 4` → `< 5`; Run the Scenario: `===4` → `===5`

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
