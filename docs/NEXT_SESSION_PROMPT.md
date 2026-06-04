# Next Session Prompt — GDC Edge AI Demo (Operational State)

**Date:** June 4, 2026 (Session Q end — H1 visually failed; do NOT start H2)
**Git Head:** `0fdc393` — clean working tree
**fault-trigger-ui image digest:** `sha256:3ee29db0` (live, has all Session Q code)
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
- All pods 1/1 Running
- ollama_online: True · model: gemma4:latest
- field_intel: ~80–120 rows · rag_documents: 18 rows

---

## STEP 2: Read DEMO_MASTER.md — Especially §12 (Status) and §15 (Engagement Requirements)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: H1 IS BROKEN — DO NOT START H2

H1 was deployed and visually reviewed in Session Q. It failed. Here are the specific failures in priority order:

### Integrity Violations (Lie to the Audience)
1. **"Motor CRITICAL" driven by `h1ElapsedMin > 15`, NOT actual temperature.** At T+16m, the motor block says "MOTOR CRITICAL" even though temp = 199°F and SCADA threshold = 280°F. This is a hardcoded timer lie. Rule: motor state must come from actual `h1SensorTemp` value.
2. **"GAS LOCK — 94% confidence" in the dual-reality bar is static text.** It always says 94% regardless of what the model actually produces. Must reflect live model confidence.
3. **SCADA gauge fallback values** ("1,400 PSI", "75.3 A") shown pre-injection when live-telemetry data is already available. Bars show hardcoded data that doesn't match the live sensor display above them.

### UX Failures (Audience Can't Understand State)
4. **No "YOU ARE HERE" on the Window of Options timeline.** The timeline shows T+10m, T+18m, PNR markers but no moving indicator showing elapsed time. A viewer can't tell where they are in the window.
5. **No "event active" indicator.** The only signal that a fault is running is that the Reset button appears. There is no prominent timer, banner, or alert state at the top of the tab. Audience doesn't know if the demo is running.
6. **SCADA gauge bars have no directional labels.** "PIP 1,340 PSI ⬇800" — the audience doesn't know if 800 means "lower is worse" or "higher is worse." Every gauge needs "↓ Lower = worse" or "↑ Higher = worse" printed on it.
7. **Phase-plane chart is unreadable to a business audience.** State-space diagrams require engineering literacy. Zones are unlabeled clearly. Axes require interpretation. The dot moves but it's not obvious what direction means danger.

### Technical Bugs
8. **AI Lead-Time RAG gap collapses to 0 after ~5 minutes.** The seed `field_intel` GVF document gets rotated out by the 100-row prune after `_intel_generator` writes ~10 documents. After this, `adjusted_rul === time_to_scada`. The prune must protect the seed doc OR re-insert it on each forecast cycle while the fault is active.
9. **Advisor `T+2m` update returns "Unable to reach AI model."** The `_triggerAdvisoryUpdate` call to `/api/agent/chat` times out or errors. No graceful fallback template. Gemma takes ~5-10s — the fetch timeout may be too short, or the model is busy from the initial stream.

---

## STEP 4: Proposed H1 V2 Redesign (Before Writing Any Code, Get Approval)

The root cause is: **one button, then try to figure out what's happening.** There is no engagement, no live narrative, no sense of urgency building.

### Design Principle
**A business person riding by on a fast horse must understand the crisis and the remaining window in 3 seconds. Without narration.**

### H1 V2 Layout
```
╔═══════════════════════════════════════════════════════════════════╗
║ BANNER: [NOMINAL] or [⚠ GAS LOCK ACTIVE · T+02:14 remaining: 16m] ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  DECISION TIMELINE (top of left column):                          ║
║  NOW ——▶— YOU ARE HERE —————————|————————|——————— FAIL            ║
║             ↑                   $0 safe  $2k     $150k only       ║
║          (elapsed)              T+18m    T+23m   after PNR        ║
║                                                                    ║
║  SENSOR BARS (left, below timeline):                              ║
║  PIP  ████████████████░░░░  1,340 PSI  Alarm at 800 ↓lower=worse  ║
║  AMPS ████████████░░░░░░░░    69 A     Alarm at  50 ↓lower=worse  ║
║  TEMP ████░░░░░░░░░░░░░░░░   199 °F    Alarm at 280 ↑higher=worse ║
║                                                                    ║
║  ⚡ SCADA sees: 4 sensors, all above/below alarm limits. No alarm. ║
║  ⚡ GDC sees:   PIP + Amps declining TOGETHER = gas lock signature ║
║               + retrieved documents confirm GVF 78%, GOR rising   ║
║                                                                    ║
║  OPTIONS (below):                                                  ║
║  ┌─────────────────┐  ┌────────────────┐  ┌───────────────────┐   ║
║  │ $0  · AVAILABLE │  │ $2k · AVAILABLE│  │ $150k · POST-PNR  │   ║
║  │ VFD 52→44 Hz    │  │ Emergency stop │  │ Pump pull         │   ║
║  │ [✔ Execute Now] │  │                │  │                   │   ║
║  └─────────────────┘  └────────────────┘  └───────────────────┘   ║
╠═══════════════════════════════════════════════════════════════════╣
║ GDC ADVISOR (right): streaming + re-fires with fallback template  ║
╚═══════════════════════════════════════════════════════════════════╝
```

### Engagement Elements to Add
- **Banner that changes.** Before inject: "✓ WELL A-1 NOMINAL — 4 sensors · no alarm." After inject: "⚠ GAS LOCK ACTIVE · T+02:14 · 16 min remaining" with a live ticking counter.
- **YOU ARE HERE marker** on the timeline. A moving arrow/dot that advances over the 25-minute window in 5× compressed time.
- **Evidence reveal sequence** on the left: text lines appear one by one as the injected fault progresses, each sentence building the case. Not a static wall — a slow revelation.
- **Advisor with fallback:** if Gemma timeouts, use a template that still says something correct.

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- `feature-trio-scenarios` stays separate from `main`
- XGBoost `*.ubj` models — do not retrain
- No npm/webpack/React — vanilla HTML/JS + Vue.js CDN only
- Token budget: batch all edits to same file in ONE replace_in_file call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- "Copilot" is a Microsoft product name — do NOT use it
