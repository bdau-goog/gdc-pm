# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 8, 2026 (Session Q — H1 Discern tab rebuild COMPLETE and deployed)
**git head:** `1fe60f4` (feat(ui): Session Q — 4-sensor chart, SVG wellbore, smart SCADA, A-3 anchor)
**fault-trigger-ui image:** `sha256:a751a83e` (1/1 Running — Session Q, current)
**inference-api image:** `sha256:d1194989` (1/1 Running — unchanged)
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected when healthy:**
- All 8 pods 1/1 Running · ollama replicas: 1
- ollama_online: True · model: gemma4:latest
- field_intel: ~2–3 · rag_documents: 18

**Also verify the scenario-replay endpoint with smart SCADA:**
```bash
curl -s "http://gdc-pm.bdau.io/api/h1/scenario-replay?fault=gas_lock" | python3 -c \
  "import sys,json;d=json.load(sys.stdin);print('n:',d['n'],'gdc:',d['gdc_detect_idx'],'scada:',d['scada_alarm_idx'],'lead:',d['lead_time_minutes'],'rule:',d.get('scada_rule_fired','MISSING')[:40],'model:',d['model_used'])"
# Expected: n: 120, gdc < scada, lead ~21+ min, rule starts with "Rate-of-change", model: esp_health.ubj
```

**Run smoke test after any deploy:**
```bash
cd ~/gdc-pm && node scripts/ui_smoke.mjs
# Expected: ✅ SMOKE TEST PASSED (12/12 assertions, 0 console errors)
```

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Session R — Next Tasks

### H1 Discern tab is COMPLETE (Session Q)

The full Session Q rebuild is deployed and verified:
- `GET /api/h1/scenario-replay` — smart SCADA rate-of-change trip (ISA-18.2 §5.3 / API RP 11S §7.2)
- 4-stack Plotly subplots (PIP/Amps/Temp/Vib) sharing x-axis, single relayout cursor
- Controls (◀◀/▶/▶▶) moved to header far right
- Slider padded l:48/r:12 to align exactly with Plotly plot area margins
- SVG wellbore (vector, reactive fluid column, gas bubbles/sand particles, PUMP/MOTOR/PERFS)
- SCADA alarm banner shows `scada_rule_fired` text from backend
- GDC disambiguation banner replaces lead-time banner as headline
- Greyed/disabled mitigation cards until respective alarm index
- Fleet scalability card (6 ESPs, one model, ISA-18.2/EEMUA-191 sourced)
- `docs/CLAIM_LEDGER.md` created with all H1 rows SURVIVES
- Smoke test: 12/12 assertions, 0 errors ✅

### Potential Session Q refinements (get user feedback first)

1. **Smart SCADA fires very late** — in the current run, `scada_alarm_idx=119` (out of 120), meaning the smart SCADA barely fires at end of the trajectory. This gives a 21+ min lead time which is honest and compelling. The rate-of-change threshold (-35 PSI/min) may be conservative; if the audience asks why SCADA fires so late, the answer is: "the rate alarm requires a sustained 2.5-min ramp, not a single spike — that's the physically correct ISA-18.2 §5.3 design." This is defensible but worth user review.
2. **SVG wellbore sizing** — the SVG is 68×154px. May want to increase if it looks small on the target display.
3. **GDC▲/SCADA▲ tick marks** — currently positioned by % of slider width. With the new l:48/r:12 padding, these should align closely with the chart lines. Verify visually.

### Next major feature: H2 Classify tab

Per DEMO_MASTER §5 — H2 Slug Flow scenario. The current H2 tab still uses the old inject-and-wait model. Same Scenario Replay architecture applies:
- `GET /api/h2/scenario-replay?fault=slug_flow` — precompute 120-step trajectory, run gas-lift classifier
- SCADA sub-tab: Vibration rising, Temp flat — SCADA alarms on vib > 5.0 mm/s
- GDC sub-tab: vib+temp decorrelation → slug flow verdict → $1,500 truck roll vs $150k well pull

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Scenario Replay (Session Q) | ✅ LIVE | SHA sha256:a751a83e. 4-stack chart, SVG wellbore, smart SCADA. |
| Smart SCADA rate-of-change trip | ✅ LIVE | ISA-18.2 §5.3 / API RP 11S §7.2. scada_rule_fired in API response. |
| `model_used: FALLBACK_SYNTHETIC` | ✅ Integrity guard | UI shows banner if model fails — never silent |
| docs/CLAIM_LEDGER.md | ✅ CREATED | All 8 H1 rows SURVIVES |
| H2 inject-and-wait model | ⚠ STILL OLD | H2 tab not yet updated to Scenario Replay |
| Vue template crash | ✅ Fixed | All `<` escaped; smoke test checks for leaks |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — use `node scripts/ui_smoke.mjs` instead
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
- SCADA threshold = smart SCADA rate-of-change (ISA-18.2) + static floor 1020 PSI (API RP 11S §7.2)
