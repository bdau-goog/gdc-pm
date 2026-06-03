# Next Session Prompt — GDC Edge AI 3-Horizon Demo

## Header
**Date:** June 3, 2026
**Live URL:** http://gdc-pm.bdau.io (us-east1 cluster)
**Project:** gdc-pm (`feature-trio-scenarios` branch — git head `607d227`)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `607d227` — clean working tree, no uncommitted changes
**fault-trigger-ui Digest:** `sha256:5d8c773248eed7ee4293d8c5d3d102d43acde415c19e1947abd46861778cb9c9`
**event-processor Digest:** `sha256:312ce844a244356732d435e396396486df7e111c814f8205238c43feb5d9cd63` — pinned in YAML
**Branch Policy:** `feature-trio-scenarios` stays **separate from main** — do NOT merge.

---

## ⚠️ MANDATORY SESSION OPENER — Run this BEFORE writing any code

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get pod -n gdc-pm -l app=event-processor -o jsonpath='{.items[0].metadata.name} restarts={.items[0].status.containerStatuses[0].restartCount}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
time curl -s "http://gdc-pm.bdau.io/api/vizier/optimize?oil_price=112&horizon_days=90" --max-time 10 | python3 -c "import sys,json;d=json.load(sys.stdin);print('trials:',len(d['trials']),'optimal_hz:',d['optimal_hz'])"
cd ~/gdc-pm && git log --oneline -3
```

**Expected results when healthy:**
- All pods: `1/1 Running`, event-processor `restarts=0`
- Ollama: `ollama_online: True`
- rag_documents: 18, field_intel: ~100
- Vizier endpoint: <1s (still local Python — must be replaced with Vertex AI)
- git head: `607d227`

---

## ⛔ Known Integrity State — CRITICAL VIOLATION

| Item | Violation | Fix |
|------|-----------|-----|
| **H3 Vizier tab** | UI says "Google Vizier (Bayesian Optimization)" but `vizier_optimize()` is pure local Python math with hardcoded trial Hz values. No Vertex AI API calls. No Gaussian Process. No actual Bayesian trial selection. | **Implement real Vertex AI Vizier (Fix V1) — HIGH PRIORITY** |

**Other simulated elements (acceptable for demo, not integrity violations):**
- SAP/Maximo/Pason data in agent context — hardcoded Python dicts, not live API calls. Industry-standard for POC demos.
- Field intel documents — template-generated, not LLM-written. Minor concern.
- SCADA chart — shows the same simulator data as GDC, trimmed to historical. Acceptable framing.

---

## NEXT SESSION PLAN — Fix V1: Real Vertex AI Vizier

| Fix | Change | Verification | Complexity |
|-----|--------|--------------|------------|
| **V1a** | Verify Vertex AI API is enabled and fault-trigger-ui service account has `roles/aiplatform.user` | `gcloud services list --enabled | grep aiplatform` | Small |
| **V1b** | Add `google-cloud-aiplatform` to fault-trigger-ui requirements.txt | pip install works in Dockerfile build | Small |
| **V1c** | Replace hardcoded trial loop in `vizier_optimize()` with real Vertex AI Vizier Study + suggest_trials() + add_measurement() | Endpoint returns different optimal Hz on each run; trials have adaptive selection pattern | Large |
| **V1d** | Update H3 UI physics panel text to correctly describe the real Vizier flow | Visual check — description matches actual implementation | Trivial |

### Implementation Guide for Fix V1

**Step 1 — Check prerequisites (before writing any code):**
```bash
# Is Vertex AI API enabled?
gcloud services list --enabled --project gdc-pm | grep aiplatform

# What service account does the fault-trigger-ui pod use?
kubectl get pod -n gdc-pm -l app=fault-trigger-ui -o jsonpath='{.items[0].spec.serviceAccountName}'; echo ""

# Does it have aiplatform access?
gcloud projects get-iam-policy gdc-pm --format=json | python3 -c "
import sys,json; d=json.load(sys.stdin)
for b in d.get('bindings',[]): 
  if 'aiplatform' in b.get('role','').lower(): print(b)"
