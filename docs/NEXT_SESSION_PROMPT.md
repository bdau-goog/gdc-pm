# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 10, 2026 (Session AP — single-alarm collapse + Bayes softening deployed)
**git head:** `7c17220` (fix(h1-single-alarm): collapse detection race to single shared alarm moment, soften Bayes posterior to 93%, remove contraindicated path)
**fault-trigger-ui image:** `sha256:7849e9e3f9bcac0e50b96165fa6e0ac12b29a00deebb3520db284b8983b4fecb` (Session AP)
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
- field_intel: 5-6 · rag_documents: 18 · telemetry_events: > 1,000,000

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: NEXT TASK — H1 BRIEFING PANEL REWORK (Batch 2)

> **✅ Session AP completed Batch 1:** The detection race is structurally gone from the scenario runtime.
> Single `alarm_idx`, both views reveal simultaneously, Bayes posterior 93.1%, no contraindicated card,
> no seizure path. Committed `7c17220`, deployed, verified live.

### What's still outstanding (Batch 2 — briefing panels):

**Hard constraints (from NEXT_SESSION_PROMPT AO — still apply):**
1. **Remove sand-stakes row from Panel 1 "The Setup".** Sand is not a setup fact; it's the decision-context reason shut-in is the conservative default. Move to Panel 5 (where it already belongs).
2. **Panel 2 "What is an Unloading Event?"** — remove dev-leak text `(Sprint 2b–2e)` and the "GDC detects before any SCADA threshold" line from the callout. Both are racing claims.
3. **Panel 3 "One Signature, Two Causes"** — drawdown footer still says "VFD trim catastrophic ~$150k" and shows a `SAND` zone. Since Batch 1 removed the catastrophe path from the scenario, the briefing should match: soften to "shut-in is the correct action — sand makes trim risky in this well type," not "catastrophic seizure." The $150k and sand are still ON SCREEN here (briefing) — user confirmed sand stays as the policy rationale, just not the catastrophe framing.
4. **Panel 5 "Why Sand Changes Everything"** — the user wants this REPLACED with a new "How Operators Decide Today" panel. See wireframe in NEXT_SESSION_PROMPT AO §STEP 3 for the agreed content. Sand is the reason shut-in is the conservative default, not a $150k catastrophe story.
5. **Panel 2 callout leak** — strip `Sprint 2b–2e` reference and the "detects before SCADA" line.

### Agreed 6-panel arc (for reference):
1. **What We're Watching — A Mature ESP** (rework P1: de-sand the setup)
2. **What is an Unloading Event?** (keep P2, strip dev-leak line)
3. **Two Causes, One Signature** (rework P3 footer: soften $150k to "riskier if drawdown" consistent with scenario)
4. **STATE vs CONTEXT** (keep P4 as-is — perfect)
5. **How Operators Decide Today** (NEW — replace sand matrix; sand = policy rationale, no catastrophe)
6. **This Pattern Is Universal** (keep P6 as-is)

### New Panel 5 content (agreed wireframe):
```
Panel 5 of 6 — The Decision    How Operators Decide Today
[ moderate-sand well · AR-trim ]

⚠ ONE ALARM: UNDERLOAD — cause unknown → gas lock OR drawdown?

     [ VFD TRIM ]              [ SHUT-IN ]
   right for gas lock         safe for BOTH causes
   stays online ~$2.5k        but DEFERS PRODUCTION
   risky if drawdown          + restart $3–8k · every time
   (sand makes it costly)

"Safe is not free. The protective shut-in is paid on every
 ambiguous alarm — including the ones that were only gas lock."
```

### Method:
1. Read current P1/P2/P3/P5 content (already in context from Session AP; use `grep -n` first)
2. Propose revised copy as ASCII wireframes / inline tables for user review
3. Get sign-off on each panel BEFORE writing HTML
4. Batch all 4 panel edits into ONE `replace_in_file` call on index.html

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| Financial Justification modal raw {{ }} | ✅ FIXED Session AJ | div balance net 0 |
| Panel 2 animated bars (infinite loop) | ✅ FIXED Session AL | h1P2Scrub scrubber |
| Panel 3 infinite bubble/drain loops | ✅ FIXED Session AL | opacity/scaleY scrubber-driven |
| Panel 1+4 flicker (color-emoji repaint) | ✅ FIXED Session AM | .h1-ok-dot + CSS squares |
| Panels 4/5/6 build shimmer (@keyframes) | ✅ FIXED Session AM | opacity-only, no transforms |
| Field Link (bandwidth claim) | ✅ REMOVED Session AM | wan-badge span deleted |
| ← Briefing re-entry button | ✅ ADDED Session AM | h1BriefingMode=true |
| ISA-101 card color scoping | ✅ FIXED Session AN | `.h1-card-green .h1-card-header` |
| SCADA leading-the-witness text | ✅ FIXED Session AN | Card A/B neutralized |
| H1 detection-race framing | ✅ FIXED Session AP | Single alarm_idx, both views reveal together |
| H1 Bayes posterior overconfidence | ✅ FIXED Session AP | 99.6% → 93.1% (LRs 3/2/1.6/1.4) |
| H1 contraindicated card + seizure path | ✅ REMOVED Session AP | drawdown both cards → shut-in |
| Tab default landing | ✅ FIXED Session AO | mainTab → 'horizon1'; How It Works → ⓘ Reference |
| Panel 6 Mining row | ✅ REMOVED Session AO | 3 rows remain: O&G / P&E / MFG |
| Panel 1 sand-stakes row ($150k on setup) | ⚠️ BATCH 2 | Needs removal; sand stays in P5 only |
| Panel 2 dev-leak line + detection race text | ⚠️ BATCH 2 | Strip "Sprint 2b–2e" + "GDC detects before SCADA" |
| Panel 3 drawdown footer ($150k seizure) | ⚠️ BATCH 2 | Soften to match scenario (no catastrophe) |
| Panel 5 sand matrix → "How Operators Decide" | ⚠️ BATCH 2 | Full replacement; sand stays as policy rationale |
| OEM Troubleshooting Guide no click handler | ⚠️ BATCH 3 | Doc 3 needs modal + content (G1–G6 gate) |
| STATE-vs-CONTEXT premise | ✅ LOCKED | Claim Ledger PREMISE row |
| SPE-174536 citation (on-screen in GDC verdict) | ⚠️ UNVERIFIED | Still on screen in Zone-1 drawdown text — OK in ⓘ Reference, flag for removal from main verdict |
| SPE-174536 citation in override modal | ⚠️ NOTE | Override modal still references SPE-174536; modal is low-visibility path now |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — use `node scripts/ui_smoke.mjs` or `curl`
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- **Deploy with explicit digest** — `kubectl rollout restart` with `:latest` does NOT pull from registry
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,400 lines, `index.html` ~3,200 lines, `app.js` ~2,300 lines — grep for line numbers first
- H2 uses inference-api (not local esp_classifier.bst)
