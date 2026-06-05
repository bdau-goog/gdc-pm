# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date / git head: Session B (June 5, 2026) — commit to be tagged after this write  
**fault-trigger-ui image:** `sha256:7b97605e` (1/1 Running — Session B)  
**inference-api image:** `sha256:d1194989` (1/1 Running — Session B, v3 esp_classifier DEPLOYED)  
**Branch:** `feature-trio-scenarios` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected healthy (Session C start):**
- fault-trigger-ui: 1/1 Running (sha256:7b97605e)
- inference-api: 1/1 Running (sha256:d1194989 — v3 model live)
- telemetry-simulator: 1/1 Running
- AlloyDB, RabbitMQ, Grafana, event-processor, Ollama: 1/1 Running
- ollama_online: True · model: gemma4:latest
- field_intel: 80–120 rows · rag_documents: 18 rows

**⚠️ RabbitMQ backlog check (new):**
```bash
kubectl exec -n gdc-pm gdc-pm-rabbitmq-server-0 -- rabbitmqctl list_queues --vhost gdc-pm name messages consumers
```
Expected: `telemetry.events  <5000  1` — if messages > 50,000, purge before proceeding:
```bash
kubectl exec -n gdc-pm gdc-pm-rabbitmq-server-0 -- rabbitmqctl purge_queue --vhost gdc-pm telemetry.events
```

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Session C — Confidence Widget (H1)

### 3a. Build the Live Diagnostic Confidence Widget in H1 tab

`h1TopClass` and `h1TopClassProb` are already wired in Vue data (Session V). The widget needs HTML/CSS only — probability bars for all 5 ESP classes, sorted descending, with a stage badge.

**Spec:**
- Poll source: `class_probs` dict from `/api/plot/forecast-data` (already populated)
- 5 class rows: gas_lock / slug_flow / sand_ingress / motor_overheat / normal — ordered by probability descending
- Each row: class label + horizontal bar (width = prob × 100%) + percentage text
- Stage badge on top class: Emerging (<60%) / Developing (60–85%) / Confirmed (≥85%)
- Color: gas_lock = red, slug_flow = amber, others = grey; normal = green
- Pre-injection: shows "normal 97%" in green (correct — classifier is working)
- Post-injection: shows fault class rising with stage progression

**Wire-up locations in index.html:**
- Find the H1 Detect tab section containing `h1TopClass` / `h1TopClassProb` refs
- Add the widget HTML below the SCADA sensor bars or in the dual-reality bar right column
- CSS: add to styles.css (`.conf-widget` block)
- Vue: `h1ClassProbs` should already be populated from `class_probs` in forecast-data poll; confirm or add

**One-file change:** index.html only (HTML for the widget) + styles.css for `.conf-widget` CSS.  
Batch both into a single pair of `replace_in_file` calls (one per file).

### 3b. Live verification after deploy

After deploy, inject gas_lock degrade for 90s and verify `h1ClassProbs.gas_lock` climbs in the UI.  
Check queue depth BEFORE injecting (should be <5000).

---

## STEP 4: Session C follow-on — H2 Discern Tab

After Confidence Widget verified:
- Build H2 tab per DEMO_MASTER.md §5
- Two-line chart (vib rising, temp flat)
- H2 evidence wall (6 chips)
- GDC Advisor verdict: "$1,500 vs $150,000"

---

## Known Integrity State — Session C start

| ID | Status | Notes |
|---|---|---|
| V-01 through V-09 | ✅ Fixed Session V | Display violations resolved |
| gas_lock `{pnr}` static template | ✅ Fixed Session B | Now `{remaining:.0f}-min advantage window` computed from `fault_onset_utc` |
| `GEMMA_FINDINGS["gas_lock"]` static | ✅ Fixed Session B | "Motor thermal window is minutes, not hours — act immediately" |
| inference-api live container | ✅ Fixed Session B | sha256:d1194989 has v3 esp_classifier |
| fault-trigger-ui slug_flow vib_range | ✅ Fixed Session B | sha256:7b97605e has correct (4.0, 6.5) range |

**All known integrity violations resolved as of Session B.**

---

## Operational Notes (Session B discoveries)

- **RabbitMQ backlog:** The `telemetry.events` queue accumulated 286,418 messages over 8h of cluster operation. Root cause: event-processor's Ollama RAG narrative generation times out after 30s per message (Ollama is busy with keepalive/intel-generator). Each timeout blocks the consumer thread. At 2 messages/min during heavy Ollama load, the queue grows faster than it drains. **Purged Session B.** Monitor at each session start.
- **Classifier v3 live verification:** normal→normal 92.5% ≥90% ✅ · gas_lock→gas_lock 100% @ conf=1.000 ✅ · slug_flow→slug_flow 100% @ conf=0.999 ✅. All offline gates pass on live cluster.
- **Point injection limitation:** Direct `/api/inject-fault` point injections get swamped by the telemetry-simulator's normal readings in the same batch. Use `/api/inject/degrade` for verification — gradual degrade readings arrive on a separate thread and survive batching.

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- `feature-trio-scenarios` stays separate from `main`
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- inference-api registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/inference-api:latest`
- Do NOT use "Copilot" anywhere
- Failing model `.ubj` files are NEVER committed
