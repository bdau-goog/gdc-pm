# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 8, 2026 (Session I+1 — doc-only handoff)
**git head:** `08c762e` (fix(ui): Session I integrity gaps — fault-type-aware status banner + envelope context banner)
**fault-trigger-ui image:** `sha256:72c65da2` (1/1 Running — Session I fix)
**inference-api image:** `sha256:d1194989` (1/1 Running — unchanged)
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
source .env && kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
source .env && kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
source .env && kubectl exec -n gdc-pm gdc-pm-rabbitmq-server-0 -- rabbitmqctl list_queues --vhost gdc-pm name messages consumers
```

**Expected when healthy:**
- All 8 pods 1/1 Running · ollama replicas: 1
- ollama_online: True · model: gemma4:latest
- field_intel: ~2 · rag_documents: 18
- telemetry.events: 0 messages · 1 consumer

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY — New spec this session)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

**The DEMO_MASTER.md was fully rewritten this session (I+1).** Read it carefully before writing any code. The core changes are:

- **H1 tab renamed "Discern"** (was "Detect")
- **No dual inject buttons** — single `⚡ Inject Unloading Anomaly` button that randomly selects Gas Lock or Fluid Drawdown behind the scenes
- **No Operating Envelope scatter chart** — replaced with dual-axis PIP/Amps Plotly trend chart
- **No 14-well pad strip** — removed
- **New layout**: Left 40% = shared persistent telemetry; Right 60% = switchable Decision Console with two sub-tabs: `🟡 SCADA View` and `🟢 GDC Advisor`
- **GDC-only Dynamic Wellbore Digital Twin** — CSS/HTML schematic showing fluid level (high/stable for Gas Lock with gold bubbles; depleted with brown sand for Drawdown)
- **Tab navigation**: Detect · Discern · Classify · Optimize

---

## STEP 3: Next Implementation Task — Session J

### The Task: Complete Clean-Slate Rewrite of the H1 "Discern" Tab

The current H1 tab HTML (lines 343–714 in `index.html`) and the related methods in `app.js` must be completely replaced with the Double-Blind Choice Game described in DEMO_MASTER.md §4. **Do not patch the old code. Start fresh within those lines.**

### Implementation Steps (In Order)

**Step 1 — app.py backend prep** (minimal, already done via `fluid_drawdown` in Session I):
- `launchHorizon1Unloading()` injects either `gas_lock` or `fluid_drawdown` randomly (50/50).
- The RAG seed documents are already seeded correctly (`field_intel` table seeded at inject time).
- No app.py changes needed unless the random selection logic needs to be backend-controlled.

**Step 2 — app.js state variables** (clean-slate reset for H1):
- **Remove**: `h1FaultType` external exposure in Vue data (keep internal to inject method — it should NOT be shown to the operator on inject, only revealed by GDC's RAG card).
- **Add**: `h1ConsoleTab: 'scada'` — tracks which sub-tab (SCADA or GDC) is displayed in the Decision Console.
- **Remove**: All references to `h1EvidenceWall`, `h1PumpOffExcluded`, `h1GasLockExcluded`, phase-plane chart code, Operating Envelope chart code, 14-well pad map code. These are all part of the old design and must be removed.

**Step 3 — `launchHorizon1Unloading()` method in app.js**:
- Randomly calls `launchHorizon1('gas_lock')` or `launchHorizon1('fluid_drawdown')` with Math.random().
- Does NOT set `h1FaultType` as a visible reactive property until revealed via GDC RAG card retrieval.
- Starts degrade, populates feed, starts advisor stream.
- `h1ConsoleTab` starts on `'scada'` (SCADA view is shown first).

**Step 4 — H1 tab HTML clean-slate** (replace lines 343–714 in `index.html`):
- Full-width banner: `DISCERN — ESP FLUID UNLOADING · [⚡ Inject Unloading Anomaly] [↺ Reset]`
- Left 40%: `div.h1-telemetry-col` containing sensor bars (PIP, Amps, Temp, Vib) + dual-axis Plotly chart (`h1-unloading-chart`).
- Right 60%: `div.h1-decision-col` containing sub-tab switcher + conditionally rendered sub-tab bodies.
  - `div.h1-sub-tab-bar`: Two buttons `[🟡 SCADA View]` `[🟢 GDC Advisor]` tracking `h1ConsoleTab`.
  - `div.h1-scada-view` (v-if="h1ConsoleTab==='scada'"): Ambiguous state text + two blind action buttons.
  - `div.h1-gdc-view` (v-if="h1ConsoleTab==='gdc'"): RAG card (clickable → opens document modal) + GDC-only wellbore schematic + GDC verdict + informed action buttons + override confirmation modal.

**Step 5 — Dynamic Wellbore Schematic** (inside `.h1-gdc-view`):
- CSS-only schematic (no external SVG). Approximate 200px-wide × 320px-tall column.
- Components: casing rectangle, perforation holes, fluid fill bar (`height` bound to `h1RawPsi`-normalized %), pump block, motor block.
- Gas Lock state: Fill level high (80%+), animated gold `.gas-bubble` divs rising.
- Drawdown state: Fill level low (20%), `.sand-particle` divs falling, pump intake exposed.

**Step 6 — Click-Through Document Modals** (two modals in `index.html`):
- `h1ShiftNoteModalOpen` / `h1SonicLogModalOpen` boolean flags.
- Each modal shows a realistic field form (static HTML, no API call needed).
  - Shift Handover Note: Header block (well, date, tour, operator name), paragraphs with GVF/GOR figures.
  - Acoustic Sonic Log: Baker Hughes-style survey form showing well parameters, measured dynamic fluid levels, pump submergence calculation.

**Step 7 — GDC Override Confirmation Modal** (inside app.js + index.html):
- `h1OverrideModalOpen: false` state variable.
- When operator clicks VFD Trim on GDC view during Drawdown: show modal, not immediate action.
- Modal text: "⚠ CRITICAL: GDC has confirmed fluid drawdown. Trim will seize pump. Override anyway?"
- Buttons: `[Override & Trim]` (triggers seizure) and `[Cancel]`.

**Step 8 — `_renderH1Charts(d)` rewrite** in app.js:
- Remove: All phase-plane chart code (`h1-phase-chart` DOM element, phase-plane traces).
- Replace with: Plotly dual-axis chart rendered into `h1-unloading-chart`.
  - Trace 1: PIP (blue, left y-axis) from `d.sensors.psi.traces[0]`
  - Trace 2: Motor Amps (green, right y-axis) from `d.sensors.amps.traces[0]`
  - Both traces trimmed to historical only (no projection lines in this chart).
  - Clean dark layout, minimal margins.

**Step 9 — CSS additions** in `styles.css`:
- `.h1-telemetry-col`, `.h1-decision-col`: Flex layout for the left/right split.
- `.h1-sub-tab-bar`, `.h1-sub-tab-btn`: Sub-tab styling, active/inactive states.
- `.h1-scada-view`, `.h1-gdc-view`: Card containers.
- `.h1-wellbore-schematic`: CSS wellbore cross-section container.
- `.gas-bubble`, `.sand-particle`, `.fluid-fill`: Keyframe animations.
- `.h1-rag-card`: Click-through document card.
- `.h1-doc-modal`: Full-screen professional document pop-up.

**Step 10 — Rebuild, deploy, verify**:
- `cd gke/fault-trigger-ui && docker build ... && docker push ...`
- `kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm`
- Verify both SCADA and GDC sub-tabs render correctly, random injection works, document modals open, override prompt fires on wrong action.

---

## Design Integrity Rules for Session J

1. **The fault type is NOT revealed in the SCADA View tab at all.** `h1FaultType` should remain hidden until GDC reveals it via the RAG card. The SCADA blind-gamble only works if the attendee doesn't know.
2. **Both action buttons (VFD Trim and Emergency Shutdown) must appear on BOTH sub-tabs.** The difference is that GDC guides the correct choice and blocks the wrong one.
3. **No dollar amounts on SCADA side** beyond the "representative" framing in the dilemma text. No hardcoded financial claims.
4. **VFD Trim during Drawdown on the GDC side requires 2 clicks** (the override modal). This is intentional: the deliberate friction makes it clear the operator is bypassing an active AI warning.
5. **The wellbore schematic is only visible in the GDC tab.** SCADA has no downhole model.

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- Batch all edits to same file in ONE `replace_in_file` call
- ALL kubectl/gcloud commands require `source .env &&` prefix
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
