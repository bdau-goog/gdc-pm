# Next Session Prompt — ESP v2 Redesign (Stage 2 COMPLETE)

## Header
**Date:** May 25, 2026
**Live URL:** http://34.138.32.109 (us-east1 cluster)
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `08b590a` — "feat: finalize stage 2 fixes and runbooks" ✅ clean working tree
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
- All pods: `1/1 Running` (fault-trigger-ui, alloydb-omni, event-processor, rabbitmq, grafana, inference-api, telemetry-sim, ollama)
- Ollama: `1` replica
- API: `ollama_online: True  model: gemma:27b`
- rag_documents: **11 rows** ⚠️ was 0 at last check — if still 0, investigate before proceeding
- fault_sessions: ≥ 2 rows

---

## ⚠️ Known Integrity State

| Item | Actual State | Action Required |
|------|-------------|-----------------|
| **rag_documents** | **0 rows** (expected 11) | Investigate and restore before any demo. If pod restart caused it, re-seed from init script. |
| fault_sessions | 2 rows ✅ | Working |
| field_intel | 100 rows ✅ | Active |
| Ollama / gemma:27b | `ollama_online: True` ✅ | Serving on GPU |
| GPU CronJobs | SUSPENDED ✅ | Use manual scripts only |

---

## GPU Management (Manual — No CronJobs)

```bash
# Start GPU (beginning of work day):
cd /home/brian/gdc-pm && ./scripts/gpu-start.sh

# Stop GPU (end of day):
cd /home/brian/gdc-pm && ./scripts/gpu-stop.sh

# Verify Gemma serving:
kubectl exec -n gdc-pm deployment/ollama -- curl -sf http://localhost:11434/api/tags \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print([m['name'] for m in d.get('models',[])])"
# Must return: ['gemma:27b']
```

---

## THIS SESSION'S OBJECTIVE: Architecture Diagram Tab

### Context: Why This Matters
The demo narrative (see `docs/DEMO_NARRATIVE_UPDATE.md`) positions GDC-PM as a **multi-modal AI platform at the tactical edge**. There is currently no visual explanation of how the pieces connect. A "How It Works" architecture tab in the live UI serves two purposes:
1. Gives a customer something to look at while the system is booting/fault-injecting
2. Grounds the demo story — shows that sensor data, unstructured docs, XGBoost, and Gemma all converge in one place

### What the Previous Attempt Did Wrong (Do NOT Repeat)
The afternoon session on May 25 produced a broken implementation. Specific failures:

1. **No upfront plan approval** — jumped straight to 1500+ lines of SVG code without getting the layout approved first
2. **Massive inline SVG** — used SVG gradients, glow filters, and `<defs>` blocks; too complex to debug without a browser
3. **Duplicate HTML** — the `<div id="tab-telemetry">` block appeared twice in the file, breaking the tab layout
4. **Wrong file modified** — `DEPLOY_FROM_SCRATCH.md` was accidentally replaced during the same session
5. **No incremental testing** — the tab was never verified to render before the session ended

### The Correct Approach for This Session

**Step 1 — Present the wireframe in ASCII, get approval before writing any HTML.**

Proposed layout for the "Architecture" tab:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HOW IT WORKS                                          │
│              GDC Predictive Maintenance — Data Flow                          │
├──────────────┬──────────────────┬───────────────────┬────────────────────────┤
│  INPUT TIER  │   MESSAGING &    │   AI ENGINE        │   OPERATOR OUTPUT      │
│              │   STORAGE        │                    │                        │
│ ESP Sensors  │                  │  XGBoost           │  Fleet Operations      │
│ ─────────────│→  RabbitMQ  ─────│→ Inference API  ───│→ Tab (health score,    │
│ Telemetry    │                  │  (3 models)        │  RUL, HITL approval)   │
│              │→  AlloyDB ───────│→ Gemma 27b      ───│→ Fleet Financials      │
│ Unstructured │   ┌─telemetry    │  (RAG + LLM)       │  Tab (cost avoided,    │
│ Documents    │   ├─field_intel  │  NVIDIA L4 GPU     │  fault audit log)      │
│ (shift notes │   ├─rag_docs     │                    │→ Grafana Telemetry     │
│  Maximo,     │   └─fault_sess.  │                    │  Tab (live charts)     │
│  lab reports)│                  │                    │                        │
└──────────────┴──────────────────┴───────────────────┴────────────────────────┘
```

**Step 2 — Build with HTML/CSS divs, NOT SVG.**

Rationale: The app's dark theme is already established via CSS variables. An HTML/CSS flexbox diagram:
- Uses the existing `var(--blue)`, `var(--surf2)`, `var(--text2)`, `var(--border2)`, `var(--muted)` tokens — no new styles needed
- Is readable as plain text (can be verified without a browser)
- Has no SVG-specific bugs (no coordinate systems, no `<defs>`, no `transform` attributes)
- Degrades gracefully if the container resizes

**Step 3 — Insert the tab skeleton first (5 lines), verify it renders, THEN add diagram content.**

**Step 4 — One file only: `gke/fault-trigger-ui/index.html`. Do NOT touch `app.py` or any doc files.**

**Step 5 — Build, push, and verify in the live cluster before declaring done.**

---

### Exact Insertion Points in index.html (2242 lines total)

**Tab button** — insert after line 491 (after the telemetry hdr-tab):
```html
<div class="hdr-tab" :class="{active: mainTab==='architecture'}" @click="mainTab='architecture'">Architecture</div>
```

**Tab content block** — insert after line 1256 (after `</div>` closing the telemetry tab, before `</div><!-- app-body -->`):
```html
<div id="tab-architecture" class="main-tab-content" :class="{active: mainTab==='architecture'}" style="overflow-y:auto;padding:32px 48px">
  <!-- architecture diagram goes here -->
