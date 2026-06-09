# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 9, 2026 (Session T — ISA-101 H1 partial redesign)
**git head:** `6a8b328` (1 commit this session)
**fault-trigger-ui image:** `sha256:45bc0846` (Session T — scrubber inside left col, physics panel, rolling x-axis)
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

## STEP 3: Session U — Next Implementation Task

### PRIORITY 1: H1 ISA-101 Decision Console Redesign (3c + 3d)

Steps 3a, 3b, and 3e are **DONE and deployed** (Session T). These remain:

**3c. Full ISA-101 Decision Console redesign — single batched `replace_in_file` on index.html.**
Read DEMO_MASTER.md §4.6 carefully. The current file still has the OLD layout:
- SVG wellbore at top of Decision Console (before the sub-tab bar)
- SCADA View: shows 2-sensor green grid pre-alarm + 2-card amber cards post-alarm (OLD, not ISA-101)
- GDC Advisor View: flat single-column layout (OLD, not 3-zone)

Target redesign (from DEMO_MASTER.md §4.6):

SCADA View:
- Pre-alarm: quiet slate, single monospace line `WELL A-3 — SURVEILLANCE ACTIVE · ALL SENSORS WITHIN LIMITS`
- Post-alarm: amber banner + 2×2 tag grid (PIP/Amps/Temp/Vib, monospace, no diagnosis)
- Two equal action cards (ISA-101 slate outline, not amber): Card A VFD Speed-Down, Card B Emergency Shut-In
- **SVG wellbore: completely hidden on SCADA view** (zero width, no placeholder)

GDC Advisor View — Three-Zone Layout:
- Zone 1: Standalone Assessment Headline (full-width, monochrome border, pre-detection scanning placeholder)
- Zone 2: Left 60% = two equal action cards + Right 40% = vertical document stack (3 cards revealed sequentially)
  - Doc 2 (`h1RagDoc2Shown`) and Doc 3 (`h1RagDoc3Shown`) state vars already wired in app.js ✅
- Zone 3: SVG wellbore strip (far right 12%, GDC only, full height)

**Remove Fleet Scale Card** from Discern tab entirely (Surveillance tab covers this).

**3d. SVG wellbore scrubber binding** (goes into the new Zone 3 SVG):
- Gas bubbles: opacity bound to `Math.max(0, h1CursorIdx - h1ReplayData.gdc_detect_idx) / (h1ReplayData.n - 1 - h1ReplayData.gdc_detect_idx)` — zero before detection
- Sand particles: same binding
- Already wired in app.js state ✅; implement in the Zone 3 SVG HTML

**After 3c+3d:** rebuild + push fault-trigger-ui, kubectl rollout restart, run smoke test.

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
| H1 Scenario Replay physics | ✅ FIXED Session S | psi_final 483–529 PSI, temp 254°F, vib 6.1–6.4, lead 7.0 min |
| Smart SCADA alarm logic | ✅ FIXED Session S | 3-rule ISA-18.2/API RP 11S — fires step 79/120 (~T=20min) |
| `esp_health.ubj` / `esp_classifier.ubj` | ✅ FIXED Session S | RMSE=0.00179, gas_lock P=0.995, all gates pass |
| Surveillance tab | ✅ NEW Session S | First tab, static content, opens by default |
| Scrubber inside Left Column | ✅ FIXED Session T | padding-left:48px aligns with Plotly margin.l:48 |
| ⓘ Physics & Logic button/panel | ✅ NEW Session T | Uses existing `.physics-panel` CSS; 4-section content |
| Rolling 30-min x-axis | ✅ NEW Session T | `xMax > 30 ? [xMax-30, xMax] : [0, max(30, xMax)]` |
| Doc reveal timers | ✅ NEW Session T | h1RagDoc2Shown (+2s), h1RagDoc3Shown (+3.5s) wired in app.js |
| SCADA tab shows GDC health header | ⚠ INTEGRITY VIOLATION | GDC-only elements visible on SCADA view. Fix in 3c. |
| SVG wellbore animations | ⚠ FIRE ONCE, STAY | Bound to `h1RagRevealed` (binary). Fix in 3d (cursor-reactive). |
| Old SVG wellbore still in Decision Console | ⚠ OLD LAYOUT | Still at top of right column. Moves to Zone 3 in 3c. |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — use `node scripts/ui_smoke.mjs` instead
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
- Gas Lock and Fluid Drawdown have IDENTICAL sensor trajectories — this is the H1 premise
- Physics panel `<` chars in text content: safe only as `< ` (space after) — never `<digit`
