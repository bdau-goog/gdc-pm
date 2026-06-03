# Next Session Prompt — GDC Edge AI 3-Horizon Demo

## Header
**Date:** June 3, 2026
**Live URL:** http://gdc-pm.bdau.io (us-east1 cluster)
**Project:** gdc-pm (`feature-trio-scenarios` branch — git head `0949491`)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `0949491` — clean working tree, no uncommitted changes
**fault-trigger-ui Digest:** `sha256:d655aad9f03941bccf14e12fa565a6002237676a3ea3117ae8eba5ace9374712`
**event-processor Digest:** `sha256:312ce844a244356732d435e396396486df7e111c814f8205238c43feb5d9cd63` — pinned in YAML
**Branch Policy:** `feature-trio-scenarios` stays **separate from main** — do NOT merge.

---

## ⚠️ MANDATORY SESSION OPENER — Run this BEFORE writing any code

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
cd ~/gdc-pm && git log --oneline -3
```

**Expected results when healthy:**
- All pods: `1/1 Running`, event-processor `restarts=0`
- Ollama: `ollama_online: True` model: `gemma4:latest`
- rag_documents: 18, field_intel: ~100
- git head: `0949491`

---

## ✅ Known Integrity State — ALL CLEAR

| Item | Status |
|------|--------|
| H3 Vizier tab | **FIXED** — real Vertex AI Vizier Gaussian Process Bandit |
| Field intel documents | **FIXED** — live Gemma4 Ollama generation via `_intel_generator()` |
| VFD cost displayed as $2,500 | **FIXED** — now correctly shows $0 (SCADA remote command, no capital) |
| H1 assessment label "INTERVENE NOW" | **FIXED** — now "Intervention Needed" with dynamic state machine |

**None — all displays now match reality.**

---

## NEXT SESSION PLAN — H1 Live Telemetry & Strategic Advisor Redesign

This is a significant demo-quality overhaul planned in detail at end of Session I. Implement in one session.

**Session scope:** 1 Large (index.html + app.py together, one deploy)

| Fix | Change | Verification | Complexity |
|-----|--------|--------------|------------|
| **H1-Live-1** | **Continuous live telemetry on tab load:** Wire `setMainTab('horizon1')` to immediately poll and chart real ESP-ALPHA-1 nominal telemetry from the DB — even before injection. SCADA card shows ticking live PSI/Temp/Amps from the latest simulator rows (no more static `'1,041 PSI'`). | Open H1 tab — SCADA card values update every 5s; GDC chart shows live historical trend | Medium |
| **H1-Live-2** | **Pre-generated baseline field intel:** Add `"normal"` key to `INTELLIGENCE_FEED` in `app.py` with 3 realistic routine well documents (daily performance scan, monthly chemistry report, PM log). `intelligence-feed` API falls back to these when no fault active. | Open H1 tab before injection — RAG pane shows 3 routine baseline documents | Small |
| **H1-Cards-1** | **Remove Financial Impact card. Two-card layout.** Change `h3-card-grid` from 3 columns to 2. Card 1 stays as SCADA. Card 2 renamed "⚡ GDC AI Assessment" and shows all three trend slopes (PIP, Amps, Temp in PSI/min, A/min, °F/min) for both nominal (100%, stable) and fault (anomaly %, declining rates). | Nominal: all slopes = 0.0/stable. Injected: all three show declining trends | Small |
| **H1-LLM-1** | **Financial-operational advice embedded in Gemma templates.** Revise `GEMMA_FINDING_TEMPLATES["gas_lock"]` in `app.py` to include the risk-weighted financial case inline: *"Expected unmitigated loss: $150,000 CAPEX (65% response failure risk = $97,500 expected cost). Recommend: SCADA VFD Speed-Down 52→44 Hz / 3,120→2,640 RPM at $0 direct cost."* | After inject, h1GemmaFinding contains risk-weighted dollar figures and both Hz+RPM | Small |
| **H1-P3** | **Backend recovery thread:** After VFD approval, `hitl_approve()` launches `_run_recovery_thread()` that posts climbing PIP/Amps readings to RabbitMQ over 36 steps, with DB timestamps spaced 5 min apart (3h wellbore recovery compressed to ~3 min real-time). Chart shows green upward trend. | After approve, chart continues to animate — green trend, sensors normalising over ~3 min | Medium |

---

### Design Detail: Two-Card Layout Wireframe

```text
+-----------------------------------------------+-----------------------------------------------+
|  📊 SCADA (Current Reading)                   |  ⚡ GDC AI Assessment                         |
|  PIP Reading:     [live ticking]               |  AI Confidence:  [—] / [94.2% gas_lock]       |
|  Winding Temp:    [live ticking]               |  Health Score:   [100.0%] / [82.1%]           |
|  Motor Amps:      [live ticking]               |  PIP Trend:      [Stable 0.0] / [−12.5/min ↓]|
|  ─────────────────────────────────             |  Amps Trend:     [Stable 0.0] / [−2.3/min ↓] |
|  ✓ SCADA: ALL NOMINAL (No alarm)               |  Temp Trend:     [Stable 0.0] / [+1.8/min ↑] |
|  No action recommended.                        |  ─────────────────────────────────────────    |
|                                                |  Status: [Monitoring…] / [Intervention Needed]|
+-----------------------------------------------+-----------------------------------------------+
```

### Design Detail: Gemma Financial-Operational Template (gas_lock)

The advisor templates in `GEMMA_FINDING_TEMPLATES["gas_lock"]` should follow this pattern:
```
"🤖 GDC Advisory: Gas lock anomaly detected ({conf}% confidence). PIP at {psi:.0f} PSI 
declining at rate consistent with gas entrainment. Expected unmitigated loss: $150,000 pump 
replacement CAPEX (65% probability of SCADA-window response failure → $97,500 risk-weighted 
expected cost). Recommended: SCADA VFD Speed-Down from 52 Hz (3,120 RPM) → 44 Hz (2,640 RPM). 
Direct cost: $0. Preserves pump asset entirely."
```

### Implementation Sequence (one session, one deploy)

**app.py changes (batch into single replace_in_file call):**
1. Add `"normal"` documents to `INTELLIGENCE_FEED`
2. Update `get_intelligence_feed()` to return normal docs when `fault_type` is `None`/`"normal"`
3. Replace `GEMMA_FINDING_TEMPLATES["gas_lock"]` with financial-operational templates
4. Add `_run_recovery_thread()` function (Phase H1-P3)
5. Wire `hitl_approve()` to call `_run_recovery_thread()` instead of immediately clearing state

**index.html changes (batch into single replace_in_file call):**
1. Change `h3-card-grid` to `grid-template-columns: 1fr 1fr` (remove 3rd column)
2. Remove the Financial Impact card HTML block entirely
3. Update GDC card title from "Prediction" to "Assessment"
4. Add PIP Trend, Amps Trend, Temp Trend rows to GDC card (reactive to h1Injected state)
5. Wire `setMainTab('horizon1')` to immediately poll live nominal telemetry + RAG feed
6. Update SCADA card metrics to use real live data for all three sensors (no static defaults)

---

## What Was Done This Session (Session I — June 3, 2026)

### Phase 1: H1 Visual & Interaction Overhaul (git `0949491`)
- **Global Tailwind Dark Slate Palette** — Replaced harsh neon palette with professional Slate-900/800 + calibrated accent colors across the entire UI
- **H1 Drag-Resizable Splitter** — Vertical `h1-splitter` div between chart pane and RAG pane; `initH1Resize()` with mouse drag + Plotly auto-resize
- **H1 Multivariate Sensor Tabs** — PIP Pressure / Motor Amps / Winding Temp tabs above GDC forecast chart; forecast payload cached in `h1ForecastData`; `setH1Sensor()` switches charts without any network call
- **H1 Assessment State Machine** — `h1Recovering` flag tracks 4 states: Monitoring → Intervention Needed → Recovering → Resolved; colors transition correctly
- **VFD Terminology** — Frequencies shown with RPM equivalents: "52 Hz → 44 Hz (3,120 → 2,640 RPM)"
- **Recovery Phase** — `approveH1VFD()` sets `h1Recovering=true`, keeps polling alive for 2 min, then auto-stops

### Phase 2: Financial Card Integrity Fix (git `0949491`)
- VFD cost corrected: `$2,500` → `$0 (SCADA remote command, no capital outlay)`
- Physics panel table net avoided: `$147,500` → `$150,000`
- Financial card restructured: shows risk-weighted SCADA-only expected loss (~$97,500 at 65% burnout probability)
- Outcome label: `Net Savings` → `Capital Preserved: $150,000`

---

## Current Cluster State (VERIFIED June 3, 2026 21:02)

```
alloydb-omni-5fcfc68fdb-9vm2z           1/1   Running   ← database
event-processor-99dd7b6d9-qjjg9         1/1   Running   ← EP-2 + Fix 13
fault-trigger-ui-7585546bf7-fpdrn       1/1   Running   ← 0949491 (Phase 1+2)
gdc-pm-rabbitmq-server-0                1/1   Running
grafana-655b6f5c7c-w2h84                1/1   Running
inference-api-5697b79566-zqdpl          1/1   Running
ollama-5bc5db749b-n6tb8                 1/1   Running   ← gemma4:latest
telemetry-simulator-867677f784-h55wd    1/1   Running
```

**field_intel count:** 100  ·  **rag_documents count:** 18

---

## Constraints

- `terraform/gke.tf` must NOT be applied.
- All demo changes: `gke/fault-trigger-ui/index.html` and `gke/fault-trigger-ui/app.py`.
- No browser on SSH remote — no `browser_action` tool.
- `feature-trio-scenarios` stays **separate from `main`**.
- XGBoost `*.ubj` models — do not retrain.

---

## Rebuild & Deploy Commands

```bash
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
# fault-trigger-ui (only file that changes regularly)
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm

