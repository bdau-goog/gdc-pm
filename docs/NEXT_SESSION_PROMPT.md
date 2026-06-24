# Next Session Prompt — GDC ESP Ops Video (Operational State)
Date: 2026-06-24 (Session BS+45 wrap) / branch: feature-trio-clean
Git HEAD: 6211202 / Image: sha256:26bab26d826948fb52417571c94e5de1e0017cbb5dad9617e0053596f9a16155

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

## STEP 3: Next Implementation Tasks (Priority Order)

All 6 tasks below are **research-gated or recording-prep**. Do NOT start code until the
MCP research pass in Task 1 returns a sourced answer.

---

### TASK 1 — MCP Research: Correct ESP gas-handling terminology 🔴 MUST DO FIRST
**Why:** The session ended without a verified answer. Per PRIME DIRECTIVE SOURCE gate,
no claim goes on screen without a citeable source. This gates Tasks 2+3.

**Research question (run via gdc-second-opinion MCP):**
> "For an ESP (electrical submersible pump) operating in a high-GOR Permian well:
> What is the correct API RP 11S / industry-standard term for the failure cause where
> free gas enters the pump stages and degrades hydraulic performance?
> Options: (a) Gas Interference, (b) Gas Entrainment, (c) Gas Lock.
> Which term refers to the degradation/cause and which refers to the acute failure state
> (pump fully vapor-bound, no fluid flow)? Please cite API RP 11S or SLB/OEM references."

