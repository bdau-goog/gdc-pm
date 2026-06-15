# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-15 / git head: 6e42e35 / branch: feature-trio-clean
Image: sha256:b2971a3fa40ad2eb9e8eafe54397547c561c6645c5032c698642d9b2338d972f

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

## STEP 3: Session Priority — H2 + H3 Briefing Panel Redesign (inherit H1 conventions)

H1 briefing redesign complete and deployed (`6e42e35`). The locked conventions now apply to H2 and H3:

**H1 conventions (locked — inherit for H2/H3):**
- **16:9 slide-native**: scale body content to fill frame; title sizes unchanged
- **Kicker = beat-name only**: H2 → THE WELL / THE SIGNATURE / THE DECISION; H3 → THE OPPORTUNITY / THE TRADEOFF / THE OPTIMIZATION
- **Statements not quotes**: un-quote demo's own assertions; keep attributed quotes (shift notes, SME)
- **Entry panels top-anchored**: text top, scenario visual below; business lead-in in Panel 1

### H2 panel-by-panel (tab_h2.html):
| Panel | Kicker | Change |
|---|---|---|
| P1 | THE WELL | Top-anchored; well spec + WAT/wax chemistry card; business lead-in ($70k–$100k averted) |
| P2 | THE SIGNATURE | Timeline strip density fill; 4 sensor tiles larger; two-tier SCADA/APM callout |
| P3 | THE DECISION | GDC verdict card; action cards taller (hot-oil ~$3–6k vs pull ~$70–100k); doc stack |

### H3 panel-by-panel (tab_h3.html):
| Panel | Kicker | Change |
|---|---|---|
| P1 | THE OPPORTUNITY | 6-well GOR table density fill |
| P2 | THE TRADEOFF | Constraint stack taller; SCADA honest framing |
| P3 | THE OPTIMIZATION | GOR-ranked Hz table; uplift card; closing "Cloud searches. Edge enforces." |

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
| ⓘ Physics panel: "physically identical / no sensor can disambiguate" | ✅ RESOLVED — `6e42e35` |

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- Tab content: `gke/fault-trigger-ui/templates/*.html` + `app.py` (index.html = shell only)
- Run `verify_templates.py` before any template build
- Source env: `source /home/brian/gdc-pm/.env`
- GPU: ollama scale-to-zero; `./scripts/gpu-start.sh` only for explicit LLM test
- No Jinja2 in templates