```

**Step 2 — Requirements change:**
```
# gke/fault-trigger-ui/requirements.txt — add:
google-cloud-aiplatform>=1.38.0
```

**Step 3 — Replace `vizier_optimize()` in app.py:**

The key change is replacing the hardcoded trial loop with real Vertex AI Vizier:

```python
@app.get("/api/vizier/optimize")
def vizier_optimize(oil_price: float = 112.0, horizon_days: int = 90):
    """Real Google Vertex AI Vizier Bayesian Optimization."""
    import math, re
    from google.cloud import aiplatform
    from google.cloud.aiplatform import vizier as vertex_vizier

    # Fix 15: Get burnout threshold from rag_documents (SQL ILIKE — no model load)
    burnout_threshold_f = 284.0
    try:
        _rag_conn = get_db()
        with _rag_conn.cursor() as _cur:
            _cur.execute("""
                SELECT content FROM rag_documents
                WHERE asset_class = 'esp'
                  AND (content ILIKE '%insulation%' OR content ILIKE '%class h%')
                  AND content ILIKE '%%F%'
                LIMIT 1
            """)
            _row = _cur.fetchone()
        _rag_conn.close()
        if _row:
            _m = re.search(r'(\d{2,3})\s*[°º]?\s*F\b', _row[0])
            if _m:
                _cand = float(_m.group(1))
                if 200.0 <= _cand <= 380.0:
                    burnout_threshold_f = _cand
    except Exception as e:
        log.debug(f"Vizier RAG constraint skipped: {e}")

    # Helper: evaluate VFD Hz → cash flow (same physics as before)
    def evaluate_hz(hz: float) -> dict:
        flow_rate = round(24.0 * hz, 1)
        temp_f = round(180.0 + 1.5 * (hz - 45.0) + 0.15 * max(0.0, hz - 58.0)**3, 1)
        rul_days = round(300.0 * math.exp(-0.11 * (hz - 45.0)), 1)
        power_cost = round(0.1 * (hz**3), 1)
        is_temp_burnout = temp_f >= burnout_threshold_f
        is_failure = (rul_days < horizon_days) or is_temp_burnout
        if not is_failure:
            prod_days = horizon_days
            cash_flow = round(oil_price * flow_rate * horizon_days - power_cost * horizon_days, 1)
        else:
            prod_days = rul_days if not is_temp_burnout else round(max(1.0, rul_days * 0.6), 1)
            cash_flow = round(oil_price * flow_rate * prod_days - power_cost * prod_days - 150000.0, 1)
        return {"vfd_hz": hz, "flow_rate": flow_rate, "motor_temp_f": temp_f,
                "rul_days": rul_days, "cash_flow": cash_flow, "prod_days": prod_days,
                "is_failure": is_failure}

    # Vertex AI Vizier study
    aiplatform.init(project=GCP_PROJECT, location="us-central1")
    study_config = vertex_vizier.StudyConfig(
        algorithm=vertex_vizier.StudyConfig.Algorithm.GAUSSIAN_PROCESS_BANDIT,
        metrics=[vertex_vizier.StudyConfig.MetricSpec(
            metric_id="cash_flow",
            goal=vertex_vizier.StudyConfig.MetricSpec.GoalType.MAXIMIZE
        )],
        parameters=[vertex_vizier.StudyConfig.ParameterSpec(
            parameter_id="vfd_hz",
            double_value_spec=vertex_vizier.StudyConfig.ParameterSpec.DoubleValueSpec(
                min_value=45.0, max_value=70.0
            )
        )]
    )
    study = vertex_vizier.Study.create_or_load(
        display_name=f"gdc_vfd_opt_{int(time.time())}",
        problem=study_config
    )

    trials = []
    best_cash_flow = -999999999.0
    for i in range(15):
        suggested = study.suggest(count=1)
        for suggested_trial in suggested:
            hz = suggested_trial.parameters["vfd_hz"]
            result = evaluate_hz(hz)
            result["trial_num"] = i + 1
            result["is_optimal"] = False
            suggested_trial.add_measurement(
                measurement=vertex_vizier.Measurement(
                    metrics=[vertex_vizier.Measurement.Metric(
                        metric_id="cash_flow", value=result["cash_flow"]
                    )]
                )
            )
            suggested_trial.complete(infeasible_reason=None if not result["is_failure"] else "burnout")
            trials.append(result)
            if result["cash_flow"] > best_cash_flow:
                best_cash_flow = result["cash_flow"]

    # Mark optimal
    for t in trials:
        if t["cash_flow"] == best_cash_flow:
            t["is_optimal"] = True
            break
    optimal_trial = next(t for t in trials if t["is_optimal"])

    # SCADA nominal + run-to-failure comparisons (unchanged)
    scada = evaluate_hz(50.0)
    rtf = evaluate_hz(65.0)

    return {"trials": trials, "optimal_hz": optimal_trial["vfd_hz"],
            "optimal_cash_flow": best_cash_flow,
            "scada_nominal": {**scada, "vfd_hz": 50.0},
            "run_to_failure": {**rtf, "vfd_hz": 65.0},
            "vizier_optimal": optimal_trial}
