# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 10, 2026 (Session AG — Sprint 1 ✅ + Sprint 2a ✅; H1 Briefing Panels 1&2 deployed)
**git head:** `d41d27b` (feat(sprint2a): H1 Briefing panels 1&2 — This Well + What is an Unload?)
**fault-trigger-ui image:** `sha256:7d22b015` (Session AG — Sprint 2a deployed)
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

## STEP 3: Session AG COMPLETE ✅ — Next Task is Sprint 2b

### Session AG Summary
Sprint 1 + Sprint 2a complete this session.

- **Sprint 1** (commit `9691e93`): All 5 integrity violations fixed — RTOC-sovereign framing, 3 sovereignty pillars, IEC 62443/Purdue, retired 200GB/VSAT/E-House/NERC-CIP errors, SCADA path label, industry generalization. Deployed `sha256:3d6009a2`.
- **Sprint 2a** (commit `d41d27b`): H1 Briefing container + Panels 1 & 2. `h1BriefingMode: true` default state; `v-else` wraps existing scenario replay. Panel 1 = This Well (scope card + nominal wellbore SVG + 4 green sensor tiles). Panel 2 = What is an Unload? (2×2 animated tiles — PIP/Amps declining with `h1-brief-decline-bar` CSS keyframe, Temp/Vib flat). "Skip to Scenario →" + "▶ Run the Scenario" CTAs wired to `h1BriefingMode=false; loadH1Scenario()`. Deployed `sha256:7d22b015`.

**Deployment note (permanent):** `kubectl rollout restart` with `:latest` does NOT pull new images (GKE node cache). Always use:
```bash
kubectl set image deployment/fault-trigger-ui -n gdc-pm \
  fault-trigger-ui=us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui@sha256:<digest>
```

### NEXT TASK — Sprint 2b: H1 Briefing — Panel 3 (One Signature, Two Causes)
**File:** `gke/fault-trigger-ui/index.html` (ONE batched replace_in_file call)
**Spec:** `docs/SPRINT_PLAN.md §Sprint 2b` and `DEMO_MASTER.md §4`

Panel 3 — *One Signature, Two Causes* — the most visually complex panel:
- Full-screen split: LEFT = Gas Lock wellbore (annulus full, bubbles entering pump) · RIGHT = Drawdown wellbore (fluid level falling)
- Below BOTH: the SAME PIP/Amps trace (proving identical sensor output)
- Animated: bubbles rising left, fluid level dropping right — both produce identical chart below
- Text: "On this well's sensor, the live decline looks the same."
- Navigation: [← Back] [Next →]

Also add `h1BriefingPanel` to the progress dots and stepper (extend to 6 dots, grey out 3–6 as "coming in Sprint 2c–2e").

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| "200 GB/day for 38 wells" (info panel) | ✅ FIXED Session AG | Deleted; replaced with sovereignty framing |
| "VSAT round-trip 15–25 minutes" (info panel) | ✅ FIXED Session AG | Deleted |
| "E-House on the well pad" deployment framing | ✅ FIXED Session AG | Replaced with RTOC / sovereign data center |
| "No cloud dependency for the decision" tagline | ✅ FIXED Session AG | Replaced with "No public-cloud dependency — sovereign, outage-immune" |
| NERC-CIP cited for upstream O&G | ✅ FIXED Session AG | Scoped to P&E BES only in all occurrences |
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
- **Deploy with explicit digest** — `kubectl rollout restart` with `:latest` does NOT pull from registry on this cluster (node cache). Always use `kubectl set image ... @sha256:<digest>`
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,400 lines, `index.html` ~2,760 lines, `app.js` ~2,300 lines — always grep for line numbers first
- H2 uses inference-api (not local esp_classifier.bst) — local .bst is 4-class without slug_flow
- Gas Lock / Drawdown STATE identical on intake-only wells — premise is now "decision window ambiguity" not "physically impossible forever"
