# Next Session Prompt — ESP v2 Redesign (Gemma 4 Live) & Git Remote Migration Handoff

## Header
**Date:** June 2, 2026
**Live URL:** http://34.138.32.109 (us-east1 cluster)
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `09595c03593f4b711c0df828259c2b89c03c951c` (Clean working tree)
**Image:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest` (deployed June 2, 2026 — Gemma 4 8B)

---

## ⚠️ MANDATORY SESSION OPENER — Run this BEFORE writing any code

```bash
# 1. Verify cluster truth
kubectl get pods -n gdc-pm --no-headers

# 2. Verify Ollama state
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""

# 3. API truth
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"

# 4. Database truth
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability \
  -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents; SELECT COUNT(*) FROM fault_sessions;"

# 5. Check Ollama PVC models
kubectl exec -n gdc-pm deployment/ollama -- ollama list
```

**Expected results when healthy:**
- All pods: `1/1 Running`
- Ollama: `1` replica, `ollama_online: True  model: gemma4:latest`
- rag_documents: **18 rows** ✅
- field_intel: **100 rows** ✅
- fault_sessions: **4 rows** ✅

---

## ⚠️ Known Integrity State (VERIFIED June 2, 2026)

| Item | Display Says | Reality | Status |
|------|-------------|---------|--------|
| Gemma model | "Gemma 4 8B" | `gemma4:latest` (8B, 128K context) | ✅ CLEAN |
| Architecture tab | v5 live | Full-width panes, ⓘ popups, SCADA subscriber | ✅ |
| Grafana URL | 35.190.137.145 | Live Grafana LB IP | ✅ Fixed |
| Field Link badge | "Field Link" | WAN state indicator | ✅ |
| Guided Tour values | Static (Health: 0.34) | Illustrative | Acceptable |
| rag_documents | 18 rows ✅ | Healthy | ✅ |
| field_intel | 100 rows ✅ | Active | ✅ |
| fault_sessions | 4 rows ✅ | Working | ✅ |
| GPU CronJobs | SUSPENDED ✅ | Manual only | ✅ |

---

## Ollama PVC Model Inventory

```
gemma4:latest    9.6 GB   ← ACTIVE (running)  Gemma 4 8B, 128K ctx
gemma3:27b       17 GB    ← fallback           Gemma 3 27B
gemma4:31b       19 GB    ← READY (downloaded) Gemma 4 31B, 128K ctx
```

Disk: 49GB PVC, all 3 models fully downloaded and ready. Free space is tight (~5.1GB free) but stable.

---

## GPU Management (Manual — No CronJobs)

```bash
cd /home/brian/gdc-pm && ./scripts/gpu-start.sh   # start of day
cd /home/brian/gdc-pm && ./scripts/gpu-stop.sh    # end of day
```

---

## NEXT SESSION PLAN (For the New Git Remote Task-Stream)

| Fix | Change | Verification | Est. complexity |
|-----|--------|--------------|-----------------|
| Switch to gemma4:31b (optional) | `kubectl set env + rebuild` if higher quality needed for next phase | API reports gemma4:31b | Small |
| Live data wiring | Fetch health score / RUL from `/api/degrade-status` for Pane 3 | Pane 3 chip shows live value | Medium |
| Update Demo Narrative | Update `docs/DEMO_NARRATIVE_UPDATE.md` with v5 architecture terms | Check markdown file contents | Small |

---

## What Was Done This Session (all deployed, live, committed)

| Version | Change | Status |
|---------|--------|--------|
| Clean up scratch scripts | **Removed rewrite_arch.py, update_arch.py, fix_arch_v3.py, fix_arch_v4.py, and fix_arch_v5.py from the repository root** | ✅ |
| Pane 2 Terminology | **Updated Intake PSI to Pump Intake Pressure (PIP) and noted positive reservoir pressure must be maintained inside Pane 2 info popup** | ✅ |
| GKE Rollout | **Rebuilt fault-trigger-ui image, pushed to GCR, restarted deployment, and verified live UI changes via HTTP curl** | ✅ |

---

## Current Cluster State (VERIFIED June 2, 2026 ~19:28 UTC)

```
alloydb-omni-5fcfc68fdb-9vm2z           1/1   Running
event-processor-7d9b594b6b-j5jp8        1/1   Running
fault-trigger-ui-68c9d65b6c-rl5bl       1/1   Running   ← Gemma 4 8B active
gdc-pm-rabbitmq-server-0                1/1   Running
grafana-655b6f5c7c-w2h84                1/1   Running   ← LB IP 35.190.137.145
inference-api-5697b79566-zqdpl          1/1   Running
ollama-5bc5db749b-n6tb8                 1/1   Running   ← gemma4:latest (8B) active
telemetry-simulator-6b9668648b-x6622    1/1   Running

Ollama: 1 replica, model: gemma4:latest, online: True ✅
AlloyDB: field_intel=100 ✅, rag_documents=18 ✅, fault_sessions=4 ✅
git: clean, ready for next session
```

---

## Outstanding Development Items (Backlog)

| Priority | Item | Note |
|----------|------|------|
| High | Upgrade to gemma4:31b (optional) | Model ready; see switch commands in prior prompt history; free gemma3:27b to make space |
| High | Live data wiring | Pane 3 from `/api/degrade-status` |
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

## Key Lessons Learned (June 2 session)

- **Context Verification & Alignment**: Always verify the active kubectl context. The developer host VM had context set to an older `us-central1` cluster which resulted in timeouts, but switching to the `gke_gdc-pm-v2_us-east1_gdc-edge-simulation` context resolved all networking issues instantly.
- **Project Isolation**: Data Sources in Terraform prevent overlap with central resources and allow developers to deploy without modifying foundational networking or cross-contaminating sibling workspaces.
