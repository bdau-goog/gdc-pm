# Next Session Prompt — ESP v2 Redesign (Architecture Tab v4)

## Header
**Date:** May 29, 2026
**Live URL:** http://34.138.32.109 (us-east1 cluster)
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `293b861` — clean working tree (untracked: `rewrite_arch.py`, `update_arch.py`, `fix_arch_v3.py`, `fix_arch_v4.py` — scratch files, safe to delete)
**Image:** `sha256:f054c1b22f42a8ed81747df5e84a740ddc5a95729ae314bdc1f458a02507e85e` (deployed May 29 — Architecture Tab v4)

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

## ⚠️ Known Integrity State (VERIFIED May 29, 2026)

| Item | Actual State | Action Required |
|------|-------------|-----------------|
| Architecture tab | ✅ v4 live at 34.138.32.109 | Visual review to confirm all changes acceptable |
| Pane 2 ⓘ sensor bullet | Still says "Intake PSI" in Pane 2 ⓘ info panel text | Minor: update to "Pump Intake Pressure (PIP)" and clarify positive pressure |
| Guided Tour values | Static/illustrative (Health: 0.34, RUL: 22.1 min) | Acceptable for demo; live-data wiring is backlog |
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
| Visual review | Final walk-through with user at live URL | User confirms layout acceptable | Small |
| Pane 2 ⓘ bullet | "Intake PSI" → "Pump Intake Pressure (PIP)" + note that PIP is positive reservoir pressure, not vacuum | Check ⓘ on Pane 2 | Small |
| Live data wiring | Fetch health score / RUL from `/api/degrade-status` to populate Pane 3 cards dynamically | Pane 3 chip shows live value | Medium |

**File surgery approach:** Use Python regex for all replacements. Do NOT use `replace_in_file` on the 3000+ line `index.html`.

---

## What Was Done This Session (all deployed, all live)

| Version | Change | Status |
|---------|--------|--------|
| v2 | Full arch tab overhaul: ⓘ popups, full-width diagrams, 38-well field-of-pads, parallel AlloyDB streams | ✅ |
| v3 | Flow polish: sensor chips cleaned up, Edge Bus simplified, Context Store relabelled, Pane 5 output cards, overflow bug fixed | ✅ |
| v4 | Final terminology polish: Vibration (no units), Message Bus, AlloyDB chip, Industry Corpus, AI-Based RUL, Actions, Operations | ✅ |

---

## Current Cluster State (VERIFIED May 29, 2026 ~00:12 UTC)

```
alloydb-omni-5fcfc68fdb-9vm2z          1/1  Running
event-processor-7d9b594b6b-j5jp8       1/1  Running
fault-trigger-ui-9dbd94597-xgh4f       1/1  Running  ← Arch Tab v4 deployed
gdc-pm-rabbitmq-server-0               1/1  Running
grafana-655b6f5c7c-w2h84               1/1  Running
inference-api-5697b79566-zqdpl         1/1  Running
ollama-5bc5db749b-jf997                1/1  Running   ← GPU
telemetry-simulator-6b9668648b-x6622   1/1  Running

Ollama replicas: 1
API: ollama_online: True  model: gemma:27b ✅
AlloyDB: field_intel=100 ✅, rag_documents=18 ✅, fault_sessions=3 ✅
git: 293b861 clean, pushed to origin/esp-v2-redesign
```

---

## Outstanding Development Items (Backlog)

| Priority | Item | Note |
|----------|------|------|
| High | Pane 2 ⓘ: "Intake PSI" → "Pump Intake Pressure (PIP)" + clarify positive pressure | ~5-line Python replace in Pane 2 info panel |
| High | Live data wiring | Pane 3 health score / Base RUL from `/api/degrade-status` |
| Medium | Demo narrative doc update | `docs/DEMO_NARRATIVE_UPDATE.md` — align with v4 terminology |
| Low | `random.sample` in intel feed | Inject gas_lock twice; confirm different items each run |
| Low | `get_gemma_finding()` dynamic | Confirm gemma_finding varies between runs |

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

## Key Lessons Learned (May 28–29 session)

- **Pump Intake Pressure (PIP) is NOT suction/vacuum.** For downhole ESPs, the pump intake is submerged in wellbore fluid under positive reservoir pressure (220–280 PSI). Only surface pumps drawing from below may see sub-atmospheric suction. Always use "Pump Intake Pressure (PIP)" — the industry-standard term.
- **"Operations" > "Operator"** for the output stage — it describes the function, not a person.
- **"Industry Corpus" > "OEM Manuals (RAG)"** for a general demo audience — it's more accessible and still accurate.
- **"Actions" > "Action Recommendation"** when space is constrained — truncated labels that overflow their boxes undermine visual credibility.
- **Domain realism validates the architecture.** The multi-well pad E-House deployment pattern is real, common in the Permian/Bakken, and completely defensible to O&G engineers.
- **Three-pass sessions are normal for UI work.** First pass = big structural change, second pass = content corrections from first review, third pass = terminology polish from second review. Each pass should be its own commit.
- **Python replace scripts accumulate.** Clean up `rewrite_arch.py`, `update_arch.py`, `fix_arch_v3.py`, `fix_arch_v4.py` from repo root at the start of next session.
