# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 10, 2026 (Session AK — wrap; next task: Panel 2+3 scrubber rebuild)
**git head:** `f226a46` (docs(handoff): Session AJ)
**fault-trigger-ui image:** `sha256:471fb64422f56fce00719dfb255aa694f03b1b45d60e904c9cc1a48b696fef21` (Session AJ)
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

**Expected when healthy:**
- All 8 pods 1/1 Running · ollama replicas: 1
- ollama_online: True · model: gemma4:latest
- field_intel: 5 · rag_documents: 18 · telemetry_events: > 1,000,000

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Next Task — Panel 2 + Panel 3 Scrubber Rebuild

### Context (from Session AK review)
User reviewed all 6 H1 Briefing panels at proper zoom. **Panels 1, 4, 5, 6 are ship-ready — do not touch them.** Panels 2 and 3 need a scrubber-control rebuild.

### Files to edit (three files, two batched calls maximum)
- `gke/fault-trigger-ui/static/app.js` — add `h1P2Scrub` / `h1P3Scrub` state
- `gke/fault-trigger-ui/static/styles.css` — remove infinite loops, add transition classes
- `gke/fault-trigger-ui/index.html` — Panel 2 + Panel 3 markup only (BATCHED — both panels in ONE replace_in_file call)

**Token discipline:** `index.html` is ~3,200 lines (~150K token return per edit). Batch ALL index.html changes into ONE `replace_in_file` call. Read with `grep -n` line bounds only.

---

### Panel 2 Spec — "What is an Unloading Event?"

**Control:** Per-panel scrubber slider `h1P2Scrub` (integer 0→100). Default 0. Reset to 0 when panel is entered (watch `h1BriefingPanel`).

**Gauge orientation: SHORT bar = worse / lower value. LEFT edge = zero/worst. RIGHT edge = healthy max.**

**4 gauges — all start GREEN at scrub=0:**

| Sensor | scrub=0 (nominal) | scrub=100 (fault) | Color transition |
|---|---|---|---|
| PIP | ~90% width · 1,245 PSI | ~30% width · 850 PSI | green → amber |
| AMPS | ~90% width · 68.2 A | ~20% width · 28 A | green → amber |
| WINDING TEMP | ~70% width · 197°F | stays 70% · 197°F | stays green |
| VIB | ~60% width · 1.4 mm/s | stays 60% · 1.4 mm/s | stays green |

Width interpolation (Vue computed or inline :style):
```js
pipWidth: (90 - 60 * this.h1P2Scrub / 100).toFixed(1) + '%'
// TEMP and VIB use fixed width, no binding
```

**Implementation approach:** Use CSS `transition: width 0.4s ease, background-color 0.3s ease` on the bar div instead of `@keyframes`. Class toggles:
- `h1-bar-nominal` → green (rgba(74,222,128,0.7))
- `h1-bar-fault` → amber (rgba(251,191,36,0.7))
- Class binding: `:class="{h1-bar-fault: h1P2Scrub > 50}"` (threshold for amber flip)

**Remove from styles.css:**
- `@keyframes h1-brief-decline` (line 1041)
- `.h1-brief-decline-bar` (line 1042)

**The diagnostic story is told with one scrub:** Two gauges go amber and shrink. Two stay green and flat. That IS the Panel 2 message without any narration.

---

### Panel 3 Spec — "One Signature, Two Causes"

**Control:** Scrubber `h1P3Scrub` (0→100). Default 0. Same reset logic.

**Wellbore SVG size fix:** The SVGs are constrained to `max-height:148px` inside a `max-height:148px` container — that's why they're postage-stamp size. Fix: change the flex container to `flex:1;min-height:0` and the SVGs to `width:auto;height:100%;max-height:280px`. This roughly doubles their visible size.

**Animation binding:**
- Gas bubbles (left wellbore): `opacity` bound to `h1P3Scrub / 100`. Speed: scrub-driven, not time-driven. Remove `.h1-wb-bubble` infinite `h1-bubble-rise` loop (styles.css:979-980 reference); replace with opacity-only CSS transition.
- Fluid drain (right wellbore): SVG fluid column `height` (or `scaleY`) bound to `1 - 0.85 * h1P3Scrub / 100`. At scrub=0 → full column. At scrub=100 → 15% height. Remove `.h1-p3-fluid-drain` infinite loop (styles.css:1043-1044).

**Bottom "SAME SENSOR OUTPUT" strip:** Apply the same Panel 2 scrubber to these bars (reuse `h1P3Scrub`). Both PIP (blue) and AMPS (green) start full-width green at 0 and recede to ~30% at 100. Orientation: short=worse. This makes the caption *"the live decline looks the same"* visually accurate.

**Remove from styles.css:**
- `@keyframes h1-p3-drain` (line 1043)  
- `.h1-p3-fluid-drain` (line 1044)
- `@keyframes h1-bubble-rise` (line 980) — only if not used elsewhere (check grep first)

---

### Deploy pattern (mandatory)
```bash
cd gke/fault-trigger-ui
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest . 2>&1 | tail -3
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest 2>&1 | tail -3
# capture sha256 from push output, then:
kubectl set image deployment/fault-trigger-ui -n gdc-pm \
  fault-trigger-ui=us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui@sha256:<digest>
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm --timeout=120s
```
**Do NOT use `kubectl rollout restart` — node cache will serve the old image.**

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| Financial Justification modal raw {{ }} | ✅ FIXED Session AJ | 2 stray </div> in arch overview pane; div balance net 0 |
| Panel 2 animated bars (infinite loop) | ⚠️ OPEN | Replace with scrubber (h1P2Scrub) per spec above |
| Panel 3 wellbore SVG size | ⚠️ OPEN | max-height:148px → flex fill; target ~280px |
| Panel 3 infinite bubble/drain loops | ⚠️ OPEN | Replace with scrubber-driven opacity/scaleY |
| STATE-vs-CONTEXT premise | ✅ LOCKED | Claim Ledger PREMISE row |
| SPE-174536 citation | ⚠️ UNVERIFIED | Using SPE-170776; 4.2 ft/s = representative |
| Panels 1, 4, 5, 6 | ✅ SHIP-READY | User approved — do NOT touch |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — use `node scripts/ui_smoke.mjs` or `curl`
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- **Deploy with explicit digest** — `kubectl rollout restart` with `:latest` does NOT pull from registry
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,400 lines, `index.html` ~3,210 lines, `app.js` ~2,300 lines — grep for line numbers first
- H2 uses inference-api (not local esp_classifier.bst)
- Sprint 3 (H2 Briefing) is deferred until Panel 2+3 are fixed
