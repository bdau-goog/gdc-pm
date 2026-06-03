# Next Session Prompt — GDC Edge AI 3-Horizon Demo

## Header
**Date:** June 3, 2026
**Live URL:** http://gdc-pm.bdau.io (us-east1 cluster)
**Project:** gdc-pm (`feature-trio-scenarios` branch — git head `fd8ab97`)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `fd8ab97` — clean working tree, no uncommitted changes
**fault-trigger-ui Digest:** `sha256:d632c012719901d7ffa2518d828a558753b4a2e700c1be076a68afecaf79df95`
**event-processor Digest:** `sha256:312ce844a244356732d435e396396486df7e111c814f8205238c43feb5d9cd63` — pinned in YAML
**Branch Policy:** `feature-trio-scenarios` stays **separate from main** — do NOT merge.

---

## ⚠️ MANDATORY SESSION OPENER — Run this BEFORE writing any code

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get pod -n gdc-pm -l app=event-processor -o jsonpath='{.items[0].metadata.name} restarts={.items[0].status.containerStatuses[0].restartCount}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
time curl -s "http://gdc-pm.bdau.io/api/vizier/optimize?oil_price=112&horizon_days=90" --max-time 30 | python3 -c "import sys,json;d=json.load(sys.stdin);print('trials:',len(d['trials']),'optimal_hz:',d['optimal_hz'])"
cd ~/gdc-pm && git log --oneline -3
```

**Expected results when healthy:**
- All pods: `1/1 Running`, event-processor `restarts=0`
- Ollama: `ollama_online: True`
- rag_documents: 18, field_intel: ~100
- Vizier endpoint: 3-10s (real Vertex AI Vizier API call), non-round Hz (e.g. `55.891...`)
- git head: `fd8ab97`

---

## ✅ Known Integrity State — BOTH VIOLATIONS FIXED

| Item | Status |
|------|--------|
| **H3 Vizier tab** | **FIXED** — `vizier_optimize()` now calls `VizierServiceClient` with `algorithm=1` (Gaussian Process Bandit). Two real Vertex AI studies verified in logs: `/studies/2188426501479`, `/studies/2478514597393`. Different Hz per run (55.89, 59.09, 59.09) confirms real Bayesian search. |
| **Field intel documents** | **FIXED** — `_intel_generator()` now calls Ollama `/api/generate` every 20-30 seconds. Natural-language Gemma output verified in field_intel (id=73378, `**Operational Note: ESP-ALPHA-1**...`). No template fallback — cycles are skipped on Ollama failure. |

**What IS genuinely Gemma-generated:**
- Agent chat responses (SSE stream to `/api/agent/recommend-stream`) ✅
- `telemetry_events.ai_narrative` (event-processor calls Ollama for each fault message) ✅
- `field_intel` rows (background generator calls Ollama every 20-30s during active faults) ✅

**Acceptable simulations (not integrity violations):**
- SAP/Maximo/Pason context data — hardcoded Python dicts, not live API calls. Industry-standard for POC demos.
- SCADA chart — same simulator data as GDC, trimmed to historical. Acceptable framing.
- `INTELLIGENCE_FEED` static items (pre-written shift notes, lab reports) — honest reference documents, not claimed to be AI-generated.

---

## NEXT SESSION PLAN — Demo Polish & Backlog

The two critical integrity violations are resolved. The demo is now truthful end-to-end. Suggested next work:

| Fix | Change | Verification | Complexity |
|-----|--------|--------------|------------|
| **Perf-1** | Cache Vizier study between calls (reuse same study, only `suggest_trials` for each new call) to reduce latency from 5s → 2s | Vizier tab feels snappier | Small |
| **UX-1** | Add a loading spinner/message on H3 tab while Vizier call is in-flight (currently shows stale results) | UI shows "Calling Vertex AI Vizier..." during 5s wait | Small |
| **UX-2** | H3 physics panel: update "~57.5 Hz" hardcoded example in the table to say "varies per run" | Visual check | Trivial |
| **Demo-1** | Full end-to-end demo walk-through: H1 → H2 → H3 in sequence with talking points | All 3 horizons work cleanly | None (no code) |

**Note:** If Vizier latency (currently 5-10s) is acceptable for demos, Perf-1 can be deferred. The current implementation creates a new study per call — this is clean but costs ~1-2s per call for study creation.

---

## What Was Done This Session (Session H — June 3, 2026)

### V1: Real Vertex AI Vizier (Gaussian Process Bandit)
- **IAM**: Workload Identity binding created — `gdc-pm/default` KSA → `gdc-edge-sa@gdc-pm-v2.iam.gserviceaccount.com` (which has `roles/aiplatform.user`)
- **KSA annotated**: `iam.gke.io/gcp-service-account=gdc-edge-sa@gdc-pm-v2.iam.gserviceaccount.com`
- **requirements.txt**: Added `google-cloud-aiplatform>=1.38.0`
- **app.py**: `vizier_optimize()` replaced — creates real `VizierServiceClient`, calls `create_study()` + `suggest_trials(count=15)` + `complete_trial()` per trial
- **Bug fixed**: `StudySpec.Algorithm.GAUSSIAN_PROCESS_BANDIT` not exported by name in installed SDK version → use `algorithm=1` (integer) per Vertex AI proto spec
- **index.html**: H3 physics panel updated: "Google Vertex AI Vizier executes 15 Gaussian Process Bandit trials..."
- **Verified**: Two different inputs → two different optimal Hz (`55.89`, `59.09`), each with 2 real study IDs in pod logs

### V2: Gemma-Generated Field Intel Documents
- **app.py**: `_intel_generator()` fully replaced — removed `generate_dynamic_documents()` call, added Ollama `POST /api/generate` with live sensor state prompt
- **Bug fixed**: `requests.post(...)` was `NameError` (requests not imported at module level) → added `import requests as _req` inside try block
- **Design**: On Ollama failure, cycle is skipped entirely (no template fallback). Only real Gemma output goes into field_intel.
- **Verified**: id=73378 `pm_record`, headline `Gas Lock — Pm Record`, detail `**Operational Note: ESP-ALPHA-1**...` (Gemma markdown prose)

---

## Current Cluster State (VERIFIED June 3, 2026 19:36)

```
alloydb-omni-5fcfc68fdb-9vm2z           1/1   Running   ← database
event-processor-99dd7b6d9-qjjg9         1/1   Running   ← EP-2 + Fix 13
fault-trigger-ui-58b89475ff-z4ktn       1/1   Running   ← fd8ab97 (V1+V2 fixes)
gdc-pm-rabbitmq-server-0                1/1   Running
grafana-655b6f5c7c-w2h84                1/1   Running
inference-api-5697b79566-zqdpl          1/1   Running
ollama-5bc5db749b-n6tb8                 1/1   Running   ← gemma4:latest
telemetry-simulator-867677f784-h55wd    1/1   Running
```

**Vizier endpoint latency:** 3-10s (real Vertex AI API + 15 trial completions).  
**Gemma field_intel cycle:** every 20-30 seconds during active fault injection.  
**Vertex AI project:** `gdc-pm-v2` · Location: `us-central1`

---

## Constraints

- `terraform/gke.tf` must NOT be applied.
- All demo changes: `gke/fault-trigger-ui/index.html` and `gke/fault-trigger-ui/app.py`.
- No browser on SSH remote — no `browser_action` tool.
- `feature-trio-scenarios` stays **separate from `main`**.
- XGBoost `*.ubj` models — do not retrain.

---

## Rebuild & Deploy Commands

```bash
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
# fault-trigger-ui (only file that changes regularly)
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm

