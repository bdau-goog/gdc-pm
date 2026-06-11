# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 11, 2026 (Session AY/AZ planning — framing locked + H3 field pivot decided)
**git head:** `b38d334` (docs: session-ay wrap)
**fault-trigger-ui image:** `sha256:de369a364855624d78d499c0d9373024d738e0ce1508c44fbd19cb0d6619f4f9`
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

**Actual at session-AY/AZ close:** 6 pods Running · ollama=0 · ollama_online=False · field_intel=11 · rag_docs=18 ✅

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

## STEP 3: Strategic Context — Decisions Locked in Session AY/AZ

**READ THIS BEFORE TOUCHING ANY CODE.** Two significant decisions were made that affect all three tabs:

### A. Framing: "Predictive Maintenance" → "Operations Advisor"
- "GDC Predictive Maintenance" on `index.html:18` is wrong — H1 and H2 are real-time operations decisions (not long-horizon PdM). The banner label must change.
- H3 *does* own a predictive sub-claim: **"predictive optimization under a safety constraint"** — predicting where the thermal failure boundary is *as a function of control setpoints*, not passive trend extrapolation. This is distinct from APM-style PdM and doesn't compete with §3 concessions.
- Final header wording: **confirm with user** ("Operations Advisor" / "Operations Intelligence" / other) before writing code.

### B. H3 — field-level joint optimization (new scope)
Today H3 optimizes ONE pump. Session AZ decision: go field-level. Rationale:
- Discern (one well) → Classify (one well) → **Optimize (the field)** — deliberate zoom-out that makes the §3 scale-gap literal.
- Red-team verdict (Gemini MCP, session AY): **SURVIVES** — gas ceiling is real/binding (RRC + contracts), well heterogeneity (GOR / thermal headroom) makes joint > independent, 20-yr production engineer "unequivocally recognizes this as a real, high-value problem."

**Gas handling explained** (for briefing Panel 1 copy): Every ESP barrel lifts associated natural gas. That gas must go into gathering → compression → sales. The gathering/compression system has a fixed throughput ceiling. When the field's total gas rate exceeds it, the operator must flare (penalized) or **curtail oil** — even though the wells *could* produce more. This is the Permian's most common real production bottleneck (Waha negative gas prices are the symptom). So: gas handling is the shared constraint that most often forces operators to leave oil in the ground.

**Red-team report at:** `/tmp/mcp-results/second_opinion_1781181758.txt`

---

## STEP 4: Next Implementation Tasks (in order)

### SPRINT F0 — Framing relabel (fast win, do first, ~30 min)
1. **Confirm** final header wording with user before writing a single line of code.
2. `index.html:18` — "GDC Predictive Maintenance" → agreed wording.
3. Copy audit: grep `predict.*maintenance|maintenance.*predict` across index.html + app.js for any stragglers.
4. Update DEMO_MASTER §1 product statement + VIDEO_SCRIPT/DEMO_STORY narration to match.

