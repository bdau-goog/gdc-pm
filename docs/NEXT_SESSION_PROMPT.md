# Next Session Prompt — GDC Edge AI 3-Horizon Demo

## Header
**Date:** June 3, 2026
**Live URL:** http://gdc-pm.bdau.io (us-east1 cluster)
**Project:** gdc-pm (`feature-trio-scenarios` branch — git head `e8f8b78`)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `e8f8b78` — clean working tree, no uncommitted changes
**fault-trigger-ui Digest:** `sha256:7da84c2480ccd3c821c00f99fe720e6fe6243910da22ac08fefcd39bea07fd49`
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
- git head: `e8f8b78`

---

## ✅ Known Integrity State — ALL CLEAR

| Item | Status |
|------|--------|
| H1 SCADA card static values (`'1,041 PSI'`) | **FIXED** — now polls `/api/live-telemetry/ESP-ALPHA-1` every 5s from real DB rows |
| H1 RAG pane empty pre-injection | **FIXED** — shows 3 baseline docs (chemistry report, PM log, daily scan) pre-injection |
| Financial Impact card 3-column layout | **FIXED** — removed; 2-card layout (SCADA + GDC Assessment) |
| Gemma gas_lock finding (generic, no financials) | **FIXED** — now embeds $97,500 risk-weighted expected loss + $0 VFD recommendation |
| VFD approval (immediate state clear, no recovery chart) | **FIXED** — `_run_recovery_thread()` posts 36 climbing DB rows over ~3 min |

**None — all displays now match reality.**

---

## NEXT SESSION PLAN — H2 Sensor Tabs + Backlog Cleanup

**Session scope:** 2–3 Small/Medium fixes

| Fix | Change | Verification | Complexity |
|-----|--------|--------------|------------|
| **H2-tabs** | H2 sensor tab bar: same `h2ActiveSensor` / `h2ForecastData` pattern as H1. Wire Vibration and Motor Temp tabs above H2 GDC chart. Zero-network tab switching. | Open H2, inject slug flow — switch between Vibration and Motor Temp tabs, no network call | Medium |
| **Perf-1** | Vizier study caching: reuse study object across calls (store in module-level `_vizier_study`). Reduces H3 tab latency from ~5s → ~2s. | Run Vizier twice — second call noticeably faster | Small |
| **H3-UX-2** | Update hardcoded "~57.5 Hz" example in H3 physics panel to "varies per run" (or dynamically show last optimal Hz). | Text no longer shows fixed 57.5 Hz | Small |
| **Clean-1** | Remove dead `generate_dynamic_documents()` function from `app.py` (~lines 164–350). No callers — dead code from pre-Phase-16 era. | `grep generate_dynamic_documents app.py` returns nothing after removal | Small |

---

## What Was Done This Session (Session J — June 3, 2026)

### H1 Live Telemetry & Strategic Advisor Redesign (git `e8f8b78`)

All 5 planned fixes implemented, deployed, and verified live:

- **H1-Live-1** — `/api/live-telemetry/{asset_id}` endpoint queries `telemetry_events` for latest `failure_type='normal'` row; `setMainTab('horizon1')` immediately polls this every 5s, updating SCADA card PIP/Temp/Amps from real DB values. `h1LivePollTimer` cleared on tab switch, restarted on reset.
- **H1-Live-2** — `"normal"` key added to `INTELLIGENCE_FEED` with 3 realistic O&G baseline docs (daily scan, monthly chemistry report, PM log). `get_intelligence_feed()` returns these when `fault_type` is `None` or `"normal"`. RAG pane label switches to "📄 Baseline Field Intelligence" pre-injection.
- **H1-Cards-1** — Financial Impact card removed. H1 `h3-card-grid` overridden to `grid-template-columns: 1fr 1fr`. GDC card renamed "⚡ GDC AI Assessment". PIP Trend, Amps Trend, Temp Trend rows added (green "Stable 0.0" → orange/red declining rates on inject).
- **H1-LLM-1** — `GEMMA_FINDING_TEMPLATES["gas_lock"]` upgraded to 3 risk-weighted financial-operational templates embedding: $150k CAPEX risk, 65% burnout probability, $97,500 expected loss, VFD 52→44 Hz (3,120→2,640 RPM) at $0 direct cost.
- **H1-P3** — `_run_recovery_thread(asset_id)` posts 36 climbing PIP/Amps readings to RabbitMQ over 3 real minutes (linear ramp from fault-level to nominal). `hitl_approve()` launches thread for `gas_lock` instead of immediately clearing `active_degrades`. Chart shows green recovery trend post-VFD-approval.

