# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-18 / git head: 25b778b / branch: feature-trio-clean
Image: sha256:1ea1a269e8c9c644d1f38dafe25e66277feb5a73752552aaeb3b24d02ffa1761

## STEP 1: Run These Four Commands First
```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```
Expected when healthy:
- fault-trigger-ui: 1/1 Running
- **ollama replicas=0 (GPU OFF — DO NOT scale up)**
- ollama_online: False, model: offline (expected dev default)
- field_intel=11, rag_documents=20

## STEP 2: Read DEMO_MASTER.md
```bash
cat docs/DEMO_MASTER.md
```

## STEP 3: Next Implementation Task

### PRIORITY 1 — Update docs/VIDEO_SCRIPT.md to match current deployed app

The video script is stale relative to Sessions BS+9 through BS+26. Do NOT change the overall structure (4 videos: Overview / H1 / H2 / H3) or narrative tone. Make only the targeted corrections below.

**Corrections required (all sourced to code, no new claims):**

**H1 Panel count and names** — Current h1.html has 5 slides, not 6:
| Old (stale) | New (current) |
|---|---|
| Panel 1: "The Setup" | Slide 1: THE SCENARIO — "Same Signal. Two Causes. One Right Decision." |
| Panel 2: "What is an Unloading Event?" | Slide 2: AMBIGUOUS TELEMETRY — "One Signature, Two Physical Realities" |
| Panel 3: "One Signature, Two Causes" | Slide 3: DECISION SUPPORT — "Motor Burnout vs. Sand Bridging" |
| Panel 4: "STATE vs. CONTEXT" | Slide 4: ADDING CONTEXT — "Fusing Telemetry and Unstructured Well History" |
| Panel 5: "How Operators Decide Today" | (REMOVED) |
| Panel 6: "This Pattern Is Universal" | Slide 5: INDUSTRIAL APPLICATION — "Solving the Edge Context Gap — At Scale" |

**H1 detection indices (integrity gate fix):**
- `gdc_detect_idx`: stale `33` → `35–46 (run-dependent)` — set by HEALTH_THRESHOLD=0.87 (BS+26)
- `alarm_idx`: stale `60` → `55–73 (run-dependent)`
- Lead time: stale "Twenty-seven data points after GDC" → "4–9 minutes before the SCADA alarm fires"

**H1 replay walkthrough:**
- "Advance scrubber to t=30 (pre-detection zone)" — remove the specific step number; use "Advance scrubber slowly into the pre-detection zone"
- "GDC detects the anomaly here — at index thirty-three" → "GDC detects the anomaly here — the amber GDC detect marker fires"
- "SCADA fires its alarm here — at index sixty" → "SCADA fires its alarm here — the red SCADA alarm marker fires, 4–9 minutes after GDC already had context"
- "Twenty-seven data points after GDC" → "minutes after GDC already assembled the document verdict"

**H1 physics — LAGGING temp/vib (BS+25, RT-hardened):**
Add this note to Slide 2/3 panel narration: "Notice: winding temperature and vibration stay near-nominal through this entire detection window — they are lagging indicators. Only pump intake pressure and motor amps decline. SCADA's thermal and vibration trip thresholds never cross in the decision window. The ambiguity is precisely why the early window matters."

**H2 vib units (script says in/s, code uses mm/s):**
- Script says "Vibration rising — from 0.15 to 0.38 inches per second RMS" — WRONG UNITS
- Live code: `vib_nom=0.9–1.2 mm/s`, `vib_end=4.2–4.9 mm/s`, ISA-18.2 HI alarm at 4.0 mm/s
- Fix to: "Vibration rising — from nominally 1.0 to 4.5 millimeters per second RMS, crossing the ISA-18.2 High alarm threshold at 4.0 mm/s"

