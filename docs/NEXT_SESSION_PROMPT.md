# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-15 / git head: e1b51f6 / branch: feature-trio-clean
Image: sha256:aac8fecc64ab962bab6dd9c20ce62d7438105eedacb2bd595b2c554dd438fa10

## STEP 1: Run These Four Commands First
```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```
Expected when healthy:
- fault-trigger-ui: 1/1 Running
- ollama replicas=0 (GPU off by default — DO NOT scale up)
- ollama_online: False, model: gemma4:latest
- field_intel/rag_documents: non-zero counts

## STEP 2: Read DEMO_MASTER.md
```bash
cat docs/DEMO_MASTER.md
```

## STEP 3: Session Priority — H1 Briefing Panel Redesign (16:9 / video-ready)

All panel changes spec'd this session. Locked conventions (H1 first, H2/H3 inherit):
- **16:9 slide-native**: scale body content to fill frame; title sizes unchanged
- **Kicker = beat-name only** (drop "Panel N of M"): THE SCENARIO / THE EVENT / THE HOOK / THE MOAT / THE DECISION / THE PLATFORM
- **Statements not quotes**: un-quote demo's own assertions; keep attributed quotes (shift notes)
- **Entry panels top-anchored**: text top, scenario visual below; business lead-in merged into Panel 1

### Panel-by-panel (tab_h1.html):
| Panel | Change |
|---|---|
| P1 | kicker→"THE SCENARIO", title→"Same Signal. Two Causes. One Right Decision.", top-anchored, business lead-in merged, metrics below text |
| P2 | density fill (tiles too sparse; enlarge heights/text/bars) |
| P3 | wellbore art: zoom to pump intake; gas-lock = dispersed bubbles at intake, annulus HIGH (NOT amber rect at top); drawdown = fluid level dropping below intake, sand only on VFD trim |
| P4 | density fill (STATE/CONTEXT rows top-packed; grow to fill frame) |
| P5 | density fill — CRITICAL MESSAGE; action cards much taller; closing = full-width hero line |
| P6 | density fill; REMOVE centered "Run the Scenario" (keep footer nav button only) |
| ⓘ | Integrity fix: retire "physically identical / no sensor can disambiguate" → "genuinely ambiguous on an intake-only string in the early decision window" (DEMO_MASTER §4.1 PREMISE ledger row) |

### 3-persona video plan (all personas cover H1+H2+H3):
- P1 Business: Operator (ESPs, lifting costs) + Halliburton (market share capture)
- P2 Product: capabilities customers need; HAL advantage if competitors lack them
- P3 Technical: Google Cloud + GDC + Gemini — build better/easier/faster/cheaper

### Build / deploy commands:
```bash
cd gke/fault-trigger-ui
python3 ../../scripts/verify_templates.py   # must pass before build
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest .
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm --timeout=90s
```

## Known Integrity Issues
| Issue | Status |
|-------|--------|
| ⓘ Physics panel: "physically identical / no sensor can disambiguate" | 🔴 OPEN — fix next session |

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- Tab content: `gke/fault-trigger-ui/templates/*.html` + `app.py` (index.html = shell only)
- Run `verify_templates.py` before any template build
- Source env: `source /home/brian/gdc-pm/.env`
- GPU: ollama scale-to-zero; `./scripts/gpu-start.sh` only for explicit LLM test
- No Jinja2 in templates
