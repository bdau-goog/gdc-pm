# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 11, 2026 (Session BB — Sprint F0 + H3-A thermal integrity fix)
**git head:** `81c3a5b` (fix(h3-thermal): use 4-feature physics polynomial directly)
**fault-trigger-ui image:** `sha256:5e58c06af22ee98fa0ebd7e3342522a4eee0357a816d08bdc961191579d08c4e`
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

**Actual at session-BB close:** 6 pods Running · ollama=0 · ollama_online=False · field_intel=11 · rag_docs=18 ✅

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

### SPRINT H3-B: Rework `vizier_optimize()` → N-well field
- N=6 wells (Pad Alpha), `gas_ceiling_mmscfd=8.0`, per-well randomized `GOR_i ∈ [400–1400 scf/bbl]`
- Constraint: Σ `associated_gas_i` ≤ ceiling; per-well RUL ≥ horizon
- Baseline comparison: independent per-pump optimization → show joint uplift explicitly

### SPRINT H3-C: H3 UI — 3-panel briefing + field optimization display
- Panel 1: oil-price spike + constraint-stack (gas binding, others muted)
- Panel 2: the tradeoff (faster Hz → more gas → hits ceiling)
- Panel 3: field-wide setpoint vector + joint-vs-independent uplift card
- Per §4.5 Briefing Pattern Spec — wireframe sign-off before HTML

### SPRINT H3-D: DEMO_MASTER §6 rewrite (field-level spec)

### SPRINT P3 — H3 copy fix (tiny)
`index.html`: "no cloud dependency" → "no public-cloud dependency for the decision."

### SPRINT P4 — H1 Batch B date-templating (small)
Sonic log / shift note / GOR lab report in `field_intel` have hardcoded 2025 dates. Template to `today − offset`.

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Briefing — all 6 panels | ✅ DEPLOYED | Session AQ |
| H1 Scenario replay | ✅ DEPLOYED | Session AP |
| H2 backend endpoint | ✅ DEPLOYED | `sha256:cd46caa8` — session AX |
| H2 Briefing panels (3 panels) | ✅ DEPLOYED | `7673efd` — session AY |
| H2 "protector fill oil" terminology | ✅ DEPLOYED | `306ef60` |
| Ariel JGP temperature limits | ✅ DEPLOYED | `2d0035a` |
| **H2 Scenario Replay UI** | **✅ DEPLOYED** | **`866522f` — session BA · workover-fluid-incompatibility reskin** |
| **Sprint F0: "GDC Operations Intelligence" header** | **✅ DEPLOYED** | **`e85f9b9`+`81c3a5b` — session BB · index.html line 18** |
| **Sprint H3-A: thermal model 4-feature fix** | **✅ DEPLOYED** | **`81c3a5b` — session BB · 4-feature physics polynomial (API RP 11S3/S5, IEEE 112)** |
| H3 field-level optimization | ❌ NOT BUILT | New scope — Sprint H3-B/C/D |
| H3 Briefing panels | ❌ NOT BUILT | Part of Sprint H3-C (needs wireframe sign-off) |
| H3 copy — "no cloud dependency" | ⚠️ NEEDS FIX | Sprint P3 |
| H1 static seed date-templating | ⚠️ NEEDS FIX | Sprint P4 — hardcoded 2025 dates |
| **esp_thermal.ubj — XGBoost version mismatch** | **✅ RESOLVED** | **Session BB: physics polynomial used directly; esp_thermal.ubj not loaded** |
| Header "GDC Predictive Maintenance" | ✅ FIXED | Session BB Sprint F0 — now "GDC Operations Intelligence" |
| Ollama GPU pod | ✅ AT 0 | GPU-discipline rule in effect. False is correct. |
| MCP gdc-second-opinion | ✅ WORKING | gemini-2.5-flash, Vertex AI ADC, gdc-pm-v2 |
| H2-C1 flush+reseal ~$8k–$15k | ⚠️ 🔴 NEEDS-EXPERT | Soft range only — labeled as estimate on screen |
| SPE papers cited (SPE-174536, SPE-170776) | ⚠️ UNVERIFIED | Not yet pulled — do not cite as hard facts |
| 51% ESP failures = operational factors | ✅ ATTRIBUTED | 2014 SPE Artificial Lift Conference survey (Gemini-verified) |

---

## H3-A Technical Notes (for next session context)

**What was done:** `esp_thermal.ubj` was retrained with 4-feature model (scripts/train_esp_thermal.py, 20k samples, P95=1.726°F). However, the model was trained with XGBoost 3.2.0 locally while the container runs XGBoost 2.0.3 — the `.ubj` format has breaking changes between major versions (confirmed: model loaded but predicted -19.8°F at 50 Hz — unphysical).

**Resolution:** The 4-feature physics polynomial (API RP 11S3/S5, IEEE 112) is now the PRIMARY thermal evaluator (not a fallback):
```
temp_f = intake_temp + 95.0 + 1.5*(hz-45) + 0.9*(amps-65) + 0.12*max(0,hz-58)³ - 0.25*(wc-30)
```
This is MORE defensible than an XGBoost approximation of itself — transparent, physics-grounded, explainable to O&G engineers. Live verification: 50Hz→188°F, 54.6Hz→198°F, 65Hz→261°F ✅

**If ever retraining esp_thermal for container:** update `requirements.txt` to `xgboost>=3.0.0` and rebuild the container, OR train inside the container using `xgboost==2.0.3`.

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No `browser_action` (SSH remote, no browser)
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,800 lines · `index.html` ~3,200 lines · `app.js` ~2,300 lines — grep first, targeted reads only
- **Wireframes → sign-off → HTML** (Sprint H3-C briefing panels need sign-off per panel spec in DEMO_MASTER)
- **No build/push/deploy without user walkthrough and verification**
- Gemini tools (gemini_search, gemini_second_opinion) on autoApprove — use freely for fact-checking
- **Ask inline questions — no option lists** (ask_followup_question options array causes display issues)
- **Keep text before tool calls short**
- **Deploy sequence:** `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status` (Artifact Registry, NOT gcr.io)
