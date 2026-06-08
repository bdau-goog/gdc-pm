# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 8, 2026 (Session O — Scenario Replay design locked into DEMO_MASTER.md §4)
**git head:** `860260f` (docs: Session N+1 handoff)
**fault-trigger-ui image:** `sha256:2c2827d1` (1/1 Running — Session N+1, still current)
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

Pay special attention to **§4.2–§4.7** (the new Scenario Replay spec, rewritten Session O).

---

## STEP 3: Session P Implementation — H1 Scenario Replay

### What changed in Session O (docs only, no code)

Session O redesigned the H1 interaction model from "inject-and-wait" to **Scenario Replay**:
- A new `GET /api/h1/scenario-replay` endpoint precomputes the full fault trajectory server-side
- The **real `esp_health.ubj` XGBoost model** runs over the trajectory in a sliding window to produce `gdc_detect_idx`
- The **SCADA hard threshold** (PIP < 800) on the same data produces `scada_alarm_idx`
- The frontend renders a **▶ Play / scrub control** over the full pre-computed arrays
- No live degrade thread, no RabbitMQ polling, no race conditions

### Implementation Order (execute strictly in sequence, verify before next step)

**Step 1 — Verify esp_health.ubj is loadable and produces valid output (5 min)**
```bash
kubectl exec -n gdc-pm deployment/fault-trigger-ui -- python3 -c "
import xgboost as xgb, numpy as np
m = xgb.Booster(); m.load_model('/app/models/esp_health.ubj')
# Feed it one row of 8 features (all zeros as a smoke test)
d = xgb.DMatrix(np.zeros((1,8)))
print('health_score:', m.predict(d))
"
```
Expected: a float between 0 and 1 (likely ~0.9 for zero-feature input). If this fails (model not found, wrong feature count), diagnose before writing any code.

**Step 2 — Add `GET /api/h1/scenario-replay` to app.py (single batched replace_in_file)**

Add this endpoint near the other `/api/h1/` endpoints (grep for `h1` in app.py to find the right location):

```python
@app.get("/api/h1/scenario-replay")
async def h1_scenario_replay(fault: str = "gas_lock"):
    """
    Returns a pre-computed fault trajectory + real XGBoost health model outputs.
    The frontend replays this deterministically (no degrade thread, no RabbitMQ).
    fault: "gas_lock" or "fluid_drawdown"
    """
    import random, math
    ft = fault if fault in ("gas_lock", "fluid_drawdown") else "gas_lock"
    fp = FAULT_PROFILES.get(ft, FAULT_PROFILES["gas_lock"])

    N = 120  # trajectory steps
    k = random.uniform(1.2, 2.5)  # ramp shape exponent (same as degrade thread)
    
    # Nominal baselines (from FAULT_PROFILES nominal ranges)
    psi_nom = random.uniform(1180, 1250)
    amps_nom = random.uniform(85, 92)
    temp_nom = random.uniform(195, 202)
    vib_nom = random.uniform(0.8, 1.4)

    psi_end = random.uniform(*fp["psi_range"])
    amps_end = (fp["amps_range"][0] + fp["amps_range"][1]) / 2.0
    temp_end = random.uniform(*fp.get("temp_range", (198, 215)))
    vib_end = random.uniform(*fp.get("vib_range", (1.0, 2.5)))

    t_step = 0.25  # minutes per step → 30 min total trajectory
    psi, amps, temp, vib, t_min = [], [], [], [], []
    for i in range(N):
        frac = ((i + 1) / N) ** k
        noise = lambda s: random.gauss(0, s)
        psi.append(round(psi_nom + (psi_end - psi_nom) * frac + noise(18), 1))
        amps.append(round(amps_nom + (amps_end - amps_nom) * frac + noise(1.5), 2))
        temp.append(round(temp_nom + (temp_end - temp_nom) * frac + noise(1.2), 1))
        vib.append(round(vib_nom + (vib_end - vib_nom) * frac + noise(0.1), 3))
        t_min.append(round(i * t_step, 2))

    # Run real XGBoost health model in sliding window
    health_scores = []
    W = 20  # window width (same as event-processor)
    try:
        import xgboost as xgb, numpy as np
        model = xgb.Booster()
        model.load_model("models/esp_health.ubj")
        for i in range(N):
            if i < W:
                health_scores.append(1.0)
                continue
            window_psi = psi[i-W:i]
            window_amps = amps[i-W:i]
            window_temp = temp[i-W:i]
            window_vib = vib[i-W:i]
            dt = t_step  # minutes
            dpsi_dt = (window_psi[-1] - window_psi[0]) / (W * dt)
            damps_dt = (window_amps[-1] - window_amps[0]) / (W * dt)
            dtemp_dt = (window_temp[-1] - window_temp[0]) / (W * dt)
            dvib_dt = (window_vib[-1] - window_vib[0]) / (W * dt)
            feats = np.array([[
                psi[-1], amps[-1], temp[-1], vib[-1],
                dpsi_dt, damps_dt, dtemp_dt, dvib_dt
            ]])
            d = xgb.DMatrix(feats)
            score = float(model.predict(d)[0])
            health_scores.append(round(score, 4))
    except Exception as e:
        # Fallback: synthetic health decline if model unavailable
        health_scores = [round(1.0 - 0.4 * ((i/N)**2), 4) for i in range(N)]

    # Detection indices
    HEALTH_THRESHOLD = 0.65
    SCADA_PIP_ALARM = 800.0
    gdc_detect_idx = next((i for i, s in enumerate(health_scores) if s < HEALTH_THRESHOLD), N - 1)
    scada_alarm_idx = next((i for i, p in enumerate(psi) if p < SCADA_PIP_ALARM), N - 1)

    lead_time_minutes = round(t_min[scada_alarm_idx] - t_min[gdc_detect_idx], 1) if scada_alarm_idx > gdc_detect_idx else 0.0

    return {
        "fault_type": ft,
        "n": N,
        "psi": psi,
        "amps": amps,
        "temp": temp,
        "vib": vib,
        "t_min": t_min,
        "health_score": health_scores,
        "gdc_detect_idx": gdc_detect_idx,
        "scada_alarm_idx": scada_alarm_idx,
        "lead_time_minutes": lead_time_minutes,
        "model_used": "esp_health.ubj" if health_scores[gdc_detect_idx] != round(1.0 - 0.4 * ((gdc_detect_idx/N)**2), 4) else "FALLBACK_SYNTHETIC"
    }
```

