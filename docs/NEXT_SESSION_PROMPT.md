# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date / git head: Session B end — `ae728c8`  
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

**⚠️ Also check RabbitMQ queue depth (new — run every session start):**
```bash
kubectl exec -n gdc-pm gdc-pm-rabbitmq-server-0 -- rabbitmqctl list_queues --vhost gdc-pm name messages consumers
```
Expected: `telemetry.events  <5000  1`  
If > 50,000: `kubectl exec -n gdc-pm gdc-pm-rabbitmq-server-0 -- rabbitmqctl purge_queue --vhost gdc-pm telemetry.events`

**Expected healthy (Session C start):**
- All 8 pods: 1/1 Running
- ollama_online: True · model: gemma4:latest
- field_intel: 80–120 rows · rag_documents: 18 rows

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Session C Primary Task — H1 V2 Visual Redesign

**This is the primary task.** The HP-HMI/ISA-101 layout with the SLB wellbore diagram was approved in DEMO_MASTER.md §7/§15 during Session R and has been blocked behind model integrity work until now. All integrity work is complete. Build it.

### Design reference: DEMO_MASTER.md §7 + §15 wireframe

**Layout (2 columns + full-width banner):**
```
╔══════════════════════════════════════════════════════════╗
║ STATUS BANNER (full width, color changes):               ║
║  Pre:  [✓ WELL A-1 NOMINAL — 4 sensors · no alarm]      ║
║  Post: [⚠ GAS LOCK ACTIVE · T+02:14 · 16 min remaining] ║
╠══════════════════════════════╦═══════════════════════════╣
║ LEFT (~50%)                  ║ RIGHT (~50%) — GDC ADVISOR║
║                              ║                           ║
║ Decision Timeline            ║ Streaming Gemma           ║
║ NOW ──▶── YOU ARE HERE ──|── ║ Auto-starts on inject     ║
║               $0  $2k  $150k ║                           ║
║                              ║ Intel Feed (live)         ║
║ Sensor Bars (directional):   ║                           ║
║ PIP  ████████░░  1,340 PSI   ║ Confidence Widget:        ║
║      ↓ Lower=worse · Alarm   ║ gas_lock  ████  78%       ║
║      ✓ Above SCADA threshold ║ normal    █     12%       ║
║                              ║ slug_flow       6%  etc   ║
║ SCADA vs GDC (plain text)    ║                           ║
║                              ║                           ║
║ Option cards (post-inject)   ║                           ║
╚══════════════════════════════╩═══════════════════════════╝
```

**SLB wellbore SVG (replaces CSS instrument panel):**
- Vertical cross-section, dark-mode, 0 ft at surface → –8,000 ft at pump intake
- Casing and tubing as concentric rectangles; perforations at bottom
- Detail callout zone at pump intake (all gas lock indicators here)
- Gas bubbles animated at intake ONLY during fault injection (physically correct)
- Motor section color-mapped to `h1SensorTemp` value only — NOT a timer
  - green: temp < 230°F / amber: 230–260°F / red: > 260°F
- Sensor leader lines: PIP, Motor Amps, Motor Winding Temp, Intake GVF%
- Inset gauge strip at bottom: "Motor Winding Temp · Class H Limit: 356°F · Current: Xf · Headroom: Yf"
- Reference aesthetic: SLB Oilfield Review journal cross-sections — technical, not decorative

**Confidence Widget (incorporate into right column):**
- 5 class rows sorted by probability descending
- Each: class label + bar (width = prob%) + percentage text
- Stage badge on top class: Emerging (<60%) / Developing (60–85%) / Confirmed (≥85%)
- Data source: `class_probs` from `/api/plot/forecast-data` (already populated)
- Vue data: `h1ClassProbs` — populate from `class_probs` in the degrade-poll interval

**HP-HMI color discipline (styles.css):**
- Gray = inactive/nominal — no decorative color
- Color = active alarm only
- Status banner: green pre-inject, amber/red post-inject with animation
- Sensor bars: green → amber → red as value approaches alarm threshold

### Implementation approach

Two `replace_in_file` calls:
1. `gke/fault-trigger-ui/index.html` — H1 layout restructure + SLB SVG + Confidence Widget HTML
2. `gke/fault-trigger-ui/static/styles.css` — HP-HMI color rules + status banner + sensor bar styles

Then: `docker build → docker push → kubectl set image → rollout status`

---

## STEP 4: After H1 V2 Visual — H2 Discern Tab

Per DEMO_MASTER.md §5:
- Two-line Plotly chart: Vibration (rising, orange) + Motor Temp (flat, blue)
- H2 evidence wall: 6 chips (vib sensor, temp sensor, shift note, separator test, choke log, OEM guide)
- GDC Advisor verdict: "$1,500 truck roll vs $150,000 unnecessary pump pull"
- Well schematic H2 variant: pump body green (healthy), surface flowline shows slug animation

---

## Known Integrity State — Session C start

**All known integrity violations resolved as of Session B.** ✅

---

## Operational Notes (Session B discoveries)

- **RabbitMQ backlog:** `telemetry.events` accumulated 286,418 messages over 8h. Root cause: synchronous event-processor (prefetch_count=1) + 30s Ollama RAG timeout = ~2 msg/min drain vs 168 msg/min publish. Purged Session B. Check queue depth at every session start.
- **Classifier v3 live verification:** normal→normal 92.5% · gas_lock→gas_lock 100% · slug_flow→slug_flow 100%. All offline gates confirmed live.
- **Point injection limitation:** Use `/api/inject/degrade` for classifier verification, not `/api/inject-fault` — gradual degrade readings survive RabbitMQ batching; point injections get swamped by concurrent simulator readings.

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
