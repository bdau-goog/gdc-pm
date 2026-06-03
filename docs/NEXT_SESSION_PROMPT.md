# Next Session Prompt — GDC Edge AI 3-Horizon Demo

## Header
**Date:** June 3, 2026
**Live URL:** http://gdc-pm.bdau.io (us-east1 cluster)
**Project:** gdc-pm (`feature-trio-scenarios` branch — git head `17aa6ac`)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `17aa6ac` — clean working tree, no uncommitted changes
**fault-trigger-ui Digest:** `sha256:63c2ade64e8496a19a46310bd3a27b945145b67b7e72e6f18cf0b04cbd636661` (Fix 9, June 3)
**event-processor Digest:** `sha256:7de3fab05e65530524137ae944cc871ca6f4baab6d709898a530298a6d7b48d1` (Fix 7, June 3)
**Branch Policy:** `feature-trio-scenarios` stays **separate from main** — do NOT merge.

---

## ⚠️ MANDATORY SESSION OPENER — Run this BEFORE writing any code

```bash
# 1. Verify cluster truth
kubectl get pods -n gdc-pm --no-headers

# 2. Verify Ollama state
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""

# 3. API truth
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"

# 4. Database truth
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability \
  -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents; SELECT COUNT(*) FROM fault_sessions;"

# 5. Check sentence_transformers
kubectl exec -n gdc-pm deployment/fault-trigger-ui -- python3 -c "from sentence_transformers import SentenceTransformer; print('sentence_transformers: OK')" 2>&1

# 6. Check Fix 9 live (polling timer leak fix)
curl -s http://gdc-pm.bdau.io/ | grep -c "polling timers"

# 7. Verify no uncommitted changes
cd ~/gdc-pm && git status && git log --oneline -3
```

**Expected results when healthy:**
- All pods: `1/1 Running`
- Ollama: `1` replica, `ollama_online: True  model: gemma4:latest`
- rag_documents: **18 rows**, field_intel: **~100 rows**, fault_sessions: **≥4 rows**
- sentence_transformers: **OK**, polling timers: **1**, git status: **clean**

---

## ⚠️ Known Integrity State — ALL CLEAR (Post Fixes 1-9)

All 9 integrity violations from prior sessions are resolved and verified live. No display vs. reality mismatches remain.

---

## NEXT SESSION PLAN — Session E: 7 Remaining Items

### TOP PRIORITY: Fix 10 — Horizon "Physics & Logic" Info Panels

**Background:** During demo walkthrough, a critical question arose: "Are there non-AI ways to diagnose these failures? Would the normal reaction be a pump pull?"

The answer is yes — experienced production engineers *can* diagnose these issues manually using multivariate correlation, but only if they have time, access to all data silos simultaneously, and engineering-level training. The problem is scale (300-500 wells per engineer) and reaction time (manual analysis happens after SCADA trips, not before). 

These info panels make the GDC value proposition explicit and self-standing, preventing a technically sophisticated audience from dismissing the demo as trivial.

**Implementation:**
1.  Add `showH1Info: false`, `showH2Info: false`, `showH3Info: false` to Vue `data()`.
2.  Add `ⓘ Physics & Logic` toggle button to each Horizon tab's banner (next to Inject/Reset).
3.  Add a detailed HTML info card below each banner (collapsible, `v-if` on the show state).

---

#### H1 Panel Content: ESP Gas Lock — "Why this isn't trivial to diagnose"

**The Physics — Failure Mode:**
Gas Void Fraction (GVF) exceeds ~70% of pump stage volume. The pump stages, now spinning through gas rather than fluid, unload: Pump Intake Pressure (PIP) collapses and motor current (Amps) drops simultaneously as the impellers lose their hydraulic load. If uncorrected for >25 minutes, the motor runs dry, overheats, and the winding insulation begins to fail (Class H insulation threshold: 284°F per API RP 11S).

