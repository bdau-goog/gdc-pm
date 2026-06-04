# Next Session Prompt — GDC Edge AI Demo (Operational State)

**Date:** June 4, 2026 (Session L end)  
**Git Head:** `e500c4d` — clean working tree  
**fault-trigger-ui image digest:** `sha256:5c6d33ae114cb6b234bea46e074f3cb675d264650c4ceab73c956c0fc7762b3f`  
**Branch:** `feature-trio-scenarios` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected healthy:**
- All pods 1/1 Running · fault-trigger-ui-587fc8fb94-vqdst
- ollama_online: True · model: gemma4:latest
- field_intel: ~99–105 rows · rag_documents: 18 rows

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

Also read the **last 2 entries** in SESSION_LOG.md (Sessions L and K).

---

## STEP 3: What Was Built This Session (H1 UI Redesign)

**Live at:** `http://gdc-pm.bdau.io` → "Detect" tab

### Changes deployed (commit `e500c4d`):

**Tab nav:** Renamed Horizon 1/2/3 → Detect / Discern / Optimize. Fleet Financials tab removed entirely.

**H1 banner:** Now a single line — "Detect — ESP Gas Lock · ESP-ALPHA-1 [ⓘ] [Inject] [Reset]". All physics description is hidden behind the ⓘ collapsible panel. "25m lead time" badge removed from banner.

**Dual-Reality Bar** (new hero element, replaces old status bar):
- Two-column compact bar spanning full width
- LEFT: SCADA · ESP-ALPHA-1 — 4 sensor readings → "✓ All Nominal · No alarm"
- RIGHT: GDC AI · ESP-ALPHA-1 — same 4 sensors + 4 context chip rows (📋 Shift note, 🧪 Lab: GOR↑, ⚡ VFD events, 📖 API RP 11S) → verdict line changes on inject
- Context chips dim/inactive pre-injection, activate via `h1EvidenceActive` counter on inject
- Verdict line: `dr-monitor` (gray) → `dr-alert` (orange) on inject → `dr-ok` (green) on recovery

**New 3-column main body** (`h1-body`):
- LEFT: `h1-well-strip` (82px wide, fixed) — thin SVG wellbore animation strip
- CENTER: `h1-center` (36%) — sensor tabs (PIP/Amps/Temp) + chart (200px) + Window of Options (`v-if="h1Injected"`)
- RIGHT: `h1-copilot-pane` (flex:1, ~52%) — LLM copilot fills full height; compact intel feed (3 items max) at bottom

**Charts now load on tab open** — `setMainTab('horizon1')` now fetches `/api/plot/forecast-data/ESP-ALPHA-1` immediately and renders baseline chart, even before injection.

**Window of Options** — now hidden until fault is injected (`v-if="h1Injected"`).

**Evidence wall + scada-compare boxes removed** — their information absorbed into the dual-reality bar.

**Live intel feed** — reduced from 7 items to 3, compact `.h1-ic-row` style.

**`_renderH1Charts`** — removed stale `h1-scada-chart` element reference.

---

## STEP 4: Next Session Flow

### A. First: Review Detect tab in browser and collect any remaining feedback

Check:
1. Dual-reality bar — does the two-column comparison read clearly?
2. SVG well strip — visible and decorative (narrow, left column)?
3. Copilot — does it fill the right side and feel dominant?
4. Charts — do they show live data on tab open (before injection)?
5. Window of Options — hidden until inject? Appears cleanly below chart?

### B. After feedback: H2 (Discern) tab redesign

Per DEMO_MASTER.md §5:
- Reuse ALL CSS from H1 redesign (`.dr-bar`, `.h1-body`, `.h1-copilot-pane`, `.h1-intel-compact`, `.wopt-container`)
- Primary visual: two-line superimposed chart — Vibration (rising, orange) + Motor Temp (flat, blue)
- Well SVG: pump body GREEN (healthy), surface flowline shows orange slug pulses
- H2 evidence chips in dual-reality bar: 📊 Vibration↑, 📊 Temp─(flat), 📋 Shift note, 🧪 Separator test, 📋 Choke log, 📖 OEM guide
- LLM copilot: "$1,500 truck roll, not $150,000 pump pull"
- No Window of Options for H2 (slug flow → dispatch, no PNR countdown)

---

## Known Integrity Violations — Fix Next Session

| Issue | Location | Symptom | Root Cause | Fix Deadline |
|-------|----------|---------|------------|-------------|
| Financial Justification modal shows raw `{{ }}` template text | `index.html` lines 2553–2636 | Modal opens but all Vue expressions render as literal text (e.g., `{{ justifyData.fault_label }}`) | Unknown — possibly Vue 3 template compilation error caused by our new H1 HTML preceding this section. Pre-existing in commit `9951199`. Cannot confirm without browser devtools. | Session M |

**Investigation needed:** Open browser devtools console on `http://gdc-pm.bdau.io` and check for Vue 3 template compilation warnings/errors. The modal is accessed via the Architecture tab. Look for any `[Vue warn]` messages related to template compilation.

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — no `browser_action` tool
- `feature-trio-scenarios` stays separate from `main`
- XGBoost `*.ubj` models — do not retrain
- Fleet Operations tab: do NOT re-add
- Financial case: LLM only, no static financial cards
- Token budget: batch all edits to same file in ONE replace_in_file call
