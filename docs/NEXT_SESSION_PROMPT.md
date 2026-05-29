# Next Session Prompt — ESP v2 Redesign (Architecture Tab v5)

## Header
**Date:** May 29, 2026
**Live URL:** http://34.138.32.109 (us-east1 cluster)
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `12f62b1` — clean working tree (scratch files in root: `rewrite_arch.py`, `update_arch.py`, `fix_arch_v3.py`, `fix_arch_v4.py`, `fix_arch_v5.py` — safe to delete)
**Image:** `sha256:8bf32b3551852396af6c2e49137681f0f8fc9528adaea50c1744993b99815e3f` (deployed May 29 — Architecture Tab v5)

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
- Ollama: `1` replica, `ollama_online: True  model: gemma:27b` (⚠ see integrity table below)
- rag_documents: **18 rows** ✅
- field_intel: **100 rows** ✅
- fault_sessions: ≥ 3 rows ✅

---

## ⚠️ Known Integrity State (VERIFIED May 29, 2026)

| Item | Display Says | Reality | Action Required |
|------|-------------|---------|-----------------|
| **Gemma label (HIGH)** | UI shows "Gemma 4 27B" | API reports `model: gemma:27b` = Gemma **2** 27B | Pull `gemma4:27b` in Ollama and update `OLLAMA_MODEL` env var — see plan below |
| Architecture tab | ✅ v5 live at 34.138.32.109 | Deployed | None |
| Grafana URL | ✅ Fixed to 35.190.137.145 | Live Grafana LB IP | None |
| Guided Tour values | Static (Health: 0.34) | Illustrative | Acceptable for demo |
| rag_documents | 18 rows ✅ | Healthy | None |
| fault_sessions | 3 rows ✅ | Working | None |
| field_intel | 100 rows ✅ | Active | None |
| Ollama replicas | 1 ✅ | Running on GPU | None |
| GPU CronJobs | SUSPENDED ✅ | Manual only | None |

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
| **#1 CRITICAL: Pull Gemma 4** | `kubectl exec -n gdc-pm deployment/ollama -- ollama pull gemma4:27b` then update model env var | API reports `model: gemma4:27b` | Medium (model download ~18GB) |
| Visual review | Walk all panes + Grafana tab now that URL is fixed | User confirms layout | Small |
| Pane 2 ⓘ bullet | "Intake PSI" → "Pump Intake Pressure (PIP)" + note positive reservoir pressure | Check ⓘ on Pane 2 | Small |
| Live data wiring | Fetch health score / RUL from `/api/degrade-status` for Pane 3 | Pane 3 chip shows live value | Medium |

### How to pull Gemma 4 27B (resolve integrity issue):
```bash
# Check available disk space first
kubectl exec -n gdc-pm deployment/ollama -- df -h /root/.ollama

# Pull gemma4:27b (requires ~18GB, GPU node must have space)
kubectl exec -n gdc-pm deployment/ollama -- ollama pull gemma4:27b

# Verify it loaded
kubectl exec -n gdc-pm deployment/ollama -- ollama list

# Update app.py OLLAMA_MODEL constant and redeploy if needed
grep -n "OLLAMA_MODEL\|gemma" gke/fault-trigger-ui/app.py
```

**File surgery approach:** Use Python regex for HTML changes. Do NOT use `replace_in_file` on the 3000+ line `index.html`.

---

## What Was Done This Session (all deployed, live, committed)

| Version | Change | Status |
|---------|--------|--------|
| v2 | Full arch tab overhaul: ⓘ popups, full-width diagrams, 38-well field-of-pads, parallel AlloyDB streams | ✅ |
| v3 | Flow polish: sensor chips, simplified stages, Pane 5 output cards, overflow bug fixed | ✅ |
| v4 | Terminology: Vibration, Message Bus, AlloyDB, Industry Corpus, AI-Based RUL, Actions, Operations | ✅ |
| v5 | Gemma 4 27B label, Context Store arrow, tab reorder, Grafana URL fix, Field Link, SCADA subscriber | ✅ |

---

## Current Cluster State (VERIFIED May 29, 2026 ~13:31 UTC)

```
alloydb-omni-5fcfc68fdb-9vm2z           1/1  Running
event-processor-7d9b594b6b-j5jp8        1/1  Running
fault-trigger-ui (new pod)              1/1  Running  ← Arch Tab v5 deployed
gdc-pm-rabbitmq-server-0                1/1  Running
grafana-655b6f5c7c-w2h84                1/1  Running  ← LB IP 35.190.137.145
inference-api-5697b79566-zqdpl          1/1  Running
ollama-5bc5db749b-n6tb8                 1/1  Running  ← model: gemma:27b (Gemma 2 — needs upgrade)
telemetry-simulator-6b9668648b-x6622    1/1  Running

Ollama replicas: 1
API: ollama_online: True  model: gemma:27b ⚠ (label says Gemma 4 — integrity gap)
AlloyDB: field_intel=100 ✅, rag_documents=18 ✅, fault_sessions=3 ✅
git: 12f62b1 clean, pushed to origin/esp-v2-redesign
```

---

## Outstanding Development Items (Backlog)

| Priority | Item | Note |
|----------|------|------|
| **Critical** | Pull and switch to gemma4:27b | UI labels say Gemma 4 but Gemma 2 is running — integrity violation |
| High | Pane 2 ⓘ bullet: "Intake PSI" → "Pump Intake Pressure (PIP)" | ~5-line Python replace; add note that PIP is positive reservoir pressure |
| High | Live data wiring | Pane 3 health score / Base RUL from `/api/degrade-status` |
| Medium | Clean up scratch scripts in repo root | `rewrite_arch.py`, `update_arch.py`, `fix_arch_v3.py`, `fix_arch_v4.py`, `fix_arch_v5.py` |
| Medium | Demo narrative doc update | `docs/DEMO_NARRATIVE_UPDATE.md` — align with v5 terminology |
| Low | `random.sample` in intel feed | Inject gas_lock twice; confirm different items each run |

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

- **Gemma 4 = intended deployment target, Gemma 2 = current reality.** The label was updated at user direction to match the intended model, but the actual pull is pending. Always document this gap explicitly — never leave it silent.
- **Grafana URL drift**: When a LoadBalancer pod is recreated, its external IP may change. The hardcoded fallback in `loadGrafana()` drifted from the live IP. Future: consider fetching the URL from the backend API (`/api/mlops/status`) rather than hardcoding.
- **"Field Link" > "WAN"** for operator-facing terminology — it describes the physical communications link back to central HQ rather than a technical acronym.
- **Parallel consumer patterns** (GDC AI path + SCADA path from same RabbitMQ broker) is the architecturally correct and realistic O&G deployment model — both consumers receive the same high-frequency stream, with SCADA doing downsampled threshold polling and GDC doing full ML inference.
