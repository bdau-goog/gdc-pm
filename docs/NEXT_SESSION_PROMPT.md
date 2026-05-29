# Next Session Prompt — ESP v2 Redesign (Gemma 4 Live)

## Header
**Date:** May 29, 2026
**Live URL:** http://34.138.32.109 (us-east1 cluster)
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `5c2dd5a` — clean working tree (scratch files in root: `rewrite_arch.py`, `update_arch.py`, `fix_arch_v3–v5.py` — safe to delete)
**Image:** `sha256:3f12d9e558db7224edb430abf82b5c7a0c7486b2b61e636188c0feb3c125aff5` (deployed May 29 — Gemma 4 8B)

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

# 5. Check Ollama PVC models (gemma4:31b may have completed background pull)
kubectl exec -n gdc-pm deployment/ollama -- ollama list
```

**Expected results when healthy:**
- All pods: `1/1 Running`
- Ollama: `1` replica, `ollama_online: True  model: gemma4:latest`
- rag_documents: **18 rows** ✅
- field_intel: **100 rows** ✅
- fault_sessions: ≥ 3 rows ✅

---

## ⚠️ Known Integrity State (VERIFIED May 29, 2026)

| Item | Display Says | Reality | Status |
|------|-------------|---------|--------|
| Gemma model | "Gemma 4 8B" | `gemma4:latest` (8B, 128K context) | ✅ CLEAN |
| Architecture tab | v5 live | Full-width panes, ⓘ popups, SCADA subscriber | ✅ |
| Grafana URL | 35.190.137.145 | Live Grafana LB IP | ✅ Fixed |
| Field Link badge | "Field Link" | WAN state indicator | ✅ |
| Guided Tour values | Static (Health: 0.34) | Illustrative | Acceptable |
| rag_documents | 18 rows ✅ | Healthy | ✅ |
| field_intel | 100 rows ✅ | Active | ✅ |
| fault_sessions | 3 rows ✅ | Working | ✅ |
| GPU CronJobs | SUSPENDED ✅ | Manual only | ✅ |

---

## Ollama PVC Model Inventory

```
gemma4:latest    9.6 GB   ← ACTIVE (running)  Gemma 4 8B, 128K ctx
gemma3:27b       17 GB    ← fallback           Gemma 3 27B
gemma4:31b       ~in progress 22% when last checked (28 MB/s, ~9 min remaining)
                            → will be ~19 GB when complete
```

Disk: 49GB PVC, 33GB used (17GB free) before gemma4:31b completes.
After gemma4:31b: ~33 + ~15 more = ~48GB (tight — may need to delete gemma3:27b afterward)

---

## GPU Management (Manual — No CronJobs)

```bash
cd /home/brian/gdc-pm && ./scripts/gpu-start.sh   # start of day
cd /home/brian/gdc-pm && ./scripts/gpu-stop.sh    # end of day
```

---

## NEXT SESSION PLAN

| Fix | Change | Verification | Est. complexity |
|-----|--------|--------------|-----------------|
| Verify gemma4:31b | Check if background pull completed; `ollama list` | Appears in list at 19GB | Small |
| Switch to gemma4:31b (optional) | `kubectl set env + rebuild` if higher quality needed | API reports gemma4:31b | Small |
| Pane 2 ⓘ bullet | "Intake PSI" → "Pump Intake Pressure (PIP)" + note positive reservoir pressure | Check ⓘ on Pane 2 | Small |
| Live data wiring | Fetch health score / RUL from `/api/degrade-status` for Pane 3 | Pane 3 chip shows live value | Medium |
| Clean up scratch scripts | Delete `rewrite_arch.py`, `update_arch.py`, `fix_arch_v3–v5.py` from repo root | git status clean | Small |

### Upgrading to gemma4:31b (when pull completes):
```bash
# Verify pull complete
kubectl exec -n gdc-pm deployment/ollama -- ollama list | grep gemma4:31b

# Switch model env var (no image rebuild needed)
kubectl set env deployment/fault-trigger-ui -n gdc-pm OLLAMA_MODEL=gemma4:31b OLLAMA_DISPLAY_MODEL=gemma4:31b

# Update HTML labels: Gemma 4 8B → Gemma 4 31B
python3 -c "
FILE='gke/fault-trigger-ui/index.html'
with open(FILE) as f: h = f.read()
h = h.replace('Gemma 4 8B','Gemma 4 31B').replace('gemma4:latest','gemma4:31b')
with open(FILE,'w') as f: f.write(h)
print('done')
"

