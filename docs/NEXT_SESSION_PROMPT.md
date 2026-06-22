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

## STEP 3: Cold-Open Status — 9-scene structure, Scenes 1-6 RENDERED, 7-9 REMAIN
Canonical structure + per-scene VO are LOCKED in `docs/VEO_COLD_OPEN.md` (SCENE↔BEAT MAP table at top).
`docs/VIDEO_SCRIPT_OPS_VIDS_V4_GROUNDED.md` §1 is reconciled verbatim — both docs agree on every line.

**Production tool (BS+36):** Scene 8 = fresh cold render (NOT Extend — lamp-out dominant event). Scene 9 = Vids build from real screen-recording.

### Remaining render tasks (Vids/Veo):
1. **Scene 7 ✅ DONE** — POV cut assembled as two sub-scenes in Vids:
   - **7A (~3s):** Veo render of Mark (hard down-left head turn, multi-channel data-light, audio suppressed) ✅ RENDERED. This is also the **Extend base clip for Scene 8**.
   - **7B (~6-7s):** Real GDC Advisor DETECTION-MOMENT screenshot ✅ DONE (GDC marker fired, hs = 0.9029, docs loading, no recommendation yet). Ken Burns: start on both markers, drift to Decision Console showing "WELL A-3 — BASELINE MONITORING · RETRIEVED CONTEXT — ALLOYDB PGVECTOR (< 2S)" loading state.
   - **VO (rebalanced split):** 7A = *"Using your secured networks and data…"* | 7B = *"…GDC combines and evaluates multiple sensor streams in real time — identifying the developing issue."* Record as one take spanning both sub-scenes.
2. **Scene 8 (Beat 7) — Operator resolved + HITL. ⬜ NEXT.** **FRESH COLD RENDER — do NOT Extend** (Extend kept the lamp on). Use a still frame from 7A as reference ingredient. Four-beat sequence: (1) satisfied certainty → (2) tap key to authorize → (3) amber lamp dims and goes DARK → (4) settles back, cool blue only. Lamp-out is the dominant visual event. **Add no-dialogue suppression clause.** **MUTE Veo audio in Vids.** VO: *"GDC then fuses your live documents with that data — diagnoses the fault, prepares the fix, and awaits your authorization."*
3. **Scene 9 (Beat 8) — Dissolve hand-off. ⬜** Build in Vids from real GDC Advisor screen-recording (FLUID DRAWDOWN fully-revealed screenshot recommended — or live screen-recording, slow push-in + brighten). VO: *"The decision — and the control — are always yours. Let's see it work on a live well right now."*

### Then:
4. **Assemble all 9 scenes in Vids**, one clip per scene, attach per-scene VO verbatim (Scene 6 sled clip reused as-is). See VEO_COLD_OPEN.md "HOW TO RECORD PER-SCENE VOICEOVER."
5. **Record Part B live-demo walkthrough** — V4_GROUNDED §3-6 + DEMO_VO_PERPANEL.md. App-verified, number-free, zero render risk. This is the finish line.

### Narrative guardrail (PRIME DIRECTIVE — do not violate):
Scene 7 pre-threshold edge is claimed **only vs. threshold-only SCADA** (4–9-min H1 lead), **never vs. best-of-breed APM** (detection converges there). Categorical moat = Scene 8 document fusion. (DEMO_MASTER §3 / NARRATIVE_GUIDANCE tier table.)

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied — would destroy the live cluster.
- All demo changes go into templates/*.html and app.py. Slides baked into image.
- GPU scale-to-zero; `gpu-start.sh` ONLY for explicit LLM test, always paired with `gpu-stop.sh`.
- VEO_COLD_OPEN.md has hidden-character lines (banner/en-dash) that defeat replace_in_file — use write_to_file as the fallback for that file (BS+29/BS+35 lesson).
