# Next Session Prompt — GDC ESP Ops Demo (Operational State)
Date: 2026-06-25 (Session BS+52+) / branch: feature-trio-clean
Git HEAD: e29c5ef / Image: sha256:e28a4c5cb2a5988f159a504287c2792880cf25310be9a637a56f85838425e57d

⚠ NOTE: 5 commits ahead of origin/feature-trio-clean — push before next session if needed.

## STEP 1: Run Four Startup Commands
```bash
kubectl get pods -n gdc-pm --no-headers
# Expected: all 1/1 Running (7 pods)

kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
# Expected: 0

curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
# Expected: ollama_online: False model: offline

kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
# Expected: field_intel = 11, rag_documents = 20
```

## STEP 2: Read DEMO_MASTER.md + DECISION_DOSSIER.md
```bash
cat docs/DECISION_DOSSIER.md   # §2 is H2 spec; §2.6 physics; Bill Barna SME confirmation
cat docs/SESSION_LOG.md | head -80
```

## STEP 3: H2 UI REDESIGN — One Atomic Deploy

### Context (derived this session — do NOT re-derive)
- Early detection is real XGBoost `esp_health.ubj` (`health_ok=True` every run, NOT fallback)
- Verified live: at GDC fire, **vib = 1.94 mm/s = 48% of the 4.0 HI limit**. Single-tag threshold CANNOT fire there.
- Lead time is **2.6–4.3 weeks** across runs (emergent from model+physics, NOT staged)
- The "seal degrading" wellbore SVG is a **dead Session BE scenario leftover** (protector seal — killed, Gate 5 fail). Must go.
- Claim scoped to **threshold SCADA only** (~85% of wells) — never "earlier than APM" (dossier §2.3 locked)
- `app.py` L7808: `roll_vib` is already computed but NOT returned in the API response → add it (needed for Q1)

### Decision log (all approved this session — do NOT re-open)
- ✅ 3-column layout: chart 44% / wellbore 22% / console 34%
- ✅ Add B2-S3.5 rewind beat: after 3-doc cascade, scrub back to GDC▲ to show thin wax / vib at 48% of limit
- ✅ Wellbore is DYNAMIC (bound to h2CursorIdx via PIP for wax band thickness) because of rewind
- ✅ Honesty tag: subtle vertical text along the bore "schematic · wax inferred from PIP" — small, not a star
- ✅ Curve NOT flattened — physics stays true; claim is "limit not crossed yet," not "SCADA is slow"
- ✅ Efficiency 'i' tooltip: "VFD-derived (head·flow·motor power, IEEE 112) — computed, not a direct sensor"

### Fix table (one atomic build+push+rollout)

| # | Fix | File · location | Notes |
|---|---|---|---|
| Q2 (🔴 integrity) | Kill seal-degradation SVG; redraw as wax-up/sensors-down cutaway, enlarged to new column | `tab_h2.html` L360–410 (SVG) + L135 (main body flex → 3-col: 44/22/34%) | Dynamic: wax band height ∝ PIP via h2CursorIdx |
| Q3 (🔴 integrity) | "Weeks post-workover" → "Weeks since last treatment" | `app.js` L2192 xaxis title | 1-line |
| Q4 | GDC▲ caption: "health <0.65 · vib still ~half HI limit" / SCADA▲ caption: "single-tag 4.0 mm/s crossed" + chart footnote (threshold-scoped) | `app.js` L2176–2186 annotations block | Use verified 48% fact; threshold-scope only |
| Q1 | Add faint rolling-avg vib overlay (what SCADA actually trips on) so SCADA▲ marker lands on its own crossing | `app.py` L7925+ (return `roll_vib` in response) + `app.js` _renderH2ReplayChart new trace | Backend + frontend |
| Q5 | Efficiency 'i' tooltip (VFD-derived, IEEE 112, computed not direct sensor) | `tab_h2.html` EFF tile label + `app.js` chart legend | Additive |
| B2-S1 card fix | Stale: "replay animating." Replace: "loads at alarm state — 90-day history already plotted, VIB-HI active, no playback forward" | `VIDS_PRODUCTION_MASTER.md` B2-S1 card | 1-line; then also update app state comment |

### Wellbore SVG spec (new, replaces L360–410 tab_h2.html)
```
Viewbox: 0 0 120 420 (wider, full-height use)
Layout (top→bottom):
  [WH]                              y=15     — static grey rect
  ║ TUBING ║                        y=15→250 — static grey lines both sides
  ░░░ WAX BAND ░░░                   y=25→120 — DYNAMIC: height ∝ PIP / psi_end
    wax fills FROM y=25 DOWN to:     height = max(8, min(100, psi[cursor] / psi_end * 100))
    fill: rgba(251,191,36, opacity)  opacity ∝ cursor progress (thin→thick)
    label: "WAX ZONE" vertical text, 5px, amber 0.45 opacity
    label: "~1,500 ft" vertical text, 4px, muted — spatial reference
  ────── off-sensor boundary ──────   y=180   dashed amber line
    label: "sensors below" 4px muted italic RIGHT of line
  [PUMP]   VIB▲ tick                 y=250   — amber when onset reached
  [PROT]   (neutral grey — NOT reddening; paraffin is NOT a seal failure)
  [MOTOR]  TEMP live readout °F      y=320   — green if nominal
  ≡PERFS≡                            y=360   — static

  Vertical honesty tag (along LEFT side of tubing):
    <text writing-mode="vertical-rl" x="12" y="250"
          font-size="4" fill="rgba(100,116,139,0.35)"
          font-style="italic">schematic · wax inferred from PIP</text>

  Sensor tick marks at pump level:
    VIB ▲ (amber, brightens after onset_idx)
    AMPS ▲ (amber, brightens after onset_idx)
    both are CSS-animated with subtle pulse (keyframe opacity 0.6→0.9 2s ease-in-out)
```

