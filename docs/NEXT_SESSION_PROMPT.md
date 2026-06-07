# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** Session E end — June 7, 2026  
**git head:** `a493549` (Phase 2 H1 integrity fixes)  
**fault-trigger-ui image:** `sha256:ec5b0306` (1/1 Running — deployed Session E)  
**inference-api image:** `sha256:d1194989` (1/1 Running — unchanged)  
**Branch:** `feature-trio-scenarios` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

Also check RabbitMQ every session start:
```bash
kubectl exec -n gdc-pm gdc-pm-rabbitmq-server-0 -- rabbitmqctl list_queues --vhost gdc-pm name messages consumers
```

**Expected healthy (Session F start):**
- All 8 pods: 1/1 Running
- ollama_online: True · model: gemma4:latest
- field_intel: 0–5 rows (only grows during active fault — correct)
- rag_documents: 18 rows
- RabbitMQ: **< 500 messages** ← P0 fix deployed Session D; if > 5,000, check event-processor logs

**If RabbitMQ > 5,000:** Check that `AI_NARRATIVE_ENABLED=false` is live:
```bash
kubectl exec -n gdc-pm deployment/event-processor -- env | grep AI_NARRATIVE
```
If it shows `rag`, the k8s deployment diverged from the yaml — re-apply: `kubectl apply -f gke/event-processor/k8s/event-processor.yaml --validate=false`

---

## STEP 2: Read These Two Documents

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
cat ~/gdc-pm/docs/BACKEND_CONFORMANCE_REPORT.md
```

---

## STEP 3: Session E Primary Work — The 6-Phase Program

**Where we are:** Phases 0 and 1 are complete. Phases 2–5 are the roadmap.

### ✅ PHASE 0 — Governance (DONE, Session D)
- Prime Directive (O&G scrutiny rule) + confidence tags prepended to `.clinerules`
- Claim Ledger mechanism established

### ✅ PHASE 1 — Truth (DONE, Session D)
- `docs/CLAIM_LEDGER.md` drafted — 14 claims in 4 sections, each tagged 🟢/🟡/🔴
- Integrity discrepancies reconciled: **$0 → $2,500** (cheapest option), **25-min PNR ≠ 45-min failure window**

### ✅ PHASE 2 — Backend Truth (DONE, Session E)
All 4 targeted H1 integrity fixes deployed and verified at `sha256:ec5b0306`:
1. **$0→$2,500 fixed** (3 locations in index.html: physics panel, RESOLVED banner, Window of Options card)
2. **Vibration sensor bar added** (4th sensor, `h1RawVib`/`h1SensorVib` wired through app.js)
3. **Thermal countdown clamped** (gates on `slopes.dtemp_dt > 0.2`; shows "— monitoring temp rise" at onset)
4. **Sensor source unified** (`_renderH1PhasePlane` now sets all 4 sensor display values from same DB trace source)

**⚠️ Action still required from USER before Phase 3:** Red-line `docs/CLAIM_LEDGER.md` as domain owner. Mark 🔴 rows VERIFY/SOFTEN/CUT (esp. C2 = SCADA reactive path costs). Send to O&G SME. Only SURVIVES rows drive the Phase 3 UI redesign.

### 🔜 PHASE 3 — H1 UI Redesign (after Claim Ledger signed off by user)
Build the Decision Clock + honest cost-ladder visual around ONLY the SURVIVES claims.
- Hero: "GDC fires at minute 2 while all 4 SCADA bars stay green — production continuity vs reactive shut-in"
- Clock: GDC acts ($2,500) → SCADA would shut-in (~$8-15k, 🔴 needs SME) → PNR → failure window
- 4 sensor bars now showing correctly in current deployment — foundation is set
- Do NOT redesign until Claim Ledger C2 is resolved (SME or softened to a range)

### 🔜 PHASE 4 — Verify H1
Live inject on cluster, confirm every on-screen number == its Claim Ledger row. SCADA comparison is honest. H1 is demo-ready.

### 🔜 PHASE 5 — Replicate to H2, then H3
Same gated pipeline. H2/H3 Claim Ledger sections not yet drafted — do after H1 is stable.

---

## Known Integrity State — Session E end

| Item | File | Status |
|---|---|---|
| "$0 direct cost" → "$2,500" | index.html | ✅ Fixed Session E (a493549) |
| Missing Vibration sensor bar | index.html | ✅ Fixed Session E (a493549) |
| Thermal countdown "993 min" at onset | index.html | ✅ Fixed Session E (a493549) |
| Sensor source unified (DB trace) | app.js | ✅ Fixed Session E (a493549) |
| FAULT_PHYSICS 45min vs PNR 25min | app.py (comment only) | ⚠ Not contradicting; comment update deferred |
| H3 Vizier hardcoded polynomial | app.py:~5293 | ❌ Phase 3+ — not blocking H1/H2 |
| esp_classifier trained on invented ranges | inference-api/models | ⚠ Phase 5 retrain |
| CLAIM_LEDGER C2 (SCADA reactive $8-15k) | docs/CLAIM_LEDGER.md | 🔴 NEEDS-EXPERT — do NOT show as hard fact |

**Integrity notes from CLAIM_LEDGER.md:**
- C2 ($8k–15k SCADA reactive cost) is 🔴 — must be verified/softened BEFORE Phase 3 UI redesign
- C3 ($150k workover) SURVIVES with qualification — "representative, varies by well"
- Sections 1 (physics) and 2 (SCADA limits) are 🟢 TEXTBOOK — safe to show

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- `feature-trio-scenarios` stays separate from `main`
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- inference-api registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/inference-api:latest`
- Do NOT use "Copilot" anywhere in H1/H2/H3
- Failing model `.ubj` files are NEVER committed
- All claims on screen must have a SURVIVES row in CLAIM_LEDGER.md before code is written
