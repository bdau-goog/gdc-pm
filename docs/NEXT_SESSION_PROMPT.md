# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: Session D (June 7, 2026) / git head: `6bc8a8a` (pre-session D)  
**fault-trigger-ui image:** `sha256:afa26b3a` (1/1 Running)  
**inference-api image:** `sha256:d1194989` (1/1 Running)  
**Branch:** `feature-trio-scenarios` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

Also check RabbitMQ queue depth every session start:
```bash
kubectl exec -n gdc-pm gdc-pm-rabbitmq-server-0 -- rabbitmqctl list_queues --vhost gdc-pm name messages consumers
```

**Expected healthy:**
- All 8 pods: 1/1 Running
- ollama_online: True · model: gemma4:latest
- field_intel: 0–5 rows (only grows during active fault injection — correct)
- rag_documents: 18 rows
- RabbitMQ: **< 500 messages** (if still > 5,000 → P0 kill-list not yet applied — do it first)

**If RabbitMQ > 5,000 at session start:**
1. Apply P0 kill first (see STEP 3)
2. Then purge: `kubectl exec -n gdc-pm gdc-pm-rabbitmq-server-0 -- rabbitmqctl purge_queue --vhost gdc-pm telemetry.events`

---

## STEP 2: Read These Two Documents

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
cat ~/gdc-pm/docs/BACKEND_CONFORMANCE_REPORT.md
```

---

## STEP 3: Session D Task List (in priority order)

### P0 — Kill System 2 / Fix RabbitMQ (blocking everything else)
**What:** Change `AI_NARRATIVE_ENABLED` from `rag` to `false` in event-processor k8s YAML.  
**File:** `gke/event-processor/k8s/event-processor.yaml` line ~69  
**Why:** Synchronous per-message Gemma call is the SOLE cause of the 32k RabbitMQ backlog. Backlog causes stale DB reads → SCADA fires falsely in H1.  
**Verify:** After `kubectl rollout restart deployment/event-processor -n gdc-pm`, wait 2 min, check queue depth — should stop growing and drain below 500.

### P1 — H1 Integrity Fixes (three bugs, one batched edit to index.html + app.js)

**P1a — Sensor bar data source desync (THESIS-KILLER)**  
Root cause: `h1RawAmps/Psi/Temp` are read from forecast-data DB trace (laggy). Must read from `/api/degrade-status/ESP-ALPHA-1.current_sensors` (in-memory, immediate).  
Fix: In the `launchHorizon1()` degrade-status poll (app.js ~line 1144), extract `current_sensors` and set `h1RawPsi`, `h1RawAmps`, `h1RawTemp`, `h1RawVib` from those fields. Remove the `_renderH1PhasePlane()` call that currently sets them from the DB trace.

**P1b — Missing Vibration bar**  
Add 4th sensor bar in index.html after the TEMP bar. `↑ Higher = worse · Alarm: > 4.0 mm/s`. Read from `h1RawVib`.

**P1c — Thermal countdown shows garbage early**  
Gate on `dtemp_dt > 0.2`: banner shows `"— monitoring temp"` until temp is actually rising. See index.html line 410.

### P2 — H1 "Race" UI Redesign (after P1 verified)
See DEMO_MASTER.md §4 H1 V2 Redesign wireframe and §15 Requirements R1-R7.  
Hero is: GDC fires (red) while all 4 SCADA bars stay green. Decision timeline with moving YOU ARE HERE dot.  
This is the big H1 UI work. Do NOT start until P0+P1 are verified.

### P3 — H2 Discern Tab (after H1 is stable)
See DEMO_MASTER.md §5 and NEXT_SESSION_PROMPT previous version for full layout wireframe.  
All app.py plumbing is done. Single batched replace_in_file to index.html only.

---

## Known Integrity State — Session D

| Item | File | Status |
|---|---|---|
| System 2 Gemma per-message (clogs queue) | event-processor.yaml | ❌ LIVE — P0 |
| h1RawAmps reads stale DB (SCADA fires false) | app.js:1237 | ❌ P1a |
| Missing Vibration sensor bar | index.html:516 | ❌ P1b |
| Thermal countdown garbage early | index.html:410 | ❌ P1c |
| H3 Vizier hardcoded polynomial (not XGBoost) | app.py:~5293 | ❌ P2 (label fix) |
| esp_classifier trained on invented ranges | inference-api/models | ⚠ P3 (retrain) |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- `feature-trio-scenarios` stays separate from `main`
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- inference-api registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/inference-api:latest`
- Do NOT use "Copilot" anywhere in H1/H2/H3
- Failing model `.ubj` files are NEVER committed
