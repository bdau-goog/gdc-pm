# Next Session Prompt — GDC ESP Cold-Open Video (Operational State)
Date: 2026-06-22 (Session BS+36) / branch: feature-trio-clean / docs-only (no app/cluster changes)
Git HEAD: a05e082 + uncommitted docs (VEO_COLD_OPEN, NEXT_SESSION_PROMPT, SESSION_LOG) — commit before next session
Image Digest: sha256:cd46caa8 (fault-trigger-ui, current — unchanged)

## STEP 1: Run These Four Commands First (Skip cluster startup unless app changes are made)
```bash
# 1. Pods (all healthy and running)
kubectl get pods -n gdc-pm --no-headers
# Expected: alloydb, event-processor, fault-trigger-ui, rabbitmq, grafana, inference-api, telemetry-simulator all 1/1 Running.

# 2. Ollama replicas (dormant by default)
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
# Expected: 0

# 3. MLOps Status (ollama offline is expected dev default)
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))" 2>/dev/null || echo "API unreachable"
# Expected: ollama_online: False model: offline

# 4. DB Counts (seeded and stable)
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
# Expected: field_intel = 11, rag_documents = 20
```

## STEP 2: Read DEMO_MASTER.md and VEO_COLD_OPEN.md
```bash
cat docs/DEMO_MASTER.md
cat docs/VEO_COLD_OPEN.md      # SCENE↔BEAT MAP at top is the canonical 9-scene order
```

## STEP 3: Cold-Open Status — ALL 9 SCENES COMPLETE ✅

**Cold open is DONE.** All 9 scenes produced and assembled in Vids. Final VO table locked in `docs/VEO_COLD_OPEN.md`.

**Final 9-scene VO (record-ready):**
| # | VO |
|---|---|
| 1 | *"Upstream oil and gas runs on engineering discipline — lifting every barrel as efficiently and safely as possible."* |
| 2 | *"Electric submersible pumps — ESPs — do that lifting. Maintaining them well keeps costs down and optimizes production."* |
| 3 | *"Occasionally, monitoring systems trigger alarms, telling you a well is in trouble. Often, these are easily diagnosed."* |
| 4 | *"But some alarms are ambiguous — the signals alone can't tell you the cause."* |
| 5 | *"The context that can help is scattered across distributed systems — slow to assemble when the decision can't wait."* |
| 6 | *"This is where Google Distributed Cloud comes in — it brings Google's AI to your data, instead of your data to the cloud."* |
| 7A | *"Using your secured networks and data…"* |
| 7B | *"…GDC combines and evaluates multiple sensor streams in real time — identifying the developing issue."* |
| 8 | *"GDC then fuses your live documents with that data — diagnoses the fault, prepares the fix, and awaits your authorization."* |
| 9 | *"The decision — and the control — are always yours. Let's see it work on a live well right now."* |

**Key production notes (BS+36):**
- Scene 7 = POV cut: 7A Veo render (Mark, hard down-left, audio suppressed) + 7B real screenshot (detection-moment: GDC marker fired, hs=0.9029, docs loading, no recommendation)
- Scene 8 = fresh cold render (NOT Extend), lamp dims and goes dark as dominant event, still-frame from 7A as ingredient
- Scene 9 = FLUID DRAWDOWN fully-revealed screenshot (or live screen-recording), slow push-in + brighten
- **Mute all Veo audio tracks in Vids.** No-dialogue suppression clause in every character render prompt (BS+36 permanent guardrail).

### Next task: Narrative review + alignment check (~6 min target)

**Goal:** Ensure the cold open (Part A) and the live demo walkthrough (Part B) are on the same message, have no contradictions, and fit within ~6 minutes total.

**Step 1 — Read the three production scripts:**
```bash
cat docs/VEO_COLD_OPEN.md      # Part A: 9-scene VO table (lines 1-20 = the VO table)
cat docs/VIDEO_SCRIPT_OPS_VIDS_V4_GROUNDED.md   # Part B: live demo walkthrough
cat docs/DEMO_VO_PERPANEL.md   # Part B: per-panel demo VO with [ACTION] notes
```

**Step 2 — Runtime check:**
- Part A (cold open): 9 scenes × ~7-10s = **~60-75s**
- Part B (live demo): How It Works + H1 + H2 + H3 + close = **~4:00** (per DEMO_MASTER)
- Total: **~5:00-5:15** (target ≤6:00) — should pass, but verify Part B word count
- Check: does the Scene 9 VO ("The decision — and the control — are always yours...") set up Part B intro cleanly?

**Step 3 — On-message consistency check:**
- Cold open claims "diagnoses the fault, prepares the fix, awaits your authorization" (Scene 8 VO) → verify the live demo HITL screen shows exactly this (GDC AGENT · ACTION PACKAGE READY · AWAITING RTOC APPROVAL + "Approve & Execute")
- Cold open says "using your secured networks and data" (Scene 7A VO) → verify V4_GROUNDED doesn't over-claim sovereignty at L2 (per DEMO_MASTER §3 BQ patch)
- Cold open says "identifies the developing issue" (Scene 7B VO) → verify Part B "How It Works" section matches this framing (multivariate pre-threshold, not "we detect faster than SCADA" against best-of-breed APM)
- Cold open says "the decision and control are always yours" (Scene 9) → verify HITL gate is prominent in H1/H2 demo narration

**Step 4 — Output:** A short alignment report: any contradictions, any timing risks, any VO lines in Part B that need adjustment. Then update V4_GROUNDED or DEMO_VO_PERPANEL if needed.

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied — would destroy the live cluster.
- All demo changes go into templates/*.html and app.py. Slides baked into image.
- GPU scale-to-zero; `gpu-start.sh` ONLY for explicit LLM test, always paired with `gpu-stop.sh`.
- VEO_COLD_OPEN.md has hidden-character lines (banner/en-dash) that defeat replace_in_file — use write_to_file as the fallback for that file (BS+29/BS+35 lesson).