</div>
```

No Vue `data()` change needed — `mainTab` is a free string, any value works.

---

### Diagram Content: What to Show

The diagram must tell this story (from `DEMO_NARRATIVE_UPDATE.md`):

| Layer | Components | Key Message |
|-------|-----------|-------------|
| **Input** | ESP sensors, SCADA, Shift notes, Maximo records, Lab reports | Multiple data modalities, not just sensors |
| **Ingestion** | RabbitMQ (telemetry bus) | Edge message broker — no cloud needed |
| **Storage** | AlloyDB Omni (PostgreSQL + pgvector) — 4 tables | Unified store: structured + unstructured |
| **AI** | XGBoost Inference API (health score + RUL) + Gemma 27b on L4 GPU (RAG + synthesis) | Multi-modal AI fully on-prem |
| **Output** | Operator HITL → approval → cost avoided → fault_sessions audit | Quantifiable ROI, closed loop |

**Keep it factual and minimal.** This is a demo aid, not a marketing brochure. Boxes, arrows (CSS borders or `→` text), and labels. No gradients, no animations, no icons that require external CDN.

---

### Recommended HTML/CSS Pattern

Use a CSS grid or flexbox with styled `<div>` cards. Example structure (to be approved by user before building):

```
[diagram-container: display:flex; gap:24px; align-items:flex-start]
  [tier-col] INPUT
    [node-card] ESP Sensors
    [node-card] Unstructured Docs
  [arrow] →
  [tier-col] INGESTION & STORAGE
    [node-card] RabbitMQ
    [node-card] AlloyDB Omni
      [sub-label] telemetry_events
      [sub-label] rag_documents (pgvector)
      [sub-label] field_intel
      [sub-label] fault_sessions
  [arrow] →
  [tier-col] AI ENGINE
    [node-card highlight-orange] XGBoost Inference
    [node-card highlight-purple] Gemma 27b (L4 GPU)
  [arrow] →
  [tier-col] OPERATOR
    [node-card] Fleet Operations (HITL)
    [node-card] Fleet Financials (ROI)
    [node-card] Grafana Telemetry
```

**Reuse existing CSS variables from the app.** Add any new styles as a scoped `<style>` block at the top of the new tab `<div>`, not in the global `<style>` section at the top of the file.

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

## What IS Working (no regressions)

| Feature | Status |
|---------|--------|
| All 4 XGBoost health models | ✅ |
| Fix 8b: Intel feed randomization | ✅ |
| Fix 9: Dynamic docs for all 11 fault types | ✅ |
| Fix 10: Dynamic Gemma finding (all fault types) | ✅ |
| Fix 11b: fault_sessions write on inject/resolve | ✅ |
| Honest Gemma status (⛔ when offline) | ✅ |
| HITL approve → savings → financials ledger | ✅ |
| gpu-start.sh / gpu-stop.sh | ✅ |
| Deploy-from-scratch runbook | ✅ |
| gemma:27b (was gemma4:27b typo — fixed) | ✅ |

---

## Constraints (never violate)
- `terraform/gke.tf` must NOT be applied without review
- All UI changes → `gke/fault-trigger-ui/index.html` and `gke/fault-trigger-ui/app.py` only
- Preserve XGBoost health score models (`*.ubj` files)
- `/api/*` endpoints must remain backward-compatible
- Do NOT commit to `main`
- O&G physics must remain authentic
- **No browser on SSH remote** — `browser_action` must NOT be used
- **`classifier_active = (fault_fraction > 0.20) or is_degrading`** — DO NOT REVERT
- **Commit after every verified deployment** — not just at session end

---

## Current Cluster State (VERIFIED May 25, 2026 ~22:32 UTC)

```
fault-trigger-ui-59fb946d59-24f5m   1/1  Running  22s   ← rebuilt from 08b590a
alloydb-omni-5fcfc68fdb-x9xc8       1/1  Running  3d9h
event-processor-7d9b594b6b-wjlkc    1/1  Running  3d8h
gdc-pm-rabbitmq-server-0            1/1  Running  3d8h
grafana-655b6f5c7c-mtmtw            1/1  Running  3d9h
inference-api-5697b79566-4q8tm      1/1  Running  3d8h
ollama-5bc5db749b-jf997             1/1  Running  10h   ← GPU
telemetry-simulator-6b9668648b-ddc66 1/1 Running  3d9h

API: ollama_online: True  model: gemma:27b ✅
AlloyDB: field_intel=100, rag_documents=0 ⚠️, fault_sessions=2
```

---

## Key Lessons Learned (May 25 — do not repeat)
- **Plan before code.** Get ASCII wireframe approved before writing a single line of HTML.
- **HTML/CSS > SVG** for diagrams on this stack. SVG is unverifiable without a browser.
- **One scope per session.** The architecture tab is the ONLY objective. Do not touch docs, app.py, or runbooks in the same session.
- **Skeleton first.** Add the empty tab and verify it appears in the UI before adding any content.
- **Duplicate div check.** After any HTML insertion, `grep -c 'id="tab-telemetry"' index.html` must return `1`.
