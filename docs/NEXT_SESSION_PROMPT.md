# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 10, 2026 (Session AF — Strategy locked; DEMO_MASTER rewritten; SPRINT_PLAN.md created)
**git head:** `0c35a8f` (docs(strategy): Session AF)
**fault-trigger-ui image:** `sha256:2f5d3cab` (Session AE — no UI changes this session)
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Five Commands First

```bash
source .env && echo "PROJECT=$GOOGLE_CLOUD_PROJECT KUBECONFIG=$KUBECONFIG"
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents; SELECT COUNT(*) FROM telemetry_events;"
```

**Expected when healthy:**
- All 8 pods 1/1 Running · ollama replicas: 1
- ollama_online: True · model: gemma4:latest
- field_intel: 5 · rag_documents: 18 · telemetry_events: > 1,000,000

---

## STEP 2: Read DEMO_MASTER.md + SPRINT_PLAN.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md    # Full spec — Session AF rewrite
cat ~/gdc-pm/docs/SPRINT_PLAN.md    # Sprint breakdown + panel specs
```

---

## STEP 3: Session AF COMPLETE ✅ — Next Task is Sprint 1

### Session AF Summary
Pure strategy session — no UI code written. Major decisions locked:
- **STATE-vs-CONTEXT** is the universal moat (replaces "physics-impossibility"). Sensors report STATE; decisions need CONTEXT in documents.
- **RTOC-sovereign canonical** deployment (not pad E-house). Sovereignty pillars: OT-segmentation/self-sufficiency (IEC 62443), data residency, governance/IP.
- **Horizontal positioning confirmed:** 4-industry mapping (O&G / P&E / Manufacturing / Mining) baked into DEMO_MASTER §3.
- **5 integrity fixes locked:** delete "200 GB/day" (wrong 1000×), delete "VSAT 15–25 min" (wrong physics), retire "decision at pad" (RTOC), retire "no cloud dependency" (replace with sovereignty framing), scope NERC-CIP to P&E BES only.
- **H1 premise corrected:** intake-only scoping + sand-as-stakes (not "physically identical forever").
- **SPRINT_PLAN.md** created — 5–6 sessions to full completion.

### NEXT TASK — Sprint 1: How It Works Reconciliation
**File:** `gke/fault-trigger-ui/index.html` (ONE batched replace_in_file call)

Six changes — all in one batched call:
1. Rewrite `ⓘ "Why Not Cloud?"` panel (lines ~1809–1817) → 3 sovereignty pillars + IEC 62443/Purdue/NERC-CIP scoping (fixes 200 GB/day + VSAT latency)
2. Retitle deployment → "Operator RTOC / sovereign data center (inside the security perimeter)"
3. Add one muted anchor line: "Runs inside the operator's security perimeter — IEC 62443 / NERC-CIP (P&E) · sovereign, outage-immune"
4. Retire "no cloud dependency for the decision" → "No public-cloud dependency — sovereign, outage-immune"
5. Reframe SCADA path label → "control-layer telemetry path" + APM-add-ML note
6. Add one "generalizes across industrial verticals" line below the TAGS / TAG-PATTERNS / DOCUMENTS centerpiece

After Sprint 1: deploy + verify with grep. Then Sprint 2 (H1 Briefing, 6 panels animated).

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| "200 GB/day for 38 wells" (info panel) | ❌ OPEN Sprint 1 | Wrong by ~1000× for scalar SCADA. Fix in Sprint 1. |
| "VSAT round-trip 15–25 minutes" (info panel) | ❌ OPEN Sprint 1 | Physically wrong (~600 ms). Fix in Sprint 1. |
| "E-House on the well pad" deployment framing | ❌ OPEN Sprint 1 | Should be RTOC. Fix in Sprint 1. |
| "No cloud dependency for the decision" tagline | ❌ OPEN Sprint 1 | Replace with sovereignty framing. Fix in Sprint 1. |
| NERC-CIP cited for upstream O&G | ❌ OPEN Sprint 1 | NERC-CIP = BES (power) only. Fix in Sprint 1. |
| All Session AE RT fixes | ✅ FIXED Session AE | 280°F, IEC 60085, scada_rule_fired, lead-time banner |
| STATE-vs-CONTEXT premise | ✅ LOCKED DEMO_MASTER §3 | Claim Ledger PREMISE row added |
| Sand/shut-in physics | ✅ LOCKED DEMO_MASTER §4.1 + P5-A/B/C | Scoped: moderate-sand well · AR-trim |
| SPE-174536 citation | ⚠️ UNVERIFIED | Replaced with SPE-170776 in Claim Ledger P4; 4.2 ft/s = representative, not a constant |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — use `node scripts/ui_smoke.mjs` instead
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,400 lines, `index.html` ~2,760 lines, `app.js` ~2,300 lines — always grep for line numbers first
- H2 uses inference-api (not local esp_classifier.bst) — local .bst is 4-class without slug_flow
- Gas Lock / Drawdown STATE identical on intake-only wells — premise is now "decision window ambiguity" not "physically impossible forever"
