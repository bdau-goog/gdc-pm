# Next Session Prompt — GDC ESP Cold-Open Video (Operational State)
Date: 2026-06-21 (Session BS+33) / branch: feature-trio-clean / docs-only (no app/cluster changes)
Task focus: **finish the Veo cold open**, then record the live-demo walkthrough. NO cluster work needed.

## STEP 0: Skip cluster startup
This is a video/narrative work-stream. ollama offline = expected. Do NOT scale GPU. Do NOT run the 4 startup commands unless you pivot to app code.

## STEP 1: Read these, in order
```bash
cat docs/VEO_COLD_OPEN.md          # the cold-open spec — READ THE M3 RESET BANNER
sed -n '1,40p' docs/SESSION_LOG.md # last session (BS+33) context
```
Also have ready (the live-demo half, already written + app-verified):
`docs/VIDEO_SCRIPT_OPS_VIDS_V4_GROUNDED.md` §2–6 · `docs/DEMO_VO_PERPANEL.md`

## STEP 2: WHERE THE COLD OPEN STANDS (the single most important thing)
**Scenes 1–5 are LOCKED and final (Movements 1–2 = the PROBLEM half).** VO is verbatim, do not reword:
1. *"Upstream oil and gas runs on engineering discipline — lifting every barrel as efficiently and safely as possible."* ✅ rendered
2. *"Electric submersible pumps - ESPs - do that lifting. Maintaining them well keeps costs down and optimizes production."* (gauge-free prompt ready)
3. *"Occasionally, monitoring systems trigger alarms, telling you a well is in trouble. Often, these are easily diagnosed."* (Beat-3 operator footage ✅; merges old 3+4A)
4. *"But some alarms are ambiguous — the signals alone can't tell you the cause."* (operator hesitates)
5. *"The context that can help is scattered across distributed systems — slow to assemble when the decision can't wait."* (overhead scattered desk)

**Movement 3 (the SOLUTION half) is VOID and must be redesigned next session.** Old Beats 5A/5B/6A/6B/7 are reference-only — do NOT render as written.

## STEP 3: THE M3 REDESIGN — the value-prop spine that MUST land (this was the missing clarity)
M1–M2 filmed the problem. **M3 must land the operator BENEFIT** as one affirmative spine, in order:
1. **MORE TIME** — GDC flags the ambiguous well early, before failure is irreversible (DEMO_MASTER §1).
2. **MORE CONTEXT INGESTED** — it reads + fuses the well's own scattered documents no sensor system reads (DEMO_MASTER §3 Diagnostic Gap / L3 moat).
3. **MORE AI/LLM-DRIVEN INSIGHT** — turns fused context into a cited, reviewable diagnosis + recommended action, in seconds, in the operator's perimeter (System A retrieval + System B Gemma; HITL).
**Net:** more time + more context + more insight → operator takes the right action every time vs. a reflexive expensive shut-in. **Sovereignty is the enabling WHERE, kept secondary — not the headline.**

## STEP 4: THE HARD RENDER LESSON (do not relearn it)
**Veo renders nouns, not concepts.** M1–M2 worked because each beat is one literal object. M3 failed because it asked Veo to draw abstractions (logical perimeter, data fusion) → it over-literalizes into hazards (explosion/liquid/lasers/steam) or draws the wrong thing (physical badge-door for a logical perimeter). **Do NOT re-attempt 5B/6A/6B as literal fusion/perimeter renders.**

**Two honest M3 paths (pick one with the user FIRST, before rendering):**
- **PATH A** — cut straight to the live app for the solution (V4's canonical answer): the cold open is the problem; dissolve into the live UI where fusion/verdict/perimeter are shown for real. Fewest renders, zero abstraction risk. (V4 §2 + DEMO_VO_PERPANEL §0.)
- **PATH B** — 1–2 literal solution beats, VO carries the meaning: only renderable solution nouns = (a) GDC hardware (Scene 5A clip already done & loved) + (b) the SAME operator now RESOLVED (calm, confident, deciding — mirrors Scene 4's hesitation, closes the human arc). No server-room "fusion" shot, no perimeter door.

## STEP 5: PATH TO FINISH (then record the demo — the easy, zero-render part)
1. Decide M3 path (A or B) with user.
2. Render remaining LITERAL clips only: Scene 2 (gauge-free wellhead), Scene 4 (operator hesitates), Scene 5 (scattered desk), + Path-B operator-resolved beat if chosen.
3. Assemble cold open in Vids (one clip per scene, per-scene VO).
4. **Record the live demo** — fully scripted + app-verified already: V4 §2–6 + DEMO_VO_PERPANEL (How It Works → H1 Discern → H2 Classify → H3 Optimize → Close). Number-free, no run desync. ZERO rendering risk.

## RENDER MECHANICS (settled BS+32 — in VEO_COLD_OPEN.md "Flow mechanics")
- Tool: **Google Flow**. Model: **Omni Flash** (references ✅, ~10s). **Extend is BROKEN** (blank video) — continuity = still-frame ingredients only. Veo 3.1 Quality CANNOT use references.
- Ingredients via **Nano Banana Pro**. Veo output count is on the video bar (not the image-default panel) — or just re-run 3–4×.
- Guardrails: no readable screens/UI; no Dell branding / never feed the Dell photo; schema-starve outdoor beats (blue valve-tree, never "oil field/pumpjack"); don't specify countable small details (gauges) — frame them out/blur.

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied. Tab content = templates/*.html + app.py. Slides baked into image. Source env: `source /home/brian/gdc-pm/.env`.
- GPU scale-to-zero; gpu-start.sh ONLY for explicit LLM test, paired with gpu-stop.sh.
