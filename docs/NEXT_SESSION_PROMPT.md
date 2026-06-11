# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 11, 2026 (Session BC — Sprint H3-B N-well field Vizier optimization)
**git head:** `84e1b5f` (feat(h3-b): N-well field Vizier optimization)
**fault-trigger-ui image:** `sha256:21bb97c56f052119b68d5a4736a1220290855cbb6fadfaa1337277cdcdc98942`
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected (dev default — GPU OFF):**
- 6 pods 1/1 Running + 3 prune CronJob Completed (ollama pod ABSENT — correct)
- ollama replicas: **0** · `ollama_online: False` — NOT a problem. Do NOT scale up.
- field_intel: **9–12** · rag_docs: **18**

**Actual at session-BC close:** 6 pods Running · ollama=0 · ollama_online=False · field_intel=11 · rag_docs=18 ✅

**GPU discipline:** OFF by default. `./scripts/gpu-start.sh` only at explicit LLM-test step (~$0.65/hr). Always paired with `./scripts/gpu-stop.sh`.

**⚠️ REGISTRY NOTE:** Artifact Registry only — NOT gcr.io.
```bash
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest gke/fault-trigger-ui/
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl set image deployment/fault-trigger-ui -n gdc-pm \
  fault-trigger-ui=us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui@sha256:<digest>
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm
```

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat /home/brian/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Next Implementation Tasks (in order)

### SPRINT H3-C: H3 UI — 3-panel briefing + field optimization display
- **Wireframe sign-off required before any HTML** (per §4.5 Briefing Pattern Spec)
- Panel 1: The Opportunity (oil-price spike + well heterogeneity setup)
- Panel 2: The Tradeoff (gas ceiling binding → constraint-stack panel: gas BOLD, others muted)
- Panel 3: The Optimization (field-wide setpoint vector + joint-vs-independent uplift card)
- Key data available from `/api/vizier/optimize`:
  - `wells[]` — per-well GOR, max_hz, independent_hz, joint_hz
  - `independent_baseline` / `joint_optimal` — oil, gas, cash_flow, uplift_bbl_d, uplift_cash_90d
  - `constraint_stack` — gas binding=True, thermal/RUL binding=False
- Replace existing H3 "ⓘ Physics & Logic" toggle panel with proper 3-panel briefing

### SPRINT H3-D: DEMO_MASTER §6 rewrite (field-level spec)
- Update §6 to reflect 6-well Pad Alpha joint optimization (N-well, gas ceiling, LP uplift)

### SPRINT P4 — H1 Batch B date-templating (small)
Sonic log / shift note / GOR lab report in `field_intel` have hardcoded 2025 dates. Template to `today − offset`.

---

## H3-B Technical Notes (for next session context)

**What was built (Session BC):**
`vizier_optimize()` rewritten for N-well field optimization. Key results on live cluster:
```
n_wells: 6 | gas_ceiling: 8.0 MMscfd
A-1 GOR=650  max=65.5 indep=63.99 joint=65.50
A-2 GOR=1100 max=65.5 indep=63.99 joint=65.50
A-3 GOR=450  max=66.0 indep=64.48 joint=66.00  ← lowest GOR, highest priority
A-4 GOR=900  max=65.5 indep=63.99 joint=65.50
A-5 GOR=1350 max=65.5 indep=63.99 joint=59.67  ← marginal well (highest GOR, throttled)
A-6 GOR=750  max=66.0 indep=64.48 joint=66.00

Independent baseline: 9,238 bbl/d @ $78.9M / 90d
Joint LP-optimal:     9,316 bbl/d @ $79.2M / 90d
Uplift: +77.9 bbl/d / +$369,225 over 90d ✅ ceiling respected at 7.9999 MMscfd
```

**LP algorithm:** Sort wells by GOR ascending → allocate gas ceiling to lowest-GOR wells first → marginal well fills remaining budget. Analytically optimal for linear objective (maximize Σ oil subject to gas budget).

**Vizier ran live (GAUSSIAN_PROCESS_BANDIT):** 15 trials, 6D parameter space. Vizier's best trial (T3, uniform ~60Hz) was sub-optimal vs LP analytical — expected with 15 trials in 6D. H3-C UI should show BOTH: Vizier exploration (existing pareto chart) + LP analytical field allocation (new panel).

**New response keys for H3-C UI:**
- `wells[i].{id, name, gor_scf_bbl, rul_base_days, max_hz, independent_hz, joint_hz}`
- `independent_baseline.{hz_setpoints[], total_oil_bbl_d, total_gas_mmscfd, total_cash_flow}`
- `joint_optimal.{hz_setpoints[], total_oil_bbl_d, total_gas_mmscfd, total_cash_flow, uplift_bbl_d, uplift_cash_90d}`
- `constraint_stack.{gas_ceiling.{binding:true, value_mmscfd, scada_mmscfd, indep_mmscfd, joint_mmscfd}, thermal_derated, rul_horizon}`

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Briefing — all 6 panels | ✅ DEPLOYED | Session AQ |
| H1 Scenario replay | ✅ DEPLOYED | Session AP |
| H2 backend endpoint | ✅ DEPLOYED | `sha256:cd46caa8` — session AX |
| H2 Briefing panels (3 panels) | ✅ DEPLOYED | `7673efd` — session AY |
| H2 Scenario Replay UI | ✅ DEPLOYED | `866522f` — session BA |
| Sprint F0: "GDC Operations Intelligence" header | ✅ DEPLOYED | `e85f9b9`+`81c3a5b` — session BB |
| Sprint H3-A: thermal model 4-feature fix | ✅ DEPLOYED | `81c3a5b` — session BB |
| **Sprint H3-B: N-well field Vizier optimization** | **✅ DEPLOYED** | **`84e1b5f` — session BC · 6-well LP-optimal, gas ceiling 8.0 MMscfd** |
| H3 UI — 3-panel briefing + field display | ❌ NOT BUILT | Sprint H3-C (wireframe sign-off first) |
| DEMO_MASTER §6 field-level spec | ❌ NOT UPDATED | Sprint H3-D |
| H1 static seed date-templating | ⚠️ NEEDS FIX | Sprint P4 — hardcoded 2025 dates |
| **esp_thermal.ubj — XGBoost version mismatch** | **✅ RESOLVED** | **Session BB: physics polynomial used directly** |
| H2-C1 flush+reseal ~$8k–$15k | ⚠️ 🔴 NEEDS-EXPERT | Soft range only — labeled as estimate on screen |
| SPE papers cited (SPE-174536, SPE-170776) | ⚠️ UNVERIFIED | Not yet pulled — do not cite as hard facts |
| 51% ESP failures = operational factors | ✅ ATTRIBUTED | 2014 SPE Artificial Lift Conference survey (Gemini-verified) |
| MCP gdc-second-opinion | ✅ WORKING | gemini-2.5-flash, Vertex AI ADC, gdc-pm-v2 |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No `browser_action` (SSH remote, no browser)
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,900 lines · `index.html` ~3,200 lines · `app.js` ~2,300 lines — grep first, targeted reads only
- **Wireframes → sign-off → HTML** (Sprint H3-C briefing panels need sign-off per panel spec in DEMO_MASTER)
- **No build/push/deploy without user walkthrough and verification**
- Gemini tools (gemini_search, gemini_second_opinion) on autoApprove — use freely for fact-checking
- **Ask inline questions — no option lists** (ask_followup_question options array causes display issues)
- **Keep text before tool calls short**
- **Deploy sequence:** `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status` (Artifact Registry, NOT gcr.io)
