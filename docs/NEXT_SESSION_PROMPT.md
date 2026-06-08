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

**Build Act 1 and Act 3 of the Interactive H1 Unloading Game:**
1. **The Dual Injection Buttons:** Add `⚡ Inject Gas Lock` and `⚡ Inject Fluid Drawdown` as active choices on the Detect Tab.
2. **Fluid Drawdown Seed Document:** In `app.py`, write the `fluid_drawdown` RAG seed document containing the 06:00 sonic log ("Fluid level 150 ft above intake").
3. **The Exclusion Logic:** Wire `app.js` so that if `fluid_drawdown` is active, the Gas Lock zone grays out and the VFD Trim button is disabled. If `gas_lock` is active, the Fluid Drawdown zone grays out.
4. **The "Wrong Choice" Consequence:** Wire the `[APPROVE VFD TRIM]` button so that clicking it during a Fluid Drawdown event triggers a motor seizure error screen with an explicit stuck pump animation.

**Optional — Phase 5+ MLOps Integrity:**
Train the `esp_thermal` XGBoost model and wire it into `vizier_optimize()` to eliminate the H3 static polynomial.

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- Batch all edits to same file in ONE `replace_in_file` call
- ALL kubectl/gcloud commands require `source .env &&` prefix
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