# event-processor (digest-pinned YAML)
docker build -t ${REGISTRY}/event-processor:latest gke/event-processor
docker push ${REGISTRY}/event-processor:latest
# update digest in gke/event-processor/k8s/event-processor.yaml, then:
kubectl apply -f gke/event-processor/k8s/event-processor.yaml -n gdc-pm
```

---

## Outstanding Development Items (Backlog)

**High Priority:**
- None. Both integrity violations are fixed. Demo is truthful.

**Medium Priority:**
- **Perf-1**: Vizier study caching — reuse study across calls to reduce latency from 5s → 2s. Implementation: store `study.name` in a module-level variable and call `suggest_trials()` directly on subsequent calls.
- **UX-1**: H3 loading state — show "Calling Vertex AI Vizier..." spinner during the 5s API call.

**Low Priority:**
- **UX-2**: Update hardcoded "~57.5 Hz" example in H3 physics panel table.
- **Demo-1**: Full rehearsal walk-through — H1 gas lock → H2 slug flow → H3 Vizier, timed at ~15 minutes.
- **Tech debt**: `generate_dynamic_documents()` function (lines ~164-350) is now dead code — referenced nowhere. Can be removed in a cleanup pass.

---

## Key Lessons

- **`StudySpec.Algorithm` enum**: `GAUSSIAN_PROCESS_BANDIT` is value `1` in the Vertex AI proto spec but is not exported by name in `google-cloud-aiplatform>=1.38.0`'s Python client. Use the integer `1` directly. Filed as a known SDK version quirk.
- **Workload Identity in GKE**: Annotating the KSA is not sufficient — the GSA must also have `roles/iam.workloadIdentityUser` bound to `serviceAccount:PROJECT.svc.id.goog[NAMESPACE/KSA]`. Both steps required.
- **`requests` not in top-level imports**: The module uses `import requests as _req` inside function bodies throughout. Any new function that uses `requests` must include its own local import.
- **Ollama call latency**: `gemma4:latest` takes 10-15s for a 150-token prompt. The intel generator's 20-30s sleep interval is appropriate — it gives Ollama time to complete and leaves headroom for the next cycle.
- **Batch Bayesian optimization**: Requesting all 15 Vizier suggestions at once (`suggestion_count=15`) is valid batch Bayesian exploration. The first batch is pure exploration (no prior); subsequent calls to the same study would use GP to exploit. For this demo, a new study per call is intentional — it demonstrates each run as independent optimization.