# event-processor (digest-pinned YAML)
docker build -t ${REGISTRY}/event-processor:latest gke/event-processor
docker push ${REGISTRY}/event-processor:latest
# update digest in gke/event-processor/k8s/event-processor.yaml, then:
kubectl apply -f gke/event-processor/k8s/event-processor.yaml -n gdc-pm
```

---

## Outstanding Development Items (Backlog)

**High Priority (next session — see NEXT SESSION PLAN above):**
- H1-Live-1, H1-Live-2, H1-Cards-1, H1-LLM-1, H1-P3 (all scoped above)

**Medium Priority:**
- **H2-tabs** — H2 sensor tabs: same `h2ActiveSensor` / `h2ForecastData` pattern as H1. Wire Vibration, Motor Temp tabs above H2 GDC chart. Zero-network tab switching.
- **Perf-1** — Vizier study caching: reuse study across calls to reduce H3 tab latency from ~5s → ~2s.

**Low Priority:**
- **H3-UX-1** — H3 loading spinner during 5s Vizier call.
- **H3-UX-2** — Update hardcoded "~57.5 Hz" example in H3 physics panel to "varies per run".
- **Clean-1** — Remove dead `generate_dynamic_documents()` function from `app.py` (~lines 164-350).
- **Demo-1** — Full rehearsal walk-through: H1 → H2 → H3, timed at ~15 minutes.

---

## Key Lessons

- **sed is safer than replace_in_file for targeted line edits** when the file contains special HTML entities like em-dash (`—`). Use `sed -i 'NNNs|old|new|'` (line-addressed) to bypass encoding edge cases.
- **Batch all `replace_in_file` calls to the same file** — each call returns the full 3,685-line file (~150K tokens). Two calls costs ~300K tokens. Always plan all edits to a file before making the first call.
- **Financial realism matters immediately to O&G audiences** — $2,500 VFD cost was caught by the user in the first review. Risk-weighted expected value (65% probability × $150k = $97.5k) is the correct framing.
- **Static placeholder metrics break demo credibility** — the H1 SCADA card showing static hardcoded `'1,041 PSI'` breaks the "live monitoring" illusion. The correct pattern is continuous polling of real simulator data from the DB, even at nominal state.
- **Financial case belongs in the LLM, not a static card** — embedding the risk-weighted expected value ($97,500 SCADA-only loss vs $0 proactive command) directly into the Gemma advisory text elevates the system from a dashboard into a Strategic Financial-Operational Copilot.
