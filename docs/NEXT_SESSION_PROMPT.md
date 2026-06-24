# Next Session Prompt — GDC ESP Ops Video (Operational State)
Date: 2026-06-24 (Session BS+45) / branch: feature-trio-clean
Git HEAD: a729236 / Image: sha256:26bab26d826948fb52417571c94e5de1e0017cbb5dad9617e0053596f9a16155

## STEP 1: Run These Four Commands First
```bash
kubectl get pods -n gdc-pm --no-headers
# Expected: all 1/1 Running (7 pods)

kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
# Expected: 0

curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
# Expected: ollama_online: False model: offline

kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
# Expected: field_intel = 11, rag_documents = 20
```

## STEP 2: Read These Documents
```bash
cat docs/SESSION_LOG.md | head -60   # last 2 entries for context
```

## STEP 3: Recording — H1 Scenario Scenes (B1-S1 → B1-S6)

**Status going in:** B1-P1 through B1-P5 ✅ DONE. Now recording the live scenario scenes.
**App URL:** http://gdc-pm.bdau.io · Tab: Discern
**Recording method:** Screen Studio · BenQ 2560×1440 native full-screen · no DevTools
**Shot bible source:** `docs/VIDS_PRODUCTION_MASTER.md §SECTION 1` (lines 419–536)

---

### B1-S1 — Start the Run · ~7s
- **APP STATE:** Discern tab → click `↺ New Scenario` → transport begins; GDC shows "BASELINE MONITORING · XGBoost routing score"
- **VO:** *"Now let's look at how GDC helps with our unloading scenario. Let's run it live — and here we see GDC scoring every channel as the event unfolds, before any single hard limit is crossed."*
- **NOTE:** Verdict (Gas Lock or Drawdown) is random. Record whichever fires. VO branches only at B1-S4.
- **FIX (BS+45):** Doc-card leak fixed — `loadH1Scenario()` now correctly resets `h1RagDoc2Shown`, `h1RagDoc3Shown`, `h1RagPending`, and clears stale timers. All 3 docs now hidden before GDC-detect line on every run.

### B1-S2 — Pre-Threshold Detect ⭐ INTEGRITY-CRITICAL · ~7s
- **APP STATE:** GDC Advisor view · scrub to `gdc_detect_idx` (~27) · amber "RETRIEVING CONTEXT" state holds · NO SCADA alarm yet (alarm_idx ~48 not reached)
- **CHOREOGRAPHY:** Play → when amber state appears (gdc_detect_idx ~27), pause. `h1RagPending=true` so amber holds indefinitely. Record VO. Press play → 1.5s later docs reveal.
- **VO:** *"GDC flags the developing drift here — ahead of any single hard limit being crossed."*
- **POST:** zoom 1.15× on amber GDC state; hold ~2s
- **DO NOT SKIP** — this is the live proof of the Part A detection claim.

### B1-S3 — SCADA View (alarm, no cause) · ~10s
- **APP STATE:** Switch to 🟡 SCADA View · scrub to `alarm_idx` (~48) · red "⚠ SCADA alarm — ambiguous underload" banner · grey (not green) action cards
- **VO:** *"This is what the control system sees. It protects the pump — trips on its hard limit, as it should — but offers no cause, no read on sand risk."*

### B1-S4 — GDC Advisor verdict + 3 documents · ~11s · A/B BRANCH
- **APP STATE:** 🟢 GDC Advisor · `h1RagRevealed=true` · verdict card + 3 doc cards (appear ~2s apart)
- **VO — GAS LOCK:** *"GDC retrieves the well's documents — annulus submerged, gas rising, sand history clean — and returns a cited verdict: gas lock. Ease the speed; keep the well online."*
- **VO — DRAWDOWN:** *"GDC retrieves the well's documents — fluid level below the intake, a known sand producer — and returns a cited verdict: drawdown. Shut it in; easing the speed here would seize the pump."*
- **POST:** zoom 1.15× on verdict card; pgvector cosine score visible
- **NOTE:** Record whichever branch fires. Do not re-run to force a specific branch.

### B1-S5 — HITL Approve · ~8s
- **APP STATE:** GDC Advisor · "GDC Agent · Action package ready · Awaiting RTOC approval" label visible · ✔ Approve & Execute button
- **VO:** *"Every recommendation is cited and reviewable. The engineer approves the action — GDC advises, the human decides."*
- **POST:** zoom 1.15× on "Awaiting RTOC approval" + approve button

### B1-S6 — Outcome · ~5s · **OPTIONAL — cut if runtime > 5:55**
- **APP STATE:** `h1Resolved=true` · "✅ RECOVERING — VFD at 44 Hz · monitoring wellbore response"
- **VO:** *"The well stays online — an ambiguous alarm became a confident, low-cost decision."*

---

## STEP 4: After H1 — Recording Order

Per VIDS_PRODUCTION_MASTER.md:

| Next | Scene | ~Time |
|---|---|---|
| BBRIDGE | H2→H3 Sovereignty Bridge — "All the AI local…" | ~8s |
| B2-S1–S4 | H2 CLASSIFY scenario (4 scenes; B2-S5 ❌ CUT) | ~50s |
| B3-S1–S3 | H3 OPTIMIZE (run Vizier → table → uplift) | ~45s |
| B3-S4 | H3 constraint provenance — CONDITIONAL (see below) | ~8s |

**B3-S4 gate** — verify before H3:
```bash
curl -s "http://gdc-pm.bdau.io/api/vizier/optimize" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print('constraintDoc.found:', d.get('constraint_doc', {}).get('found'))"
# Expected: constraintDoc.found: True
```

## Deploy Command (permanent reference)
```bash
cd gke/fault-trigger-ui
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest .
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
```
**Registry:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/` (NOT gcr.io)

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- GPU scale-to-zero; `gpu-start.sh` ONLY for explicit LLM test (~$0.65/hr)
- VEO_COLD_OPEN.md has hidden-character lines — use write_to_file not replace_in_file
- B1-P1 through B1-P5 VO locked: recorded, match bible verbatim ✅
- B2-S5: ❌ CUT — do not record
- BBRIDGE VO: "all AI local, no cloud required" (not "air-gap capable")
- Reference tab integrity scrub COMPLETE (BS+44) — tab_architecture.html all panes SURVIVES ✅
