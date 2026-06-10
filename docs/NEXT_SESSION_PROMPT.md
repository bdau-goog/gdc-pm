# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 10, 2026 (Session AQ → tonight's sprint series)
**git head:** `5637c1a` (docs: Session AQ handoff)
**fault-trigger-ui image:** `sha256:2fd95932a9b8ae9ca0eb6c961cf9a031b264a97ad69705fb8197a05999414a9a` (Session AQ)
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Five Commands First

```bash
source .env && echo "PROJECT=$GOOGLE_CLOUD_PROJECT KUBECONFIG=$KUBECONFIG"
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected when healthy:**
- All 8 pods 1/1 Running · ollama replicas: 1
- ollama_online: True · model: gemma4:latest
- field_intel: 5-6 · rag_documents: 18

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: TONIGHT'S SPRINT SERIES — Target: Video-Ready by Morning

**Goal:** H2 and H3 get the same briefing-panel treatment as H1. Then a full video script + Veo concepts. Each sprint: wireframes → user sign-off → one batched `replace_in_file` → deploy → verify.

**Current state:**
- H1 Discern: ✅ 6-panel briefing + scenario replay (fully shipped)
- H2 Classify: ❌ NO briefing panels — jumps straight to scenario replay
- H3 Optimize: ❌ NO briefing panels — jumps straight to Vizier sliders
- Video script: ❌ not written
- Veo intros: ❌ not written

**Files affected tonight:**
- `index.html` (~3,200 lines) — H2 briefing + H3 briefing — ONE call per sprint
- `static/app.js` (~2,300 lines) — add `h2BriefingMode`, `h2BriefingPanel`, `h2P2Scrub`, `h3BriefingMode`, `h3BriefingPanel` — ONE call per sprint
- `docs/VIDEO_SCRIPT.md` — new file
- Build → push → deploy after each sprint

---

## SPRINT 3 — H2 Briefing (3 Panels) ← START HERE

**Architecture:** identical to H1 — `h2BriefingMode: true` + `h2BriefingPanel: 1` in app.js; `v-if="h2BriefingMode"` container before `<template v-else>` wrapper around existing H2 scenario. Reuse all H1 briefing CSS (`.h1-p4-fadein`, `.h1-p4-ctx-card`, `.h1-p5-cell`, `.h1-p6-row`).

**app.js additions (add alongside h1BriefingMode in data()):**
```js
h2BriefingMode: true,
h2BriefingPanel: 1,
h2P2Scrub: 0,        // Panel 2 scrubber: 0=nominal · 100=alarm
```

**H2 header bar change:** Add `← Briefing` button (same as H1, triggers `h2BriefingMode=true`).

### Panel 1 of 3 — What is Slug Flow?
```
Tag:   Panel 1 of 3 — The Equipment
Title: What is Slug Flow?
Sub:   Why a surface flowline problem shows up as a downhole alarm

LEFT column (explanation):
  Context callout (blue):
    "The RTOC operator watches vibration, temperature, PIP, and Amps
     on this well. The pump is 9,800 ft down. The problem is on surface."

  Info box (WELL ESP-ALPHA-3 · PAD ALPHA):
    Formation    | Mature Permian · moderate GLR
    Pump         | ESP · 52 Hz · healthy
    Sensor string| Intake PDG — same 4 sensors as the Discern well
    Surface      | High GLR → gas+liquid slugs cycling in flowline
    Mechanism    | Slug impacts wellhead → mechanical shock → tubing → pump intake

RIGHT column (surface SVG animation):
  Horizontal flowline with animated amber slug pulses (CSS, left→right)
  Wellhead below
  Pump & motor (both GREEN ✓)
  Sensor readouts (nominal green): VIB 1.1 mm/s · TEMP 198°F · PIP 1,220 PSI · AMPS 67 A
```

### Panel 2 of 3 — Why It Looks Like a Failing Pump
```
Tag:   Panel 2 of 3 — The Hook
Title: Why It Looks Like a Failing Pump
Sub:   Same SCADA alarm. Very different cause.

Scrubber: 0=nominal · 100=alarm (h2P2Scrub)

