# Next Session Prompt — ESP v2 Redesign (Guided Tour Architecture Tab)

## Header
**Date:** May 28, 2026
**Live URL:** http://34.138.32.109 (us-east1 cluster)
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `a224143` — clean working tree ✅
**Image:** `sha256:b95558ae8b82a2c7977a621587fb1ae09a2283f683ccb61cf62d4f214a972d4e` (deployed May 28 — includes 6-pane Guided Tour)

---

## ⚠️ MANDATORY SESSION OPENER — Run this BEFORE writing any code

```bash
# 0. Push uncommitted commits to origin
cd ~/gdc-pm && git push

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
- rag_documents: **18 rows** ✅
- fault_sessions: ≥ 3 rows ✅

---

## ⚠️ Known Integrity State (VERIFIED May 28, 2026)

| Item | Actual State | Action Required |
|------|-------------|-----------------|
| Architecture tab | ✅ 6-pane Guided Tour deployed and verified at 34.138.32.109 | Visual review by user recommended |
| Guided Tour content | Static (hardcoded example values) | Could be made live-data-aware in a future session |
| rag_documents | 18 rows ✅ | Healthy |
| fault_sessions | 3 rows ✅ | Working |
| field_intel | 100 rows ✅ | Active |
| Ollama / gemma:27b | `ollama_online: True` ✅ | Running on GPU |
| GPU CronJobs | SUSPENDED ✅ | Use manual scripts only |

---

## GPU Management (Manual — No CronJobs)

```bash
cd /home/brian/gdc-pm && ./scripts/gpu-start.sh   # start of day
cd /home/brian/gdc-pm && ./scripts/gpu-stop.sh    # end of day
```

---

## NEXT SESSION OBJECTIVES

### Priority 1 — Guided Tour Content Review + Iteration

Review the live Architecture tab at http://34.138.32.109 → "How It Works" and plan changes.

**Known feedback from user (May 28):**
- **System Overview pane:** The `SCADA RTU` chip label should be replaced with a list of the actual physical sensors (PSI, Temp, Vibration, Motor Amps) rather than the RTU acronym. The point is to show what the sensors ARE, not the protocol device that reads them.

**Review checklist per pane:**
| Pane | Review focus |
|------|-------------|
| 1 — System Overview | Replace "SCADA RTU" chip with sensor list chips |
| 2 — Data Ingestion | Verify sensor physics descriptions are accurate |
| 3 — ML Detection | Confirm 6-feature list matches actual model features |
| 4 — Context Fusion | Verify AlloyDB row counts match live cluster (18 rag_docs, 100+ field_intel) |
| 5 — AI Reasoning | Confirm Gemma latency claim (<8s) is realistic |
| 6 — Operator Value | Review financial figures |

**File surgery approach:** Use Python regex to replace the arch tab, as before.

### Priority 2 — Live Data Wiring (Optional Enhancement)

The guided tour currently uses static/illustrative values (e.g., "Health: 0.34", "RUL: 22.1 min"). If desired, these could be updated to show live values from the active cluster state on specific panes.

---

## What Was Done This Session

| Feature | Status |
|---------|--------|
| Architecture tab Vue context bug (orphaned HTML) | ✅ Fixed — modals were outside #app, template syntax was rendering raw |
| Architecture tab: broken 4-tier flat layout | ✅ Replaced with 6-pane Guided Tour |
| Guided Tour: 6 focused sub-tabs | ✅ Deployed — System Overview, Data Ingestion, ML Detection, Context Fusion, AI Reasoning, Operator Value |
| `archPane` Vue state variable | ✅ Injected into data() |
| New CSS component library | ✅ `.arch-stage`, `.arch-chip`, `.arch-connector`, `.arch-narrative-card`, `.arch-compare-row` etc. |

---

## Constraints (never violate)
- `terraform/gke.tf` must NOT be applied without review
- Preserve XGBoost models (`*.ubj` files)
- `/api/*` endpoints must remain backward-compatible
- Do NOT commit to `main`
- **No browser on SSH remote** — `browser_action` must NOT be used
- **Commit after every verified deployment**
- **CSS goes in `<head>` — never in a `<style>` tag inside `#app`**
- **Use Python regex for large HTML block replacements** — `replace_in_file` fails on 2500+ line files

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

## Current Cluster State (VERIFIED May 28, 2026)

```
fault-trigger-ui-86b7d49c95-6pcq9   1/1  Running  (Guided Tour deployed)
alloydb-omni-5fcfc68fdb-x9xc8       1/1  Running  
event-processor-7d9b594b6b-wjlkc    1/1  Running  
gdc-pm-rabbitmq-server-0            1/1  Running  
grafana-655b6f5c7c-mtmtw            1/1  Running  
inference-api-5697b79566-4q8tm      1/1  Running  
ollama-5bc5db749b-jf997             1/1  Running   ← GPU
telemetry-simulator-6b9668648b-ddc66 1/1 Running  

Ollama replicas: 1
API: ollama_online: True  model: gemma:27b ✅
AlloyDB: field_intel=100, rag_documents=18 ✅, fault_sessions=3
git: a224143 clean, pushed to origin/esp-v2-redesign
```

---

## Key Lessons Learned (May 28 session)

- **Orphaned HTML outside `#app` silently breaks Vue compilation** — Vue3 production builds don't throw console errors, they just stop compiling templates. Modals showing `{{ template }}` raw syntax is the symptom. Always verify `</div><!-- app-body -->` is the last thing before the modals.
- **Python regex replacement is the only reliable approach for large HTML files** — The `replace_in_file` tool consistently fails to match multi-line blocks in 2500+ line files due to whitespace/character edge cases.
- **Verify with `curl | grep -c` not just `kubectl get pods`** — Pod running doesn't mean the right code is live. `curl -s http://34.138.32.109/ | grep -c "archPane"` confirms the actual deployed content.
