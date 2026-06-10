# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 10, 2026 (Session AQ-wrap — pattern locked, ready to build H2/H3)
**git head:** `81d3e40` (to be updated after this commit)
**fault-trigger-ui image:** `sha256:2fd95932a9b8ae9ca0eb6c961cf9a031b264a97ad69705fb8197a05999414a9a`
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Five Commands First

```bash
source .env && echo "PROJECT=$GOOGLE_CLOUD_PROJECT KUBECONFIG=$KUBECONFIG"
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected:** 8 pods 1/1 · ollama_online: True · gemma4:latest · field_intel: 5-6 · rag_docs: 18

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY — especially §4.5 Briefing Pattern Spec)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: SIGN-OFF FIRST (≤5 min) — then build

Before writing a single line of HTML, get yes/no on these 5 questions:

1. **Beat taxonomy** — H2: Setup/Hook/Decision · H3: Opportunity/Tradeoff/Optimization — OK?
2. **H2 Panel-3 title** — "Do NOT Pull — It's a $1,500 Fix" — OK?
3. **H3 framing** — optimization with the OEM thermal-limit doc as the "context guardrail" thread connecting it to L3 — OK?
4. **CTA labels** — H2 `▶ Run the Scenario` · H3 `▶ Run the Optimization` — OK?
5. **Palette toning** — apply toned-down chrome (§4.5 values) to H1 briefing **in the same pass** as building H2? Or H1 retrofit deferred?

---

## STEP 4: TONIGHT'S BUILD SEQUENCE

**Sprint 0 (optional, fold into Sprint 3):** Tone H1 briefing palette to §4.5 values — border 0.20–0.22, fill 0.04–0.07. One `replace_in_file` on `index.html`.

**Sprint 3 — H2 Briefing (3 panels):**  
Architecture: `h2BriefingMode: true`, `h2BriefingPanel: 1`, `h2P2Scrub: 0` in `app.js`. Add `v-if="h2BriefingMode"` briefing container before `<template v-else>` wrapping the existing H2 scenario. Add `← Briefing` button to H2 header. Reuse all H1 briefing CSS classes (no new keyframes).

Panel wireframes — see §4.5 + NEXT_SESSION_PROMPT archive or PLAN MODE session AQ-continued:
- **P1 of 3 — The Equipment:** "What is Slug Flow?" · Left: callout + WELL ESP-ALPHA-3 info box · Right: surface flowline SVG (slug pulses) + healthy pump/motor
- **P2 of 3 — The Hook:** "Why It Looks Like a Failing Pump" · Scrubber (h2P2Scrub) · 2×2 tiles: VIB amber/rising, TEMP green/flat, PIP slate/dipping, AMPS slate/dipping · Blue callout: "Bearing failure raises BOTH. Here temp is flat."
- **P3 of 3 — The Decision:** "Do NOT Pull — It's a $1,500 Fix" · SCADA-sees (slate) vs GDC-retrieves (amber/green) two-column layout · 3 docs revealed · Quote + CTA

**Sprint 4 — H3 Briefing (3 panels) + H3 header rename:**  
`h3BriefingMode: true`, `h3BriefingPanel: 1` in `app.js`. Same briefing wrapper pattern. Rename H3 header: `"Optimize — VFD Bayesian Optimization"`.
- **P1 of 3 — The Opportunity:** "Oil Price Jumped 40%" · Left: callout + VFD tradeoff info box · Right: Hz-vs-revenue bar zones (CSS)
- **P2 of 3 — The Tradeoff:** "Speed Makes Money — and Heat" · CSS table (4 Hz rows, temp, status, revenue) · Quote + IEC 60085 citation
- **P3 of 3 — The Optimization:** "Find the Edge, Respect the Limit" · Left: how-it-works bullets · Right: CSS Pareto sketch · Quote + CTA

**Sprint 5 — Video Script + Veo concepts:**  
New `docs/VIDEO_SCRIPT.md` — 8 segments, ~5 min. Three Veo intro concepts.

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Briefing — all 6 panels | ✅ COMPLETE Session AQ | Batch 2 deployed |
| H2 Briefing panels | ⚠️ SPRINT 3 | Zero infrastructure |
| H3 Briefing panels | ⚠️ SPRINT 4 | Zero infrastructure |
| DEMO_MASTER §4.5 | ✅ WRITTEN Session AQ-wrap | Briefing Pattern Spec — canonical |
| H1 palette toning | ⚠️ SPRINT 0 | User confirmed "tone down 2 notches" — fold into Sprint 3 call |
| Video Script | ⚠️ SPRINT 5 | docs/VIDEO_SCRIPT.md does not exist |
| OEM Troubleshooting Guide modal | ⚠️ BATCH 3 | H1 Doc 3 no click handler — low priority |
| SPE-174536 in Zone-1 verdict | ⚠️ LOW | Acceptable in ⓘ context |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — verify with `kubectl exec grep`
- **Batch all edits to same file in ONE `replace_in_file` call**
- **Deploy with explicit digest** — `kubectl rollout restart :latest` does NOT pull from registry
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,400 lines · `index.html` ~3,200 lines · `app.js` ~2,300 lines — grep first
- **Wireframes → sign-off → HTML** (never write HTML without sign-off)
- H2 uses inference-api (not local esp_classifier.bst)