2×2 sensor tiles (scrubber-driven):
  VIB    | RISING ↑ → goes AMBER · "4.2 mm/s — ISA-18.2 HI ALARM"
  TEMP   | FLAT → stays GREEN  · "198°F — cooling intact"
  PIP    | SLIGHTLY declining → slate · "hydraulic loading at intake"
  AMPS   | SLIGHTLY declining → slate · "cyclic load on impeller"

Key insight callout (blue):
  "Vibration rises. Temperature stays flat.
   A bearing failure or pump wear raises BOTH.
   This pattern has one explanation: the fault is not at the motor."
```

### Panel 3 of 3 — STATE vs. CONTEXT (Exoneration)
```
Tag:   Panel 3 of 3 — The Decision
Title: Do NOT Pull. It's a $1,500 Fix.
Sub:   GDC reads three documents. SCADA sees one alarm.

TWO-COLUMN layout (reuse H1 P5 card style):

LEFT — "SCADA sees:"           RIGHT — "GDC retrieves:"
  ⚠ VIBRATION HI ALARM           Surface Choke Valve Log
  VIB 4.2 mm/s                   "3 adjustments this tour · unstable"
  TEMP 198°F (flat)
  → Default action:              Separator Test Report
    REQUEST PUMP PULL             "1.8 bbl slug · 14-min period · GLR rising"
    (mobilize workover)
                                  Night Shift Note
                                  "Pumping rough but temp is normal"

Bottom quote (full-width):
  "The documents say: do NOT pull.
   $1,500 surface technician + choke valve vs. $150k false workover."

CTA: ▶ Run the Scenario
```

---

## SPRINT 4 — H3 Briefing (3 Panels)

**Architecture:** Same pattern — `h3BriefingMode: true` + `h3BriefingPanel: 1`; wrap existing Vizier tab. Reuse H1 CSS. H3 header title should also be renamed: `"📈 Horizon 3 — Long-Term: Oil Price Optimization (Vizier)"` → `"Optimize — VFD Bayesian Optimization"`.

**app.js additions:**
```js
h3BriefingMode: true,
h3BriefingPanel: 1,
```

### Panel 1 of 3 — The Opportunity
```
Tag:   Panel 1 of 3 — The Setup
Title: Oil Price Jumped 40%
Sub:   Every Hz of headroom is now real money.

Left column:
  Callout: "WTI at $125/bbl. Your ESP runs at 52 Hz — conservative, safe.
            Every Hz you safely add is barrels you're leaving in the ground."

  Info box (THE VFD TRADEOFF):
    Current Hz    | 52 Hz · 3,120 RPM
    Flow rate     | ~288 BPD nominal
    Motor temp    | 197°F (safe · limit: 280°F)
    Revenue/day   | ~$36k/day at $125/bbl

Right column (animated revenue vs. Hz bar):
  Horizontal bars showing revenue increasing with Hz
  Green zone: 45–57 Hz (safe)
  Amber zone: 57–62 Hz (thermal risk)
  Red zone:   62–68 Hz (burnout)
```

### Panel 2 of 3 — The Risk
```
Tag:   Panel 2 of 3 — The Physics
Title: The Motor Thermal Tradeoff
Sub:   Higher Hz = more barrels. Until it isn't.

Static chart (CSS bars — no Plotly):
  Hz     | Temp  | Status
  50 Hz  | 220°F | ✔ SAFE     · $31.5k/day
  55 Hz  | 248°F | ✔ SAFE     · $34.8k/day
  60 Hz  | 271°F | ⚠ WARNING  · $38.2k/day (approaching 280°F limit)
  65 Hz  | 298°F | ✘ BURNOUT  · $38.2k - $150k penalty = -$111.8k/day

Quote: "The optimal Hz is not the highest safe Hz.
        It is the Hz that maximizes cash flow over your operating horizon
        without breaching the thermal limit — and it changes with oil price."

Citation: Class H insulation IEC 60085 · 356°F nameplate; operators derate to 280°F
```

### Panel 3 of 3 — The Solution
```
Tag:   Panel 3 of 3 — How GDC Solves It
Title: 15 Bayesian Trials in Seconds
Sub:   Not a field trial. Not a spreadsheet. A Gaussian Process.

