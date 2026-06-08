# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 8, 2026 (Session H end)  
**git head:** `2cd9768` (feat(ui): Phase 1 H1 — Pad Alpha map, Operating Envelope, Split card)  
**fault-trigger-ui image:** `sha256:39bbce50` (1/1 Running — Session H)  
**inference-api image:** `sha256:d1194989` (1/1 Running — unchanged)  
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
source .env && kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
source .env && kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
source .env && kubectl exec -n gdc-pm gdc-pm-rabbitmq-server-0 -- rabbitmqctl list_queues --vhost gdc-pm name messages consumers
```

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Session H State Summary & Next Tasks

### What was done Session H:
1. **Document consolidation (clean break):** `feature-trio-clean` branch created. Standalone `CLAIM_LEDGER.md` deleted — merged into `DEMO_MASTER.md` appendix. `INTEGRITY_AUDIT.md` and `BACKEND_CONFORMANCE_REPORT.md` archived. Active docs reduced to 3 files.
2. **Phase 1 H1 UI deployed (`2cd9768`):**
   - **Pad Alpha overview strip:** 14-well Vue-driven map above the H1 banner. Well A-1 pulses amber when fault injected. Proves scale story visually.
   - **3-column layout:** Left (25% sensors + timeline), Center (40% Operating Envelope + Decision Split Card), Right (35% GDC Advisor + Intel Feed).
   - **Operating Envelope (Plotly scatter):** X=Motor Amps, Y=Intake PSI. Live trail migrates from Nominal → Gas Lock zone. Three background zones (Nominal/Gas Lock/Pump-Off Risk). SCADA alarm lines. When `h1EvidenceActive >= 2` (shift note retrieved), Pump-Off zone dims to gray + `❌ EXCLUDED (L3 Fused)` label.
   - **Decision Split Card:** Left half: SCADA (Ambiguous, Pump-Off risk); Right half: GDC (L3 context fused, safe to trim, `[APPROVE VFD TRIM]` HITL button).
   - `h1EnvelopeHistory[]`, `h1PumpOffExcluded` Vue state + `_renderEnvelopeChart()` + watcher on `h1EvidenceActive`.

### Next Tasks (Session I):

**Option A: Wire Pump-Off Exclusion to actual RAG retrieval**
Currently `h1PumpOffExcluded` is set when `h1EvidenceActive >= 2` (2nd evidence wall item activated at 2s delay). To make it fully honest, tie it to retrieval of a specific "annulus level" or "pump-off excluded" field_intel document instead of the timer. Requires small `app.py` change to include a `pump_off_excluded` field in the intel feed item type, and `app.js` to watch for it.

**Option B: Phase 2 — RAG Document Cards (clickable, styled as field docs)**
Style the Intel Feed cards in the right column to look like authentic field documents (file-type badges, metadata header). Implement the Document Viewer Modal (click feed card → opens full doc content with source, author, timestamp).

**Option C: H2 Slug Flow discriminator chart + Evidence Board**
Build the two-line chart (Vibration rising, Motor Temp flat) + H2 evidence board (6 cards). This is the `$1,500 vs $150,000` false-positive-prevention demo. All wiring is in `app.py` — pure `index.html` addition.

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- Batch all edits to same file in ONE `replace_in_file` call
- ALL kubectl/gcloud commands require `source .env &&` prefix
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
