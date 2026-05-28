# Next Session Prompt — ESP v2 Redesign (Guided Tour Polish)

## Header
**Date:** May 28, 2026
**Live URL:** http://34.138.32.109 (us-east1 cluster)
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `6fe5880` — clean working tree (untracked: `update_arch.py` — scratch file, safe to ignore or delete)
**Image:** `sha256:b95558ae8b82a2c7977a621587fb1ae09a2283f683ccb61cf62d4f214a972d4e` (deployed May 28 — 6-pane Guided Tour)

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
- field_intel: **100 rows** ✅
- fault_sessions: ≥ 3 rows ✅

---

## ⚠️ Known Integrity State (VERIFIED May 28, 2026)

| Item | Actual State | Action Required |
|------|-------------|-----------------|
| Architecture tab | ✅ 6-pane Guided Tour live at 34.138.32.109 | Polish pass required — see next session plan |
| "SCADA RTU" chip | Incorrect label in Pane 1 (System Overview) | Replace with individual sensor chips (PSI, Temp, Vib, Amps) |
| Guided Tour values | Static/illustrative (e.g. Health: 0.34) | Acceptable for now; live-data wiring is optional |
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

## NEXT SESSION PLAN

| Fix | Change (one sentence) | Verification | Est. complexity |
|-----|----------------------|--------------|-----------------|
| Pane 1 sensor chips | Replace "SCADA RTU" chip with 4 sensor chips: Intake PSI, Winding Temp, Vibration mm/s, Motor Amps | View System Overview pane — chips visible | Small |
| Full pane review | Walk through all 6 panes and capture any other content/label issues | User review at live URL | Small |
| Content iteration | Apply any agreed content changes from review | User confirms panes look correct | Small–Medium |

**File surgery approach:** Use Python regex to replace arch tab block (as in `update_arch.py` pattern). Do NOT use `replace_in_file` on the 2600-line `index.html`.

---

## What Was Done This Session

| Feature | Status |
|---------|--------|
| Architecture tab Vue context bug | ✅ Fixed — orphaned HTML was pushing modals outside `#app`, breaking Vue compilation |
| Architecture tab: broken 4-tier flat layout | ✅ Replaced with 6-pane Guided Tour |
| Guided Tour: 6 focused sub-tabs | ✅ Deployed and verified live |
| `archPane` Vue state variable | ✅ Injected into data() |
| New CSS component library | ✅ `.arch-stage`, `.arch-chip`, `.arch-connector`, `.arch-narrative-card`, `.arch-compare-row` |
| `rag_documents` (was 0 rows) | ✅ Re-seeded to 18 rows via `scripts/ingest_manuals.py` |

---

## Constraints (never violate)
- `terraform/gke.tf` must NOT be applied without review
- Preserve XGBoost models (`*.ubj` files)
- `/api/*` endpoints must remain backward-compatible
- Do NOT commit to `main`
- **No browser on SSH remote** — `browser_action` must NOT be used
- **Commit after every verified deployment**
- **CSS goes in `<head>` — never in a `<style>` tag inside `#app`**
- **Use Python regex for large HTML block replacements** — `replace_in_file` fails on 2600+ line files

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

## Current Cluster State (VERIFIED May 28, 2026 ~21:53 UTC)

```
alloydb-omni-5fcfc68fdb-9vm2z          1/1  Running
event-processor-7d9b594b6b-j5jp8       1/1  Running
fault-trigger-ui-86b7d49c95-2jqgr      1/1  Running  ← Guided Tour deployed
gdc-pm-rabbitmq-server-0               1/1  Running
grafana-655b6f5c7c-w2h84               1/1  Running
inference-api-5697b79566-zqdpl         1/1  Running
ollama-5bc5db749b-jf997                1/1  Running   ← GPU (3d9h uptime)
telemetry-simulator-6b9668648b-x6622   1/1  Running

Ollama replicas: 1
API: ollama_online: True  model: gemma:27b ✅
AlloyDB: field_intel=100 ✅, rag_documents=18 ✅, fault_sessions=3 ✅
git: 6fe5880 clean, pushed to origin/esp-v2-redesign
```

---

## Outstanding Development Items (Backlog)

| Priority | Item | Note |
|----------|------|------|
| High | Guided Tour content polish | Pane 1: "SCADA RTU" → sensor chips; review all 6 panes for label accuracy |
| Medium | Live data wiring for Tour | Fetch active health score / RUL from `/api/degrade-status` to populate Pane 3 cards |
| Low | Demo narrative doc update | `docs/DEMO_NARRATIVE_UPDATE.md` has context; may want to align with new Tour structure |

---

## Key Lessons Learned (May 28 session)

- **Orphaned HTML outside `#app` silently breaks Vue compilation.** Vue3 production builds don't throw console errors — they just stop processing templates. Modals rendering `{{ raw template }}` text is the symptom. Always verify that `</div><!-- app-body -->` is the last element before the modals.
- **Python regex is the only reliable approach for large HTML file surgery.** `replace_in_file` consistently fails to match multi-line blocks in 2600+ line files.
- **Verify content is live with `curl | grep -c`.** `kubectl get pods` shows the pod is running; `curl -s http://host/ | grep -c "archPane"` confirms the right code is actually served.
- **"SCADA RTU" is too technical for a demo audience.** Show what the sensors measure, not the protocol device that reads them.
