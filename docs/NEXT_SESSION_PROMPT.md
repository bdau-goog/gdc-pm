# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 8, 2026 (Session J — H1 Discern tab clean-slate deployed)
**git head:** `5d3a9c8` (feat(ui): Session J — H1 Discern tab clean-slate rewrite)
**fault-trigger-ui image:** `sha256:2fe914a6` (1/1 Running — Session J)
**inference-api image:** `sha256:d1194989` (1/1 Running — unchanged)
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
source .env && kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
source .env && kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected when healthy:**
- All 8 pods 1/1 Running · ollama replicas: 1
- ollama_online: True · model: gemma4:latest
- field_intel: ~2 · rag_documents: 18

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Next Implementation Task — Session K

### What Was Completed in Session J

The H1 "Discern" tab has been completely rebuilt as the **Double-Blind Choice Game**. All 10 steps from NEXT_SESSION_PROMPT (Session I+1) are done and deployed:

✅ Single `⚡ Inject Unloading Anomaly` button (random 50/50 Gas Lock / Fluid Drawdown)  
✅ Left 40% telemetry column: 4 sensor bars + dual-axis Plotly PIP/Amps trend chart  
✅ Right 60% Decision Console with `🟡 SCADA View` / `🟢 GDC Advisor` sub-tabs  
✅ SCADA View: ambiguous dilemma, blind gamble buttons, outcome states  
✅ GDC Advisor: pgvector RAG card (click-through), CSS Dynamic Wellbore Digital Twin, verdict, informed buttons  
✅ Override confirmation modal (2-click deliberate bypass for VFD trim during Drawdown)  
✅ Baker Hughes Acoustic Sonic Log modal + Operator Shift Handover Note modal  
✅ Status banner hides fault type until `h1RagRevealed = true` (2s post-injection)  
✅ All CSS: sub-tabs, wellbore schematic, bubble/sand animations, field doc tables  

### Next Tasks (in priority order)

**Task K-1 — Live Demo Walk-Through Smoke Test**
- Open http://gdc-pm.bdau.io in a browser, navigate to **Detect** tab (now shows "Discern")
- Click ⚡ Inject Unloading Anomaly
- Verify: (a) SCADA tab shows ambiguous state + blind gamble buttons; (b) GDC Advisor shows "⏳ Retrieving…" then RAG card appears at ~2s; (c) Wellbore schematic renders correctly for whichever fault was injected; (d) Click the RAG card → professional field doc modal opens; (e) Try wrong action from GDC tab → override modal fires
- **If any visual issues**: use `kubectl logs deployment/fault-trigger-ui -n gdc-pm --tail=50` to check for Python errors

**Task K-2 — Tab Navigation Label Fix**
- Header tab still says "Detect" (line ~25 in index.html). Per DEMO_MASTER.md §7, the tab should read "Discern".
- Fix: `<div class="hdr-tab" ... @click="setMainTab('horizon1')">Detect</div>` → `>Discern</div>`
- Also: "Discern" tab currently says "Discern" in H2 banner (`🟡 Horizon 2 — Mid-Term`). H2 tab in header says "Discern" but should say "Classify".
- Batched single replace_in_file to fix both tab labels.

**Task K-3 — H2 "Classify" Tab Layout Upgrade** (from DEMO_MASTER.md §5)
- Slug Flow scenario needs same clean SCADA/GDC split treatment as H1.
- Current H2 is functional but lacks the SCADA vs GDC dual-pane narrative.

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| Header tab "Detect" label | ⚠ Stale | Should read "Discern" — H1 tab only |
| H2 header tab label | ⚠ Stale | Reads "Discern" in header, should be "Classify" |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- Batch all edits to same file in ONE `replace_in_file` call
- ALL kubectl/gcloud commands require `source .env &&` prefix
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
