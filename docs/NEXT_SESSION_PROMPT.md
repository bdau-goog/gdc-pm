# Next Session Prompt — GDC ESP Ops Demo (Operational State)
Date: 2026-06-25 (Session BS+52 wrap) / branch: feature-trio-clean
Git HEAD: 5a50a3d / Image: sha256:9d4a536dbafb238d1403d98dcd6bd504beede3ecb92be330374ff22c65b63e64

⚠ NOTE: 5 commits ahead of origin/feature-trio-clean — push before next session if needed.

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
cat docs/DECISION_DOSSIER.md   # MANDATORY — §3 is curtailment scenario spec; §4 is Why GDC
cat docs/SESSION_LOG.md | head -80  # last 2 entries for context
```

## STEP 3: Recording Progress

### ✅ DONE
- B0.1–B0.4 (Intro)
- B1-P1–P5 + B1-S1–S6 (H1 — FULLY RECORDED)
- H2 panels: fully updated, deployed (user recording)

### ✅ TASKS 4C + 4D + 5 COMPLETE (this session)

**Task 4C — tab_h3.html curtailment panel (DONE + verified):**
- Event card (amber): "Off-Sensor Curtailment Notice / Midstream gas-takeaway curtailment: 8.0 → 6.0 MMscfd"
- 6-well re-allocation table: Plan Hz / GDC Smart Hz / SCADA Baseline Hz / Role (Trimmed/Holds)
- Revenue delta badge: +$12.9M vs uniform throttle (live-computed from `evaluate_field()`)
- Honesty tag: ⏺ Architecture view — system-to-system flow
- Footnote: ⚠ Edge only trims intra-pad; inter-pad: next cloud cycle

**Task 4D — slides/h3.html + VIDS VO reframe (DONE + verified):**
- Slide 3 curtailment sentence added (amber callout)
- B3-P3 VO: cloud does searching; edge re-allocates under curtailment; VFD owns motor protection trips
- B3-S3 VO: leads with +$12.9M revenue delta; curtailment re-allocation vs dumb-SCADA
- B3-S5 VO: gas-ceiling constraint at edge; motor trips stay with VFD/SCADA; off-sensor curtailment notice

**Task 5 — Why GDC platform tab (DONE + verified):**
- New nav tab "Why GDC" between Optimize and ⓘ Reference
- Three pillars: Form Factor Fit (blue) / Fleet Governance (green, NOT OT/PLC) / Sovereign AI Platform (purple)
- RTOC deployment shape: Cloud → Regional RTOC (GDC cluster) → Basin Wells
- "base models + local fine-tuning" (NOT "deploy identically") — §4.5 compliant
- Product names: Gemini / Gemini Enterprise Agent Platform (user-confirmed 2026 names)
- Scenarios connection card ties H1/H2/H3 to platform story

### ⏳ NEXT: Record H3 (B3-P1 through B3-S5)

**Pre-recording verification (run before starting H3 recording):**
```bash
# Verify constraintDoc.found=True (required for B3-S4)
curl -s "http://gdc-pm.bdau.io/api/vizier/optimize" | python3 -c "import sys,json;d=json.load(sys.stdin);print('constraintDoc.found:',d.get('constraint_doc',{}).get('found'))"
# Must return: True

# Verify curtailment panel data
curl -s "http://gdc-pm.bdau.io/api/vizier/optimize" | python3 -c "import sys,json;d=json.load(sys.stdin);c=d.get('curtailment',{});print('revenue_delta:',c.get('revenue_delta'),'wells:',len(c.get('wells_curtailed',[])))"
# Must return: revenue_delta: 12899592.0 wells: 6
```

**H3 recording order (per VIDS_PRODUCTION_MASTER.md):**
- B3-P1 → B3-P2 → B3-P3 (briefing slides — already updated this session)
- B3-S1: Run Vizier Optimization button
- B3-S2: Baseline Hz column (uniform throttle)
- B3-S3: GDC Optimal + curtailment panel (lead with revenue delta +$12.9M)
- B3-S4: Constraint provenance doc card (constraintDoc.found=True confirmed ✅)
- B3-S5: Edge gas-ceiling constraint + VFD/SCADA own motor trips

**After H3:** Record BBRIDGE (between H2 and H3), then BCLOSE.

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
- **Why GDC product names:** Gemini / Gemini Enterprise Agent Platform (user-confirmed 2026)

## Recording Progress
- ✅ B0.1–B0.4 (Intro) DONE
- ✅ B1-P1–P5 + B1-S1–S6 (H1 scenario) DONE
- ⏳ BBRIDGE — record after H2
- ⏳ H2 (B2-P1 through B2-S4) — user recording; panels deployed c2257a3
- ⏳ H3 (B3-P1 through B3-S5) — record now (Task 4C/4D deployed this session)
- ⏳ BCLOSE — record last