### Updated B2 Scene Cards (replace in VIDS_PRODUCTION_MASTER.md §SECTION 2)

**B2-S1 — Start the Run · ~5s** (REWRITE — old card was stale re: "replay animating")
```
APP STATE   : H2 tab · click ↺ New Scenario
              Loads at scada_alarm_idx — 90-day history fully plotted, VIB-HI alarm ACTIVE
              Wellbore shows full wax band (cursor at alarm = max wax); vib at alarm-state level
              NO forward playback — this is a history-triage view, not a live event

CAMERA/MOVE : [LIVE] click ↺ New Scenario; show the loaded alarm state
              [POST] static — the drama is already on screen

VO          : "Let's run it. The well has been degrading for weeks — and the monitoring
              platform already has an answer: bearing wear. Let's see what the documents say."
```

**B2-S3.5 — Rewind to GDC Detection · ~8s** (NEW SCENE — insert after B2-S3)
```
APP STATE   : H2 tab · 🟢 GDC Advisor · h2VerdictRevealed=true
              SCRUB CURSOR BACK from scada_alarm_idx → gdc_detect_idx
              Wellbore: wax band visibly THINNER (earlier in restriction build-up)
              Chart: vib reads ~1.9–2.0 mm/s — clearly below the 4.0 HI line
              GDC▲ marker is where cursor lands

VISUAL      : Wax band thins on rewind; vib at ~half the alarm limit; GDC detect marker now active

CAMERA/MOVE : [LIVE] drag scrubber from alarm state back left to GDC▲ marker;
              hold ~2s at gdc_detect_idx; show vib well below the ISA HI line
              [POST] zoom 1.15× on vib trace + GDC▲ marker; hold on the gap between
              the marker and the 4.0 HI dashed line

VO          : "GDC didn't wait for the alarm. Back here — weeks earlier — vibration is
              still well below the hard limit. But the multivariate health score already
              saw the correlated drift across all four channels. This is the window where
              the surface treatment still works — before the restriction starves the pump.
              Act on the drift, not the alarm."

PANEL QUOTE : Vibration value at gdc_detect_idx (~1.94 mm/s) vs ISA HI 4.0 line
              GDC▲ marker caption "health <0.65 · vib still ~half HI limit"

INTEGRITY   : Verified live: vib at gdc_detect_idx = 1.94 mm/s = 48% of 4.0.
              Single-tag threshold CANNOT fire there. XGBoost sees joint drift.
              Claim scoped to threshold SCADA only (dossier §2.3).
```

**B2-S4 — Action Contrast · ~8s** (unchanged — still the right close)

### Runtime delta
- B2-S3.5 adds ~8s → H2 total ~67s (was ~59s). Still well under 6:00 total.

## Recording Progress
- ✅ B0.1–B0.4 (Intro) DONE
- ✅ B1-P1–P5 + B1-S1–S6 (H1 scenario) DONE
- ⏳ H2 (B2-P1 through B2-S4) — UI redesign needed first (above); record AFTER deploy + verify
- ⏳ BBRIDGE — record after H2
- ⏳ H3 (B3-P1 through B3-S5) — panels deployed; record after H2
- ⏳ BCLOSE — record last

## Deploy Command (permanent reference)
```bash
cd gke/fault-trigger-ui
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest .
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
```
**Registry:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/` (NOT gcr.io)

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- GPU scale-to-zero; `gpu-start.sh` ONLY for explicit LLM test (~$0.65/hr)
- B2-S5: ❌ CUT — do not record
- BBRIDGE VO: "all AI local, no cloud required" (not "air-gap capable")
- **Autonomy numeric knob: ❌ BLOCKED** — IEC 61511 FAILS
- **GAS LOCK VO physics:** PIP drops / casing annulus pressure rises — do NOT change
- **H3 MUST-NOT-SAY:** See DECISION_DOSSIER.md §3.7
- **Why-GDC MUST-NOT-SAY:** See DECISION_DOSSIER.md §4.5
- **H2 early-detect claim:** threshold SCADA only — never "earlier than APM" (dossier §2.3)
- **H2 wax band:** "schematic · wax inferred from PIP" — displayed, not a measurement
- **live_vizier=True: announce before calling** — creates a billable Vizier study
