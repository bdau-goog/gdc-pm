# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 10, 2026 (Session AH — Sprint 2b ✅ H1 Briefing Panel 3 deployed)
**git head:** `1c02e6b` (feat(sprint2b): H1 Briefing Panel 3 — One Signature, Two Causes)
**fault-trigger-ui image:** `sha256:68948a277` (Session AH — Sprint 2b deployed)
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

## STEP 3: Session AH COMPLETE ✅ — Next Task is Sprint 2c

### Session AH Summary
Sprint 2b complete this session.

- **Sprint 2b** (commit `1c02e6b`): H1 Briefing Panel 3 — "One Signature, Two Causes". Full-screen split: LEFT = Gas Lock (blue fluid column, 3 animated `h1-wb-bubble` rising, pump ⚠ PUMP, green MOTOR ✓) vs RIGHT = Fluid Drawdown (depleted dark casing, `h1-p3-fluid-drain` CSS scaleY animation showing fluid level falling, amber pump ⚠, sand zone near perfs). Bottom strip: identical PIP + Amps declining trace (reused `h1-brief-decline-bar`) with italic quote *"On this well's sensor, the live decline looks the same."* Progress dots extended to 6 (dots 4-6 cosmetically greyed). Panel counter updated to `/6`. Run the Scenario CTA moved from panel 2 → panel 3. CSS: `@keyframes h1-p3-drain` + `.h1-p3-fluid-drain` added to styles.css. Deployed `sha256:68948a277`.

**Deployment note (permanent):** `kubectl rollout restart` with `:latest` does NOT pull new images (GKE node cache). Always use:
```bash
kubectl set image deployment/fault-trigger-ui -n gdc-pm \
  fault-trigger-ui=us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui@sha256:<digest>
```

### NEXT TASK — Sprint 2c: H1 Briefing — Panel 4 (STATE vs. CONTEXT)
**File:** `gke/fault-trigger-ui/index.html` (ONE batched replace_in_file call)
**Spec:** `docs/SPRINT_PLAN.md §Sprint 2c` and `DEMO_MASTER.md §4`

Panel 4 — *STATE vs. CONTEXT* — the moat argument, animated two-column reveal:
- **LEFT column (STATE):** PIP, Amps, Temp, Vib readouts pulse in. Text: "Even a perfect gauge sharpens the STATE. It cannot report what happened last week."
- **RIGHT column (CONTEXT):** Document cards appear one by one — workover record · GOR trend · offset-frac report · shift note. Text: "The deciding context lives here. Not on any sensor."
- Full-width bottom quote: "You cannot instrument your way out of a context gap."
- Navigation: [← Back] [Next →] (advances to panel 5)
- Progress dot 4 activates when at panel 4

Also: extend `v-if="h1BriefingPanel < 3"` → `< 4` for Next button, `===3` → `===4` for Run the Scenario.

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
- `app.py` ~6,400 lines, `index.html` ~2,827 lines, `app.js` ~2,300 lines — always grep for line numbers first
- H2 uses inference-api (not local esp_classifier.bst) — local .bst is 4-class without slug_flow
- Gas Lock / Drawdown STATE identical on intake-only wells — premise is now "decision window ambiguity" not "physically impossible forever"
