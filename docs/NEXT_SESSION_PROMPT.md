# Next Session Prompt — GDC ESP Ops Demo (Operational State)
Date: 2026-06-25 (Session BS+50 wrap) / branch: feature-trio-clean
Git HEAD: c2257a3 / Image: sha256:747ad68a622cc2cc8dcb7a3d93a7f03cbddfc425b2eaac28511c17a59e19cd39

⚠ NOTE: 2 commits ahead of origin/feature-trio-clean — push before next session if needed.

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
cat docs/DECISION_DOSSIER.md   # MANDATORY — §3.5 is the H3 build spec
cat docs/SESSION_LOG.md | head -60  # last entry for context
```

## STEP 3: Recording Progress

### ✅ DONE
- B0.1–B0.4 (Intro)
- B1-P1–P5 + B1-S1–S6 (H1 — FULLY RECORDED)
- H2 panels: fully updated, deployed, record-ready (being recorded by user)

### ⏳ NEXT: TASK 4 — H3 Iterative Vizier + Plan-vs-Live (1–2 hrs)
**Read DECISION_DOSSIER.md §3.5 fully before touching app.py.**
**File:** `app.py` — function `vizier_optimize()` at ~L6701–6770

**Step 4A — Make Vizier loop iterative:**
Replace `suggest_trials(count=15)` single-batch with **3 rounds of 5 trials** → score on edge → re-suggest.
- Round 1 establishes feasible boundary; rounds 2–3 concentrate search.
- Makes "searches and learns" **literally true** (not just a claim).
- Still ~15 trials; Vizier cost stays within free tier.

Verify first:
```bash
curl -s "http://gdc-pm.bdau.io/api/vizier/optimize" | python3 -c "import sys,json;d=json.load(sys.stdin);print('trials:',len(d.get('trials',[])),'\nfeasible:',sum(1 for t in d.get('trials',[]) if not t.get('is_failure')))"
```

**Step 4B — Plan-vs-live-state split (new function `reconcile_live()`):**
- Return both `plan_hz_vec` (Vizier computed) AND `live_hz_vec` (after edge reconciles)
- Inject: well A-5 gets live motor temp +12°F above the plan's assumption (simulates degrading seal)
- Enforce `hz_live[i] ≤ hz_plan[i]` for ALL wells — edge ONLY trims DOWN (never up; up-reallocation would breach shared gas ceiling)
- Return `trims[]` list showing which wells were adjusted and why

**Step 4C — Presentation (`templates/tab_h3.html`):**
- Add cloud-plan panel (Vizier results) + edge-reconcile panel (A-5 trimmed with reason)
- Render infeasible trials as ✗ and feasible as ✓ in trial log (data already in `is_failure`)
- Add: `<span style="font-size:0.50rem;color:var(--muted);font-style:italic">⏺ Architecture view — system-to-system flow</span>` honesty tag
- Label: "GDC-plan Hz" (what Vizier said) vs "GDC-live Hz" (what edge enforced after A-5 hot)

**Step 4D — Verify H3-S4 constraintDoc.found=True:**
```bash
curl -s "http://gdc-pm.bdau.io/api/vizier/optimize" | python3 -c "import sys,json;d=json.load(sys.stdin);print('constraintDoc.found:',d.get('constraint_doc',{}).get('found'))"
```
Must return `True` consistently before recording B3-S4.

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
- **H3 MUST-NOT-SAY:** See DECISION_DOSSIER.md §3.6
- **Why-GDC MUST-NOT-SAY:** See DECISION_DOSSIER.md §4.5
- **H3 edge trims DOWN only** — no up-reallocation (breaches shared gas ceiling)

## Recording Progress
- ✅ B0.1–B0.4 (Intro) DONE
- ✅ B1-P1–P5 + B1-S1–S6 (H1 scenario) DONE
- ⏳ BBRIDGE — record after H2
- ⏳ H2 (B2-P1 through B2-S4) — user recording; panels deployed c2257a3
- ⏳ H3 (B3-P1 through B3-S5) — record after Task 4 + 4D verification
- ⏳ BCLOSE — record last