**The Traditional Engineering Workflow (Why Engineers Don't Always Catch It in Time):**
An experienced production engineer would manually cross-correlate PIP decline rate with motor current decline rate. If both sensors drop in sync, it indicates gas-locking (not mechanical wear, which only raises temp and vibration). However:
- This requires manually pulling trend plots from the SCADA historian.
- It requires knowing to *look*, which only happens if someone notices the PIP is drifting low.
- By the time SCADA fires a low-PIP alarm, the PNR may have passed.

**How GDC/AI Improves Detection:**
- Continuously calculates $dPSI/dt$ and $dAmps/dt$ slopes at 5s cadence across all wells simultaneously.
- XGBoost detects the correlated 4-sensor signature (falling PIP, falling amps, stable temp, stable vibration) as a gas_lock pattern at 94% confidence — well before any single sensor crosses an alarm threshold.
- Lead time established: **25 minutes** before SCADA would alarm.

**Cost Avoidance:**
| | Reactive (SCADA) | Proactive (GDC) |
|---|---|---|
| **Detection method** | Single threshold alarm when PIP < 180 PSI | Multivariate XGBoost slope correlation |
| **Detection timing** | ~5 min before lockup | **25 min** advance notice |
| **Action taken** | Emergency shut-in + pump pull evaluation | Automated VFD reduction 52Hz → 44Hz |
| **Downhole equipment cost** | $150,000 pump replacement if lockup occurs | $2,500 VFD software command |
| **Downtime** | 5–7 days (pull + replace) | Zero downtime |
| **Net capital avoided** | — | **$147,500** |

---

#### H2 Panel Content: Flowline Slug Flow — "Why the normal reaction IS a pump pull (and why that's wrong)"

**The Physics — Failure Mode:**
High Gas-Liquid Ratio (GLR) causes intermittent gas pockets and liquid slugs to cycle through the surface flowline. Heavy liquid slugs impacting the wellhead piping transmit mechanical shocks down the tubing string, vibrating the downhole ESP sensor (1.1 → 2.4 mm/s rise). **The downhole pump is completely healthy.** The fault is entirely at the surface choke manifold.

**The Traditional Engineering Workflow (Why Engineers Get It Wrong):**
When a downhole vibration alarm fires in a conventional SCADA environment, the default and safest assumption is downhole mechanical wear — damaged impeller stages, worn thrust bearing, or shaft misalignment. 

The traditional method to distinguish surface slugging from downhole mechanical damage:
1. **Thermal Correlation:** Downhole mechanical wear → internal friction → motor winding temperature **climbs rapidly**. Surface slugging → fluids flowing normally → winding temperature **stays flat**. If winding temperature is stable while vibration rises, the pump is mechanically intact.
2. **Current Ripple Analysis:** Surface slugging causes alternating gas pockets and liquid slugs, producing current ripple (oscillating amps). Bearing wear produces smooth, monotonically rising current.

An experienced engineer with access to winding temperature data *can* rule out a pump pull by inspecting temp vs. vibration correlation. However:
- **Lease operators are not always senior engineers.** They are trained to be conservative and protect the asset.
- The data is often in different systems (vibration in CygNet, temperature in a downhole monitoring tool portal, lab reports in SharePoint).
- The conservative default action is: **shut in and order a workover.** This is the single most costly avoidable decision in ESP production operations.

**How GDC/AI Improves Detection:**
- XGBoost correlates vibration rise vs. winding temperature stability in real-time.
- The AI correctly identifies 52% confidence "slug_flow" (ambiguous, surface issue) rather than a downhole fault.
- Gemma retrieves the OEM ESP troubleshooting manual section: *"Vibration drift without motor temperature elevation indicates surface flowline slugging."*
- Dynamic lab report from the intelligence feed: *"Separator test confirms high-GLR slug regime in the flowline."*
- Gemma's synthesized assessment: **Do NOT pull. Dispatch surface technician to adjust choke valve backpressure.**

**Cost Avoidance:**
| | Reactive (Conservative SCADA) | Proactive (GDC) |
|---|---|---|
| **Detection method** | Single vibration threshold alarm | Multivariate temp + vibration correlation |
| **Default operator action** | Shut in + schedule pump pull | Dispatch lease operator to choke valve |
| **What is actually wrong?** | Surface flowline slugging | Surface flowline slugging |
| **Pump pull cost** | **$150,000** (unnecessary) | **$0** — pump confirmed healthy |
| **Truck roll cost** | $1,500 (emergency dispatch) | **$1,500** (or $0 if batched) |
| **Net capital avoided** | — | **$148,500** |

---

#### H3 Panel Content: Oil Price Optimization — "Extracting maximum value without burning out the asset"

**The Physics — The Tradeoff:**
Running an ESP at higher VFD frequency (Hz) increases flow rate and revenue. However, motor winding temperature increases non-linearly with frequency — at high frequencies, excess heat degrades Class H polyimide insulation exponentially. Once winding temperature exceeds 270°F consistently, RUL drops from years to weeks. Burnout costs $150,000 in capital + $45,000/day in deferred production.

**The Traditional Engineering Approach:**
Production engineers historically set a conservative, static VFD setpoint (typically 48–52Hz) that keeps temperature well within limits. This is safe but **leaves significant revenue untapped** when oil prices spike. Manual optimization requires:
- Running individual "Hz trials" with 48-hour stabilization periods each.
- Manually correlating flow rate gains against temperature trends.
- Weeks of testing per well, while the high-price window may last only days.

**How GDC/AI Improves the Decision:**
- GDC's XGBoost RUL model continuously projects thermal degradation trajectories at each hypothetical Hz setpoint.
- The curated OEM manual's Class H insulation temperature limit (284°F per API RP 11S) is retrieved from AlloyDB pgvector and used as a hard constraint in the Vizier optimization.
- **Google Vizier (Bayesian Optimization)** executes 15 targeted trials over the Hz search space, intelligently balancing exploration (testing new Hz values) with exploitation (refining the best known region). Each trial takes milliseconds on the edge ML model — not 48 hours in the field.
- Vizier converges on the **Pareto Frontier** — the maximum Hz that maximizes net cash flow without triggering motor burnout.
- The operator deploys the recommendation instantly with "Deploy Recommendation."

**Financial Model:**
The Vizier cash flow model for each trial is:
`Net Cash Flow = (Flow Rate × Oil Price × Horizon Days) − Power Costs − (Burnout Penalty if RUL < Horizon)`

Where:
- Burnout Penalty = $150,000 (replacement) + (Days of downtime × $45,000/day)
- The OEM-retrieved temperature limit determines whether a given Hz setpoint crosses into burnout territory.

---

### Fix 11 — `slug_flow` in frontend `FAULT_META` (Small · HTML-only)

In `index.html` JS constants, add:
```javascript
slug_flow: {label:'Slug Flow', color:'#ffb300', desc:'Flowline slugging — surface choke valve backpressure', aclass:'esp'},
```
And update `FAULTS_BY_CLASS.esp`:
```javascript
esp: ['gas_lock', 'slug_flow', 'sand_ingress', 'motor_overheat'],
```

**Verification:** Fleet Ops → inject slug_flow → fault label shows "Slug Flow" not raw key.

---

### Fix 12 — `last_cloud_sync` live timestamp (Small · app.py rebuild)

In `app.py`, replace `"2026-05-13T14:30:00Z"` with a live query:
```python
def _get_last_event_time() -> str:
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT MAX(event_time) FROM telemetry_events")
            row = cur.fetchone()
        conn.close()
        if row and row[0]:
            return row[0].isoformat() + "Z"
    except Exception:
        pass
    return "unknown"
```
And reference it: `"last_cloud_sync": _get_last_event_time()`

**Verification:** `curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('last_cloud_sync'))"` → shows recent timestamp.

---

### Fix 13 — Upgrade Ollama to gemma4:31b (Medium · YAML only, no Docker rebuild)

In `gke/event-processor/k8s/event-processor.yaml`, add env var:
```yaml
- name: OLLAMA_MODEL
  value: "gemma4:31b"
```
Deploy with `kubectl apply -f gke/event-processor/k8s/event-processor.yaml -n gdc-pm`. Allow 5min GPU warm-up on first inference (19GB model, but already on PVC).

---

### Fix 14 — Frontend `ASSET_META` expansion (Medium · HTML-only)

Add gas lift (GLIFT-BRAVO-*) and mud pump (PUMP-CHARLIE-*) assets to `SITES`, `ASSET_META`, `FAULTS_BY_CLASS`, `FAULT_META`, and `SENSOR_LABELS` JS constants. These assets already exist in telemetry but are invisible to Fleet Operations.

---

### Fix 15 — H3 Vizier RAG Constraint (Low · app.py rebuild)

In `/api/vizier/optimize`, retrieve Class H insulation temp limit from pgvector before the trial loop and use it as the burnout threshold (replacing hardcoded 270°F).

---

### Recommended Batching for Session E

- **Deploy A:** Fix 10 + Fix 11 (HTML-only, ~1 min)
- **Deploy B:** Fix 12 + Fix 15 (app.py rebuild, ~15 min)
- **Deploy C:** Fix 13 (kubectl apply, ~3 min + 5 min GPU warm-up)
- **Deploy D:** Fix 14 (HTML-only, ~1 min)

---

## Physics & Logic Engineering Rationale (Do Not Lose This — Source Material)

This section captures the engineering reasoning developed in the June 3 session that must flow into the info panels in Fix 10. **Do not remove from handoff.**

### Why Horizon 2 Is the Most Vulnerable to Audience Challenge

A technically sophisticated audience (production engineers, operations managers) will immediately ask:
> *"An experienced engineer can look at a flat winding temperature and rising vibration and know it's not a downhole pump problem. This doesn't require AI."*

The correct answer is: **Yes, and here's the operational reality of why that doesn't happen:**
1. **Scale:** One production engineer manages 300–500 wells. They cannot manually inspect thermal correlations in 5 different data systems for every minor vibration drift.
2. **Siloed Data:** SCADA historian (vibration/pressure), downhole monitoring portal (winding temp), SharePoint (lab reports), and CygNet (alarms) are all separate systems. The correlation requires manual extraction from each.
3. **Operator Conservatism:** Lease operators on-site are not senior engineers. Faced with a vibration alarm and liability exposure, the default safe action is to shut in and order a pull. This is policy, not ignorance.
4. **Reaction vs. Prediction:** Even when the experienced engineer does the correlation manually, it typically happens *after* the SCADA alarm has already fired and the well is shut in. GDC detects the pattern 12–24 hours before the SCADA alarm, allowing the well to stay on production throughout.

---

## Current Cluster State (VERIFIED June 3, 2026 16:07)

```
alloydb-omni-5fcfc68fdb-9vm2z           1/1   Running   0
event-processor-5bfb656765-b9s7q        1/1   Running   ← Fix 7 (gemma4:latest default)
fault-trigger-ui-cf7bf4444-vw9s6        1/1   Running   ← Fix 9 (timer leak fix)
gdc-pm-rabbitmq-server-0                1/1   Running
grafana-655b6f5c7c-w2h84                1/1   Running
inference-api-5697b79566-zqdpl          1/1   Running
ollama-5bc5db749b-n6tb8                 1/1   Running
telemetry-simulator-867677f784-h55wd    1/1   Running
```

DB: field_intel: 100, rag_documents: 18, fault_sessions: 4

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
# HTML-only changes (Fix 10, Fix 11, Fix 14)
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm

# app.py changes (Fix 12, Fix 15) — same commands as above

# gemma4:31b upgrade (Fix 13) — YAML only, NO REBUILD
kubectl apply -f gke/event-processor/k8s/event-processor.yaml -n gdc-pm
kubectl rollout status deployment/event-processor -n gdc-pm

# event-processor Python changes — use digest (imagePullPolicy: IfNotPresent)
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/event-processor:latest gke/event-processor
docker push ${REGISTRY}/event-processor:latest
NEW_DIGEST=$(gcloud artifacts docker images describe ${REGISTRY}/event-processor:latest --format='value(image_summary.digest)' 2>/dev/null)
kubectl set image deployment/event-processor event-processor=${REGISTRY}/event-processor@${NEW_DIGEST} -n gdc-pm
kubectl rollout status deployment/event-processor -n gdc-pm
```

**Deploy timing:** fault-trigger-ui HTML-only: ~1 min. event-processor (5.49GB): ~9 min. event-processor YAML only: ~3 min + 5 min GPU warm-up.

---

## Key Lessons (carry-forward)

- **event-processor requires `kubectl set image @sha256:<digest>`** — `imagePullPolicy: IfNotPresent` means `rollout restart` uses cached old image on the node.
- **`setMainTab()` is the nav chokepoint for H1/H2/H3** — "Fleet Operations" and "Fleet Financials" use inline `@click` and bypass it.
- **H2 is the most vulnerable to technical pushback** — Frame it as a *scale and data silo problem*, not a detection accuracy problem. A single engineer can do this for one well; GDC does it for 300 wells simultaneously with sub-second latency.
- **The Physics & Logic panels are commercially critical** — They transform the demo from "look at the AI" into "understand why this specific failure mode is worth $148,500 to detect early". Budget one full session (Session E) to implement them carefully.
