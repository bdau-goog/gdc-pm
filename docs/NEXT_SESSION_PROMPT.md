# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 10, 2026 (Session AN — ISA-101 color/UX pass + Batch 1 scenario fixes deployed)
**git head:** `074d803` (fix(scenario): ISA-101 color/UX pass — P6 text bump, neutral SCADA cards, color-scoped action cards, Formation overflow, animation snap, y-axis labels, narration removed)
**fault-trigger-ui image:** `sha256:0a50d175109affb718e3ca3a5c8cf81117d7c2384a80a58c37f216b9dd214b5c` (Session AN)
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

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Next Task — FOUNDATIONAL FIRST, then Batch 2 / Stage B

### ⚠️ FOUNDATIONAL (resolve before any H1 code — everything else is blocked on this)

**Is the H1 document-fusion premise strong enough to lead the demo, or is it a supporting act for H2?**

After this session's honest review, the following concessions are locked:
- **Detection speed:** conceded to advanced APM (SmartSignal/PRiSM/Mtell tie us on multivariate ML). "GDC detects before SCADA" is true only vs a conservative threshold trip, not vs best-of-breed. Not a durable claim.
- **Document access:** non-exclusive. The sonic log, GOR report, shift note are all in the operator's systems. We have no exclusive access advantage.
- **Shut-in is the safe default:** a good engineer shuts in. It's safe for both gas lock and drawdown. The "forced bad choice" frame is false.

**What survives:** Fleet-scale document-fusion efficiency — GDC retrieves and correlates scattered docs against live telemetry in seconds across 200-500 wells, enabling confident production-preserving action instead of reflexive shut-in. This is real but is an *efficiency/workflow* claim, not a categorical superiority claim.

**The "contrived" feeling traces here:** We've been framing an efficiency claim as a SCADA-competition victory. Every honest concession weakened the frame because the frame was wrong.

**Two paths — ruling needed at session start:**
- **Path A:** Reframe H1. Drop the SCADA race. Stage H1 as "sovereign cited-evidence analyst" — alarm fires (both systems, same time), GDC hands the operator an auditable document-fusion verdict in seconds vs. hours of manual research, at fleet scale. No lead-time claim. L3 only.
- **Path B:** Consider H2 (slug flow) as the stronger lead scenario. H2's wrong-action consequence ($150k unnecessary pump pull) is crisper, cleaner, and doesn't have the "but you can just shut in safely" exposure. H1 becomes the pattern-setter; H2 demonstrates the concrete value.

**No H1 code until this ruling lands.** Timeline relabel, lead-time removal, Stage B panels, and the Alarm→PNR reframe are all downstream and on hold.

---

### Batch 2 — Next Session Tasks (queued, pending foundational ruling)

**2A — HP-HMI Color Full-Compliance Pass (no content approval needed, code-only):**
Per ISA-101.01 §5 / HP-HMI: gray is normal, color = alarm only. Current violations to fix in ONE batched `replace_in_file`:
- GDC Recommended/Contraindicated card backgrounds → remove green/red tint (pure `var(--surf)` or transparent)
- Card borders → keep thin, reduce to ~30% opacity
- Zone-1 verdict box bg → near-black (`rgba(15,23,42,0.8)`), no green/orange tint
- Zone-1 headline color → soften to ~60% opacity or wrap in small colored status pill
- Result: card color appears ONLY as a thin border + header pill, body is all `var(--text2)`

**2B — Requires User Copy Sign-Off Before Code (G1–G6 gate):**
1. **OEM Troubleshooting Guide modal** — Doc 3 in evidence panel has NO click handler. Need to author fictional-vendor content (G1) showing procedure, not verdict (G2), with appropriate cosine sim context. Draft copy for user review first.
2. **Additional doc cards** — Workover/Completion record establishing sand history (G3: concerning-in-hindsight, not smoking gun). Optional: offset-frac report. Draft copy for user review first.

### Stage B — Content Reworks (Panels 1, 2, 3, 6, 7) — pending "GDC detects before SCADA" ruling
See NEXT_SESSION_PROMPT.md Session AM for full Stage B panel table.

**Open ruling still needed:**
- **"GDC detects before SCADA" claim** — strip from briefing? (rec: yes — rest on L3 moat)

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| Financial Justification modal raw {{ }} | ✅ FIXED Session AJ | div balance net 0 |
| Panel 2 animated bars (infinite loop) | ✅ FIXED Session AL | h1P2Scrub scrubber |
| Panel 3 infinite bubble/drain loops | ✅ FIXED Session AL | opacity/scaleY scrubber-driven |
| Panel 1+4 flicker (color-emoji repaint) | ✅ FIXED Session AM | .h1-ok-dot + CSS squares |
| Panels 4/5/6 build shimmer (@keyframes) | ✅ FIXED Session AM | opacity-only, no transforms |
| Field Link (bandwidth claim, DEMO_MASTER §9) | ✅ REMOVED Session AM | wan-badge span deleted |
| ← Briefing re-entry button | ✅ ADDED Session AM | h1BriefingMode=true |
| ISA-101 card color scoping | ✅ FIXED Session AN | `.h1-card-green .h1-card-header` scopes color to header only |
| SCADA leading-the-witness text | ✅ FIXED Session AN | Card A guidance stripped; Card B neutralized |
| Narration sentence in evidence panel | ✅ FIXED Session AN | Deleted (was out of place, not evidence) |
| Formation box clipped at right | ✅ FIXED Session AN | overflow:visible on zone-3 container |
| Bubble/sand animation near-invisible | ✅ FIXED Session AN | Opacity snaps to 0.55 at gdc_detect_idx |
| Y-axis labels bare units only | ✅ FIXED Session AN | Descriptive: "Pump Intake Pressure (PSI)" etc. |
| Panel 6 of 6 text too small | ✅ FIXED Session AN | kicker 0.68rem, h2 1.85rem, rows 0.70rem |
| OEM Troubleshooting Guide no click handler | ⚠️ BATCH 2 | Doc 3 needs modal + content (G1–G6 gate) |
| STATE-vs-CONTEXT premise | ✅ LOCKED | Claim Ledger PREMISE row |
| SPE-174536 citation | ⚠️ UNVERIFIED | Using SPE-170776; 4.2 ft/s = representative |
| "GDC detects before SCADA" in Panel 2 + scenario | ⚠️ PENDING RULING | My rec: strip from briefing; keep as model output in scenario only |
| Panel 1 vertical space + lead-in copy | ⚠️ STAGE B | Too sparse; dives into VFD/sand too early |
| Panel kicker copy (Setup/Event/Hook/Moat/etc.) | ⚠️ DEFERRED | Simple pass after structure lands |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — use `node scripts/ui_smoke.mjs` or `curl`
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- **Deploy with explicit digest** — `kubectl rollout restart` with `:latest` does NOT pull from registry
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,400 lines, `index.html` ~3,210 lines, `app.js` ~2,300 lines — grep for line numbers first
- H2 uses inference-api (not local esp_classifier.bst)