### SPRINT P1 — H2 Scenario Replay UI (pre-approved DEMO_MASTER §5)
The existing H2 replay UI renders the **old slug-flow scenario** (stale wording). Reskin to workover-fluid-incompatibility:
- **Dual-sensor Plotly chart:** `efficiency[]` (declining, amber) + `vib[]` (rising, purple). X-axis: time (weeks, 0–8). GDC detect▲ marker (amber) / SCADA HI▲ marker (red). Already correctly rendered in `_renderH2ReplayChart()` — just update labels.
- **SCADA View** Zone 1 verdict: "Mechanical degradation — investigation recommended" (bearing wear — APM's correct-symptom-wrong-root-cause call). Action cards: (A) Request Pump Pull / (B) Continue Monitoring.
- **GDC Advisor View** Zone 1: "Elastomer seal degradation — NOT bearing wear." Zone 2 left: flush+reseal ~$8k–$15k est. ⚠ vs pump-pull ~$70k–$100k averted. Zone 2 right: **5 staggered doc reveals** — Workover completion report [DYNAMIC] fires with RAG → OEM matrix (+2s) → Prior pull record (+3.5s) → Shift note [DYNAMIC] (+5s) → Well history (+6.5s). Five docs total; two Gemma-generated per run.
- **Backend:** `/api/h2/scenario-replay` already returns correct payload. Endpoint is live, no backend changes needed.
- **Gate:** No new wireframe sign-off needed — fully specified in DEMO_MASTER §5.

### SPRINT H3 — Field-level Optimize (replaces old "H3 briefing 3 panels")
This is the biggest remaining sprint. Four sub-tasks, in order:

**H3-A: Retrain `esp_thermal.ubj` → multi-feature** ← REQUIRED (red-team FAIL)
- Current model: `temp_f = f(hz)` only — **physically unsound** (winding temp depends on motor current, fluid temp, load, cooling — not just speed). This was a pre-existing integrity hole now surfaced by red-team.
- New model: `temp_f = f(hz, motor_amps, intake_fluid_temp, water_cut_pct)`.
- Training data: generate from FAULT_PROFILES physics with per-variable Gaussian noise (same approach as H1 classifier retrain, Session S/W).
- Verify: max prediction delta vs physics polynomial ≤ ±2°F across operating range; confirm in `scripts/retrain_edge_models.py` or new dedicated script.

**H3-B: Rework `vizier_optimize()` → N-well field**
- Input params: `oil_price`, `horizon_days`, **`n_wells` (default 6, Pad Alpha)**, `gas_ceiling_mmscfd` (default 8.0 — confirm with user as realistic for Pad Alpha).
- Vizier search space: per-well `hz_i` ∈ [45, 65] for i=1..N.
- Constraints: (a) Σ `associated_gas_i(hz_i)` ≤ `gas_ceiling`; (b) per-well `rul_days_i(hz_i)` ≥ `horizon_days`.
- `associated_gas_i = oil_rate_i × GOR_i` where `GOR_i` is **per-well randomized** in [400–1400 scf/bbl] at startup (reflecting real Permian well heterogeneity — this is what makes joint > independent).
- Objective: maximize Σ `net_cash_flow_i`.
- Baseline comparison: **independent per-pump optimization** (N separate single-Hz Vizier runs) — show the joint uplift explicitly so the claim is demonstrated, not asserted.

**H3-C: H3 UI**
- **Panel 1** (The Opportunity): oil-price spike scenario; field overview (6 wells, Pad Alpha); constraint-stack panel:
  ```
  ▸ Gas handling / compression takeaway   ← BINDING ✦  (bold amber)
       ~8.0 MMscf/d ceiling · gathering + flaring limit
  ▸ Produced-water / SWD capacity          headroom     (muted)
  ▸ Electrical bus / transformer thermal   headroom     (muted)
  ```
- **Panel 2** (The Tradeoff): faster Hz → more oil → more gas → hits ceiling; per-well thermal RUL tradeoff; why you can't just run every well flat-out.
- **Panel 3** (The Optimization): GDC finds the **field-wide setpoint vector** (each well a different Hz), maximizing total $ subject to gas + thermal constraints; "joint vs independent" uplift card with a live number; edge safety constraint holds when WAN drops.
- Replace the current toggle "ⓘ Physics & Logic" panel (~line 2011 of index.html) with the proper 3-panel briefing per §4.5 chrome spec.

**H3-D: DEMO_MASTER §6 rewrite**
- Scrap current §6 (single-pump, single-constraint, "honest hybrid NOT air-gap" language).
- Write field-level spec with: (a) gas-handling scenario + correct causal chain; (b) multi-feature thermal model physics; (c) constraint-stack panel design; (d) 4-test survival table (mirrors H2 §5); (e) joint-vs-independent framing.

### SPRINT P3 — H3 copy fix (tiny)
`index.html`: "no cloud dependency" → "no public-cloud dependency for the decision." (1–2 lines.)

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
| H2 Scenario replay UI | ❌ NOT BUILT | SPRINT P1 — existing UI has old slug-flow copy |
| H3 field-level optimization | ❌ NOT BUILT | New scope — replaces single-pump H3 |
| H3 Briefing panels | ❌ NOT BUILT | Part of SPRINT H3-C |
| H3 copy — "no cloud dependency" | ⚠️ NEEDS FIX | SPRINT P3 |
| H1 static seed date-templating | ⚠️ NEEDS FIX | SPRINT P4 — hardcoded 2025 dates |
| **esp_thermal.ubj — single-feature (Hz only)** | **❌ INTEGRITY HOLE** | **SPRINT H3-A — must retrain multi-feature (Hz, amps, fluid_temp, water_cut). Red-team FAIL. Current model is physically unsound per API RP 11S3/S5, IEEE 112.** |
| Header "GDC Predictive Maintenance" | ⚠️ WRONG FRAMING | SPRINT F0 — confirm new wording with user before touching code |
| Ollama GPU pod | ✅ AT 0 | GPU-discipline rule in effect. False is correct. |
| MCP gdc-second-opinion | ✅ WORKING | gemini-2.5-flash, Vertex AI ADC, gdc-pm-v2 |
| H2-C1 flush+reseal ~$8k–$15k | ⚠️ 🔴 NEEDS-EXPERT | Soft range only — labeled as estimate on screen |
| SPE papers cited (SPE-174536, SPE-170776) | ⚠️ UNVERIFIED | Not yet pulled and confirmed — do not cite as hard facts |
| 51% ESP failures = operational factors | ✅ ATTRIBUTED | 2014 SPE Artificial Lift Conference survey (Gemini-verified) |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No `browser_action` (SSH remote, no browser)
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,800 lines · `index.html` ~3,200 lines · `app.js` ~2,300 lines — grep first, targeted reads only
- **Wireframes → sign-off → HTML** (H2 replay pre-approved; H3 briefing panels need sign-off per panel spec above)
- **No build/push/deploy without user walkthrough and verification**
- Gemini tools (gemini_search, gemini_second_opinion) on autoApprove — use freely for fact-checking
- **Ask inline questions — no option lists** (ask_followup_question options array causes display issues)
- **Keep text before tool calls short**
- **Deploy sequence:** `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status` (Artifact Registry, NOT gcr.io)
