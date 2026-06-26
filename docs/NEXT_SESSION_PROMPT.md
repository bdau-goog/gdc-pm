# Next Session Prompt — GDC ESP Ops Demo (Operational State)
Date: 2026-06-26 (Session BS+57) / branch: feature-trio-clean
Git HEAD: c9e57bc / Image: sha256:13e44d7e8b1d8c641b91ccf73b8eb72c7895ef00795b4dbc9a24d0c3e0bd5f78
⚠ NOTE: Push origin/feature-trio-clean before or after next session.

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
cat docs/DECISION_DOSSIER.md   # §2 H2 spec; §3 H3 spec; §3.7 Must-NOT-SAY
cat docs/SESSION_LOG.md | head -60
```

## STEP 3: Next Tasks — H3 Code Fix + BBRIDGE + H3 Recording + BCLOSE

### Recording Progress
- ✅ B0.1–B0.4 (Intro) DONE
- ✅ B1-P1–P5 + B1-S1–S6 (H1) DONE
- ✅ B2-P1–P3 + B2-S1 + B2-S3 + B2-S3.5 + B2-S4 (H2) DONE — B2-S2 merged into S1; B2-S5 CUT
- ⏳ BBRIDGE — record next (no code change needed; 8s sovereignty callback)
- ⏳ H3 (B3-P1 through B3-S5) — B3-P1/P2/P3 slides updated (de-staccato, Session BS+57); B3-S1 blocked on iterative Vizier fix (see below)
- ⏳ BCLOSE — record after H3
- ⏳ BWHY (Why GDC tab) — NEW: tab validated + deployed Session BS+57; ~18s closing beat; scene card in VIDS_PRODUCTION_MASTER.md §BWHY

### ⭐ BLOCKER: Iterative Vizier Loop Fix (before H3 B3-S1 recording)
- **File:** `app.py` — `suggest_trials(count=15)` at L6734 is a single batch, NOT iterative
- **Fix:** Wrap in 3-round loop (3×5 trials → score → re-suggest) so "searches and learns" is literally true
- **Pattern:** look for `_FALLBACK_VECS` 3-round fallback loop in app.py — LIVE Vizier path needs same structure
- **After fix:** deploy + verify `vizier_algorithm` returns `GAUSSIAN_PROCESS_BANDIT` (not `deterministic_convergence_demo`)
- **Then:** record B3-P1 → B3-S5

### BBRIDGE Recording (no code fix needed)
Navigate to Intro tab → Slide 3 (GDC Deployment Models). Cursor Air-Gapped card (H1/H2), then Connected card (H3).
VO: "The first two cases ran entirely on-prem, all AI local, no cloud required. The third is the connected model: it reaches the cloud for Bayesian search, but only the setpoints and their scores ever leave the site, your data never follows, and the safety decision always stays local."
⚠ No em dashes — Vids Avatar TTS rule (em dash causes avatar to tap out; use commas/colons)

### H3 Scene Order: B3-P1 → B3-P2 → B3-P3 → B3-S1 → B3-S2 → B3-S3 → B3-S4 (conditional) → B3-S5 → BCLOSE
All H3 UI and slides are deployed and record-ready (sha256:ab2e90d4).
Pre-recording: verify constraintDoc.found=True before recording B3-S4 (curl /api/vizier/optimize).

## Deploy Command (permanent reference)
```bash
cd gke/fault-trigger-ui
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest .
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
```
**Registry:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/` (NOT gcr.io)

## VO Style Rule (established BS+56)
- **Connected/flowing sentences** — not staccato fragments. One thought leads to the next naturally.
- **Attribution explicit** — "To the operator, that pattern reads as..." not implied.
- **No em dashes** in VO — Vids Avatar TTS taps out. Use commas or colons instead.
- **No numbers in VO** — panels carry every figure.

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- GPU scale-to-zero; `gpu-start.sh` ONLY for explicit LLM test (~$0.65/hr)
- B2-S5: ❌ CUT — do not record
- BBRIDGE VO: "all AI local, no cloud required" (not "air-gap capable")
- **Autonomy numeric knob: ❌ BLOCKED** — IEC 61511 FAILS
- **GAS LOCK VO physics:** PIP drops / casing annulus pressure rises — do NOT change
- **H3 MUST-NOT-SAY:** See DECISION_DOSSIER.md §3.7
- **Why-GDC MUST-NOT-SAY:** See DECISION_DOSSIER.md §4.5 (includes "local fine-tuning" HARD-NO, "Anthos" retired)
- **H2 early-detect claim:** threshold SCADA only — never "earlier than APM" (dossier §2.3)
- **H2 wax band:** "schematic · wax inferred from PIP" — displayed, not a measurement
- **live_vizier=True: announce before calling** — creates a billable Vizier study
- **SCADA domain rule (BS+56):** SCADA reports tag values and alarm states ONLY. It does not opine on cause. Never have SCADA assert a diagnosis.
- **Why-GDC tab (BS+57):** GKE Enterprise / Config Sync (not Anthos); "on-prem LLM" for synthesis (Gemma/Ollama — not "Gemini Enterprise Agent Platform"); Vizier is cloud, not edge. Tab validated + deployed sha256:13e44d7e.
