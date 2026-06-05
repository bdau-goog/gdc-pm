# Next Session Prompt — GDC Edge AI Demo (Operational State)

**Date:** June 5, 2026 (Session W end)  
**Git Head:** `c4ca13e` — ESP classifier v3, all offline gates pass  
**fault-trigger-ui image:** `sha256:b57066d4` (1/1 Running — Session V, unchanged)  
**inference-api image:** `sha256:62e007c5` (1/1 Running — Session W first deploy, STALE — replace in Session B)  
**inference-api models:** `esp_classifier.ubj` at `c4ca13e` — the correct v3 model (NOT yet in the live container)  
**Branch:** `feature-trio-scenarios` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected healthy (Session B start):**
- fault-trigger-ui: 1/1 Running
- inference-api: 1/1 Running (sha256:62e007c5 — stale, will be replaced this session)
- telemetry-simulator: 1/1 Running (was scaled up Session W)
- AlloyDB, RabbitMQ, Grafana, event-processor, Ollama: 1/1 Running
- ollama_online: True · model: gemma4:latest
- field_intel: 80–120 rows · rag_documents: 18 rows

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Session B — Wire In + Rebuild + Verify

### 3a. Fix "25 minutes" static template in app.py (integrity violation)

Two places need dynamic elapsed-time replacement:
1. `GEMMA_FINDING_TEMPLATES["gas_lock"]` — template variable `{pnr}` reads from
   `PNR_MINUTES.get(fault_type)` = 25 (static). Replace with remaining window:
   `elapsed = (utcnow - fault_onset_utc).total_seconds()/60; remaining = max(0, PNR_MINUTES[ft] - elapsed)`
2. `GEMMA_FINDINGS["gas_lock"]` static string — `"Act within 25 minutes before pump stall"` → 
   `"Act within {remaining:.0f} minutes before pump stall"` computed the same way.
   (Function: `get_gemma_finding()` at line 4527; `active_degrades` already has `fault_onset_utc`)

### 3b. Rebuild inference-api with new esp_classifier.ubj

The v3 model is in `gke/inference-api/models/esp_classifier.ubj` at `c4ca13e`.
The live pod still has the Session W first-pass model (sha256:62e007c5, trained before fixes).

```bash
# Scale ALL pods to 0 first (clean slate)
kubectl scale deployment/inference-api --replicas=0 -n gdc-pm
kubectl scale deployment/telemetry-simulator --replicas=0 -n gdc-pm

# Rebuild fault-trigger-ui (picks up the app.py {pnr}→dynamic fix)
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest gke/fault-trigger-ui/
docker push ...
DIGEST_UI=$(docker inspect --format='{{index .RepoDigests 0}}' ...)

# Rebuild inference-api (picks up esp_classifier.ubj v3)
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/inference-api:latest gke/inference-api/
docker push ...
DIGEST_INF=$(docker inspect --format='{{index .RepoDigests 0}}' ...)

# Deploy both
kubectl set image deployment/fault-trigger-ui fault-trigger-ui=${DIGEST_UI} -n gdc-pm
kubectl set image deployment/inference-api inference-api=${DIGEST_INF} -n gdc-pm
kubectl scale deployment/inference-api --replicas=1 -n gdc-pm
kubectl scale deployment/telemetry-simulator --replicas=1 -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/inference-api -n gdc-pm
```

### 3c. Live non-circular verification

After both pods 1/1 Running, wait 5 min of steady normal, then:
```sql
-- Should show normal→normal dominates
SELECT failure_type, predicted_label, COUNT(*) FROM telemetry_events
WHERE asset_type='esp' AND event_time > NOW() - INTERVAL '5 minutes'
GROUP BY failure_type, predicted_label;
```
Then inject gas_lock + slug_flow (one each), verify:
```sql
SELECT failure_type, predicted_label, COUNT(*), ROUND(AVG(confidence),3)
FROM telemetry_events WHERE asset_type='esp' AND event_time > NOW() - INTERVAL '6 minutes'
GROUP BY failure_type, predicted_label ORDER BY 1, 3 DESC;
```
**Gate:** normal→normal ≥90%, gas_lock→gas_lock ≥80%, slug_flow→slug_flow ≥80%.

Update `MODEL_FOUNDATIONS.md §6` with the confusion matrix.

---

## STEP 4: Session B follow-on — Confidence Widget (H1)

After models pass live verification:
- Build the "Live Diagnostic Confidence" widget in H1 tab
- `h1TopClass`/`h1TopClassProb` are already wired in Vue data (Session V)
- Needs HTML/CSS only: probability bars for all 5 classes, sorted descending
- Stage badge: Emerging (<60%) / Developing (60–85%) / Confirmed (≥85%)

---

## Known Integrity State — Session B start

| ID | Status | Notes |
|---|---|---|
| V-01 through V-09 | ✅ Fixed Session V | Display violations resolved |
| gas_lock `{pnr}` static template | 🔴 Open | Shows "25 min" regardless of elapsed time; app.py line 4506 |
| `GEMMA_FINDINGS["gas_lock"]` static | 🔴 Open | "Act within 25 minutes" hardcoded; app.py ~line 4597 |
| inference-api live container | 🔴 Stale | sha256:62e007c5 has pre-fix model; v3 at c4ca13e not yet deployed |
| fault-trigger-ui slug_flow vib_range | 🔴 Stale | Container still has (2.2,3.2); source correct (4.0,6.5) at HEAD |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- `feature-trio-scenarios` stays separate from `main`
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- inference-api registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/inference-api:latest`
- Do NOT use "Copilot" anywhere
- Failing model `.ubj` files are NEVER committed