**Integrity gate table at bottom of script** — update rows:
| Row | Old value | New value |
|---|---|---|
| GDC detection index 33 | `app.py gdc_detect_idx → 33` | `app.py gdc_detect_idx → 35–46 (run-dependent, HEALTH_THRESHOLD=0.87)` |
| SCADA alarm index 60 | `app.py alarm_idx → 60` | `app.py alarm_idx → 55–73 (run-dependent)` |

**Screen Flow Summary table** — update H1 row:
- Old: `H1 | P1→P2→P3→P4→P5→P6 → Run → Replay | HITL approval card`
- New: `H1 | P1→P2→P3→P4→P5 → Run → Replay | HITL approval card`

**Rule for VIDEO_SCRIPT update:** ONLY make the corrections listed above. Do NOT rewrite narration passages, change Veo prompts, or alter H2/H3 content beyond the vib units fix. Minimal diff.

---

## Known Integrity Issues
| Issue | Status |
|-------|--------|
| `PIP` (61 occurrences) → `Pump Inlet Pressure` in app.js/app.py/templates | ⏸ Deferred |
| Authored `~$2,500` / `~$150k` → comparative language in app replay sections | ⏸ Deferred |
| `$150,000` × 3 in tab_architecture.html (ROI Equation + Fleet Financials) | ⏸ Deferred |
| `VIDEO_SCRIPT.md`: stale H1 panel count/indices/vib units (see Priority 1 above) | ⏳ Next session |

## Physics Rulings Locked (BS+20 + BS+25 retrain + BS+26 threshold tune)
- **PIP/Amps are LEADING indicators** — decline from T+0 on the power-law curve.
- **Temp/Vib are LAGGING indicators** — near-nominal through the decision window (~55% of replay),
  then gentle sub-trip rise. Temp: 197 → ~225°F. Vib: 1.4 → ~3.2 mm/s. Both GREEN throughout.
  - Only PIP/Amps cross SCADA alarm thresholds.
  - API RP 11S §4.2: thermal mass delays winding-temp rise; cavitation onset mild until high GVF.
  - RT-hardened: gdc-second-opinion SURVIVES-IF-REWORDED (absolute language softened).
- **esp_health.ubj retrained (BS+25)** on lag_onset=0.55 trajectory in xgboost==2.0.3 venv.
  RMSE=0.00185. Health < 0.30 at 90.1% of sequence (SCADA alarm zone correctly placed).
- **HEALTH_THRESHOLD = 0.87 (BS+26)** — empirically tuned so gdc_detect_idx fires 4.8–9.5m before
  SCADA alarm. hs_at_alarm ≈ 0.83 across runs; threshold 0.04-point margin above alarm zone.
  H2 HEALTH_THRESHOLD = 0.65 (untouched — H2 paraffin scenario gdc_detect_idx=23 < alarm_idx=78 ✅).
- **"Identical"** softened to **"indistinguishable on an intake-only string"** throughout.

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- Tab content: `gke/fault-trigger-ui/templates/*.html` + `app.py` (index.html = shell only)
- Slides: `gke/fault-trigger-ui/slides/` — **baked into the image** (COPY slides/ in Dockerfile)
- Run `verify_templates.py` before any template build
- Source env: `source /home/brian/gdc-pm/.env`
- GPU: ollama scale-to-zero; `./scripts/gpu-start.sh` ONLY for explicit LLM test; ALWAYS pair with gpu-stop.sh
- **NO ollama-scheduler CronJobs**
- No Jinja2 in templates
- **Vizier:** One call per explicit ▶ Run click only

## Build / deploy commands
```bash
cd gke/fault-trigger-ui
python3 ../../scripts/verify_templates.py   # must pass before build
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest .
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm --timeout=90s
```

## Slide URLs for live review
| Purpose | URL |
|---|---|
| H1 deck | gdc-pm.bdau.io/slides/h1.html |
| H2 deck | gdc-pm.bdau.io/slides/h2.html |
| H3 deck | gdc-pm.bdau.io/slides/h3.html |
| Intro deck | gdc-pm.bdau.io/slides/intro.html |
