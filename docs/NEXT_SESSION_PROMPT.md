# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-20 (Session BS+30) / git head: pending commit / branch: feature-trio-clean / docs-only
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

## STEP 3: Next Task — Build Movement 3 in Google Flow, import to Vids (docs/VEO_COLD_OPEN.md)

`docs/VEO_COLD_OPEN.md` is the deliverable (12-scene narrated cold open). **Session BS+30 pivoted generation to Google Flow** (labs.google/flow) because Vids-embedded Veo has no cross-shot context (root cause of the Beat-6 churn). Workflow: **generate clips in Flow (use Ingredients for reusable assets + scene extension) → import to Vids → attach per-scene VO.** See the new "GENERATION TOOLING" section in the doc.

**Validated renders so far:** Beat 1 (aerial blue valve-tree field), Beat 3 (operator side-profile), 5A (3 silver sleds — had minor steam, prompt now negates it). **Awaiting Flow rebuild:** 5A→5B (Extend, split into 2 scenes), 6A/6B.

**LOCKED this session — do NOT reopen:**
- Beat 6 = **EFFECT CUT**: NO abstract "fusion" effect, NO beams/lasers, NO paper, NO liquid/sparks/steam. 6A/6B are calm literal server-room shots; the **VO carries "merges and compares."** (4 render failures: explosion→liquid→lasers proved the concept is Veo-hostile.)
- 5A VO = the GDC inversion ("AI to your data, not your data to the cloud"); 5B VO = security/governance with **governed egress** ("only what you approve ever leaves" — NOT "never leaves," which contradicts H3/Vizier).
- Real gear = 3 slim silver Dell sleds; **never show Dell branding; never feed the Dell photo as an ingredient.**
- Veo hazard rule: hard-negate steam/sparks/fire/liquid/beams — atmospheric metaphors over-literalize into O&G hazards.

**Likely tasks next session:** (1) help the user drive Flow (Ingredients setup, scene extension) as they build 5A→6B; (2) retune any beat Flow renders off; (3) carryover from BS+28: schema-starve rewrite of VEO_PROMPTS.md outdoor scenes (Scene 1 ~line 31, 4b ~62, 5 ~70, 6 ~80).

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
