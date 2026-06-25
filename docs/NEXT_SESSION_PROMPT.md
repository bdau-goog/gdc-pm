# Next Session Prompt — GDC ESP Ops Demo (Operational State)
Date: 2026-06-25 (Session BS+51 wrap) / branch: feature-trio-clean
Git HEAD: 3899b95 / Image: sha256:aac31c2c5fc2330e29654a91affc9cb5e2471618bb155ffad5f1df82f49dcb9f

⚠ NOTE: 3 commits ahead of origin/feature-trio-clean — push before next session if needed.

## STEP 1: Run Four Startup Commands
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

## STEP 2: Read DEMO_MASTER.md + DECISION_DOSSIER.md
```bash
cat docs/DECISION_DOSSIER.md   # MANDATORY — §3 is now the curtailment scenario spec
cat docs/SESSION_LOG.md | head -80  # last 2 entries for context
```

## STEP 3: Recording Progress

### ✅ DONE
- B0.1–B0.4 (Intro)
- B1-P1–P5 + B1-S1–S6 (H1 — FULLY RECORDED)
- H2 panels: fully updated, deployed, record-ready (being recorded by user)

### ⏳ NEXT: TASK 4 BACKEND ✅ DONE — Now build TASK 4 UI + TASK 4 SLIDES

**H3 backend is deployed and verified (3899b95):**
- `/api/vizier/optimize` runs in 0.20s warm (deterministic_convergence_demo)
- `curtailment.revenue_delta=12899592.0` live-computed ✅
- `constraintDoc.found=True` ✅
- `live_vizier=False` gate: no Vizier studies created by accident ✅
- **11 active Vizier studies deleted** — billing stopped

**⚠ VIZIER COST DISCIPLINE (PERMANENT):**
- `/api/vizier/optimize` ALWAYS uses deterministic fallback (live_vizier=False default)
- To invoke real Vizier: `curl ".../api/vizier/optimize?live_vizier=true"` — announce first
- Real Vizier creates a study + 15 trials on EVERY CALL. Do NOT call it casually.
- 100 free trials/mo; $1/trial after. 11 studies already spent the budget this month.

**Step 4C — tab_h3.html: curtailment panel (new UI beat):**
- File: `templates/tab_h3.html`
- API data available: `d.curtailment.{event, curtailed_ceiling, trigger, smart_hz_vec, scada_hz_vec, revenue_delta, uplift_bbl_d, wells_curtailed[]}`
- What to show:
  - **Curtailment event card**: "📨 GatherCo Notice — Line PA-6-0047: capacity reduced 8.0 → 6.0 MMscfd (4-hr event)" with trigger label "Off-sensor — gathering-system capacity reduction"
  - **GDC smart re-allocation panel**: per-well table (Plan Hz / Curtailed Smart Hz / Curtailed SCADA Hz / Role) — oil-rich wells stay up/hold, gassy wells trimmed
  - **Revenue delta badge**: GDC smart vs dumb-SCADA, `+${{ curtailment_revenue_delta / 1e6 | toFixed(1) }}M vs uniform throttle` (90-day horizon)
  - **Honesty tag**: `⏺ Architecture view — system-to-system flow`
- Show AFTER the existing uplift card (add below it, same dashboard)
- Small "⚠ Edge only trims intra-pad (it owns its tie-in). Inter-pad: next cloud cycle." footnote

**Step 4D — slides/h3.html + VIDS VO reframe:**
- Slide 3 ("Cloud Searches. Edge Enforces.") needs one added sentence re curtailment:
  "When gathering changes after the plan ships — a curtailment notice the cloud never saw — the edge re-allocates the pad in real time, protecting revenue under the cut."
- VIDS B3-P3 + B3-S3/S5 VOs: concede VFD owns motor protection; edge beat = curtailment re-allocation vs dumb-SCADA; lead with revenue delta
- B3-S4 (constraintDoc) is clear: `constraintDoc.found=True` confirmed ✅

**Step 4E — Verify B3-S4 before recording:**
```bash
curl -s "http://gdc-pm.bdau.io/api/vizier/optimize" | python3 -c "import sys,json;d=json.load(sys.stdin);print('constraintDoc.found:',d.get('constraint_doc',{}).get('found'))"
# Must return: True
```

### TASK 5 — "Why GDC" Platform Tab (~30 min)
**Read DECISION_DOSSIER.md §4 fully before building.**
**Run this search FIRST before writing any tab text:**
```python
gemini_search("What is the current 2026 product name for Vertex AI enterprise / Gemini Enterprise Agent Platform in Google Cloud?")
```
Tab placement: after "Optimize" / before "ⓘ Reference"
Three pillars: form factor fit / fleet governance (ACM+FM, apps+infra only, NOT OT/PLC) / sovereign AI platform + Model-Ops (base models + local fine-tuning)
See DECISION_DOSSIER.md §4.3–§4.5 for locked thesis and must-not-say list.

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
- B2-S5: ❌ CUT — do not record
- BBRIDGE VO: "all AI local, no cloud required" (not "air-gap capable")
- **Autonomy numeric knob: ❌ BLOCKED** — IEC 61511 FAILS
- **GAS LOCK VO physics:** PIP drops / casing annulus pressure rises — do NOT change
- **H3 MUST-NOT-SAY:** See DECISION_DOSSIER.md §3.7
- **Why-GDC MUST-NOT-SAY:** See DECISION_DOSSIER.md §4.5
- **H3 edge intra-pad realloc is SAFE** (edge owns its tie-in) — see §3.3 refined
- **H3 edge does NOT protect motors** — VFD owns overtemp; do not re-use that beat
- **live_vizier=True: announce before calling** — creates a billable Vizier study

## Recording Progress
- ✅ B0.1–B0.4 (Intro) DONE
- ✅ B1-P1–P5 + B1-S1–S6 (H1 scenario) DONE
- ⏳ BBRIDGE — record after H2
- ⏳ H2 (B2-P1 through B2-S4) — user recording; panels deployed c2257a3
- ⏳ H3 (B3-P1 through B3-S5) — record after Task 4C + 4D verification
- ⏳ BCLOSE — record last
