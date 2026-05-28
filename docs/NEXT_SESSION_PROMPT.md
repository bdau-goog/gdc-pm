# Next Session Prompt — ESP v2 Redesign (Architecture Tab v2)

## Header
**Date:** May 28, 2026
**Live URL:** http://34.138.32.109 (us-east1 cluster)
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `526990b` — clean working tree (untracked: `rewrite_arch.py`, `update_arch.py` — scratch files, safe to delete)
**Image:** `sha256:a632953176694cd12d605c35e12a5e643fbdc33e302ea7116cd519c0f089af16` (deployed May 28 — Architecture Tab v2)

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
| Architecture tab | ✅ v2 live at 34.138.32.109 — full-width diagrams, ⓘ popups | Visual review with user to confirm layout satisfactory |
| Guided Tour values | Static/illustrative (Health: 0.34, RUL: 22.1 min) | Acceptable for now; live-data wiring is optional |
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
| Visual review | Walk through all 6 panes with user at live URL, capture any content/layout issues | User confirms panes look correct | Small |
| ⓘ panel review | Confirm ⓘ info popups display correctly, content is accurate per pane | Click ⓘ on each of 6 panes | Small |
| Live data wiring | Fetch active health score / RUL from `/api/degrade-status` to populate Pane 3 cards dynamically | Health score chip shows live value | Medium |
| Pane 2 connector label | "MQTT" is slightly misleading (it's AMQP via RabbitMQ); consider updating to "AMQP/RabbitMQ" | Visual check | Small |

**File surgery approach:** Use Python regex to replace specific blocks. Do NOT use `replace_in_file` on the 3000+ line `index.html`.

---

## What Was Done This Session

| Feature | Status |
|---------|--------|
| Arch tab v2: Narrative → ⓘ info popups | ✅ Deployed and verified live |
| All 6 panes: full-width diagram layout | ✅ Deployed and verified live |
| Pane 1: SCADA RTU → 4 sensor chips | ✅ Deployed: Intake PSI, Winding Temp, Vibration mm/s, Motor Amps |
| Pane 1: step 3 label → "ML Anomaly Detection" | ✅ Deployed — distinguishes XGBoost from LLM (Pane 5) |
| Pane 1: SCADA comparison updated | ✅ "15-min downsampled WAN poll" vs "5s local stream — no WAN needed" |
| Pane 2: 6 wells → 38 wells across 6 pads | ✅ Deployed: Pad Alpha (6W) through Pad Foxtrot (6W) |
| Pane 4: parallel-stream AlloyDB layout | ✅ Deployed: ML / RAG / Field Intel shown as 3 independent input streams |
| ⓘ info panels: E-House/GDC Software Only context | ✅ Deployed across all 6 panes |
| ⓘ info panels: Local vs WAN network explanation | ✅ In Pane 1 and Pane 2 info panels |
| Vue `archInfoOpen` state + CSS component | ✅ arch-info-btn, arch-info-panel, arch-info-section |
| Architecture domain validation | ✅ Confirmed: Multi-Well Pad E-House is the correct O&G deployment pattern for GDC Software Only |

---

## Current Cluster State (VERIFIED May 28, 2026 ~22:57 UTC)

```
alloydb-omni-5fcfc68fdb-9vm2z          1/1  Running  ← PostgreSQL + pgvector
event-processor-7d9b594b6b-j5jp8       1/1  Running  ← RabbitMQ consumer
fault-trigger-ui-59c9bb56c7-b2g7r      1/1  Running  ← Arch Tab v2 deployed (69s)
gdc-pm-rabbitmq-server-0               1/1  Running
grafana-655b6f5c7c-w2h84               1/1  Running
inference-api-5697b79566-zqdpl         1/1  Running
ollama-5bc5db749b-jf997                1/1  Running   ← GPU (3d10h uptime)
telemetry-simulator-6b9668648b-x6622   1/1  Running

Ollama replicas: 1
API: ollama_online: True  model: gemma:27b ✅
AlloyDB: field_intel=100 ✅, rag_documents=18 ✅, fault_sessions=3 ✅
git: 526990b clean, pushed to origin/esp-v2-redesign
```

---

## Outstanding Development Items (Backlog)

| Priority | Item | Note |
|----------|------|------|
| High | Live data wiring for Tour panes | Pane 3 health score / RUL cards could fetch from `/api/degrade-status` |
| Medium | Pane 2 connector label: "via MQTT" → "via AMQP" | Minor correctness fix — RabbitMQ uses AMQP, not raw MQTT |
| Medium | Demo narrative doc update | `docs/DEMO_NARRATIVE_UPDATE.md` may need alignment with new 6-pane Guided Tour |
| Low | `random.sample` in intel feed | Inject gas_lock twice; confirm different 3 items each run |
| Low | `get_gemma_finding()` dynamic | Check gemma_finding varies between runs |

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

## Key Lessons Learned (May 28 session)

- **Domain realism > demo polish.** A 10-minute architecture discussion about where the compute physically lives produced a far stronger demo story than any amount of visual tweaking. Validate O&G physical topology before finalizing any architecture diagram.
- **"SCADA is local" is a frequent misconception.** Central SCADA is often hundreds of miles away in a regional operations centre. The physical compute (GDC) lives in the well-pad E-House alongside the VFDs and motor control centres. This is the key differentiator.
- **"5s telemetry cadence" is the local edge stream** — not a bandwidth-intensive WAN uplink. The WAN only carries low-bandwidth insights. This distinction is important for the demo narrative.
- **XGBoost vs LLM responsibility is frequently confused.** XGBoost does purely numerical anomaly detection. The LLM synthesises documents + ML output. Keeping these clearly labelled (ML Anomaly Detection vs AI Context Fusion) prevents audience confusion.
- **ⓘ info popups are the right UX for demo environments.** Cluttered sidebars distract the presenter. On-demand technical detail lets the presenter control the depth of explanation.
- **Python regex replacement scripts are the only safe approach** for surgery on 3000+ line HTML files. Keep rewrite scripts in the repo root for reuse.
