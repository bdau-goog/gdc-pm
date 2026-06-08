# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 8, 2026 (Session P — H1 Scenario Replay COMPLETE and deployed)
**git head:** `fb7b71c` (feat(ui): Session P Step 3 — H1 Discern tab Scenario Replay rewrite)
**fault-trigger-ui image:** `sha256:97033866` (1/1 Running — Session P, current)
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

**Also verify the new endpoint is live:**
```bash
curl -s "http://gdc-pm.bdau.io/api/h1/scenario-replay?fault=gas_lock" | python3 -c \
  "import sys,json;d=json.load(sys.stdin);print('n:',d['n'],'gdc:',d['gdc_detect_idx'],'scada:',d['scada_alarm_idx'],'lead:',d['lead_time_minutes'],'model:',d['model_used'])"
# Expected: n: 120, gdc < scada, lead > 0, model: esp_health.ubj
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

## STEP 3: Session Q — Next Tasks

### H1 Scenario Replay is COMPLETE (Session P)

The full Scenario Replay architecture is deployed and verified:
- `GET /api/h1/scenario-replay` — live (real XGBoost model, gdc < scada, lead time computed)
- Discern tab — `↺ New Scenario` button, Play/Pause/Fast/Reset + scrubber
- SCADA sub-tab gates on `h1CursorIdx >= scada_alarm_idx`
- GDC sub-tab gates on `h1FaultTypeRevealed` (cursor crosses gdc_detect_idx) → 1.5s delay → `h1RagRevealed`
- Smoke test: 12/12 assertions, 0 errors

### What to review first

Open the UI at http://gdc-pm.bdau.io and click the **Discern** tab. It should:
1. Auto-load a scenario (loading spinner → chart appears within ~2s)
2. Show `↺ New Scenario` button in header
3. Show Play/scrub controls with GDC▲ and SCADA▲ markers on scrubber
4. Left: dual-Y chart (PIP blue + Amps green) with amber dashed GDC line + red dashed SCADA line
5. Right: SCADA sub-tab shows "✓ Sensors within limits" (pre-alarm), GDC shows health score
6. Click Play → cursor advances, sensor tiles update, lead-time banner appears after SCADA alarm

### Potential refinements (user feedback needed)

1. **Lead time magnitude** — the current run showed 5.0 min. If this feels small on screen, the trajectory parameters could be tuned. The value is HONEST (real model + real physics). Do not inflate it.
2. **SCADA threshold display** — SCADA view shows "&lt;1,000 PSI" as the alarm threshold. This is correct (see NEXT_SESSION_PROMPT Session P notes on why 800 PSI was wrong). If the audience pushes back, the defence is: "1000 PSI ≈ 15% below nominal 1200 PSI — this is the API RP 11S §7.2 underload setpoint."
3. **GDC hs display** — pre-detect cursor shows raw health score. Consider whether to show it or hide it before the reveal.
4. **New Scenario button placement** — currently top-right in header. May want to also offer it after SCADA alarm fires.

### Next major feature: H2 Classify tab

Per DEMO_MASTER §5 — H2 Slug Flow scenario. The current H2 tab still uses the old inject-and-wait model. Same Scenario Replay architecture applies:
- `GET /api/h2/scenario-replay?fault=slug_flow` — precompute 120-step trajectory, run classifier
- SCADA sub-tab: Vibration rising, Temp flat — SCADA alarms on vib > 5.0 mm/s
- GDC sub-tab: vib+temp decorrelation → slug flow verdict → $1,500 truck roll vs $150k well pull

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Scenario Replay | ✅ LIVE | Session P complete. SHA sha256:97033866. |
| `model_used: FALLBACK_SYNTHETIC` | ✅ Integrity guard | UI shows banner if model fails — never silent |
| Old inject-and-wait / sparklines | ✅ REMOVED | No longer in index.html |
| Vue template crash | ✅ Fixed | All `<` escaped; smoke test checks for leaks |
| H2 inject-and-wait model | ⚠ STILL OLD | H2 tab not yet updated to Scenario Replay |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — use `node scripts/ui_smoke.mjs` instead
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
- SCADA threshold = 1000 PSI (confirmed correct — 800 PSI never fires with current FAULT_PROFILES)