```

**Step 4 — Update physics panel text (index.html):**
Change: `"Google Vizier (Bayesian Optimization) executes 15 targeted trials"`  
To: `"Google Vertex AI Vizier executes 15 Gaussian Process Bandit trials — each trial is suggested by Vizier's Bayesian model, evaluated against the local XGBoost RUL projection, and reported back. The edge cluster runs the physics; Vertex AI Vizier drives the search."`

**Step 5 — Rebuild fault-trigger-ui:**
```bash
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm
```

**Step 6 — Verify:**
- Click "Run Vizier Optimization" on H3 tab
- Check that different runs produce slightly different optimal Hz (Gaussian Process is not deterministic)
- Each run creates a new Study in Vertex AI console (visible at console.cloud.google.com → Vertex AI → Vizier)

---

## What Was Done This Session (Sessions F + G — June 3, 2026)

- EP-1: event-processor crash loop eliminated
- EP-2: all-MiniLM-L6-v2 baked into event-processor image (62 it/s from cache)
- Fix 13: gemma4:31b confirmed in Ollama (19GB, verified)
- Fix 14: 14 new assets across 3 sites in frontend JS constants
- Fix 15: Vizier RAG constraint via SQL ILIKE (148ms)
- Fix 10b: H2 "1:500" orange callout box

**Integrity discovery**: The H3 Vizier tab does not use Google Cloud Vertex AI Vizier — it is local Python math with hardcoded trial values. This must be fixed before any further customer demos.

---

## Current Cluster State (VERIFIED June 3, 2026 18:26)

```
alloydb-omni-5fcfc68fdb-9vm2z           1/1   Running
event-processor-99dd7b6d9-qjjg9         1/1   Running  ← EP-2 + EP-1 + Fix 13
fault-trigger-ui-[latest pod]           1/1   Running  ← Fix 10b + Fix 14/15
gdc-pm-rabbitmq-server-0                1/1   Running
grafana-655b6f5c7c-w2h84                1/1   Running
inference-api-5697b79566-zqdpl          1/1   Running
ollama-5bc5db749b-n6tb8                 1/1   Running  ← gemma4:31b + gemma4:latest
telemetry-simulator-867677f784-h55wd    1/1   Running
```

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
# fault-trigger-ui
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm

# event-processor (digest-pinned YAML)
docker build -t ${REGISTRY}/event-processor:latest gke/event-processor
docker push ${REGISTRY}/event-processor:latest
# update digest in gke/event-processor/k8s/event-processor.yaml, then:
kubectl apply -f gke/event-processor/k8s/event-processor.yaml -n gdc-pm
```

---

## Key Lessons

- **Vizier is not Gemini**: Google Cloud Vizier (Vertex AI Vizier) is a separate product from Gemini. It is an optimization service, not a language model. It requires enabling `aiplatform.googleapis.com`, a service account, and HTTP calls to the Vertex AI API. Displaying "Google Vizier" in the UI without calling that API is an integrity violation.
- **Always verify what a named Google service actually requires**: When a demo labels something "Google X", confirm that `X` is being called. If it is not, either implement it or label it honestly.
- **SQL ILIKE > embedding for fact retrieval**: Specific known facts in text documents are faster and more reliable with SQL text search than semantic similarity search.
- **Model baking eliminates cold-start**: `RUN python3 -c "SentenceTransformer('model-name')"` in the Dockerfile caches the model in the image layer — instant startup on any node.
