# Next Session Prompt — GDC ESP Ops Demo (Operational State)
Date: 2026-06-25 (Session BS+53) / branch: feature-trio-clean
Git HEAD: 9f1482f / Image: sha256:a2970c6a0b0d8ba2643d6d3457596421b0a153f80f1ef2f51fdc63af41dcb02b

⚠ NOTE: 6 commits ahead of origin/feature-trio-clean — push before next session if needed.

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
cat docs/DECISION_DOSSIER.md   # §2 is H2 spec; §2.6 physics; Bill Barna SME confirmation
cat docs/SESSION_LOG.md | head -80
```

## STEP 3: Next Tasks — H2 Recording + H3 Iterative Vizier

### H2 UI — FULLY DEPLOYED (sha256:a2970c6a) ✅
All 6 fixes shipped and verified live:
| Fix | Status | Verified |
|---|---|---|
| Q2 🔴 | New wax-up SVG wellbore (3-col 44/22/34%) — PROT neutral grey | ✅ "schematic · wax inferred from PIP" in live HTML |
| Q3 🔴 | "Weeks since last treatment" (was "post-workover") | ✅ grep confirmed in app.js |
| Q4 | GDC▲ "health <0.65 · vib ~half HI limit" / SCADA▲ "single-tag 4.0 mm/s crossed" + footnote | ✅ grep confirmed |
| Q1 | `roll_vib` returned in API + rolling-avg trace on chart | ✅ API: roll_vib present=True len=80 |
| Q5 | Efficiency `title` tooltip "VFD-derived (IEEE 112)" | ✅ "VFD-derived" in live HTML |
| B2-S1 | VIDS_PRODUCTION_MASTER.md card rewritten (loads at alarm state) | ✅ committed |
| B2-S3.5 | New rewind beat inserted in VIDS_PRODUCTION_MASTER.md | ✅ committed |

### READY TO RECORD: H2 (B2-P1 through B2-S4 + new B2-S3.5)
- Load at alarm state: `h2CursorIdx = scada_alarm_idx` on New Scenario click ✅
- Wellbore: wax band dynamic (cursor-bound, thins on rewind to gdc_detect_idx) ✅
- B2-S3.5 rewind beat: scrub cursor from alarm → gdc_detect_idx after doc cascade; VO: "Act on the drift, not the alarm."
- Verified: vib at gdc_detect_idx = 1.94 mm/s = 48% of 4.0 HI limit — claim scoped to threshold SCADA only

### H3 — Iterative Vizier loop fix (blocking H3 recording)
- **File:** `app.py` — `suggest_trials(count=15)` at L6734 is a single batch, NOT iterative
- **Fix needed:** Wrap in 3-round loop (3×5 trials → score → re-suggest) so "searches and learns" is literally true
- **Pattern** already in app.py: look for the 3-round fallback loop in `_FALLBACK_VECS` — the LIVE Vizier path needs the same structure
- After fix: deploy + verify `vizier_algorithm` returns `GAUSSIAN_PROCESS_BANDIT` (not `deterministic_convergence_demo`)
- Then record B3-P1 → B3-S5

## Recording Progress
- ✅ B0.1–B0.4 (Intro) DONE
- ✅ B1-P1–P5 + B1-S1–S6 (H1 scenario) DONE
- ⏳ H2 (B2-P1 through B2-S4 + B2-S3.5) — UI deployed, **record now**
- ⏳ BBRIDGE — record after H2
- ⏳ H3 (B3-P1 through B3-S5) — panels deployed; iterative Vizier fix needed first
- ⏳ BCLOSE — record last

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
- **H2 early-detect claim:** threshold SCADA only — never "earlier than APM" (dossier §2.3)
- **H2 wax band:** "schematic · wax inferred from PIP" — displayed, not a measurement
- **live_vizier=True: announce before calling** — creates a billable Vizier study
