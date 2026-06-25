# Next Session Prompt — GDC ESP Ops Demo (Operational State)
Date: 2026-06-25 (Session BS+49 wrap) / branch: feature-trio-clean
Git HEAD: (see latest commit) / Image: sha256:ff5f96d1c4c2e5d71bd76eb867336c8d388a9e8db15b8a8a207236c5fbc7ff98

## ⚠ CRITICAL: Read These Before Anything Else
```bash
cat docs/DECISION_DOSSIER.md   # MANDATORY before any H1/H2/H3/platform work
cat docs/SESSION_LOG.md | head -120  # last 2 entries for context
```

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

## STEP 2: Context — What Sessions BS+48 + BS+49 Locked

Sessions BS+48/BS+49 were planning-only (no code deployed). Everything has been decided and is documented in DECISION_DOSSIER.md. The next session is 100% BUILD AND RECORD. The remaining recording list at session end:

**Still to record:** B1-S5, B1-S6, BBRIDGE, H2 (all scenes), H3 (all scenes), BCLOSE

---

## STEP 3: Build Task List (in order, 2-day finish)

### TASK 0 (10 min) — H1 Consistency Audit (read-only, before B1-S5/S6 recording)
Check THREE things only. Fix only what fails. Do NOT re-record anything done.
1. Confirm no H1 VO/slide claims "GDC detects faster than SmartSignal/PRiSM/Mtell" (should already be clean — DEMO_MASTER §3 rule)
2. Confirm H1 reads as **AMBIGUOUS** (not "confident wrong answer") — the contrast with H2 must be clear
3. Confirm H1-P4 carries fleet-scale argument (MINUTES TO HOURS framing; optionally add "across hundreds of wells per shift, automatically" — slide text only, not a re-record)

If 1–3 pass: proceed. If any fail: targeted slide-text fix only. **No scene re-records.**

### TASK 1 (15 min) — H2 Instant-Triage Load (one-line code change + deploy)
**File:** `static/app.js` — function `loadH2Scenario()` at ~L2057
```
After: this.h2ReplayData = data;
Add:   this.h2CursorIdx = data.scada_alarm_idx || 0;
```
**Verify FIRST:** `curl http://gdc-pm.bdau.io/api/h2/scenario-replay | python3 -c "import sys,json;d=json.load(sys.stdin);print('scada_alarm_idx:',d.get('scada_alarm_idx'))"`
**Effect:** Tab opens with 90-day static history plotted, VIB-HI alarm already active, doc cascade ready — no more 8-week slow playback
**Deploy:** docker build → push → rollout restart → verify live

### TASK 2 (30–60 min) — H2 VO + Slide Framing (reframe to sharpened thesis)
**Read DECISION_DOSSIER.md §2.2–§2.4 fully before touching any slide text.**

