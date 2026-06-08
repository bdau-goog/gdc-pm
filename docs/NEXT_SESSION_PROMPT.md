# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 8, 2026 (Session P — backend done, frontend pending)
**git head:** `d76b252` (feat: add GET /api/h1/scenario-replay + Playwright smoke test harness)
**fault-trigger-ui image:** `sha256:2c2827d1` (1/1 Running — Session N+1; **NOT rebuilt yet** — endpoint in git only)
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
- field_intel: ~2–3 · rag_documents: 18

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

Pay special attention to **§4.2–§4.7** (Scenario Replay spec).

---

## STEP 3: H1 Scenario Replay — Remaining Work

### Session P status — verified facts (do NOT re-derive)

| Step | Status | Notes |
|------|--------|-------|
| 1: smoke-test esp_health.ubj | ✅ DONE | health_score: [0.6981253] for zero input |
| 2: `GET /api/h1/scenario-replay` in app.py | ✅ DONE | Line 5809, committed `d76b252`. **Not deployed.** |
| 3: Rewrite H1 Discern tab (app.js + index.html) | ⏳ **TODO** | Primary task next session |
| 4: docker build → push → rollout → verify | ⏳ TODO | After Step 3 |

**The `/api/h1/scenario-replay` endpoint is NOT live until after Step 4 (rebuild).**

### Confirmed technical facts (locked — do not re-derive)

- **Model feature names** (`esp_health.ubj`): `psi`, `temp_f`, `vibration`, `motor_amps`, `dpsi_dt`, `dtemp_dt`, `dvib_dt`, `damps_dt`
- **SCADA threshold = 1000 PSI** — NOT 800 PSI. `FAULT_PROFILES` `psi_range` is (875–1100); PIP never crosses 800. 1000 PSI = API RP 11S §7.2 underload setpoint. Implemented at app.py:5895.
- **Smoke test**: `node scripts/ui_smoke.mjs` — run after every deploy. Currently 7/7 pass on live cluster.

### Step 3 spec: Rewrite H1 Discern tab

**New Vue state to add (app.js data section):**
```js
h1ReplayData: null,        // full trajectory object from /api/h1/scenario-replay
h1CursorIdx: 0,            // current scrubber position
h1Playing: false,          // auto-advance timer running
h1PlayTimer: null,         // setInterval handle
h1FaultTypeRevealed: false, // true once cursor crosses gdc_detect_idx
```

**New methods (app.js):**
- `loadH1Scenario()` — `GET /api/h1/scenario-replay?fault=<random gas_lock|fluid_drawdown>`, stores in `h1ReplayData`, calls `_renderH1ReplayChart()`, resets cursor to 0.
- `h1Play(fast=false)` — `setInterval` advancing `h1CursorIdx` by 1 every 100ms (fast: 30ms). Stops at N-1.
- `h1Pause()` — clears timer.
- `h1Reset()` — cursor=0, `h1FaultTypeRevealed=false`, re-renders.
- `h1Scrub(idx)` — sets cursor, updates Plotly cursor line via `Plotly.relayout`.
- `_renderH1ReplayChart()` — Plotly dual-Y chart (`#h1-replay-chart`): PIP (blue, left Y) + Amps (green, right Y), amber dashed at `gdc_detect_idx`, red dashed at `scada_alarm_idx`, grey moving cursor.
- Watch `h1CursorIdx` → when ≥ `h1ReplayData.gdc_detect_idx` → `h1FaultTypeRevealed = true`.

**index.html Discern tab changes:**
- REMOVE: `⚡ Ingest Pad Anomalies` button, all `h1Injected`-gated blocks, sparkline divs (`#h1-spark-*`), `h1EvidenceWall` activation sequence, degrade polling
- ADD: `[↺ New Scenario]` button → `loadH1Scenario()`
- ADD: `[◀◀ Reset] [▶ Play] [▶▶ Fast]` buttons + `<input type="range">` scrubber bound to `h1CursorIdx`
- ADD: `#h1-replay-chart` div (full width left column, Plotly dual-Y)
- ADD: 4 sensor tiles (PIP / Amps / Temp / Vib) showing value at cursor position
- KEEP: `.h1-action-card`, `.h1-card-green`, `.h1-card-contraindicated` CSS unchanged
- KEEP: GDC Advisor sub-tab + SCADA sub-tab structure — gate with `h1FaultTypeRevealed` and `h1CursorIdx >= h1ReplayData.scada_alarm_idx`

### Step 4 verify commands

```bash
cd ~/gdc-pm/gke/fault-trigger-ui
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest .
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm

# Backend verify (must pass before touching frontend):
curl -s "http://gdc-pm.bdau.io/api/h1/scenario-replay?fault=gas_lock" | python3 -c \
  "import sys,json;d=json.load(sys.stdin);print('n:',d['n'],'gdc:',d['gdc_detect_idx'],'scada:',d['scada_alarm_idx'],'lead:',d['lead_time_minutes'],'model:',d['model_used'])"
# Expected: n: 120, gdc < scada, lead > 0, model: esp_health.ubj

# UI smoke test (run after every deploy):
node scripts/ui_smoke.mjs
# Expected: ✅ SMOKE TEST PASSED (7/7 assertions, 0 console errors)
```

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 inject-and-wait / sparklines | ⚠ DEPRECATED | Still in frontend until Step 3 ships |
| H1 action cards / financial CSS | ✅ Keep | Reused unchanged in new model |
| Vue template crash | ✅ Fixed (Session N) | All `<` escaped |
| h1EvidenceWall TypeError | ✅ Fixed (Session N+1) | Initialized with 5 objects |
| `model_used: FALLBACK_SYNTHETIC` | ✅ Integrity guard | UI must surface this if shown — never silently swallow |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — use `node scripts/ui_smoke.mjs` instead
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
