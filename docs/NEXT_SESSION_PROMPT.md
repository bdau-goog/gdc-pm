# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 10, 2026 (Session AI — Sprint 2c+2d ✅ H1 Briefing Panels 4+5 deployed)
**git head:** `db26131` (feat(sprint2d): H1 Briefing Panel 5 — Why Sand Changes Everything (2x2 decision matrix))
**fault-trigger-ui image:** `sha256:3f8ecc7cbef399b964c61f803b9d2ce11c1dfad71aaf287beb74de8d9d8ec52e` (Session AI — Sprint 2d deployed)
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

## STEP 3: Session AI COMPLETE ✅ — Next Task is Sprint 2e

### Session AI Summary
Sprints 2c AND 2d complete this session.

- **Sprint 2c** (commit `52baa53`): H1 Briefing Panel 4 — "STATE vs. CONTEXT". Full-screen two-column animated reveal. LEFT = blue STATE column (4 sensor tiles fading in at 0.1/0.4/0.7/1.0/1.3s). RIGHT = amber CONTEXT column (4 document cards at 1.6/2.2/2.8/3.4/4.0s). Bottom quote: *"You cannot instrument your way out of a context gap."* CSS: `h1-p4-fadein` + `h1-p4-state-row` + `h1-p4-ctx-card` with `animation-fill-mode:both`.

- **Sprint 2d** (commit `db26131`): H1 Briefing Panel 5 — "Why Sand Changes Everything". 3×3 CSS grid decision matrix with scope badge "moderate-sand well · AR-trim". Cells appear one by one via `h1-p5-cellin` scale(0.92→1) animation: Cell 1 VFD TRIM × GAS LOCK ✅ SAFE ~$2,500 (delay 0.2s) → Cell 2 VFD TRIM × DRAWDOWN ❌ CATASTROPHIC ~$150k with `h1-p5-sand-fill` animation growing from 0→82% at 2.5s (sand accumulating bar) → Cell 3 SHUT-IN × GAS LOCK ⚠ DEFERRED ~$1-3k restart (delay 1.8s) → Cell 4 SHUT-IN × DRAWDOWN ✅ RECOVERABLE (delay 2.6s). Bottom quote row (delay 3.4s): *"Blind to the cause, trim risks seizure. Shut-in is safe in both — the rational default."* + *"The context that removes the blindness is in the documents. GDC reads them in seconds."* Dot 5 upgraded from static cosmetic to reactive Vue-bound. Next `< 4` → `< 5`. Run the Scenario `===4` → `===5`. Hint text: 5-case ternary. HTML entities used (&#x2705; &#x274C; &#x26A0;) in place of emoji to avoid any template-parse issues. Deployed `sha256:3f8ecc7cbef399b964c61f803b9d2ce11c1dfad71aaf287beb74de8d9d8ec52e`.

**Deployment note (permanent):** `kubectl rollout restart` with `:latest` does NOT pull new images (GKE node cache). Always use:
```bash
kubectl set image deployment/fault-trigger-ui -n gdc-pm \
  fault-trigger-ui=us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui@sha256:<digest>
```

### NEXT TASK — Sprint 2e: H1 Briefing — Panel 6 (Universal Pattern)
**File:** `gke/fault-trigger-ui/index.html` (ONE batched replace_in_file call)
**Spec:** `docs/SPRINT_PLAN.md §Sprint 2e` and `DEMO_MASTER.md §4 Panel 6`

Panel 6 — *This Pattern Is Universal* — 4-row animated table:
- **4-row table appears row by row** (each row: asset | STATE sensor | CONTEXT document):
  - O&G ESP · PIP / Amps declining → Workover record / GOR trend / shift note
  - Power transformer · Load current rising → Loading plan / maintenance log / seasonal forecast
  - Factory motor · Vibration rising → Lubrication record / OEM bulletin / line throughput log
  - Haul truck · Fuel consumption rising → Haul-road report / service history / grade profile
- Caption per row: "sensor STATE → document CONTEXT" arrow
- Full-width quote: "This is not an oilfield trick. It is the structural gap in every industrial AI deployment."
- `[▶ Run the Scenario]` CTA — hands off to `h1BriefingMode=false; loadH1Scenario()`
- Progress dot 6 activates. Next button removed (only Run the Scenario). Run the Scenario: `===5` → `===6`
- Dot 6 upgraded from static cosmetic to reactive Vue-bound.

**Note on Financial Justification modal:** Pre-existing bug (confirmed present before Session AI work) — the modal div has `position:fixed;inset:0` and may intercept clicks before Vue fully mounts. Root cause unknown (not related to Session AI changes — div balance was -21 before and after). Investigate separately if time permits; not blocking the briefing panels.

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
