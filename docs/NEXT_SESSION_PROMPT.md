# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 11, 2026 (Session BA — H2 Replay UI deployed)
**git head:** `866522f` (feat(h2-replay): reskin H2 Scenario Replay UI)
**fault-trigger-ui image:** `sha256:a87b424b44cca53d4da6da2fffe837b777b8ccb0daed7aa0e62f624227681e3b`
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

**Actual at session-BA close:** 6 pods Running · ollama=0 · ollama_online=False · field_intel=11 · rag_docs=18 ✅

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

## STEP 3: Strategic Context — What Was Done in Session BA

**H2 Scenario Replay UI (Sprint P1) — DEPLOYED ✅**

The H2 replay UI has been fully reskinned from slug-flow to workover-fluid-incompatibility:
- **app.js:** `h2SlugFlowRevealed` → `h2VerdictRevealed`; doc4/doc5 state+timers added; `_renderH2ReplayChart()` now uses `efficiency[]` (amber) + `vib[]` (purple) on dual y-axis, x-axis "Weeks post-workover"; fixed `scada_hi_idx` → `scada_alarm_idx` field mismatch (was a silent bug).
- **index.html:** Physics & Logic panel → workover-fluid content; alarm banners fixed; SCADA view → bearing-wear framing, pump_pull outcome; GDC Advisor → "ELASTOMER SEAL DEGRADATION — NOT BEARING WEAR", 5 doc reveals (Workover Completion Report → OEM Matrix → Prior Pull Record → Field Tour Note → Well History); SVG wellbore → downhole PROTECTOR seal degrading amber→red; health% display replaces slug_flow_prob%.
- **Smoke test:** `scenario: workover_fluid_incompatibility`, `health_ok: True`, `efficiency[0]: 75.03`, `scada_alarm_idx: 79`, 5 doc_reveals. All correct.

---

## STEP 4: Next Implementation Tasks (in order)

### SPRINT F0 — Framing relabel (fast win, ~30 min)
1. **Confirm** final header wording with user first — "Operations Advisor" / "Operations Intelligence" / other.
2. `index.html:18` — "GDC Predictive Maintenance" → agreed wording.
3. Copy audit: `grep -n "predict.*maintenance\|maintenance.*predict" gke/fault-trigger-ui/index.html gke/fault-trigger-ui/static/app.js`
4. Update DEMO_MASTER §1 product statement + narration docs.

### SPRINT H3 — Field-level Optimize (replaces old single-pump H3)
Four sub-tasks in order:

**H3-A: Retrain `esp_thermal.ubj` → multi-feature** ← REQUIRED INTEGRITY FIX
- Current model: `temp_f = f(hz)` only — physically unsound (winding temp depends on motor current, fluid temp, load, cooling per API RP 11S3/S5, IEEE 112)
- New model: `temp_f = f(hz, motor_amps, intake_fluid_temp, water_cut_pct)`
- Generate training data from FAULT_PROFILES physics with Gaussian noise
- Verify: max prediction delta vs physics polynomial ≤ ±2°F

**H3-B: Rework `vizier_optimize()` → N-well field**
- N=6 wells (Pad Alpha), `gas_ceiling_mmscfd=8.0`, per-well randomized `GOR_i ∈ [400–1400 scf/bbl]`
- Constraint: Σ `associated_gas_i` ≤ ceiling; per-well RUL ≥ horizon
- Baseline comparison: independent per-pump optimization → show joint uplift explicitly

**H3-C: H3 UI — 3-panel briefing + field optimization display**
- Panel 1: oil-price spike + constraint-stack (gas binding, others muted)
- Panel 2: the tradeoff (faster Hz → more gas → hits ceiling)
- Panel 3: field-wide setpoint vector + joint-vs-independent uplift card

**H3-D: DEMO_MASTER §6 rewrite** (field-level spec)

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
| H3 field-level optimization | ❌ NOT BUILT | New scope — Sprint H3 |
| H3 Briefing panels | ❌ NOT BUILT | Part of Sprint H3-C |
| H3 copy — "no cloud dependency" | ⚠️ NEEDS FIX | Sprint P3 |
| H1 static seed date-templating | ⚠️ NEEDS FIX | Sprint P4 — hardcoded 2025 dates |
| **esp_thermal.ubj — single-feature (Hz only)** | **❌ INTEGRITY HOLE** | **Sprint H3-A — must retrain multi-feature. Red-team FAIL.** |
| Header "GDC Predictive Maintenance" | ⚠️ WRONG FRAMING | Sprint F0 — confirm new wording with user before touching code |
| Ollama GPU pod | ✅ AT 0 | GPU-discipline rule in effect. False is correct. |
| MCP gdc-second-opinion | ✅ WORKING | gemini-2.5-flash, Vertex AI ADC, gdc-pm-v2 |
| H2-C1 flush+reseal ~$8k–$15k | ⚠️ 🔴 NEEDS-EXPERT | Soft range only — labeled as estimate on screen |
| SPE papers cited (SPE-174536, SPE-170776) | ⚠️ UNVERIFIED | Not yet pulled — do not cite as hard facts |
| 51% ESP failures = operational factors | ✅ ATTRIBUTED | 2014 SPE Artificial Lift Conference survey (Gemini-verified) |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No `browser_action` (SSH remote, no browser)
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,800 lines · `index.html` ~3,200 lines · `app.js` ~2,300 lines — grep first, targeted reads only
- **Wireframes → sign-off → HTML** (Sprint H3 briefing panels need sign-off per panel spec in DEMO_MASTER)
- **No build/push/deploy without user walkthrough and verification**
- Gemini tools (gemini_search, gemini_second_opinion) on autoApprove — use freely for fact-checking
- **Ask inline questions — no option lists** (ask_followup_question options array causes display issues)
- **Keep text before tool calls short**
- **Deploy sequence:** `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status` (Artifact Registry, NOT gcr.io)
