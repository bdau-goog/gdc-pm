# Next Session Prompt — GDC Edge AI Demo (Operational State)

**Date:** June 4, 2026 (Session Q end — Phase-plane chart, SCADA CSS gauges, AI lead-time panel, LLM re-triggering, context-fusion server fix)
**Git Head:** `245e50a` — clean working tree
**fault-trigger-ui image digest:** `sha256:3ee29db0e41e93dbfb503481e231201835c291085576164fb3778e0889126e9a`
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
- All pods 1/1 Running · new fault-trigger-ui pod (post 245e50a rollout)
- ollama_online: True · model: gemma4:latest
- field_intel: ~80–120 rows · rag_documents: 18 rows

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

Also read the **last 2 entries** in SESSION_LOG.md (Sessions Q and P).

---

## STEP 3: What Was Just Deployed (Session Q)

Two commits shipped and verified:

### Commit 1 (a4cb95d) — Server-side context fusion fix
- `/api/inject/degrade` now INSERTs a seed `field_intel` row (Tour 2 Shift Note, GVF 78%, GOR 1310 scf/bbl) immediately on gas_lock inject
- `adjust_rul_with_documents()` matches "estimated at 78%" regex → applies 0.6× multiplier
- **Verified:** `time_to_scada_minutes: 17.9` vs `adjusted_rul_minutes: 10.7` → **7.2 min real context-fusion gap**

### Commit 2 (245e50a) — H1 visual redesign
1. **Phase-plane chart** replaces the broken flat-line "Minutes Until Failure" chart
   - X axis: Motor Winding Temp (°F), Y axis: Motor Amps (A)
   - Green safe zone / amber warning / red gas-lock zone (background shapes)
   - SCADA alarm lines: Amps < 50A (horizontal dashed red), Temp > 280°F (vertical dashed red)
   - Scatter trail of last 20 operating points (purple line + dots)
   - Current operating point: large color-coded dot (green/amber/red)
   - **The point moves into the red zone during gas lock — before crossing either SCADA line**

2. **SCADA CSS gauge cluster** replaces the confusing normalized-delta chart
   - 4 horizontal bars: PIP / Amps / Temp / Vib
   - Each bar has a colored fill (width = % of range) + red tick mark at SCADA alarm threshold
   - Footer: "⚠ PIP + Amps declining — still above SCADA alarm limits" during fault

3. **AI Lead-Time Advantage panel** (post-inject, below gauges)
   - Sensor-only model: `time_to_scada_minutes` (orange)
   - Context-fused (RAG): `adjusted_rul_minutes` (orange)
   - RAG contribution: real gap from AlloyDB (green, ~7 min)
   - Label: "Shift note + GOR lab report fused via AlloyDB RAG"

4. **Vue `watch:` block** for LLM re-triggering
   - `h1FeedItems` watcher: new document at top of feed → `_triggerAdvisoryUpdate('feed', newItem)`
   - `h1OptALabel` watcher: VIABLE→MARGINAL → urgency update; MARGINAL→EXPIRED → final warning

5. **`_triggerAdvisoryUpdate(type, item)` method** — calls `/api/agent/chat` with live sensor context, streams response appended below "── GDC Advisor · T+Xm ──" separator

6. **Scheduled advisor updates** at T+50s and T+2min after inject (setTimeout-based)

---

## STEP 4: What Still Needs Visual Verification

Load http://gdc-pm.bdau.io → Detect tab, click "Inject Gas Lock":

1. **Phase-plane chart** — operating point (dot) should start in green safe zone, migrate toward/into red gas-lock zone as amps decline and temp rises
2. **SCADA gauge bars** — PIP and Amps bars should visibly shrink; status text changes to "⚠ Sensors changing — no alarm yet"
3. **AI Lead-Time Advantage panel** — appears post-inject showing ~7 min RAG gap
4. **Advisor re-triggers** — wait ~50s for the second Gemma assessment to appear below the separator line
5. **Context chips** in dual-reality bar activate in sequence (shift note, lab GOR↑, VFD events, API RP 11S)

---

## STEP 5: Next Implementation Task — H2 (Discern) Tab Redesign

After H1 is visually verified, implement H2 per DEMO_MASTER.md §5:
- Two-line primary chart: Vibration (rising, orange) + Motor Temperature (flat, blue) — same Y-axis — **the single most visual proof of slug flow vs bearing wear**
- Evidence wall with H2-specific chips (6 sources activating)
- GDC Advisor auto-starts on inject: *"$1,500 truck roll vs $150,000 pump pull"* verdict
- Reuse all H1 CSS patterns (`.h1-advisor`, `.h1-lead-time`, `.sgg-*`, Vue watchers)

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
