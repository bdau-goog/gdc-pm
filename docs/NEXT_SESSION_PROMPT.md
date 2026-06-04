# Next Session Prompt — GDC Edge AI Demo (Operational State)

**Date:** June 4, 2026 (Session O end — H1 chart redesign + SVG full-height fix deployed)
**Git Head:** `ecb2316` — clean working tree
**fault-trigger-ui image digest:** `sha256:272dfff07c020cf45b61069e61ffd967cfe87237873796861db19ed632f5e36f`
**Branch:** `feature-trio-scenarios` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected healthy:**
- All pods 1/1 Running · new fault-trigger-ui pod (post ecb2316 rollout)
- ollama_online: True · model: gemma4:latest
- field_intel: ~99–110 rows · rag_documents: 18 rows

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

Also read the **last 2 entries** in SESSION_LOG.md (Sessions O and N).

---

## STEP 3: Next Implementation Task — Verify H1 Demo Flow + Begin H2

### What Was Just Deployed (Session O)

All H1 chart redesign changes from DEMO_MASTER.md §4 are live:

1. ✅ **Primary chart** — "⏱ Minutes Until Pump Failure" with 3 lines:
   - Gray (SCADA flat at 120) · orange dashed (sensor-only from `d.time_to_scada_minutes`) · solid orange (context-fused from `d.adjusted_rul_minutes`)
   - Shaded fill + annotation bracket "⚡ Context Fusion: −Nm" when gap > 0
   - Pre-injection: all 3 lines flat at 120 (calm nominal state)
2. ✅ **Secondary chart** — "📡 SCADA Raw Telemetry" (id=`h1-scada-chart`) with PIP/Amps/Temp sensor tabs and "✓ No SCADA alarm triggered" annotation
3. ✅ **Layout** — well strip moved to far right (CSS `order:5`, 180px wide) via `.h1-body>:nth-child(2){display:none}` to hide the old left splitter
4. ✅ **SVG callout labels** — "Intake: Nominal" → "Intake: 68% GVF ⚠" and "Motor: Cooling normal" → "Motor: Cooling lost ⚠" on inject
5. ✅ **"Copilot" → "GDC Advisor"** — all CSS classes (`.h1-advisor`, `.h1-advisor-hdr`, etc.), Vue data props (`h1AdvisorHtml`, `h1AdvisorStreaming`, `h1AdvisorTimer`, `h1AdvisorText`), method `_startAdvisorStream`, HTML labels
6. ✅ **Dynamic feed poll** — `h1FeedPollInterval` every 15s during active fault, cleared on reset
7. ✅ **NS handle** — now always visible between primary and SCADA chart (no longer gated by `v-if="h1Injected"`)
8. ✅ **Well strip SVG full-height** — SVG wrapped in `flex:1; position:relative` div, SVG `position:absolute; width/height:100%` so it fills the column rather than being clipped to its 200×265 aspect ratio

### First Task: Verify H1 End-to-End

Load http://gdc-pm.bdau.io → Detect tab:
- Pre-injection: 3 flat lines at 120 min, "📡 SCADA — No alarm triggered" annotation on SCADA chart ✓
- Click "Inject Gas Lock": GDC lines begin declining, SCADA line stays at 120, bracket appears when context-fused < sensor-only ✓
- Well strip: callout labels update on inject ✓
- GDC Advisor (not "Copilot") header streams diagnosis ✓
- Feed poll refreshes every 15s ✓
- Window of Options appears below SCADA chart ✓

### Second Task: H2 (Discern) Tab Redesign

After H1 is verified visually, implement H2 per DEMO_MASTER.md §5:
- Two-line primary chart: Vibration (rising, orange) + Motor Temperature (flat, blue) — same Y-axis
- H2 dual-reality bar with 6 evidence chips activating in sequence
- Well schematic: pump body glows GREEN (healthy), surface flowline shows slug animation
- GDC Advisor auto-starts on inject with "$1,500 vs $150,000" diagnostic verdict
- Reuse all new H1 CSS patterns (`.h1-advisor`, `.h1-advisor-pane`, `.dr-bar`)

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — no `browser_action` tool
- `feature-trio-scenarios` stays separate from `main`
- XGBoost `*.ubj` models — do not retrain
- Fleet Operations tab: do NOT re-add
- Financial case: LLM only, no static financial cards
- Token budget: batch all edits to same file in ONE replace_in_file call
- Correct registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- "Copilot" is a Microsoft product name — do NOT use it anywhere in the UI
