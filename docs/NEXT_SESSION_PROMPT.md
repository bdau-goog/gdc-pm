# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 8, 2026 (Post-Consolidation)  
**git head:** `feature-trio-clean` — branch for clean UI rebuild  
**fault-trigger-ui image:** `sha256:df7f9433` (1/1 Running — last deployed Session G)  
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

## STEP 3: Phase 1 — H1 UI Rebuild (Three-Act Screen)

### What to build (all in `index.html` + `static/styles.css` + `static/app.js`):

**ACT 1 — Pad Alpha Well Map (Entry Point)**
- A dark-mode Vue-driven grid of 14 well-icons (CSS divs, no SVG library).
- Nominal: all wells show gray status dots.
- On fault inject: `ESP-ALPHA-1` pulses amber + GDC Alert banner slides in.
- Clicking `ESP-ALPHA-1` transitions to the Single-Well Diagnostic Screen (Act 2+3).

**ACT 2 — 3-Column Single-Well Diagnostic Screen**
- Col 1 (~25%): ISA-101 horizontal sensor bars (PIP, Amps, Temp, Vib) with directional labels + SCADA alarm ticks.
- Col 2 (~40%): The **Operating Envelope Plotly scatter chart** (see below).
- Col 3 (~35%): GDC Advisor (streaming Gemma text + superscript citations) + Intel Feed (file-styled RAG document cards that pulse-glow on new AI doc generation).

**ACT 3 — The Decision Split Card (full width, below 3 columns)**
- LEFT box (yellow): SCADA View — Ambiguous. Pump-Off risk visible. Conservative path only.
- RIGHT box (green): GDC Advisor — Gas Lock Confirmed. L3 evidence listed. `[APPROVE VFD TRIM]` HITL button.

**The Operating Envelope Chart (Plotly — the most engineeringly credible visual)**
- X-axis: Motor Amps (0–120A), Y-axis: Intake Pressure PSI (0–1,600)
- Plotly background shapes: Green=Nominal, Amber=Gas Lock, Red=Pump-Off Risk zones.
- SCADA alarm dashed lines: Horizontal at 800 PSI, Vertical at 50A.
- Live orange dot trail (last 20 operating points) migrates into the Gas Lock zone during fault.
- **L3 Exclusion Transition (the key demo moment):** When RAG retrieves the shift note, the Pump-Off zone dims to dark gray + label *"❌ EXCLUDED: L3 Context — Pump-Off ruled out"* appears dynamically.

### Implementation approach:
- All changes go into `index.html`, `static/styles.css`, `static/app.js` as a single batched `replace_in_file` per file.
- No `app.py` changes required (all backend endpoints exist: `/api/inject-fault`, `/api/degrade-status`, `/api/live-telemetry`, `/api/agent/recommend-stream`).
- Deploy: `docker build → docker push → kubectl rollout restart`.

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- Batch all edits to same file in ONE `replace_in_file` call
- ALL kubectl/gcloud commands require `source .env &&` prefix
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
