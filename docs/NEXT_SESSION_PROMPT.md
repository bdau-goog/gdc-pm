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

## NEXT SESSION OBJECTIVE: "How It Works" Architecture Tab

Full implementation plan (HTML/CSS Flexbox approach, exact code blocks, insertion points):
→ **`docs/ARCHITECTURE_TAB_PLAN.md`**

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
