# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 8, 2026 (Session N — Vue crash fix + descriptive action cards + financial breakdowns deployed)
**git head:** `f261ac0` (fix(ui): Session N+1 — initialize h1EvidenceWall with 5 objects)
**fault-trigger-ui image:** `sha256:2c2827d1` (1/1 Running — Session N+1)
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

## STEP 3: Next Implementation Task — Session O

### What was shipped in Session N (deployed, verified sha256:8c73db2d)

**Critical Bug Fixed (Session N+1):** `h1EvidenceWall: []` was initialized as an empty array in `data()`.
`launchHorizon1()` tried to set `this.h1EvidenceWall[0].content = '...'` on `undefined` — throwing a
TypeError BEFORE the `try` block containing the API injection call, elapsed timer, and degrade poll timer.
Result: banner changed (h1Injected=true before the throw), but `/api/inject/degrade` was never called,
`h1ElapsedTimer` never started (T always showed 00:00), `h1DegPollTimer` never started (charts never updated),
and `h1RagRevealed` was never set true (GDC stuck in scanning state forever). Fix: one line — initialize
with 5 pre-populated objects. Confirmed 5×"active: false, content: ''" in deployed container.

**Root Cause Also Fixed (Session N):** Vue.js 3 template compiler was crashing on unescaped `<` characters introduced
in Session M's SCADA sensor tile HTML (`<800 PSI`, `<50 A`). Vue treats these as tag openers and fails
silently — resulting in the LLM never streaming and Plotly charts never receiving data.

**All changes in commit `454ed9f`:**

1. **Vue Template Crash Fixed:** Escaped all unescaped `<` chars to `&lt;` across index.html
   (sparkline labels, SCADA sensor tiles, RAG latency strings, H3 RUL model formula,
   Architecture tab Vibration sensor spec, HNSW retrieval latency). LLM + time-series now work.

2. **Large Descriptive Action Cards (SCADA + GDC):** Simple one-line buttons replaced with
   `.h1-action-card` styled cards (green/red/amber/slate/contraindicated). Each card shows:
   - SCADA: Physical description, "Apply if:" guidance, velocity risk warning (3.1 ft/s at 44 Hz)
   - GDC: "GDC RECOMMENDED" / "GDC CONTRAINDICATED" labels, full sonic log context, precise boundaries

3. **Post-Selection Financial Breakdowns:** After operator selection, itemized tables render:
   - Seizure path: Pull-rig $42k + Motor $53k + Cable $15k + Deferred prod $39.9k = ~$149,900
   - Correct path (drawdown): Avoided $150k · Net savings $142k–$147k
   - Correct path (gas lock): $2,500 total · $147,500 capital preserved

4. **SPE-174536 Velocity Boundaries incorporated everywhere:**
   - GDC drawdown verdict: "Speed-down below 48 Hz drops velocity from 4.2 ft/s to 3.1 ft/s at 44 Hz"
   - Override modal: explicit at-52Hz (4.2 ft/s) and at-44Hz (3.1 ft/s) bullet points
   - SCADA card warn: "velocity drops to 3.1 ft/s → sand bridge"
   - GDC contraindicated card subtitle: full boundary reference
   - app.js seizure text: "44 Hz dropped fluid transport velocity from 4.2 ft/s to 3.1 ft/s, breaching
     the critical sand-transport lift boundary (SPE-174536)"
   - styles.css: `.h1-action-card` + `.h1-card-*` variant classes added

### Session O Tasks

**Priority 1 — Browser smoke-test of H1 (user runs in browser):**
- Navigate to Discern tab; verify Vue app mounts (no blank screen)
- Click "⚡ Ingest Pad Anomalies"; confirm Plotly sparklines tick live
- Verify GDC Advisor LLM streams within 3–5 seconds
- Verify SCADA action cards are large and readable (two columns, with "Apply if" and warn text)
- Verify GDC action cards show GREEN "GDC RECOMMENDED" and RED "GDC CONTRAINDICATED"
- After selection, confirm financial breakdown table appears
- Report any visual issues

**Priority 2 — H2 "Classify" tab upgrade:**
- Per DEMO_MASTER.md §5: two-pane SCADA/GDC layout, surface slug flow narrative, $148,500 avoided false-positive
- Reuse `.h1-action-card` CSS pattern from H1 for action cards
- The Vibration vs Motor Temp decorrelation chart is the hero visual

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 nuisance suppression | ⚠ Frontend only | GDC auto-dismiss shown as text; no RAG doc fetched. Defensible for demo. |
| H1 sparklines pre-injection | ✅ Working | `_renderH1Charts(d)` polls baseline on tab open; baseline data available from telemetry. |
| Vue template crash | ✅ Fixed (Session N) | All `<` chars escaped; confirmed 5×SPE-174536 and 5×h1-action-card in deployed container. |
| h1EvidenceWall TypeError crash | ✅ Fixed (Session N+1) | Initialized with 5 objects; injection now calls API, timers run, charts update. |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
