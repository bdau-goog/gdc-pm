# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date / git head: Session C end — `bc71f69`
**fault-trigger-ui image:** `sha256:afa26b3a` (1/1 Running — Session C)
**inference-api image:** `sha256:d1194989` (1/1 Running — Session B, v3 esp_classifier DEPLOYED, unchanged)
**Branch:** `feature-trio-scenarios` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**⚠️ Also check RabbitMQ queue depth (run every session start):**
```bash
kubectl exec -n gdc-pm gdc-pm-rabbitmq-server-0 -- rabbitmqctl list_queues --vhost gdc-pm name messages consumers
```
Expected: `telemetry.events  <5000  1`
If > 50,000: `kubectl exec -n gdc-pm gdc-pm-rabbitmq-server-0 -- rabbitmqctl purge_queue --vhost gdc-pm telemetry.events`

**Expected healthy (Session D start):**
- All 8 pods: 1/1 Running
- ollama_online: True · model: gemma4:latest
- field_intel: 80–120 rows · rag_documents: 18 rows
- RabbitMQ: telemetry.events < 5,000 (purged end of Session C at ~14k)

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Session D Primary Task — H2 Discern Tab

**H1 is now demo-ready.** Three integrity violations and four UX failures from the Session Q audit are all resolved as of Session C commits 4f2847e + bc71f69.

**H2 is the next task.** Per DEMO_MASTER.md §12 Phase 2 and §5 (H2 Visual Design Directive):

### H2 key facts before coding
- **Asset:** ESP-ALPHA-3 · **Fault:** `slug_flow`
- **Data wiring: ALL DONE in app.py** — `INTELLIGENCE_FEED["slug_flow"]` (3 session docs: sf_1 choke log, sf_2 separator test, sf_3 shift note), fault injection, truck-roll dispatch, `_renderH2Charts()`, degrade poll. **No app.py changes needed.**
- **Implementation:** Single batched `replace_in_file` to `index.html` only.
- **Visual design directive (Session C decision, in DEMO_MASTER §5):** Lead with Layer 3 / Context Fusion as the hero. The two-line chart (vib up, temp flat) is the **setup** — it creates the ambiguity. The punchline is the 6-source evidence wall + OEM "do not pull well" RAG retrieval + Advisor verdict. Full rationale: `docs/narratives/H2_SLUG_FLOW.md`.

### H2 index.html layout (replace the current `<div class="h3-dashboard">` block in horizon2 tab)

```
╔═══════════════════════════════════════════════════════════════╗
║ STATUS BANNER (same pattern as H1):                           ║
║  Pre: [✓ ESP-ALPHA-3 NOMINAL — vibration nominal]             ║
║  Post: [⚠ SLUG FLOW DETECTED · surface issue · pump healthy] ║
╠═══════════════════════════════════╦═══════════════════════════╣
║ LEFT (~50%)                       ║ RIGHT (~50%) — GDC ADVISOR║
║                                   ║                           ║
║ TWO-LINE CHART (the setup):       ║ Streaming Gemma verdict:  ║
║  Vibration — orange, RISING       ║ "Vibration elevated. Temp ║
║  Motor Temp — blue, FLAT          ║  completely flat. Surface ║
║  SCADA trip: 5.0 mm/s (not hit)   ║  slugging. Do NOT pull."  ║
║                                   ║                           ║
║ 6-SOURCE EVIDENCE WALL            ║ INTEL FEED                ║
║ (activates in sequence):          ║                           ║
║ 📊 Vib 1.1→2.4 mm/s ↑            ║                           ║
║ 📊 Motor temp 198°F — FLAT ✓      ║                           ║
║ 🔧 Choke log: 3 adjustments       ║                           ║
║ 🧪 Separator: 1.8bbl slugs 14min  ║                           ║
║ 📋 Shift note: rough but temp OK  ║                           ║
║ 📖 OEM: "vib+flat temp=surface"   ║                           ║
║                                   ║                           ║
║ TRUCK ROLL CTA (post-inject):     ║                           ║
║ [🚛 Dispatch — $1,500 truck roll] ║                           ║
╚═══════════════════════════════════╩═══════════════════════════╝
```

**Vue data already wired in app.js:** `h2Injected`, `h2Resolved`, `h2TruckRollDispatched`, `h2TruckRollCountdown`, `h2FeedItems`, `h2GemmaFinding`, `h2SensorVib`, `h2SensorTemp` — all populated by existing app.js methods.

**The two-line Plotly chart** uses `_renderH2Charts(d)` already in app.js, which renders `h2-gdc-chart` (vib) and `h2-scada-chart`. These divs exist in the current HTML but the layout around them is the old H3-style card grid — replace with the H1-style 2-column layout.

---

## STEP 4: After H2 — H3 Optimize Tab polish

Per DEMO_MASTER §12 Phase 3 (minor items, H3 already functional):
- Financial delta bar on Pareto chart
- "Edge + Cloud" architecture badge on Vizier optimal card
- GDC Advisor prompt for optimization context

---

## Known Integrity State — Session C end

**All known integrity violations resolved as of Session C.** ✅

Session C specifically resolved:
- **Thermal window hardcoded as 25 min** → Now `h1WindowTotal` captured from `thermal_lead_time_minutes` at first non-null poll (per-run, varies every inject). Fractions 0.72/0.92 drive option expiry. `bc71f69`.
- **H1 V2 visual redesign** (status banner, YOU ARE HERE dot, directional sensor bars, SCADA vs GDC plain text). `4f2847e`.

Flagged for follow-up (not blocking):
- **280°F vs 284°F vs 356°F inconsistency** across app.py thermal computation, index.html physics panel, and DEMO_MASTER §9. All defensible but should be reconciled to one consistent wording. Not blocking any demo scenario.

---

## Operational Notes (Session C discoveries)

- **RabbitMQ backlog:** Accumulated 13,986 messages over ~9h. Purged end of Session C. Same root cause as Session B (synchronous event-processor, Ollama 30s timeout). Check at every session start.
- **H1 thermal window:** `thermal_lead_time_minutes` is null early in fault injection (temp hasn't started rising yet). `h1WindowTotal` falls back to `time_to_scada_minutes` until thermal becomes available. This is correct and on-message — shows GDC detected before temp even moved.
- **H2 deadline note:** For slug flow (H2), motor temp stays FLAT — thermal deadline is irrelevant. H2 has a 120-min PNR window (`PNR_MINUTES["slug_flow"] = 120` in app.py). The window widget is not needed for H2 — the urgency story is "$1,500 now vs $150,000 if you pull the pump" not a countdown.

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