# Update app.py default
sed -i 's/gemma4:latest/gemma4:31b/g' gke/fault-trigger-ui/app.py

# Rebuild and deploy (then delete gemma3:27b to free space)
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm

# Free space after upgrade (delete old models)
kubectl exec -n gdc-pm deployment/ollama -- ollama rm gemma3:27b
```

---

## What Was Done This Session (all deployed, live, committed)

| Version | Change | Status |
|---------|--------|--------|
| arch v2–v5 | Full architecture tab overhaul: ⓘ popups, field-of-pads, SCADA subscriber, Gemma 4 labels, tab reorder, Grafana URL fix, Field Link | ✅ |
| gemma3:27b | Pulled Gemma 3 27B as interim upgrade | ✅ (kept as fallback) |
| **gemma4:latest** | **Gemma 4 8B with 128K context — live and running** | ✅ |
| gemma4:31b | Background pull in progress | ⏳ ~9 min from last check |
| Code integrity | All labels match running model throughout | ✅ CLEAN |

---

## Current Cluster State (VERIFIED May 29, 2026 ~13:52 UTC)

```
alloydb-omni-5fcfc68fdb-9vm2z           1/1  Running
event-processor-7d9b594b6b-j5jp8        1/1  Running
fault-trigger-ui-6b9c5bb869-b8gck       1/1  Running  ← Gemma 4 8B active
gdc-pm-rabbitmq-server-0                1/1  Running
grafana-655b6f5c7c-w2h84                1/1  Running  ← LB IP 35.190.137.145
inference-api-5697b79566-zqdpl          1/1  Running
ollama-5bc5db749b-n6tb8                 1/1  Running  ← gemma4:latest (8B) active
telemetry-simulator-6b9668648b-x6622    1/1  Running

Ollama: 1 replica, model: gemma4:latest, online: True ✅
AlloyDB: field_intel=100 ✅, rag_documents=18 ✅, fault_sessions=3 ✅
git: 5c2dd5a clean, pushed to origin/esp-v2-redesign
```

---

## Outstanding Development Items (Backlog)

| Priority | Item | Note |
|----------|------|------|
| High | Upgrade to gemma4:31b (optional) | Already pulling; when done, see switch commands above; free gemma3:27b to make space |
| High | Pane 2 ⓘ: "Intake PSI" → "Pump Intake Pressure (PIP)" | 5-line Python replace |
| High | Live data wiring | Pane 3 from `/api/degrade-status` |
| Medium | Clean up scratch Python scripts | `rewrite_arch.py`, `fix_arch_v3–v5.py` in repo root |
| Medium | Demo narrative doc update | `docs/DEMO_NARRATIVE_UPDATE.md` — align with v5 terminology |

---

## Constraints (never violate)
- `terraform/gke.tf` must NOT be applied without review
- Preserve XGBoost models (`*.ubj` files)
- `/api/*` endpoints must remain backward-compatible
- Do NOT commit to `main`
- **No browser on SSH remote** — `browser_action` must NOT be used
- **Commit after every verified deployment**
- **CSS goes in `<head>` — never in a `<style>` tag inside `#app`**
- **Use Python regex for large HTML block replacements** — `replace_in_file` fails on 3000+ line files
- **Never display X when Y is running** — label reality, or document the gap immediately

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

## Key Lessons Learned (May 29 session)

- **Gemma 4 parameter counts are different from Gemma 3.** Gemma 4's sizes are: 8B, 12B (unclear), 31B — NOT 27B. Always check HuggingFace before assuming the Ollama tag.
- **`gemma4:latest` = 8B in Ollama.** The default is not the largest model. Use `gemma4:31b` for the largest.
- **128K context is the Gemma 4 headline feature** — 16× larger than Gemma 3's 8K. For edge AI demos, this is a stronger story than parameter count because it means the full fault session history fits in a single prompt.
- **GPU scheduling deadlock**: Rolling update of the Ollama deployment fails because the GPU is exclusive. Use `Recreate` strategy or manually delete old pod + rollback if needed.
- **Disk management matters on model PVCs**: At 49GB PVC with multiple 15-17GB models, always check `df -h` before pulling a new model. Delete old models before pulling new ones.
- **`ollama pull` resumes from partial blobs**: If a pull is interrupted, Ollama caches partial blobs. Resume with the same pull command and it picks up from the last complete chunk.
