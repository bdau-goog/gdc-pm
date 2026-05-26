# Next Session Prompt — ESP v2 Redesign (Stage 2 COMPLETE)

## Header
**Date:** May 26, 2026
**Live URL:** http://34.138.32.109 (us-east1 cluster)
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `41253bd` — clean working tree ✅
**Note:** Branch is 9 commits ahead of `origin/esp-v2-redesign` — push to origin at session start.
**Image:** `sha256:9f7e623c6e3ee1...` (deployed 12:49 UTC May 26 — includes Architecture tab)

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
- rag_documents: **11 rows** ⚠️ was 0 at last check — investigate before any demo
- fault_sessions: ≥ 3 rows ✅

---

## ⚠️ Known Integrity State (VERIFIED May 26, 2026 ~12:55 UTC)

| Item | Actual State | Action Required |
|------|-------------|-----------------|
| **rag_documents** | **0 rows** (expected 11) | HIGH — investigate before demo. Check if init-schema job ran correctly. Re-seed if needed. |
| Architecture tab | **Visually confirmed ✅** (screenshot May 26) | Needs polish — see Priority 1 |
| fault_sessions | 3 rows ✅ | Working |
| field_intel | 100 rows ✅ | Active |
| Ollama / gemma:27b | `ollama_online: True` ✅ | Running on GPU |
| GPU CronJobs | SUSPENDED ✅ | Use manual scripts only |
| git origin | 9 commits behind | Push at session start: `git push` |

---

## GPU Management (Manual — No CronJobs)

```bash
cd /home/brian/gdc-pm && ./scripts/gpu-start.sh   # start of day
cd /home/brian/gdc-pm && ./scripts/gpu-stop.sh    # end of day
```

---

## NEXT SESSION OBJECTIVES

### Priority 1 — Architecture Tab Polish (confirmed rendering, specific issues)

**CONFIRMED RENDERING (screenshot May 26):** The 4-tier layout, dark theme cards, GDC EDGE CLUSTER dashed box, and NVIDIA GPU box all render correctly. The tab looks like a native part of the UI.

**Specific issues to fix (small CSS/HTML changes only):**

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| **SCADA node has arrow-right pointing toward AI Engine** | `class="arch-node arrow-right"` on SCADA is incorrect — SCADA is a separate legacy path, not an input to GDC AI | Remove `arrow-right` from SCADA node |
| **Fault Injector arrow is visually unmoored** | Fault Injector is at the bottom of Tier 1 far from RabbitMQ in Tier 2 | Remove `arrow-right` from Fault Injector; add note label instead |
| **No HMI/threshold output shown from SCADA** | SCADA → HMI path exists in the narrative but only SCADA is visible | Add "Operator HMIs" and "Threshold-Based RUL" as small subdescription lines inside the SCADA card (not separate nodes) to avoid layout complexity |
| **Vertical alignment between tiers** | SCADA sits at top of Tier 2, GDC box fills the rest — no visual connector | Add a thin connector line or note text between SCADA and the GDC box to show they receive the same telemetry stream |

**File surgery approach:**
- All CSS is in `<head>` → search for `/* ══ Architecture Tab ══ */`
- All HTML is in `<div id="tab-architecture">`
- For multi-block HTML edits, use Python regex (NOT `replace_in_file`)

---

### Priority 2 — Investigate rag_documents = 0 (High, ~15 min)

```bash
# Check what tables exist and their row counts
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability \
  -c "\dt" \
  -c "SELECT COUNT(*) FROM rag_documents;"

# Check if the init-schema job completed successfully
kubectl get job alloydb-init-schema -n gdc-pm

# Check init job logs for seeding errors
kubectl logs -n gdc-pm job/alloydb-init-schema 2>&1 | tail -30

# If empty, re-seed manually:
# python3 scripts/ingest_manuals.py
```

The `rag_documents` table is critical — it stores the industry corpus (ESP/gas_lift/mud_pump/top_drive manuals) used by Gemma for RAG. Expected: 11 rows (esp:3, gas_lift:3, mud_pump:3, top_drive:2).

