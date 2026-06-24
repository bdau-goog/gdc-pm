# Next Session Prompt — GDC ESP Ops Video (Operational State)
Date: 2026-06-24 (Session BS+44) / branch: feature-trio-clean
Git HEAD: a766dac / Image: sha256:d127b3f9ccc5f1dfc19fda00946bde3fc32419f8891e536ab589c06edaaad6ac

## STEP 1: Run These Four Commands First
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

## STEP 2: Read These Documents
```bash
cat docs/SESSION_LOG.md | head -120   # last 3 entries for context
```

## STEP 3: Reference Tab Integrity Scrub

**Objective:** Audit all 7 panes of `tab_architecture.html` (769 lines) against the
`.clinerules` Prime Directive. Build a mini Claim Ledger. Fix any OPEN items.

**Context:** The tab has a top-level amber disclaimer:
`"Walkthrough Example — not live data · Values shown illustrate a single pipeline execution"`
This is the honest framing. The scrub checks whether the individual displayed values
are *consistent with our code*, not that they equal live API output.

### The 7 panes and their known risk areas:

| Pane | Key | Known risk |
|---|---|---|
| 1 System Overview | `archPane==='overview'` | ROI comparison cards, IEC standard cites — review only |
| 2 Telemetry Ingestion | `archPane==='ingestion'` | Minimal numbers; mostly clean |
| 3 Unstructured Data Ingestion | `archPane==='docingest'` | Just written (BS+43) — honest by design ✅ |
| **4 ML Detection** | `archPane==='detection'` | **Sensor values + model outputs: grep-verify** |
| **5 Context Fusion** | `archPane==='context'` | Stream 3 doc examples; timing claims |
| **6 AI Reasoning** | `archPane==='reasoning'` | **Hardcoded RUL values: 22.1 min base → 14.2 min AI** |
| **7 Operations** | `archPane==='operator'` | **ROI numbers: $150k / $366k / $7.8M+** |

### Pane 4 specific checks (ML Detection):
The walkthrough example uses: PSI=185, Temp=218°F, Vib=0.41 mm/s, Amps=63.2A,
Health=0.34, Confidence=91.4%, Base RUL=22.1 min.

Verify these are plausible mid-window values (not endpoint values) against code:
```bash
grep -n "psi_range\|temp_range\|vib_range\|amps_range\|gas_lock" gke/fault-trigger-ui/app.py | grep -i "gas_lock\|FAULT_PROFILE" | head -20
# psi_range=(875,1100) — PSI 185 is BELOW this, but mid-window decline from 1245 is plausible
# CHECK: is 185 PSI defensible as a mid-decline demonstration value?
```

### Pane 6 specific checks (AI Reasoning):
```bash
grep -n "RUL\|rul_minutes\|14\.2\|22\.1\|adjusted_rul" gke/fault-trigger-ui/app.py | head -20
# Base RUL 22.1 min → AI-adjusted 14.2 min: is this ratio plausible?
# adjust_rul_with_documents() applies 0.6× multiplier for high GVF
# 22.1 × 0.64 ≈ 14.1 min — check the formula confirms this is reachable
```

### Pane 7 specific checks (Operations / ROI):
```bash
grep -n "150.000\|150k\|150,000\|366\|7\.8M\|workover\|pull_cost\|FAULT_PHYSICS\|rig_rate" gke/fault-trigger-ui/app.py | head -20
# Expected: FAULT_PHYSICS["gas_lock"] has cost_emergency ~150000
# $366k = $150k pull + 48hr downtime × $45k/day = $150k + $216k = $366k — verify arithmetic
# $7.8M annualized: check if this traces to any code constant or is an authored estimate
```

### Scrub output format (create inline, no new file needed):
For each flagged claim, one line in the session:
```
| Pane | Claim | Source | Status: SURVIVES / OPEN |
```
Fix OPEN items in one batched `replace_in_file` call per file.
`verify_templates.py` must pass before deploy.

---

## STEP 4 (if time): B3-S4 Pre-Recording Verification

Before recording B3-S4 (H3 constraint provenance), verify constraintDoc renders reliably:
```bash
curl -s "http://gdc-pm.bdau.io/api/vizier/optimize" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print('constraintDoc.found:', d.get('constraint_doc', {}).get('found'))"
# Expected: constraintDoc.found: True
# If False: check app.py pgvector query at L6530-6545 — seed doc may be missing
```

## Deploy Command (permanent reference)
```bash
cd gke/fault-trigger-ui
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest .
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
```
**Registry:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/` (NOT gcr.io — that's the old project)

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- GPU scale-to-zero; `gpu-start.sh` ONLY for explicit LLM test (~$0.65/hr)
- VEO_COLD_OPEN.md has hidden-character lines — use write_to_file not replace_in_file
- B1-P5 VO locked: recorded, matches bible verbatim ✅
- B2-S5: ❌ CUT — do not record
- BBRIDGE VO: "all AI local, no cloud required" (not "air-gap capable")
