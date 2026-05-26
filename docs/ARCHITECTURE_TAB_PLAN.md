# Architecture Tab — Development Plan

**Status:** Approved for implementation  
**Target:** Add a "How It Works" tab to `gke/fault-trigger-ui/index.html`  
**Approach:** Mermaid.js (self-hosted, no CDN)

---

## The CxO Story This Diagram Tells

Reading left to right, in one glance:

1. **Your existing SCADA and sensors keep working** — GDC is additive, not a rip-and-replace
2. **GDC captures the same telemetry AND your operational knowledge** (records, standards) in one place
3. **XGBoost predicts failure mathematically** — SCADA only alarms after a threshold is breached (too late)
4. **Gemma reads context the way your best engineer would** — ops records, lab reports, industry standards — at the edge, with no cloud, in seconds
5. **The output is an informed RUL, a recommended action, and a dollar figure** — not just an alarm
6. **Everything runs on-premises inside GDC** — the GPU sub-box makes the compute requirement visible

---

## Approved Diagram Definition

**Preview at https://mermaid.live before any coding session begins.**

> ⚠️ **mermaid.live has three tabs: Code · Config · Docs.**
> Paste the diagram into the **Code tab only.** The Config tab expects JSON — pasting Mermaid syntax there produces `SyntaxError: Unexpected token 'l', "flowchart L"... is not valid JSON`. This is a UI mistake, not a syntax error.

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

  FI["Fault Injector\n(Demo Only)"]:::demo

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

  classDef demo fill:#1e1e1e,stroke:#555,color:#666
```

---

## Why Mermaid.js (not SVG)

| Approach | Problem |
|----------|---------|
| Hand-coded SVG | Requires visual preview to verify; LLMs reason about text, not pixels; 1500+ lines; broke the file in the May 25 afternoon session |
| HTML/CSS flexbox | Cannot represent non-linear edges (arrows that cross tiers) |
| Mermaid.js | Text-based definition (~50 lines); LLM can write and verify it; browser renders SVG automatically; dark theme built-in |

---

## Implementation Steps

### Pre-Session (run once manually — ~2 minutes)

```bash
# 1. Download Mermaid.js as a static asset (no CDN — demo is self-contained)
curl -L https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js \
     -o /home/brian/gdc-pm/gke/fault-trigger-ui/static/mermaid.min.js

# 2. Verify FastAPI mounts /static (check app.py)
grep "StaticFiles\|/static" /home/brian/gdc-pm/gke/fault-trigger-ui/app.py
```

If `/static` is not mounted in `app.py`, add this (only permitted `app.py` change):
```python
app.mount("/static", StaticFiles(directory="static"), name="static")
```

---

### Session Work — index.html only (3 insertions)

**Current file:** 2242 lines. Three surgical insertions required.

---

**Insertion 1 — `<head>` section (after existing scripts, ~line 15):**
```html
<script src="/static/mermaid.min.js"></script>
<script>mermaid.initialize({startOnLoad:true, theme:'dark', flowchart:{useMaxWidth:true, htmlLabels:true}})</script>
```

---

**Insertion 2 — Tab button, after line 491 (after the Fleet Telemetry `hdr-tab`):**
```html
<div class="hdr-tab" :class="{active: mainTab==='architecture'}" @click="mainTab='architecture'">How It Works</div>
```

---

**Insertion 3 — Tab content block, after line 1256 (after `</div>` closing the telemetry tab, BEFORE `</div><!-- app-body -->`):**
```html
<div id="tab-architecture" class="main-tab-content" :class="{active: mainTab==='architecture'}" style="overflow-y:auto;padding:32px 48px;background:var(--bg)">
  <div style="max-width:1200px;margin:0 auto">
    <div style="font-size:1.1rem;font-weight:700;color:var(--text2);margin-bottom:6px">GDC Predictive Maintenance — How It Works</div>
    <div style="font-size:0.75rem;color:var(--muted);margin-bottom:24px">Production deployment architecture · data flows left to right</div>
    <pre class="mermaid">
[PASTE APPROVED MERMAID DEFINITION HERE]
    </pre>
  </div>
</div>
```

No Vue `data()` changes needed — `mainTab` is a free string.

---

### Verification Sequence (do not skip any step)

```bash
# 1. Duplicate div check — both must return 1
grep -c 'id="tab-telemetry"' gke/fault-trigger-ui/index.html
grep -c 'id="tab-architecture"' gke/fault-trigger-ui/index.html

# 2. Mermaid.js in place
ls -lh gke/fault-trigger-ui/static/mermaid.min.js

# 3. Build and deploy
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm

# 4. Verify static file is served from the pod
kubectl exec -n gdc-pm deployment/fault-trigger-ui -- ls /app/static/mermaid.min.js

# 5. Verify tab appears in the page
curl -s http://34.138.32.109/ | grep -c "How It Works"   # must return 1

# 6. Commit
git add gke/fault-trigger-ui/static/mermaid.min.js gke/fault-trigger-ui/index.html
git commit -m "feat: add How It Works tab with Mermaid.js architecture diagram"
```

---

## Session Rules (non-negotiable)

1. **Preview at mermaid.live first.** Do not write a single line of HTML until the diagram text is approved.
2. **Skeleton before content.** Add the empty tab div, build+deploy, confirm the tab is clickable — then add the Mermaid `<pre>` block in a second deploy.
3. **One file for diagram content:** `index.html`. Plus `static/mermaid.min.js` as a binary asset.
4. **Zero SVG hand-coding.**
5. **Do not touch:** `app.py` (unless static mount missing), any docs, `DEPLOY_FROM_SCRATCH.md`, `NEXT_SESSION_PROMPT.md`.
6. **Commit after verified deployment only.**

---

## What Went Wrong in the Previous Attempt (May 25 afternoon)

Do not repeat these:

| Failure | Root Cause |
|---------|-----------|
| 1500-line hand-coded SVG | No visual preview available on SSH remote; LLM cannot verify pixel coordinates |
| Duplicate `<div id="tab-telemetry">` | SVG inserted at wrong position without checking context |
| `DEPLOY_FROM_SCRATCH.md` accidentally modified | Session scope was too wide — touched files outside the stated objective |
| No incremental testing | Tab was never verified to render before session ended |
| No plan approval | Jumped from requirement directly to 1500 lines of code |