**Expected answer:** gas interference (or gas entrainment) = the cause/degradation;
gas lock = the acute failure endpoint (what we're racing to prevent).
Once confirmed, lock the authoritative cause-term and apply in Tasks 2+3.

---

### TASK 2 — Relabel H1 verdict cause-term (gas lock → confirmed cause-term)
**Scope:** UI display only. Internal enum `gas_lock` and `fault_type='gas_lock'` stay
as-is throughout app.py / app.js. Only the text visible to the audience changes.

**Files and exact locations:**

**A. `gke/fault-trigger-ui/templates/tab_h1.html` line 298:**
```
✔  GAS LOCK CONFIRMED
```
→ Change to: `✔  GAS [CONFIRMED TERM] CONFIRMED — free gas in pump stages`

**B. `gke/fault-trigger-ui/templates/tab_h1.html` line 302:**
```
Docs fused: Shift Note (06:15 Tour 2) + Separator GOR Lab · Casing annulus fully submerged. Gas pocket in pump stages.
```
→ Tune description to reflect the new term + mention GAS LOCK is what is being prevented:
e.g. "Casing annulus fully submerged. Gas interference in pump stages. VFD trim vents
gas before gas-lock and motor burnout."

**C. `gke/fault-trigger-ui/slides/h1.html` Slide 2 left wellbore label:**
→ Already says "GAS ENTRAINMENT" — verify it's the correct cause-term from Task 1.
If the correct term is "gas interference," relabel. If "entrainment" is acceptable,
leave and note the cause-term consistency. Either way add "(→ prevents Gas Lock)" below it.

**D. `docs/DEMO_MASTER.md` §2 H1 row and §4.1:**
→ Update "Gas Lock or Fluid Drawdown" scenario name to "[Correct cause-term] or Fluid Drawdown"
in the table. Update §4.1 text that currently says "Gas Lock (GVF rising)".

**E. `docs/VIDS_PRODUCTION_MASTER.md` B1-S4 VO (line ~487–492):**
→ Update the Gas Lock VO branch from "cited verdict: gas lock" to "cited verdict: [confirmed term]."
B1-S4 has NOT been recorded yet — this is a free change.

---

### TASK 3 — GVF 78% RT fix (two-part integrity issue)

**Problem A:** UI card in `tab_h1.html` line 454 hardcodes `"GVF 78% at intake"`.
78% contradicts our own OEM bulletin (app.py line 1256: "At GVF above approximately
20–25%, pump hydraulic output drops sharply") — at 78%, the pump would already be
fully gas-locked, not in early interference. An ESP engineer will catch this in 30
seconds.
**Fix:** Change the UI hardcode to a defensible early-interference figure.
Candidates: ~25–35% GVF (above the onset threshold, not yet full lock).
Exact value TBD based on Task 1 research — pick the value consistent with "early
detection window" narrative. If rag_sections[0].full_text is being rendered, also
check what the retrieved shift note says.

**Problem B:** The seeded `app.py` shift note (line 1205) says only "GVF estimated
elevated based on casing pressure behaviour" — **no number**. The UI card says 78%.
That's a No-Silent-Lies violation (displayed ≠ actual source).
**Fix:** Either (a) add a specific GVF number to the shift-note seed text (using the
corrected defensible figure from Problem A), OR (b) change the UI card to use
comparative language "GVF estimated elevated" with no hard number.
Option (b) is safer per §7.5 content policy (no authored hard numbers in briefing copy).

**After fixing the seed text:** re-embed by triggering a re-seed. The simplest way is:
```bash
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c \
  "DELETE FROM rag_documents WHERE doc_title ILIKE 'Well A-3 — Tour 2 Shift Note%';"
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
# The _seed_l3_scenario_docs_bg() thread re-inserts on startup with new embedding
```

---

### TASK 4 — Doc 3 card integrity fix (No-Silent-Lies)
**Problem:** `tab_h1.html` Doc 3 card (line 488) has a **hardcoded label**
("OEM Troubleshooting Guide · Gas Volume Fraction Handling · Permian ESP Operational Manual")
but the **modal** renders `rag_sections[2]` — whatever pgvector ranked 3rd.
On a recent run, rag_sections[2] was the ESP Workover Inspection Record (not the OEM
bulletin). Card said one thing; modal showed another. Classic No-Silent-Lies violation.

**Fix (3 lines in tab_h1.html, starting line 487):**
Change the hardcoded title/subtitle to bind to `rag_sections[2].title`:
```html
<!-- before: hardcoded "OEM Troubleshooting Guide" -->
<div style="font-weight:700;font-size:0.62rem;line-height:1.3">OEM Troubleshooting Guide
  <br><span ...>Gas Volume Fraction Handling · Permian ESP Operational Manual</span>
</div>

<!-- after: dynamic from live retrieval -->
<div style="font-weight:700;font-size:0.62rem;line-height:1.3">
  {{ h1ReplayData && h1ReplayData.rag_sections && h1ReplayData.rag_sections[2]
     ? h1ReplayData.rag_sections[2].title : 'Retrieved Field Document' }}
</div>
```
Also update the SVG icon text label from `OEM` to something neutral (e.g. `DOC`) or
bind to a short word derived from the title.

**This task is independent of Tasks 1–3 and can ship first if desired.**

---

### TASK 5 — Recording plan: clicking into document modals on camera
**Context (raised BS+45):** The B1-S4 choreography in `VIDS_PRODUCTION_MASTER.md`
says "let docs + verdict render; zoom each doc card briefly" but does NOT include
clicking into any document modal to show the full field record. The user noted we
should enter at least one document during recording — showing the full modal is the
*proof* of L3 document fusion.

**Decision needed before recording B1-S4:**
Which document should be opened on camera? Options:
- Doc 1 (Shift Note or Sonic Log — the primary discriminating document)
- Doc 2 (Separator Lab Report — GOR numbers)
- Doc 3 (whatever rag_sections[2] is — see Task 4 above)

**Recommendation:** Open Doc 1 on camera for ~3s (it's the primary evidence that
resolves Gas Lock vs Drawdown), then close and proceed to approve. Add to B1-S4
choreography in VIDS_PRODUCTION_MASTER.md.

**Note:** Modals are fully functional — this is a recording-only change to the bible,
not a code change.

---

### TASK 6 — HITL remediation UX: Approve → Notify Ops (not auto-send VFD)
**Context (raised BS+45):** Current UX: click "✔ Approve & Execute" → executes the
VFD trim directly (or shows recovery state). User wants: Approve → GDC generates a
**notification/work order to the operations team** rather than auto-sending the VFD
command. This is more realistic HITL: GDC advises + packages the action → engineer
approves → ops team receives notification to execute.

**Impact assessment:**
- The current `approveH1VFD()` in `app.js` calls `/api/agent/hitl-approve` and then
  shows a recovery state. The backend registers the approval in `field_intel`.
- A UX change here affects: button label, post-approval state text, and possibly the
  outcome card.

**Proposed UX (for discussion next session):**
1. Button label: "✔ Approve & Dispatch Recommendation" (not "Approve & Execute")
2. Post-approval card: "RECOMMENDATION DISPATCHED — Ops team notified. Awaiting
   field confirmation. VFD adjustment to be executed by operations personnel."
3. NOT: "✅ RECOVERING — VFD at 44 Hz" (which implies the VFD was changed by GDC)

**Before coding:** Run in-persona hostile-engineer RT on the proposed UX change
(does "ops team notification" framing still make the HITL value-prop land?). This
is a narrative/UX decision, not just a code change.

---

## STEP 4: After H1 — Recording Order (unchanged from BS+44)

| Next | Scene | ~Time |
|---|---|---|
| BBRIDGE | H2→H3 Sovereignty Bridge | ~8s |
| B2-S1–S4 | H2 CLASSIFY scenario (B2-S5 ❌ CUT) | ~50s |
| B3-S1–S3 | H3 OPTIMIZE (Vizier → table → uplift) | ~45s |
| B3-S4 | H3 constraint provenance — CONDITIONAL | ~8s |

**B3-S4 gate:**
```bash
curl -s "http://gdc-pm.bdau.io/api/vizier/optimize" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print('constraintDoc.found:', d.get('constraint_doc', {}).get('found'))"
# Expected: constraintDoc.found: True
```

**⚠️ DO NOT record B1-S4 until Tasks 1–4 are resolved.** The recording will show
the wrong terminology and a wrong/ambiguous doc card label. All other scenes
(B1-S1, B1-S2, B1-S3, B1-S5, B1-S6) are safe to record now.

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
- Reference tab integrity scrub COMPLETE (BS+44) ✅
- **B1-S4: ⛔ HOLD — do not record until Tasks 1–4 resolved this session**

## What BS+45 Shipped (already deployed, do not re-do)
- Doc-card leak fix: `loadH1Scenario()` now resets h1RagDoc2Shown/h1RagDoc3Shown/h1RagPending + clears stale timers. Image sha256:26bab26d committed a729236.
- B1-S1 bridge VO updated: "Now let's look at how GDC helps with our unloading scenario…" (VIDS_PRODUCTION_MASTER line 428, commit a729236).
