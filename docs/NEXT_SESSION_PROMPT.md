# Next Session Prompt — ESP v2 Redesign (Architecture Tab v3)

## Header
**Date:** May 28, 2026
**Live URL:** http://34.138.32.109 (us-east1 cluster)
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `7873322` — clean working tree (untracked: `rewrite_arch.py`, `update_arch.py`, `fix_arch_v3.py` — scratch files, safe to delete)
**Image:** `sha256:2ac9c3f00f12c5dbc205cf4cebe46270ff84259d93c4af52bcb900e0f02e4f9b` (deployed May 28 — Architecture Tab v3)

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
| Architecture tab | ✅ v3 live at 34.138.32.109 | Visual review with user to confirm layout satisfactory |
| Pane 2 ⓘ info sensor list | Still says "Intake PSI" in the bullet text (inside ⓘ panel) | Minor: rename to "Pump Intake Pressure (PIP)" in Pane 2 info panel |
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
| Visual review | Walk through all 6 panes with user at live URL, confirm layout is acceptable | User confirms | Small |
| Pane 2 ⓘ sensor bullet | Rename "Intake PSI" → "Pump Intake Pressure (PIP)" and add note that PIP is positive (reservoir) pressure, not vacuum | Check ⓘ panel on Pane 2 | Small |
| Live data wiring | Fetch active health score / RUL from `/api/degrade-status` to populate Pane 3 cards dynamically | Health score chip shows live value | Medium |

**File surgery approach:** Use Python regex for replacements. Do NOT use `replace_in_file` on the 3000+ line `index.html`.

---

## What Was Done This Session

### Architecture Tab v2 (deployed May 28)
| Feature | Status |
|---------|--------|
| All 6 panes: full-width diagram layout, narrative → ⓘ info popups | ✅ |
| Pane 1: 4 sensor chips, ML Anomaly Detection label, E-House narrative in ⓘ | ✅ |
| Pane 2: 38 wells across 6 pads (field-of-pads) | ✅ |
| Pane 4: 3-column parallel-stream AlloyDB input layout | ✅ |
| Vue `archInfoOpen` state + CSS info panel components | ✅ |

### Architecture Tab v3 (deployed May 28 — same session, second pass)
| Feature | Status |
|---------|--------|
| Pane 1 sensors: removed ESP Wells + Fault Injector; Intake PSI → Pump Intake Pressure | ✅ |
| Pane 1 Edge Bus: simplified to RabbitMQ Broker only | ✅ |
| Pane 1 ML stage: simplified to XGBoost Health Score only | ✅ |
| Pane 1 Context Store: Field Intel → Operations Reports; ML Assessments → Model-Based RUL | ✅ |
| Pane 1 AI Fusion: separated Gemma engine from outputs with explicit "Outputs →" divider | ✅ |
| Pane 4 Stream 1: relabeled Real-Time ML → Model-Based RUL; added ↓ arrows on each box | ✅ |
| Pane 4 Stream 3: Field Intelligence → Operations Reports | ✅ |
| Pane 5: two side-by-side output cards (AI-Informed RUL + Action Recommendation) | ✅ |
| Pane 5: removed bottom "Why the RUL Changed" explanatory callout | ✅ |
| Layout: `align-items:flex-start` fixes inner-box overflow bug | ✅ |
| Architecture domain validation | ✅ Multi-Well Pad E-House confirmed as correct GDC Software Only deployment pattern |

---

## Current Cluster State (VERIFIED May 28, 2026 ~23:57 UTC)

```
alloydb-omni-5fcfc68fdb-9vm2z          1/1  Running
event-processor-7d9b594b6b-j5jp8       1/1  Running
fault-trigger-ui-<new pod>             1/1  Running  ← Arch Tab v3 deployed
gdc-pm-rabbitmq-server-0               1/1  Running
grafana-655b6f5c7c-w2h84               1/1  Running
inference-api-5697b79566-zqdpl         1/1  Running
ollama-5bc5db749b-jf997                1/1  Running   ← GPU (3d10h+ uptime)
telemetry-simulator-6b9668648b-x6622   1/1  Running

Ollama replicas: 1
API: ollama_online: True  model: gemma:27b ✅
AlloyDB: field_intel=100 ✅, rag_documents=18 ✅, fault_sessions=3 ✅
git: 7873322 clean, pushed to origin/esp-v2-redesign
```

---

## Outstanding Development Items (Backlog)

| Priority | Item | Note |
|----------|------|------|
| High | Pane 2 ⓘ bullet: "Intake PSI" → "Pump Intake Pressure (PIP)" | Add note clarifying PIP is positive reservoir pressure (not vacuum) — ~5-line Python replace |
| High | Live data wiring for Tour panes | Pane 3 health score / RUL cards could fetch from `/api/degrade-status` |
| Medium | Demo narrative doc update | `docs/DEMO_NARRATIVE_UPDATE.md` may need alignment with v3 arch tab terminology |
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

- **Domain realism > demo polish.** A 10-minute architecture discussion about where the compute physically lives produced a far stronger demo story than any visual tweaking.
- **"Intake for a pump is suction so it should be a vacuum, right?"** — For surface pumps, yes. For a downhole ESP 3km underground, the pump intake (PIP) is under positive reservoir pressure (220–280 PSI). The fluid enters the pump under hydrostatic head from the reservoir, not suction. Always use the domain-accurate term "Pump Intake Pressure (PIP)."
- **XGBoost vs LLM responsibility distinction:** XGBoost performs purely numerical anomaly detection (Model-Based RUL). The LLM synthesises documents + ML output into AI-Informed RUL and Action Recommendations. Keep these clearly separated in the UI and labelled accordingly.
- **"Operations Reports" is clearer than "Field Intel"** for a general demo audience — it maps directly to what operators understand (shift notes, lab reports, work orders).
- **Python regex scripts are the only safe approach** for surgery on 3000+ line HTML files. Keep all fix scripts in the repo root with descriptive names for traceability.
- **Two-pass sessions are normal.** First pass deploys the big change; second pass applies the user's visual review corrections. Plan for it.
