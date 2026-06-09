# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 9, 2026 (Session S — Physics Audit + Surveillance Tab, code+deploy)
**git head:** `327d85d` (4 commits this session)
**fault-trigger-ui image:** `sha256:d0fc6935` (Session S — Surveillance tab + corrected physics)
**inference-api image:** `sha256:357c78da` (Session S — retrained esp_classifier.ubj)
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
- field_intel: ~2–5 · rag_documents: 18

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Session T — Next Implementation Task

### PRIORITY 1: H1 Frontend ISA-101 Redesign (`index.html`)

**All 5 sub-tasks are a single batched `replace_in_file` pass on index.html.**
Read DEMO_MASTER.md §4.6 carefully before writing any code.

**3a. Move timeline scrubber inside Left Column (above `#h1-replay-chart`):**
- Remove from its current position (below the banner, full-width)
- Insert inside the Left Column div, immediately above `#h1-replay-chart`
- Set `padding-left: 48px; padding-right: 12px` (matches Plotly `margin: {l:48, r:12}`)
- This makes the scrubber auto-resize with the left column at any width

**3b. Add `ⓘ Physics & Logic` info drawer button:**
- In the Discern tab header bar, next to `↺ New Scenario`
- Toggles a collapsible info panel explaining: ESP Unloading Physics, SCADA 4-rule trip logic, XGBoost pre-threshold multivariate detection, L3 RAG context fusion

**3c. ISA-101 Decision Console full redesign (replaces current layout):**
See DEMO_MASTER.md §4.6 for exact 3-zone layout spec.

SCADA View:
- Pre-alarm: quiet slate, single monospace line `WELL A-3 — SURVEILLANCE ACTIVE · ALL SENSORS WITHIN LIMITS`
- Post-alarm: amber banner + 2×2 tag grid (PIP/Amps/Temp/Vib, monospace, no diagnosis)
- Two equal action cards (ISA-101 slate outline): Card A VFD Speed-Down, Card B Emergency Shut-In (both functional)
- **SVG wellbore: completely hidden on SCADA view** (zero width, no placeholder)

GDC Advisor View — Three-Zone Layout:
- Zone 1: Standalone Assessment Headline (full-width, monochrome border, pre-detection scanning placeholder)
- Zone 2: Left 60% = two equal action cards + Right 40% = vertical document stack (3 cards revealed sequentially)
- Zone 3: SVG wellbore strip (far right 12%, GDC only, scrubber-reactive)

**Remove Fleet Scale Card** from Discern tab entirely (Surveillance tab covers this).

**3d. SVG wellbore scrubber binding:**
- Gas bubbles: opacity bound to `Math.max(0, h1CursorIdx - h1ReplayData.gdc_detect_idx) / (h1ReplayData.n - h1ReplayData.gdc_detect_idx)` — zero before detection
- Sand particles: same binding for fluid_drawdown
- Hidden entirely on SCADA view tab

**3e. Chart x-axis: after 120-step replay, transition to rolling 30-min live window**

**After all 5 sub-tasks:** rebuild + push fault-trigger-ui, kubectl rollout restart, run smoke test.

---

### PRIORITY 2: Deploy and Verify

```bash
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest gke/fault-trigger-ui/
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm

# Smoke test
cd ~/gdc-pm && node scripts/ui_smoke.mjs
# Expected: ✅ SMOKE TEST PASSED (12/12 assertions, 0 console errors)
```

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Scenario Replay physics | ✅ FIXED Session S | psi_final 529–601, temp 254–257°F, vib 4.9–5.1, lead 7.0 min |
| Smart SCADA alarm logic | ✅ FIXED Session S | 3-rule ISA-18.2/API RP 11S — fires step 79/120 (~T=20min) |
| `esp_health.ubj` / `esp_classifier.ubj` | ✅ FIXED Session S | RMSE=0.00179, gas_lock P=0.995, all gates pass |
| Surveillance tab | ✅ NEW Session S | First tab, static content, opens by default, smoke test 12/12 |
| SCADA tab shows GDC health header | ⚠ INTEGRITY VIOLATION | GDC-only elements (hs=0.6953, XGBoost threshold) visible on SCADA view. Fix in Phase 3c. |
| SVG wellbore animations | ⚠ FIRE ONCE, STAY | Fire on `h1RagRevealed = true` and stay indefinitely. Fix in Phase 3d. |
| Scrubber vs chart misalignment | ⚠ NOT IN LEFT COLUMN | Scrubber is outside the resizable left column. Fix in Phase 3a. |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — use `node scripts/ui_smoke.mjs` instead
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
- Gas Lock and Fluid Drawdown have IDENTICAL sensor trajectories — this is the H1 premise
