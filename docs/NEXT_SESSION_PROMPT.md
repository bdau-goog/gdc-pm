# Next Session Prompt — GDC Edge AI Demo (Operational State)

**Date:** June 4, 2026 (Session N end — design approved, not yet implemented)
**Git Head:** `ae3a03f` — clean working tree
**fault-trigger-ui image digest:** `sha256:55e5626853cc1d6da10390159b90432eeacaf60e265254d765428cdb1a26a0db`
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
- All pods 1/1 Running · fault-trigger-ui-64d4b6b944-9m5xb
- ollama_online: True · model: gemma4:latest
- field_intel: ~99–110 rows · rag_documents: 18 rows

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

Also read the **last 2 entries** in SESSION_LOG.md (Sessions N and M).

---

## STEP 3: Implementation Task — H1 Chart Redesign + Layout Fixes

This session has ONE task: implement the approved chart redesign and layout changes in `index.html`. All changes in a single batched `replace_in_file` call.

### Approved Design (from Session N discussion — FINAL, DO NOT REVISIT)

#### A. Primary H1 Chart: "Minutes Until Pump Failure" — 3-Line Context Fusion

The central visual argument of the Detect tab. **No raw sensor values on the Y-axis.**

```
Y-axis: "Minutes Until Pump Failure" (descending = more urgent)
X-axis: Rolling time window (showing last ~30 min of history)

Line 1 (gray, thick):
  "📡 SCADA Threshold Monitoring"
  Stays HIGH — deterministic threshold hasn't been crossed yet
  Honest: SCADA is not stupid, it just can't compute the pattern

Line 2 (orange dashed):
  "⚡ GDC AI: Sensor-Only"
  XGBoost pattern recognition, no documents
  Source value: d.time_to_scada_minutes from API
  Drops faster than SCADA line — multi-sensor correlation working

Line 3 (solid bright orange, LOWEST):
  "⚡ GDC AI: Context-Fused"
  After reading shift log + lab test from AlloyDB RAG
  Source value: d.adjusted_rul_minutes from API
  Drops FASTEST — RAG pipeline amplifying the signal
  
Shaded bracket between Line 2 and Line 3:
  Label: "⚡ Context Fusion: −[N]m (shift note + GOR lab test [¹][³])"
  N = Math.round(time_to_scada_minutes - adjusted_rul_minutes)
  Only rendered when N > 0 (gap exists)
```

**Pre-injection state:** Three flat horizontal lines near a nominal "well healthy" level (e.g., 120+ minutes). Clean, calm, no alarm.

**Post-injection behavior:** GDC lines begin declining as health score degrades. Context-fused line diverges below sensor-only line ~15–30s after injection (when first RAG documents are retrieved). Presenter can point to the divergence in real-time.

**Implementation notes:**
- `_renderH1Charts(d)` receives the full forecast-data API response
- `d.time_to_scada_minutes` = sensor-only estimate (already in API)
- `d.adjusted_rul_minutes` = RAG-adjusted estimate (already in API)
- Pre-injection: render flat lines; post-injection: plot actual computed values
- Chart ID: keep `id="h1-gdc-chart"` (existing DOM element)
- Do NOT hardcode any time values — all computed from live API response

#### B. Secondary Chart: SCADA Raw Telemetry (retain below primary)

Keep a smaller SCADA telemetry chart below the primary chart with a horizontal NS resize handle between them. The SCADA chart shows:
- Raw PIP/Amps/Temp (selected sensor tab) as a live line
- SCADA alarm threshold as a flat dashed red line
- Post-injection: the live line declines slowly while staying ABOVE the threshold
- Label: "📡 SCADA View — No alarm triggered"
- This chart is the honest companion: SCADA isn't wrong, it just fires later

Chart ID for SCADA: `id="h1-scada-chart"` (new element to add)

#### C. Layout Changes

1. **Well strip → far right:** Move `.h1-well-strip` div from BEFORE h1-center to AFTER h1-copilot-pane (last child of h1-body). Set `width:180px; align-self:stretch; order:3`.
2. **Add SVG callout labels** on the well strip (dynamic, large enough to read):
   - At pump intake: `"Intake: Nominal"` → `"Intake: 68% GVF ⚠"` on inject
   - At motor: `"Motor: Cooling normal"` → `"Motor: Cooling lost ⚠"` on inject
3. **Column order:** Charts (left, ~44%) | GDC Advisor (center, ~38%) | Well schematic (right, ~18%)
4. **"Copilot" → "GDC Advisor" everywhere:**
   - HTML label: `"🤖 GDC Advisor — Gemma 4 · On-Cluster · No Cloud Required"`
   - Placeholder text: `"Ask a follow-up question…"` → keep, just rename the header
   - CSS class rename: `.h1-copilot` → `.h1-advisor` (and all variants)
   - Vue data: `h1CopilotHtml` → `h1AdvisorHtml`, `h1CopilotStreaming` → `h1AdvisorStreaming`, `h1CopilotTimer` → `h1AdvisorTimer`, `h1CopilotText` → `h1AdvisorText`
   - Method: `_startCopilotStream` → `_startAdvisorStream`
   - **IMPORTANT:** Update all uses across index.html in one pass — do NOT miss any
5. **Dynamic feed poll:** Add `setInterval(() => { fetch('/api/intelligence-feed/ESP-ALPHA-1?fault_type=gas_lock').then(...).then(d => { if(d) this.h1FeedItems = d.items || []; }); }, 15000)` during `h1Injected && !h1Resolved` state. Clear the interval on reset.

#### D. app.py Change (small, required for the chart)

The `/api/plot/forecast-data` endpoint already returns `adjusted_rul_minutes`. Verify it is non-null during active faults. If `adjusted_rul_minutes` comes back null (RAG hasn't run yet), the chart should use `time_to_scada_minutes` for both lines (gap = 0, context fusion bracket hidden).

No other app.py changes required.

---

## STEP 4: Implementation Sequence (Atomic Fix Rule)

1. **First:** `grep -n` key sections to confirm line numbers before editing
2. **Second:** Single batched `replace_in_file` on `index.html` with all changes
3. **Third:** `docker build → docker push → kubectl rollout restart`
4. **Fourth:** Verify live at `http://gdc-pm.bdau.io`
5. **Fifth:** Update docs and commit

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — no `browser_action` tool
- `feature-trio-scenarios` stays separate from `main`
- XGBoost `*.ubj` models — do not retrain
- Fleet Operations tab: do NOT re-add
- Financial case: LLM only, no static financial cards
- Token budget: batch all edits to same file in ONE replace_in_file call
- Correct registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- "Copilot" is a Microsoft product name — do NOT use it anywhere in the UI
