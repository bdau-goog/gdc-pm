# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-20 / git head: 987fa99 (pre-commit; this session = docs-only) / branch: feature-trio-clean
Image: sha256:1ea1a269e8c9c644d1f38dafe25e66277feb5a73752552aaeb3b24d02ffa1761 (unchanged — Session BS+29 was docs-only)

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

## STEP 3: Next Task — VEO COLD OPEN is render-ready (docs-only work)

`docs/VEO_COLD_OPEN.md` is the PRIMARY deliverable and is now a **12-scene** narrated story intro
(Beats 1, 2, 3, 4A, 4B, 4C, 5A, 5B, 6A, 6B, 7), Part A ≈ 70–80s, then live demo ≈ 4 min, total < 6:00.
Session BS+29 restructured Beat 4→4A/B/C, Beat 5→5A/B, Beat 6→6A/B and made the VO arc internally consistent
(4C "scattered" → 6A "merges…scattered documents" → 6B "in seconds").

**The user is doing all Veo rendering + VO recording (I author prompts, cannot view video).** Validated so far:
Beat 1 (aerial blue christmas-tree field) and Beat 3 (operator side-profile). Beats 4A/4B/4C/5A/5B/6A/6B
are written and awaiting render. **Continuity = feed a still frame of the prior clip as a reference-image
ingredient; prompt prose like "same desk as Beat 3" will NOT reproduce a shot (Veo has no cross-gen memory).**

**Likely next tasks (await the user's render feedback first):**
1. Retune any beat the user reports as off (pumpjack bias / garbled fake UI text / off-length). Veo lessons locked
   in-doc: never show a readable screen (garbles to "SCADA MIIPLUPUO"/"CdNet"); no head-on face (creepy gaze);
   use blue-body/red-handwheel valve-tree to starve the pumpjack schema; O&G screens by SHAPE only
   (wellbore completion schematic / P-T trend charts / pump curve), never audio-waveform or seismic-nebula.
2. **Carryover from BS+28:** apply the same schema-starve rewrite to `VEO_PROMPTS.md` outdoor scenes
   (Scene 1 ~line 31, Scene 4b ~62, Scene 5 ~70, Scene 6 ~80) — they still carry "Permian Basin oil field/pad"
   + "NO beam pump jacks" negatives that backfire.
3. If the user wants the demo VO tightened, trim `DEMO_VO_PERPANEL.md` H1 section first (densest).

**Rules for this work:** docs-only; no app/code/deploy. Spoken track stays **number-free** (panels carry figures).
Honesty gate: Beat 6 credits multivariate scoring ("merges and compares") but must NOT claim detection
superiority over advanced APM — the full detection story lives in the live-demo How-It-Works, not the intro.

## STEP 3-ALT: If returning to the live app instead
The stale `docs/VIDEO_SCRIPT.md` (OLD 4-video script) still has BS+27 Priority-1 corrections pending
(H1 5-panel count, dynamic indices, mm/s units). The Vids kit supersedes it for Persona #2; only fix
`VIDEO_SCRIPT.md` if you specifically need that legacy script.

## Physics Rulings Locked (unchanged — BS+20 + BS+25 + BS+26)
- **PIP/Amps LEADING** (decline from T+0); **Temp/Vib LAGGING** (near-nominal through ~55% of replay, then gentle sub-trip rise, green throughout). Only PIP/Amps cross SCADA thresholds.
- HEALTH_THRESHOLD=0.87 (H1): gdc_detect fires 4–9 min before SCADA alarm. H2 HEALTH_THRESHOLD=0.65.
- "indistinguishable on an intake-only string" (not "identical"); "Gas Volume Fraction"; "Motor Burnout".

## Realism facts for Veo/scripts (validated vs docs/rag_source/esp_manual.md)
- ESP = low-profile **christmas-tree (valve-stack) wellhead** — NOT a beam pump jack (starve the schema, don't negate; don't say "finned" → heat-exchanger look).
- VFD = **separate surface cabinet + step-up transformer on a skid**, set back from the wellhead — not part of the tree.
- Hot-oil treatment = service truck **at the wellhead** (down tubing/annulus), not the chemical-injection port.

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- Tab content: `gke/fault-trigger-ui/templates/*.html` + `app.py` (index.html = shell only)
- Slides: `gke/fault-trigger-ui/slides/` — baked into the image
- Run `verify_templates.py` before any template build
- Source env: `source /home/brian/gdc-pm/.env`
- GPU: ollama scale-to-zero; `./scripts/gpu-start.sh` ONLY for explicit LLM test; ALWAYS pair with gpu-stop.sh
- No Jinja2 in templates · Vizier: one call per ▶ Run click only
- Deploy with explicit `@sha256:<digest>` (`:latest` rollout-restart re-uses cached image on this cluster)

## Build / deploy commands (only if returning to the app)
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