Verify with: `curl -s http://gdc-pm.bdau.io/api/h1/scenario-replay?fault=gas_lock | python3 -c "import sys,json;d=json.load(sys.stdin);print('gdc_idx:',d['gdc_detect_idx'],'scada_idx:',d['scada_alarm_idx'],'lead_min:',d['lead_time_minutes'],'model:',d['model_used'])"`

Expected: `gdc_idx` < `scada_idx`, `lead_time_minutes` > 0, `model: esp_health.ubj`.

**Step 3 — Rewrite H1 Discern tab frontend (app.js + index.html, one batched call each)**

The full UI rewrite replaces the inject-and-wait model with the play/scrub model. Key changes:

*app.js Vue state additions:*
- `h1ReplayData: null` — full trajectory from API
- `h1CursorIdx: 0` — current scrubber position
- `h1Playing: false` — auto-advance timer running
- `h1PlayTimer: null` — setInterval reference
- `h1FaultTypeRevealed: false` — true once cursor crosses gdc_detect_idx

*app.js methods:*
- `loadH1Scenario()` — calls `/api/h1/scenario-replay?fault=<random>`, stores in `h1ReplayData`, renders chart, resets cursor to 0.
- `h1Play(fast=false)` — starts `setInterval` advancing `h1CursorIdx` by 1 every 100ms (fast: 30ms). Stops at N-1.
- `h1Pause()` — clears interval.
- `h1Reset()` — cursor to 0, clears `h1FaultTypeRevealed`, re-renders.
- `h1Scrub(idx)` — sets `h1CursorIdx`, triggers reactive updates, updates Plotly cursor line via `Plotly.relayout`.
- Watcher on `h1CursorIdx`: when crosses `gdc_detect_idx` → set `h1FaultTypeRevealed = true`.

*index.html Discern tab:*
- Remove all `⚡ Ingest Pad Anomalies` button, `h1Injected`, `h1EvidenceWall`, inject-triggered polling
- Add `[↺ New Scenario]` button → `loadH1Scenario()`
- Add Play/Reset/Fast buttons + HTML range `<input type="range">` scrubber bound to `h1CursorIdx`
- Replace sparkline cards with single `#h1-replay-chart` (Plotly, dual Y-axis PIP+Amps) + 4 cursor-position sensor tiles below
- GDC Advisor sub-tab: show `h1FaultTypeRevealed`-gated content (baseline text before, RAG card + wellbore twin after)
- SCADA sub-tab: show `h1CursorIdx >= scada_alarm_idx`-gated alarm state
- Reuse ALL existing `.h1-action-card`, `.h1-card-green`, `.h1-card-contraindicated` CSS from Session N

**Step 4 — Build, push, deploy, verify**
```bash
cd ~/gdc-pm/gke/fault-trigger-ui
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest .
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm
# Verify:
curl -s http://gdc-pm.bdau.io/api/h1/scenario-replay?fault=gas_lock | python3 -c "import sys,json;d=json.load(sys.stdin);print('n:',d['n'],'lead:',d['lead_time_minutes'],'model:',d['model_used'])"
```

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 inject-and-wait model | ⚠ DEPRECATED | Replaced by Scenario Replay per DEMO_MASTER §4.2. Frontend still uses old model until Step 3 is implemented. |
| H1 sparklines / degrade thread | ⚠ DEPRECATED | To be replaced by `#h1-replay-chart` + scrubber in Step 3. |
| H1 action cards / financial breakdowns | ✅ Keep (Session N) | CSS + outcome logic reused unchanged in new model. |
| Vue template crash | ✅ Fixed (Session N) | All `<` chars escaped. |
| h1EvidenceWall TypeError | ✅ Fixed (Session N+1) | Initialized with 5 objects. |
| `model_used` field | ✅ Integrity guard | Endpoint returns `"FALLBACK_SYNTHETIC"` if model load fails — UI must display this if shown. |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
- The `model_used` field in the replay response is an integrity guard: if it reads `FALLBACK_SYNTHETIC`, that must be surfaced somewhere in the UI (even a small badge), never silently swallowed