---

## What IS Working (deployed and verified)

| Feature | Status |
|---------|--------|
| All 4 XGBoost health models | ✅ |
| Fix 9: Dynamic docs all 11 fault types | ✅ |
| Fix 10: Dynamic Gemma finding | ✅ |
| Fix 11b: fault_sessions write path | ✅ |
| HITL approve → savings → financials | ✅ |
| gpu-start.sh / gpu-stop.sh | ✅ |
| Honest Gemma status (⛔ offline) | ✅ |
| Architecture tab (HTML/CSS, native) | ✅ Deployed — visual confirmation pending |

---

## Architecture Tab — Technical Notes for Next Session

**CSS location:** Global `<head>` `<style>` block, search for `/* ══ Architecture Tab ══ */`

**Root cause of the styling failure this session:** `<style>` tags placed inside the Vue `#app` root div are silently ignored by browsers. All CSS must live in the `<head>` `<style>` block.

**File surgery approach:** For large multi-block edits to `index.html`, use Python (`python3 -c "..."` or heredoc) instead of `replace_in_file`. The file is 2400 lines and `replace_in_file` fails on large exact-match blocks.

**`--purple` CSS variable:** Not defined in `:root`. The arch CSS uses `#b388ff` directly instead.

---

## Constraints (never violate)
- `terraform/gke.tf` must NOT be applied without review
- Preserve XGBoost models (`*.ubj` files)
- `/api/*` endpoints must remain backward-compatible
- Do NOT commit to `main`
- **No browser on SSH remote** — `browser_action` must NOT be used
- **Commit after every verified deployment**
- **CSS goes in `<head>` — never in a `<style>` tag inside `#app`**

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

## Current Cluster State (VERIFIED May 26, 2026 ~12:55 UTC)

```
fault-trigger-ui-6b689c5f47-8rlwd   1/1  Running  5m   (Architecture tab deployed)
alloydb-omni-5fcfc68fdb-x9xc8       1/1  Running  4d
event-processor-7d9b594b6b-wjlkc    1/1  Running  3d23h
gdc-pm-rabbitmq-server-0            1/1  Running  3d23h
grafana-655b6f5c7c-mtmtw            1/1  Running  4d
inference-api-5697b79566-4q8tm      1/1  Running  3d22h
ollama-5bc5db749b-jf997             1/1  Running  24h   ← GPU
telemetry-simulator-6b9668648b-ddc66 1/1 Running  4d

Ollama replicas: 1
API: ollama_online: True  model: gemma:27b ✅
AlloyDB: field_intel=100, rag_documents=0 ⚠️, fault_sessions=3
git: 9 commits ahead of origin, working tree clean
```

---

## Outstanding Backlog (post-Architecture tab)

| Priority | Item | Note |
|----------|------|------|
| High | Restore rag_documents (0→11 rows) | Re-seed with `scripts/ingest_manuals.py` if needed |
| High | Push 9 commits to origin | `git push` at session start |
| Medium | Architecture tab visual confirmation | User to review at live URL |
| Medium | Architecture tab polish | Once visual confirmed, decide if further tuning needed |
| Low | Demo narrative improvements | `docs/DEMO_NARRATIVE_UPDATE.md` has context |

---

## Key Lessons Learned (May 26 session)

- **`<style>` tags inside `#app` are silently ignored** — always put CSS in the global `<head>` `<style>` block. This was the root cause of 3 failed deploys.
- **Use Python for large file surgery** — `replace_in_file` fails on 2400-line files with multi-block patterns. Python regex/string replacement is safer and gives explicit success/failure output.
- **Don't mix tooling experiments with integration** — the Mermaid.js exploration (Code tab vs Config tab confusion, syntax errors) consumed significant tokens. When a tool has a known working alternative (HTML/CSS), use it.
- **Architecture tab CSS:** `--purple` is not in the app's `:root`. Use `#b388ff` directly.
