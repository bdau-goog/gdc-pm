# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** Session G end — June 8, 2026  
**git head:** `a2eee90` (fix(ui): Phase 3 — cost-ladder ticks, wopt card B cost, sensor bar widths pre-injection)  
**fault-trigger-ui image:** `sha256:df7f9433` (1/1 Running — Session G)  
**inference-api image:** `sha256:d1194989` (1/1 Running — unchanged)  
**Branch:** `feature-trio-scenarios` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
source .env && kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
source .env && kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

Also check RabbitMQ every session start:
```bash
source .env && kubectl exec -n gdc-pm gdc-pm-rabbitmq-server-0 -- rabbitmqctl list_queues --vhost gdc-pm name messages consumers
```

**⚠️ NOTE: All kubectl/gcloud commands MUST be prefixed with `source .env &&`**

**Expected healthy (Session H start):**
- All 8 pods: 1/1 Running (completed cronjobs are normal)
- ollama_online: True · model: gemma4:latest
- field_intel: 0–5 rows (only grows during active fault)
- rag_documents: 18 rows
- RabbitMQ: **< 500 messages** (P0 fix from Session D holding)

---

## STEP 2: Read These Two Documents

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
cat ~/gdc-pm/docs/CLAIM_LEDGER.md
```

---

## STEP 3: Session G State Summary

### What was done Session G:
1. **Phase 3 cost-ladder + integrity fixes** (`a2eee90`):
   - Decision timeline tick at 72%: `$0→$2k` → `SCADA reactive · ~$3k–$8k` (CLAIM_LEDGER C2)
   - Decision timeline tick at 92%: `PNR` → `PNR · ~$150k only`
   - Wopt card B: `~$2,000 workover cost` → `~$3,000–$8,000 (shut-in + restart)` + C2 footnote
   - app.js: `h1RawPsi/Temp/Amps` now set from live-telemetry poll pre-injection — sensor bar fills now show correct live widths (not hardcoded 88%/83%/24% fallbacks) before fault injection
   - Motor CRITICAL state audited: `h1ElapsedMin > 15` is NOT in the codebase — already fixed in Session V; banner uses `parseInt(h1SensorTemp||'0') >= 260`. Integrity table corrected.

### REMAINING PHASE 3 TASKS (for Session H):

**Next task — two options, pick one per session:**

**Option A: H1 "cost-ladder row" visual below the decision timeline**
Add a horizontal row showing the 3 cost nodes explicitly labeled with cost + action:
```
$2,500 GDC ACT NOW ——▶—————— $3k–$8k SCADA trip ——— $150k PNR ONLY → FAIL
```
This is a new HTML element (cost-ladder row under `.h1-tl-bar`). Pure index.html addition, no app.py needed.

**Option B: RAG seed collapse protection (app.py)**
With `AI_NARRATIVE_ENABLED=false`, the `_intel_generator` is NOT running so no prune fires. The seed doc persists. This bug is **NOT active** in current deployment. Defer unless demo shows empty intel feed.

**Note:** The DEMO_MASTER.md §12 wireframe (lines 488–528) showed the cost ladder labels as the primary remaining Phase 3 element. Option A is the natural next step.

**Do NOT start new code until reviewing DEMO_MASTER.md §12 wireframe (lines 488–528)**

---

## Known Integrity State — Session G end

| Item | File | Status |
|---|---|---|
| "$0 direct cost" → "$2,500" | index.html | ✅ Fixed Session E (a493549) |
| Missing Vibration sensor bar | index.html | ✅ Fixed Session E (a493549) |
| Thermal countdown "993 min" at onset | index.html | ✅ Fixed Session E (a493549) |
| Sensor source unified (DB trace) | app.js | ✅ Fixed Session E (a493549) |
| Motor CRITICAL state from elapsed time | index.html | ✅ Audited Session G — already fixed in Session V; banner uses h1SensorTemp |
| Pre-injection sensor bar fill widths hardcoded | app.js | ✅ Fixed Session G (a2eee90) — h1RawPsi/Temp/Amps set from live-telemetry |
| Timeline tick "$0→$2k" wrong | index.html | ✅ Fixed Session G (a2eee90) → "SCADA reactive · ~$3k–$8k" |
| Wopt card B cost "$2,000" wrong | index.html | ✅ Fixed Session G (a2eee90) → "$3,000–$8,000" + C2 footnote |
| RAG seed doc collapses after ~5 min | app.py | ⚠ Non-issue with AI_NARRATIVE_ENABLED=false (no prune fires) |
| FAULT_PHYSICS 45min vs PNR 25min comment | app.py | ⚠ Comment update deferred |
| H3 Vizier hardcoded polynomial | app.py:~5293 | ❌ Phase 5+ — not blocking H1/H2 |
| esp_classifier trained on invented ranges | inference-api/models | ⚠ Phase 5 retrain |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- `feature-trio-scenarios` stays separate from `main`
- Batch all edits to same file in ONE `replace_in_file` call
- **ALL kubectl/gcloud commands now require `source .env &&` prefix** (workspace isolation active)
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- inference-api registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/inference-api:latest`
- Do NOT use "Copilot" anywhere in H1/H2/H3
- Failing model `.ubj` files are NEVER committed
- All claims on screen must have a SURVIVES row in CLAIM_LEDGER.md before code is written
