# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** Session D end — June 7, 2026  
**git head:** `77be959` (pre-session D docs commit pending)  
**fault-trigger-ui image:** `sha256:afa26b3a` (1/1 Running — unchanged this session)  
**inference-api image:** `sha256:d1194989` (1/1 Running — unchanged this session)  
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

**Expected healthy (Session E start):**
- All 8 pods: 1/1 Running
- ollama_online: True · model: gemma4:latest
- field_intel: 0–5 rows (only grows during active fault — correct)
- rag_documents: 18 rows
- RabbitMQ: **< 500 messages** ← P0 fix was deployed; if > 5,000 again, check event-processor logs

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
- Integrity discrepancies reconciled: **$0 → $2,500** (cheapest option), **25-min PNR ≠ 45-min failure window** (not contradicting)
- One-sentence H1 claim written (Section 5 of ledger)
- **Action required from USER before Phase 2:** Red-line `docs/CLAIM_LEDGER.md` as domain owner. Mark 🔴 rows VERIFY/SOFTEN/CUT. Send flagged rows to O&G SME. Only SURVIVES rows become pixels.

### 🔜 PHASE 2 — Backend Truth (next session, after ledger is signed off)
Target: make the code emit EXACTLY the ledger's numbers, cleanly.
1. **Fix $0→$2,500 integrity bug:** UI says "$0 direct cost" but `RESOLUTION_OPTIONS["gas_lock"]["early"]` = $2,500. Fix in index.html Window of Options cards.
2. **Fix sensor bar data source desync (I1, the thesis-killer):** `h1RawAmps/Psi/Temp/Vib` read from stale DB trace → read from `/api/degrade-status/ESP-ALPHA-1.current_sensors` (in-memory, immediate). ONE batched replace_in_file on app.js.
3. **Add Vibration sensor bar (I2):** banner claims "4 sensors" but only shows 3. One sensor bar block in index.html.
4. **Clamp thermal countdown (I3):** gate on `dtemp_dt > 0.2` before showing "N min to 280°F."
5. **Reconcile FAULT_PHYSICS["gas_lock"]:** total_hours=0.75 (45min) is total failure window; PNR_MINUTES=25 is when cheap options close. These are NOT contradicting — the UI must show 25-min PNR and not conflate with 45-min total failure.
6. **Resume backend narrative walkthrough** (paused Session D): trace H1 inject→advisor chain against DEMO_MASTER §13, verify each step produces the ledger's claimed outputs. Mark any new gaps in BACKEND_CONFORMANCE_REPORT.md.

### 🔜 PHASE 3 — UI Truth, H1 only (after Phase 2 verified)
Build the H1 Decision Clock + honest cost-ladder visual, against ONLY the SURVIVES claims from the ledger.
- Hero: "GDC fires at minute 2 while all 4 SCADA thresholds are green — production continuity vs reactive shut-in"
- Clock: GDC acts → SCADA would trip → PNR → failure window (honest escalation, not binary)
- Cost ladder: $2,500 now / $8-15k reactive / $150k worst case (🔴 row C2 must be resolved first)
- Do NOT start this phase until Phase 2 is verified deployed.

### 🔜 PHASE 4 — Verify H1
Live inject on cluster, confirm every on-screen number == its ledger row. SCADA comparison is honest. H1 is demo-ready.

### 🔜 PHASE 5 — Replicate to H2, then H3
Same gated pipeline. H2/H3 Claim Ledger sections not yet drafted — do after H1 is stable.

---

## Known Integrity State — Session D end

| Item | File | Status |
|---|---|---|
| "$0 direct cost" in UI (should be $2,500) | index.html | ❌ Phase 2 — known, queued |
| h1RawAmps reads stale DB (SCADA alarm fires false) | app.js:1237 | ❌ Phase 2 — known, queued |
| Missing Vibration sensor bar | index.html:516 | ❌ Phase 2 — known, queued |
| Thermal countdown garbage early | index.html:410 | ❌ Phase 2 — known, queued |
| FAULT_PHYSICS total_hours=45min conflated with PNR=25min | app.py | ⚠ Phase 2 — not contradicting, but must be clarified |
| H3 Vizier hardcoded polynomial | app.py:~5293 | ❌ Phase 3+ — not blocking H1/H2 |
| esp_classifier trained on invented ranges | inference-api/models | ⚠ Phase 5 retrain |

**Integrity notes from CLAIM_LEDGER.md:**
- C2 (SCADA reactive path $8k–15k) is 🔴 NEEDS-EXPERT — do NOT show as a hard number until SME verifies
- C3 ($150k workover) SURVIVES with qualification — "representative, varies by well"
- All of Section 1 (physics) and Section 2 (SCADA limits) are 🟢 TEXTBOOK — safe to show

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
