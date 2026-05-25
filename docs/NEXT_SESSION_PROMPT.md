# Next Session Prompt — ESP v2 Redesign (Stage 2 COMPLETE)

## Header
**Date:** May 25, 2026
**Live URL:** http://34.138.32.109 (us-east1 cluster)
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `530b281` — clean working tree
**Image:** `sha256:ecae6a004c82c169cebdd7821b67043dd570c321f388293a90e39ba435318837` (rebuilt from 08b590a, deployed 22:32 UTC May 25)

---

## ⚠️ MANDATORY SESSION OPENER — Run this BEFORE writing any code

```bash
# 1. Verify cluster truth
kubectl get pods -n gdc-pm --no-headers

# 2. Verify Ollama state
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""

# 3. API truth
curl -s http://34.138.32.109/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"

# 4. Database truth
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability \
  -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents; SELECT COUNT(*) FROM fault_sessions;"
```

**Expected results when healthy:**
- All pods: `1/1 Running`
- Ollama: `1` replica, `ollama_online: True  model: gemma:27b`
- rag_documents: **11 rows** ⚠️ was 0 at last check — if still 0, investigate before proceeding
- fault_sessions: ≥ 2 rows

---

## ⚠️ Known Integrity State

| Item | Actual State | Action Required |
|------|-------------|-----------------|
| **rag_documents** | **0 rows** (expected 11) | Investigate first. Check if alloydb-init-schema completed; may need re-seed. |
| fault_sessions | 2 rows ✅ | Working |
| Ollama / gemma:27b | `ollama_online: True` ✅ | Serving on GPU |
| GPU CronJobs | SUSPENDED ✅ | Use manual scripts only |

---

## GPU Management (Manual — No CronJobs)

```bash
cd /home/brian/gdc-pm && ./scripts/gpu-start.sh   # start of day
cd /home/brian/gdc-pm && ./scripts/gpu-stop.sh    # end of day
```

---

## THIS SESSION'S OBJECTIVE: Architecture Tab ("How It Works")

### The Story This Diagram Must Tell (CxO / Business Audience)

Reading left to right, in one glance, a non-technical executive should understand:

1. **Your existing SCADA and sensors keep working** — GDC is additive, not a rip-and-replace
2. **GDC captures the same telemetry AND your operational knowledge** (records, standards) — in one place
3. **XGBoost predicts failure mathematically** — SCADA only alarms after a threshold is breached (too late)
4. **Gemma reads context the way your best engineer would** — ops records, lab reports, industry standards — at the edge, with no cloud, in seconds
5. **The output is an informed RUL, a recommended action, and a dollar figure** — not just an alarm
6. **Everything runs on-premises inside GDC** — the GPU sub-box makes the compute requirement visible

---

### The Diagram — Mermaid.js Flowchart

**BEFORE THE SESSION:** Preview this at https://mermaid.live to confirm it tells the right story.
Then proceed. Do NOT start coding until this definition is approved.

```
flowchart LR

  subgraph SRC["Data Sources"]
    direction TB
    Sensors["Field Sensors\nESP · Compressor · Turbine · Transformer"]
    OpsRec["Operations Records\nShift Notes · Work Orders · Lab Reports"]
    Corpus["Industry Corpus\nISO Standards · OEM Manuals · Failure Libraries"]
  end

  subgraph OT["Legacy OT  (unchanged)"]
    direction TB
    SCADA["SCADA\nThreshold Monitoring"]
    HMI["Operator HMIs"]
    TRUL["Threshold-Based RUL\nStatic Alarm"]
  end

  subgraph GDC["GDC Edge Cluster — On-Premises · No WAN Required"]
    direction TB
    MQ["RabbitMQ\nReal-Time Telemetry Bus"]
    AlloyDB[("AlloyDB Omni\nPostgreSQL + pgvector\nUnified Asset Data Store")]
    XGB["XGBoost ML\nHealth Score · Fault Probability\nInitial RUL"]
    subgraph GPU["NVIDIA L4 GPU"]
      Gemma["Gemma 27b\nLLM + RAG Engine"]
    end
  end

  subgraph OUT["Operator Interface"]
    direction TB
    RUL["AI-Informed RUL\nvs. SCADA Estimate"]
    Recs["Recommended Action\n+ HITL Approval"]
    Ledger["Cost Avoided\nFinancial Ledger"]
    Chat["Asset Chatbot\nOperator Q&A · Insights"]
  end

  FI["⚙ Fault Injector\n(Demo Only)"]:::demo

  Sensors -->|live telemetry| MQ
  MQ -->|sensor stream| SCADA
  SCADA --> HMI
  SCADA -->|threshold alarm| TRUL

  MQ -->|structured events| AlloyDB
  OpsRec -->|ingested + vectorized| AlloyDB
  Corpus -->|RAG knowledge base| AlloyDB

  AlloyDB -->|telemetry features| XGB
  XGB -->|health score + confidence| Gemma
  AlloyDB -.->|pgvector RAG retrieval| Gemma

  Gemma -->|context-aware RUL| RUL
  TRUL --> RUL
  Gemma -->|action recommendation| Recs
  Recs -->|operator approved| Ledger
  Gemma -->|knowledge retrieval| Chat

  FI -.->|simulated event| MQ

  classDef demo fill:#1e1e1e,stroke:#444,color:#555,stroke-dasharray:5 5
```

---

### Implementation — No CDN (Self-Contained)

The demo environment has no internet access from the client browser. Mermaid.js must be bundled.

