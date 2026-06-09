# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 9, 2026 (Session U — ISA-101 3-zone Decision Console complete)
**git head:** `c06aaf9` (1 commit this session)
**fault-trigger-ui image:** `sha256:a33a0833` (Session U — 3c+3d Decision Console, cursor-reactive SVG wellbore)
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Five Commands First

```bash
source .env && echo "PROJECT=$GOOGLE_CLOUD_PROJECT KUBECONFIG=$KUBECONFIG"
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents; SELECT COUNT(*) FROM telemetry_events;"
```

**Verification (Command 5 — inference model audit):**
```bash
kubectl exec -n gdc-pm deployment/fault-trigger-ui -- python3 -c "import urllib.request, json; print(list(json.loads(urllib.request.urlopen('http://inference-api:8080/model-info').read().decode())['models'].keys()))"
```

**Expected when healthy:**
- Workspace: `PROJECT=gdc-pm-v2` · `KUBECONFIG=/home/brian/gdc-pm/.kubeconfig`
- All 8 pods 1/1 Running · ollama replicas: 1
- ollama_online: True · model: gemma4:latest
- field_intel: ~2–5 · rag_documents: 18 · telemetry_events: > 0
- inference-api models: `['esp_classifier', 'gas_lift_classifier', 'mud_pump_classifier', 'top_drive_classifier', ...]`

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Session V — Next Implementation Tasks

### ALL H1 STEPS NOW COMPLETE ✅
Steps 3a, 3b, 3c, 3d, and 3e are **DONE and deployed** (Sessions T + U).

### PRIORITY 1: H2 Slug Flow Scenario Replay
Per DEMO_MASTER.md §5: Build the Classify tab H2 scenario replay following the same architecture as H1.

- Backend: `GET /api/h2/scenario-replay?fault=slug_flow` — precompute vibration + temperature trajectory (120 steps), confirm slug flow decorrelation (vib rises, temp FLAT), return discriminator data
- Frontend: Replace the current static H2 Classify tab content with a proper Scenario Replay layout (▶ Play / scrub, dual-sensor chart: vib rising + temp flat, SCADA vs GDC verdict)
- Verdict cards: GDC confirms downhole pump is green (healthy), recommends $1,500 surface truck roll; SCADA path leads to $150k false-positive pump pull

### PRIORITY 2: Deploy and Verify H2
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
| ISA-101 SCADA view redesign | ✅ NEW Session U | Quiet slate pre-alarm, 2×2 tag grid post-alarm, slate cards |
| GDC 3-zone layout (3c) | ✅ NEW Session U | Zone 1 headline, Zone 2 action cards + doc stack, Zone 3 SVG |
| Cursor-reactive SVG wellbore (3d) | ✅ NEW Session U | Bubbles/sand opacity = (cursorIdx - gdc_detect_idx) / (n-1-gdc_detect_idx) |
| Fleet Scale Card | ✅ REMOVED Session U | Surveillance tab handles fleet scale context |
| Document stack (Zone 2 right) | ✅ NEW Session U | 3 doc cards revealed sequentially via h1RagRevealed / h1RagDoc2Shown / h1RagDoc3Shown |
| H2 Classify tab | ⏳ NEXT Session V | Still shows old static content — needs Scenario Replay architecture |

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
- `app.py` ~5,996 lines, `index.html` ~2,389 lines — always grep for line numbers first
