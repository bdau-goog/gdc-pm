# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-18 / git head: cf5529a / branch: feature-trio-clean
Image: sha256:1ea1a269e8c9c644d1f38dafe25e66277feb5a73752552aaeb3b24d02ffa1761 (unchanged — Session BS+28 was docs-only)

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

## STEP 3: Next Implementation Task — REFINE THE VIDS VIDEO KIT (docs-only)

Session BS+28 produced a complete Vids video kit for **Persona #2 (ESP operations leadership)**, narrated from a **Google Cloud third-party** POV. The video pattern is: **narrated Veo story intro (~60s) → "let's dive into the demo" → live screen-recorded demo (~4–4.5 min)**, total < 6:00. The user is generating the Veo intro clips and will return with feedback.

**The kit (all in docs/):**
| File | Role |
|---|---|
| `VEO_COLD_OPEN.md` | **PRIMARY** — 7-beat Veo story intro, PER-BEAT VO (1 clip = 1 Vids scene = 1 ~8s line), + "how to record per-scene VO in Vids" |
| `DEMO_VO_PERPANEL.md` | Per-panel + per-scenario demo VO ([ACTION]/[VO]/zoom), verified vs live slides/templates |
| `VIDEO_SCRIPT_OPS_VIDS_V3_NUMBERFREE.md` | Number-free cinematic register (kept) |
| `VIDEO_SCRIPT_OPS_VIDS_V4_GROUNDED.md` | Number-free operator-grounded register (kept) |
| `VEO_PROMPTS.md` | Full per-section Veo scene library (alt to cold-open) |
| `RECORDING_GUIDE.md` | Capture/assembly: record full-screen → crop 16:9 in Vids; QuickTime-capture + Vids-Voiceover decoupling |

**Likely next tasks (await user's Veo results first):**
1. **Veo pumpjack-bias cleanup carryover:** `VEO_COLD_OPEN.md` beats 1/2/5 already rewritten to "starve the schema" (no "oil field/pad/well", describe finned valve-tree + control skid, top-down/tight framings). **TODO: apply the same schema-starve rewrite to `VEO_PROMPTS.md` outdoor scenes — Scene 1 (line ~31), Scene 4b (~62), Scene 5 (~70), Scene 6 (~80)** so both files are consistent. They still contain "Permian Basin oil field/pad" + "NO beam pump jacks" negatives that backfire.
2. **Tune specific beats** the user reports as pumpjack-contaminated or off-length against their VO line.
3. If the user wants the demo VO tightened, trim `DEMO_VO_PERPANEL.md` H1 section first (densest).

**Rules for this work:** docs-only; no app/code/deploy. Spoken track stays **number-free** (panels carry figures). Keep realism guardrails (VFD = separate surface skid, NOT on the christmas tree; ESP = valve-tree wellhead, never beam pump; hot-oil at the wellhead). **Constraint: I can author Veo prompts but cannot view/interpret generated video** — the user does the visual QA.

## STEP 3-ALT: If returning to the live app instead
The stale `docs/VIDEO_SCRIPT.md` (the OLD 4-video script) still has the BS+27 Priority-1 corrections pending (H1 5-panel count, dynamic indices, mm/s units). The new Vids kit supersedes it for Persona #2; only fix `VIDEO_SCRIPT.md` if you specifically need that legacy script.

## Physics Rulings Locked (unchanged — BS+20 + BS+25 + BS+26)
- **PIP/Amps LEADING** (decline from T+0); **Temp/Vib LAGGING** (near-nominal through ~55% of replay, then gentle sub-trip rise, green throughout). Only PIP/Amps cross SCADA thresholds.
- HEALTH_THRESHOLD=0.87 (H1): gdc_detect fires 4–9 min before SCADA alarm. H2 HEALTH_THRESHOLD=0.65.
- "indistinguishable on an intake-only string" (not "identical"); "Gas Volume Fraction"; "Motor Burnout".

## Realism facts for Veo/scripts (validated vs docs/rag_source/esp_manual.md)
- ESP = low-profile **christmas-tree (valve-stack) wellhead** — NOT a beam pump jack (Veo's default; starve the schema, don't negate).
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