#### Pre-Session Step (run once manually before starting):
```bash
# Download Mermaid.js into the static assets folder
curl -L https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js \
     -o /home/brian/gdc-pm/gke/fault-trigger-ui/static/mermaid.min.js

# Verify FastAPI serves static files (check this line exists in app.py):
grep "StaticFiles\|/static" /home/brian/gdc-pm/gke/fault-trigger-ui/app.py
```
If FastAPI doesn't already mount `/static`, add one line to `app.py` (this is the ONLY permitted `app.py` change this session).

#### The 3 Insertions in index.html

**Insertion 1 — In `<head>`, after existing scripts (around line 10-20):**
```html
<script src="/static/mermaid.min.js"></script>
<script>mermaid.initialize({startOnLoad:true, theme:'dark', flowchart:{useMaxWidth:true, htmlLabels:true}})</script>
```

**Insertion 2 — Tab button, after line 491 (after Fleet Telemetry hdr-tab):**
```html
<div class="hdr-tab" :class="{active: mainTab==='architecture'}" @click="mainTab='architecture'">How It Works</div>
```

**Insertion 3 — Tab content, after line 1256 (after `</div>` closing telemetry tab, before `</div><!-- app-body -->`):**
```html
<div id="tab-architecture" class="main-tab-content" :class="{active: mainTab==='architecture'}" style="overflow-y:auto;padding:32px 48px;background:var(--bg)">
  <div style="max-width:1200px;margin:0 auto">
    <div style="font-size:1.1rem;font-weight:700;color:var(--text2);margin-bottom:6px">GDC Predictive Maintenance — How It Works</div>
    <div style="font-size:0.75rem;color:var(--muted);margin-bottom:24px">Production deployment architecture — data flows left to right</div>
    <pre class="mermaid">
[PASTE APPROVED MERMAID DEFINITION HERE]
    </pre>
  </div>
</div>
```

No Vue `data()` changes needed. No `app.py` changes (unless static mount is missing).

---

### Verification Sequence (in order — do not skip steps)

```bash
# Step 1: Confirm no duplicate tab divs
grep -c 'id="tab-telemetry"' gke/fault-trigger-ui/index.html   # must return 1
grep -c 'id="tab-architecture"' gke/fault-trigger-ui/index.html # must return 1

# Step 2: Confirm mermaid.min.js is in place
ls -lh gke/fault-trigger-ui/static/mermaid.min.js

# Step 3: Build and push
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm

# Step 4: Verify the new pod serves the static file
kubectl exec -n gdc-pm deployment/fault-trigger-ui -- ls /app/static/mermaid.min.js

# Step 5: Verify the tab appears
curl -s http://34.138.32.109/ | grep -c "How It Works"   # must return 1

# Step 6: Commit
git add gke/fault-trigger-ui/static/mermaid.min.js gke/fault-trigger-ui/index.html
git commit -m "feat: add Architecture tab with Mermaid.js data flow diagram"
```

---

### Rules for This Session (non-negotiable)

1. **One file only for diagram content:** `index.html` (plus `static/mermaid.min.js` as a binary asset)
2. **Zero SVG hand-coding.** The diagram definition is the approved Mermaid text above.
3. **Skeleton first:** Add the empty tab div, build+push, confirm "How It Works" tab appears and is clickable, THEN add the Mermaid content.
4. **Duplicate div check after every insertion** (see Step 1 above).
5. **Commit after verified deployment.** Not before.
6. **Do not touch:** `app.py` (unless static mount missing), `DEPLOY_FROM_SCRATCH.md`, `NEXT_SESSION_PROMPT.md`, any other docs.

---

## What IS Working (no regressions from 08b590a)

| Feature | Status |
|---------|--------|
| All 4 XGBoost health models | ✅ |
| Fix 9: Dynamic docs all 11 fault types | ✅ |
| Fix 10: Dynamic Gemma finding | ✅ |
| Fix 11b: fault_sessions write path | ✅ |
| HITL approve → savings → financials | ✅ |
| gpu-start.sh / gpu-stop.sh | ✅ |
| Honest Gemma status | ✅ |

---

## Constraints (never violate)
- `terraform/gke.tf` must NOT be applied without review
- Preserve XGBoost models (`*.ubj` files)
- `/api/*` endpoints must remain backward-compatible
- Do NOT commit to `main`
- **No browser on SSH remote** — `browser_action` must NOT be used
- **Commit after every verified deployment**

---

## Rebuild & Deploy Commands
```bash
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm
```

---

## Current Cluster State (VERIFIED May 25, 2026 ~22:32 UTC)

```
fault-trigger-ui   1/1  Running  (sha256:ecae6a — clean 08b590a build)
alloydb-omni       1/1  Running
event-processor    1/1  Running
gdc-pm-rabbitmq    1/1  Running
grafana            1/1  Running
inference-api      1/1  Running
ollama             1/1  Running  (GPU · gemma:27b serving)
telemetry-sim      1/1  Running

AlloyDB: field_intel=100, rag_documents=0 ⚠️, fault_sessions=2
```

---

## Key Lessons (May 25 — do not repeat)
- **Mermaid text > SVG coordinates.** Cline reasons about text, not pixels. Mermaid.js converts text to SVG automatically.
- **Preview at mermaid.live before any code.** The diagram definition is the deliverable; HTML integration is 10 lines.
- **Skeleton tab first, content second.** Two deploys, two commits. Never combine.
- **Duplicate div check is mandatory** after every HTML insertion.
- **One scope per session.** Architecture tab only. Nothing else.