Left column:
  ✔ Vertex AI Vizier: suggests Hz values to test
  ✔ Edge XGBoost: evaluates thermal safety for each Hz (milliseconds, not 48h)
  ✔ Pareto frontier: the maximum Hz that maximizes cash flow without burnout
  ✔ Changes with oil price — run it again when prices move

Right column (static Pareto diagram — CSS only):
  Curved frontier line
  X-axis: VFD Hz (45→68)
  Y-axis: Net Cash Flow
  Star marker: "Vizier Optimal ★ ~57.5 Hz"
  Red zone right of frontier: "Burnout penalty zone"

Quote: "Manual Hz trials: 48h per setpoint. Weeks of testing per well.
        GDC Vizier: 15 trials in seconds. Optimal on every oil-price move."

CTA: ▶ Run Optimization
```

---

## SPRINT 5 — Video Script (docs/VIDEO_SCRIPT.md)

**New file.** ~5 minutes / 7 segments. Narrator voice + on-screen captions.

| Segment | Duration | Maps to |
|---|---|---|
| 1 — The Pattern | ~45s | STATE-vs-CONTEXT · 4 industries · Panel 4+6 |
| 2 — This Well | ~30s | ESP setup · intake-only · sand · Panels 1–3 |
| 3 — The Hook | ~30s | One signature, two causes · Panel 3 |
| 4 — H1 Discern (live) | ~90s | Full scenario replay |
| 5 — H2 Classify (live) | ~45s | Slug flow exoneration |
| 6 — H3 Optimize (live) | ~30s | Vizier 15 trials |
| 7 — Why GDC Sovereign | ~30s | RTOC · IEC 62443 · outage-immune |
| 8 — Close | ~15s | "GDC: the AI goes to the data." |

**Veo intro concepts (3 options, ~15–20s each):**
1. **Industrial realism:** Dawn aerial over Permian Basin padsite → zoom underground to pump motor → telemetry lines surfacing as data streams → cut to RTOC console
2. **Data fusion:** Split-screen wellbore (sensor data, flat and ambiguous) + document corpus (shift notes, sonic logs flickering) → merge into single GDC verdict
3. **Scale story:** 1 well → 6 wells → 38 wells → map of Permian → `"One AI. Every well. Simultaneously."` → GDC logo

---

## SPRINT 6 — Look & Feel Polish (fold into Sprint 3 or 4 call)

These are minor but needed for consistency:
1. H2 tab header title: keep as-is ("Classify — ESP Slug Flow Discrimination") — already correct
2. H3 tab header: rename `"📈 Horizon 3 — Long-Term: Oil Price Optimization (Vizier)"` → `"Optimize — VFD Bayesian Optimization"` (matches "Discern" / "Classify" naming pattern)
3. Add `← Briefing` button to H3 header bar (same as H1/H2)
4. H3 tab nav in header: already "Optimize" ✅ — no change needed

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| Financial Justification modal raw {{ }} | ✅ FIXED Session AJ | |
| All H1 Briefing panels | ✅ COMPLETE Session AQ | 6 panels, all reworks deployed |
| H2 briefing panels | ⚠️ SPRINT 3 | Zero infrastructure — start from scratch |
| H3 briefing panels | ⚠️ SPRINT 4 | Zero infrastructure — start from scratch |
| Video Script | ⚠️ SPRINT 5 | docs/VIDEO_SCRIPT.md does not exist |
| OEM Troubleshooting Guide no click handler | ⚠️ BATCH 3 | H1 Doc 3 — deferred |
| SPE-174536 citation in Zone-1 verdict | ⚠️ LOW | Still on screen; acceptable in ⓘ context |
| STATE-vs-CONTEXT premise | ✅ LOCKED | |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — verify with `kubectl exec grep`
- **Batch all edits to same file in ONE `replace_in_file` call**
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- **Deploy with explicit digest** — `kubectl rollout restart` with `:latest` does NOT pull from registry
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,400 lines, `index.html` ~3,200 lines, `app.js` ~2,300 lines — grep for line numbers first
- H2 uses inference-api (not local esp_classifier.bst)
- Wireframes → user sign-off → HTML (never write HTML before sign-off)
