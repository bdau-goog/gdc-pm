# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 8, 2026 (Session I end)
**git head:** `5485592` (feat(ui): Session I — Fluid Drawdown dual-inject game, dual-zone envelope exclusion, seizure diagnostic state)
**fault-trigger-ui image:** `sha256:1b7a05fb` (1/1 Running — Session I)
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

**Expected when healthy:**
- All 8 pods 1/1 Running · ollama replicas: 1
- ollama_online: True · model: gemma4:latest
- field_intel: ~2 (pre-fault, grows after inject) · rag_documents: 18
- telemetry.events: 0 messages · 1 consumer

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Session I State Summary & Next Tasks

### What was done Session I:
1. **Interactive H1 Unloading Game deployed (`5485592`):**
   - **Dual Inject Buttons:** `⚡ Gas Lock` (red) and `⚡ Fluid Drawdown` (orange) on the Detect tab banner. Both buttons disabled after first inject (anti-double-click).
   - **Dynamic Evidence Wall:** Evidence cards swap content based on which fault is active. Gas Lock → GVF separator logs, shift note. Fluid Drawdown → 06:00 sonic log, flat GOR, sand bridging contraindication.
   - **Dual-Zone Operating Envelope Exclusion:**
     - Gas Lock: Pump-Off Risk zone grays out + `❌ Pump-Off EXCLUDED (L3 Fused)` label after evidence wall reaches item 2.
     - Fluid Drawdown: Gas Lock zone grays out + `❌ Gas Lock EXCLUDED (L3 Fused)` label after evidence wall reaches item 2.
   - **Fluid Drawdown backend:** `fluid_drawdown` added to `FAULT_PROFILES`, `PNR_MINUTES`, `REMEDIATION_TIERED`, `FAULT_PHYSICS`, `REMEDIATION_COSTS`, `INTELLIGENCE_FEED`, `GEMMA_FINDING_TEMPLATES`. 06:00 Sonic Log RAG seed document auto-inserted on inject.
   - **Decision Split Card rewired:** GDC column switches between Gas Lock path (VFD Trim is correct) and Fluid Drawdown path (Emergency Shutdown is correct + VFD Trim shown as contraindicated option that still works to demonstrate consequence).
   - **h1Seized state:** If user clicks VFD Trim during Fluid Drawdown, `h1Seized = true` → split card shows `❌ Pump Seized — Sand Bridged Downhole` diagnostic with explanation. Professional, non-theatrical.
   - **executeH1Shutdown():** New method for safe Fluid Drawdown resolution. Cancels degrade, marks resolved, shows green success text.

### Known Design Decisions (Session I):
- (a) No CSS animations for seizure state — inline styles in the split card are sufficient and more professional.
- (b) VFD Trim button during Fluid Drawdown is intentionally still clickable (shows as red warning) so the presenter can demonstrate the consequence path without it being a dead end.
- (c) `h1FaultType` is tracked in Vue state (not derived from API) — it's set at inject time and cleared on reset.
- (d) `_startAdvisorStream()` still uses the `h1GemmaFinding` from the API (which is now fault-type-aware) rather than hardcoded text.

### Next Tasks (Session J):
1. **Operating Envelope context banner:** When `h1PumpOffExcluded` is true (Gas Lock), the existing `.h1-pumpoff-excluded` banner text is accurate. When `h1GasLockExcluded` is true (Drawdown), the center section still shows the old Gas Lock text. Update the envelope section `v-if` conditions to show the correct exclusion text for each scenario.
2. **Status Banner text for Fluid Drawdown:** The `h1-sb-msg` when `h1Injected && !h1Recovering && !h1Resolved` always says `"GAS LOCK ACTIVE"` regardless of `h1FaultType`. Add a `v-if` condition to show `"FLUID DRAWDOWN ACTIVE"` or `"GAS LOCK ACTIVE"` based on `h1FaultType`.
3. **Optional — Phase 5+ MLOps Integrity:** Train the `esp_thermal` XGBoost model and wire it into `vizier_optimize()` to eliminate the H3 static polynomial.

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- Batch all edits to same file in ONE `replace_in_file` call
- ALL kubectl/gcloud commands require `source .env &&` prefix
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