The locked H2 thesis is: **"Clear signal. Confident APM verdict. Wrong action."** (opposite of H1's ambiguity)
- APM is RIGHT about the symptom (bearing wear pattern)
- APM is WRONG about the cause (paraffin restriction, off-sensor)
- GDC's L2 model catches the anomaly **pre-alarm** → routes to L3 doc search → names paraffin → averts pull

**What to check in `slides/h2.html`:**
- Slide 2 kicker must read "THE SIGNAL SAYS PULL" (should already be correct — confirm)
- Slide 2 sub-text must NOT say "ambiguous" — should say "clear signal, wrong answer" or "THE SIGNAL SAYS PULL"
- Confirm Slide 1 setup card mentions paraffin/wax waxy crude background (present in current slide)
- Fleet-scale framing: one sentence in Slide 2 or 3 should carry "across hundreds of wells per surveillance shift, GDC catches it automatically and researches the provenance"

**What to check in VIDS_PRODUCTION_MASTER.md B2 scene cards:**
- B2-P2 VO: confirm "bearing wear / pull" framing is "clear confident diagnosis → wrong action" not "ambiguous"
- B2-P2 VO: confirm fleet-scale ("caught early across hundreds of wells") is present or add it
- B2-S3 VO: confirm "paraffin restriction, NOT bearing wear" is the pivot, not just "bearings are actually fine"

If slide text needs updating: batched replace_in_file on slides/h2.html ONLY. Verify, deploy, confirm live.

**H2 Must-NOT-Say (check all VO + slides):**
- ❌ "Vibration crossed ISA-HI and the pump is pristine" (overclaims — bearing damage may exist once HI crossed)
- ❌ "Hot-oil guarantees full removal" → use "low-cost surface remediation" or "surface treatment"
- ❌ "GDC detects before APM" → L3 provenance is the win, not detection speed
- ❌ "APM missed this" → APM correctly identified the bearing-wear pattern; it missed the CAUSE (off-sensor)

### TASK 3 (30 min) — Record H2 Scenes
After Tasks 1 + 2 verified live, record B2-P1 through B2-S4 per VIDS_PRODUCTION_MASTER.md §SECTION 2 scene cards.
- B2-S5 is ❌ CUT — do not record
- Both action cards (hot-oil RECOMMENDED + pull AVERTED) must be visible for B2-S4

### TASK 4 (1–2 hrs) — H3 Iterative Vizier + Plan-vs-Live Build
**Read DECISION_DOSSIER.md §3.5 fully before touching app.py.**

**Step 4A — Make Vizier loop iterative** (`app.py` ~L6701–6770, function `vizier_optimize()`):
- Replace `suggest_trials(count=15)` single-batch with **3 rounds of 5 trials** → score on edge → re-suggest
- Vizier learns the gas-ceiling boundary from round-1 rejections → raises feasible rate
- Makes "searches and learns" **literally true** (not just a claim)
- Still ~15 trials; cost stays within free tier ($0)

**Step 4B — Plan-vs-live-state split** (new function `reconcile_live()`):
- Return both `plan_hz_vec` (what Vizier computed) AND `live_hz_vec` (after edge reconciles)
- Inject: well A-5 gets live motor temp +12°F above the plan's assumption (simulates degrading seal)
- Enforce `hz_live[i] ≤ hz_plan[i]` for ALL wells — edge ONLY trims DOWN (never up; up-reallocation would breach shared gas ceiling)
- Return `trims[]` list showing which wells were adjusted and why

**Step 4C — Presentation** (`tab_h3.html`):
- Add cloud-plan panel (Vizier results) + edge-reconcile panel (A-5 trimmed with reason)
- Render infeasible trials as ✗ and feasible as ✓ in trial log (data already in `is_failure`)
- Add: `<span style="font-size:0.50rem;color:var(--muted);font-style:italic">⏺ Architecture view — system-to-system flow</span>` honesty tag
- Label: "GDC-plan Hz" (what Vizier said) vs "GDC-live Hz" (what edge enforced after A-5 hot)

**Step 4D — Verify H3-S4** constraintDoc.found=True:
- `curl "http://gdc-pm.bdau.io/api/vizier/optimize" | python3 -c "import sys,json;d=json.load(sys.stdin);print('constraintDoc.found:',d.get('constraint_doc',{}).get('found'))"`
- Must return `True` consistently — if not, fix the RAG query at app.py ~L6540–6570 before recording B3-S4

### TASK 5 (30 min) — "Why GDC" Platform Tab (new nav tab)
**Read DECISION_DOSSIER.md §4 fully before building this tab.**

**Design:** Architecture/procurement beat. No demo-runnable content. Three pillars + RTOC scale shape.
1. **Form factor fit** — validated hardware across connected/software/air-gapped deployments
2. **Fleet governance** — ACM/Config-Sync + Fleet Management for GDC platform + apps (explicitly NOT OT/PLC/SCADA)
3. **Sovereign AI platform + Model-Ops depth** — same Google stack on-prem (GKE/AlloyDB Omni/Vertex/Gemini); train centrally; deploy **base models** with **local fine-tuning**; govern rollouts fleet-wide

**RTOC scale shape for the tab:**
- "A handful of regional operations centers per major, each governing thousands of wells"
- "One GDC cluster per regional RTOC" → fleet governance across that basin's wells
- Cite: YPF ~280 wells/engineer, SLB ALSC 847 wells — "hundreds of wells per surveillance engineer"

**MUST run grounded search FIRST:** `gemini_search("What is the current 2026 product name for Vertex AI enterprise / Gemini Enterprise Agent Platform in Google Cloud?")` before writing any product-name text.

**Must-NOT-Say:**
- ❌ Any competitive names (AWS Outposts, Azure Local, DIY)
- ❌ "Deploy models identically" → "base models + local fine-tuning"
- ❌ "Config-Sync manages your PLCs/SCADA"
- ❌ "Zero OT integration work"
- ❌ "Vendor-neutral" unscoped

**Tab placement:** New nav tab between "Classify" and "Optimize" **OR** after "Optimize" and before "ⓘ Reference" — your call on sequence. My lean: after "Optimize" / before "ⓘ Reference" so it reads as the procurement close after seeing all three horizons.

### TASK 6 (30 min) — Resume Recording
After Tasks 0–5 verified live:
- Record B1-S5, B1-S6 per VIDS_PRODUCTION_MASTER.md §SECTION 1 scene cards (VOs locked from BS+47)
- Record BBRIDGE
- Record H2 (if not already done in Task 3)
- Record H3 (following H3 3-act: cloud plan → edge reconcile A-5 trim → sovereign/scale)
- Record BCLOSE

---

## Deploy Command (permanent reference)
```bash
cd gke/fault-trigger-ui
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest .
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
```
**Registry:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/` (NOT gcr.io)

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- GPU scale-to-zero; `gpu-start.sh` ONLY for explicit LLM test (~$0.65/hr)
- VEO_COLD_OPEN.md has hidden-character lines — use write_to_file not replace_in_file
- B1-P1 through B1-S4 VO locked: recorded, match bible ✅
- B2-S5: ❌ CUT — do not record
- BBRIDGE VO: "all AI local, no cloud required" (not "air-gap capable")
- **Autonomy numeric knob: ❌ BLOCKED** — IEC 61511 FAILS
- **GAS LOCK VO physics:** PIP drops (SCADA signal). Casing annulus pressure rises (gas lock evidence). Do NOT change either.
- **H3 MUST-NOT-SAY list:** See DECISION_DOSSIER.md §3.6
- **H2 MUST-NOT-SAY list:** See DECISION_DOSSIER.md §2.3 + §2.7
- **Why-GDC MUST-NOT-SAY list:** See DECISION_DOSSIER.md §4.5
- **DEMO_MASTER §5/§6:** deferred update — dossier is the authoritative record; update §5/§6 BEFORE next major scenario review session

## Open Items (confirm before pixels)
1. Branding source-check: Vertex AI → Gemini Enterprise 2026 product name (search before Why-GDC tab text)
2. SME gut-check: H2 "caught pre-alarm → bearing damage not yet inevitable" framing (Bill Barna or equiv.)
3. Wells/engineer display figure: soften to "hundreds" or confirm lower bound from SME

## Recording Progress (for reference)
- ✅ B0.1–B0.4 (Intro) DONE
- ✅ B1-P1–B1-P5 (H1 briefing) DONE
- ✅ B1-S1–B1-S4 (H1 scenario) DONE
- ⏳ B1-S5, B1-S6 — record after Task 0 audit
- ⏳ BBRIDGE — record
- ⏳ H2 (B2-P1 through B2-S4) — record after Tasks 1–2
- ⏳ H3 (B3-P1 through B3-S5) — record after Task 4
- ⏳ BCLOSE — record
