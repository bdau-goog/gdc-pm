# Next Session Prompt — GDC ESP Ops Video (Operational State)
Date: 2026-06-25 (Session BS+48 wrap) / branch: feature-trio-clean
Git HEAD: 94f99e6 / Image: sha256:ff5f96d1c4c2e5d71bd76eb867336c8d388a9e8db15b8a8a207236c5fbc7ff98

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
cat docs/H3_DECISION_DOSSIER.md      # MANDATORY before any H3 work — full reasoning, eliminations, build plan
cat docs/SESSION_LOG.md | head -80   # last 2 entries for context
```

## STEP 3: PRIME DIRECTIVE — What BS+48 Locked

### H2 (Classify) — Instant-Triage + Provenance framing ✅ DESIGN LOCKED
**Identity:** Operator tool. Provenance / avoid-unnecessary-$100k-pull.
**UI change (build):** Load H2 at active alarm state (`h2CursorIdx = data.scada_alarm_idx` after `this.h2ReplayData = data`) instead of idx=0.
- **File:** `static/app.js` function `loadH2Scenario()` ~L2057–2090
- **Change:** One line: `this.h2CursorIdx = data.scada_alarm_idx;` after `this.h2ReplayData = data;`
- **Why:** 8-week slow playback is wrong for a provenance/single-alarm story. Load at alarm = "this alarm is active NOW; here's how GDC resolves it."
- **Verify:** `curl http://gdc-pm.bdau.io/api/h2/scenario-replay` → confirm `scada_alarm_idx` is in response.

### H3 (Optimize) — Two-Timescale Architecture ✅ DESIGN LOCKED
**FULL DOSSIER: `docs/H3_DECISION_DOSSIER.md` — READ THIS ENTIRE FILE BEFORE ANY H3 CODE.**

**Identity:** Real system-to-system architecture story (NOT an operator tool).
**Thesis:** Two-timescale RTO-over-MPC hierarchy:
- Cloud (Vizier): global/slow/economic — divides shared gas budget across field periodically
- Edge (GDC): local/fast/continuous — reconciles cloud plan against live per-asset reality; trims DOWN only (never UP — up-reallocation breaches shared gas ceiling); data never leaves site
- SCADA: executes; owns regulatory control and hard trips

**MUST-NOT-SAY (RT-confirmed, permanent):**
1. ❌ "Operators don't trust control vendors with data" (FUD, FAILS)
2. ❌ "GDC invented hierarchical control" (it's textbook RTO/MPC)
3. ❌ "The edge does the global optimization"
4. ❌ "14 of 15 proposals rejected" as a hero stat (fix feasible-rate first)
5. ❌ "Vendor-neutral" unscoped (scope to "neutral relative to equipment vendors")
6. ❌ GitOps manages PLC/SCADA/Level-1/2 configs

**5-angle moat (no anti-competitor FUD):**
1. Greenfield reach: ~76% O&G operators run NO ML APM (cited: uptimeai.com/reliamag.com 2023)
2. Horizontal platform vs point product (GKE/AlloyDB/Vertex runs all three horizons)
3. Unstructured fusion APM can't do — CATEGORICAL, STRONGEST
4. Sovereign fleet Model-Ops (GitOps config + Vertex-train→edge-deploy + governed IAM; NOT PLC/Level-1/2)
5. Data-gravity / outage-tolerance

### Vizier Live Cloud Facts (Verified 2026-06-25)
- Project: `gdc-pm-v2` / us-central1
- 10 real studies: `gdc_pad_alpha_field_opt_*`
- Latest study 593258648990: **14/15 INFEASIBLE, 1 feasible** (root cause: shared gas ceiling + wide independent bounds + single batch)
- Code: `suggest_trials(count=15)` at app.py L6734 = **single batch, NOT iterative** → "learns per-trial" = silent lie
- Cost: 100 free trials/mo, $1/trial after; dev/test safe; no GPU

## STEP 4: Next Implementation Tasks (in order)

### Task 1 (small, build first): H2 instant-triage load
- `static/app.js` loadH2Scenario() ~L2057
- After `this.h2ReplayData = data;` add: `this.h2CursorIdx = data.scada_alarm_idx || 0;`
- Verify: tab opens at active alarm, 90-day static history plotted, VIB-HI alarm visible
- Deploy → verify live

### Task 2 (CORE H3 build — see dossier §10 for exact spec):
1. **Iterative Vizier loop** — `app.py` ~L6701–6770: replace `suggest_trials(count=15)` single-batch with 3 rounds of 5 → score → re-suggest. Raises feasible rate; makes "searches/learns" honest.
2. **Plan-vs-live-state split** — add `reconcile_live(plan_hz_vec, live_well_params)` to vizier_optimize() return. One well (A-5) gets live motor temp +12°F injected. Enforce `hz_live[i] ≤ hz_plan[i]` (trim-DOWN-only rule).
3. **Presentation (tab_h3.html)** — cloud plan panel + edge reconcile panel + "⏺ Architecture view — system-to-system flow" tag + render infeasible trials as ✗ and feasible as ✓.
4. **Verify H3-S4** constraintDoc.found=True: RAG query for midstream contract must return found=True consistently before recording.

### Task 3 (recording prep):
- After Tasks 1–2 verified live: resume recording per VIDS_PRODUCTION_MASTER.md
- B1-S5, B1-S6, BBRIDGE, H2, H3, BCLOSE still to record
- H3 recording follows the 3-act: cloud plan (real Vizier) → edge reconcile (A-5 hot → trim down) → sovereign/scale

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
- B1-P1 through B1-S4 VO locked: recorded, match bible ✅
- B2-S5: ❌ CUT — do not record
- BBRIDGE VO: "all AI local, no cloud required" (not "air-gap capable")
- **Autonomy numeric knob: ❌ BLOCKED** — IEC 61511 FAILS
- **GAS LOCK VO physics:** PIP drops (SCADA signal). Casing annulus pressure rises (gas lock evidence). Do NOT change either.
- **H3 MUST-NOT-SAY list:** See §3 above and `docs/H3_DECISION_DOSSIER.md` §6.
- **DEMO_MASTER §5/§6 update deferred:** Too large for safe late-night edit. Dossier is the authoritative record. Update §5/§6 as a separate Task 0 or wrap them into the H3 build session.