**Verified live:**
- `curl /api/live-telemetry/ESP-ALPHA-1` → `psi: 1284.7 temp_f: 182.7 motor_amps: 72.5`
- `curl /api/intelligence-feed/ESP-ALPHA-1?fault_type=normal` → 3 baseline docs (nm_1, nm_2, nm_3)
- `curl /api/intelligence-feed/ESP-ALPHA-1?fault_type=gas_lock` → Gemma finding starts "🤖 GDC Advisory: Gas lock anomaly detected (96% confidence). PIP at 1000 PSI decl..."

---

## Current Cluster State (VERIFIED June 3, 2026 21:41)

```
alloydb-omni-5fcfc68fdb-9vm2z           1/1   Running   ← database
event-processor-99dd7b6d9-qjjg9         1/1   Running   ← EP-2 + Fix 13
fault-trigger-ui-74b899c6f7-lz8lm       1/1   Running   ← e8f8b78 (Session J)
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
```

---

## Outstanding Development Items (Backlog)

**High Priority (next session — see NEXT SESSION PLAN above):**
- H2-tabs, Perf-1, H3-UX-2, Clean-1 (all scoped above)

**Medium Priority:**
- **H1-P3-polish** — Recovery chart green color: during `h1Recovering`, the H1 chart traces are still styled orange (fault color). Swap to green during recovery to visually confirm the VFD command worked. Implementation: in `_renderH1Charts`, check `this.h1Recovering` and override `line.color` on the telemetry trace to `'#4ade80'`.
- **H2-Financial** — H2 Financial Impact card currently shows static $148,500. Wire it reactively: show $0 before injection, $148,500 after, with "avoided" label when resolved.

**Low Priority:**
- **H3-UX-1** — H3 loading spinner during 5s Vizier call.
- **Demo-1** — Full rehearsal walk-through: H1 → H2 → H3, timed at ~15 minutes.
- **Clean-2** — The `generate_dynamic_documents()` dead-code removal also cleans up `adjust_rul_with_documents()` if no longer called. Verify callers before removing.

---

## Key Lessons

- **`telemetry_events` has `failure_type='normal'` rows** — the live simulator writes these continuously. Query `WHERE failure_type = 'normal' ORDER BY event_time DESC LIMIT 1` to get nominal sensor values without any injected fault bleeding through.
- **`h1LivePollTimer` must skip when `h1Injected=true`** — the guard `if (this.h1Injected) return;` inside `_pollLive1` prevents the nominal DB poll from clobbering the injected degrade values while a fault is active.
- **`get_intelligence_feed()` with `fault_type="normal"` returns 0 live items** — the `field_intel` table only stores AI-generated docs for active faults; `fault_context='normal'` returns no rows. This is correct: the 3 canned baseline docs in `INTELLIGENCE_FEED["normal"]` are the right source for pre-injection context.
- **Batch all edits to a file into one `replace_in_file` call** — this session executed exactly 2 `replace_in_file` calls (one per file) for 6+9 SEARCH/REPLACE blocks respectively, saving ~400K tokens vs sequential calls.
- **`_run_recovery_thread` must check `asset_id not in active_degrades`** — the reset button calls `cancel_degrade` which pops `active_degrades`. The recovery loop guard `if asset_id not in active_degrades: break` ensures a mid-recovery reset exits cleanly.
