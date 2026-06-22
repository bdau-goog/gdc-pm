# Next Session Prompt — GDC ESP Cold-Open Video (Operational State)
Date: 2026-06-22 (Session BS+35) / branch: feature-trio-clean / docs-only (no app/cluster changes)
Git HEAD: a05e082 + uncommitted docs (VEO_COLD_OPEN, V4_GROUNDED, SESSION_LOG, this file) — commit before next session
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

**Production tool (BS+35 decision):** remaining solution-half beats are made in **Vids/Veo using EXTEND**.

### Remaining render tasks (Vids/Veo):
1. **Scene 7 (Beat 6) — Pre-threshold scoring.** Prompt = VEO_COLD_OPEN.md "Beat 6 (Scene 7)". Mark's eyes, calm/blue-green, screen-free. Render as the **Extend base clip**. VO: *"At the edge, GDC scores the combined pattern across all channels simultaneously — identifying the drift before SCADA can alarm."*
2. **Scene 8 (Beat 7) — Operator resolved + HITL.** **EXTEND from Scene 7.** Mark's resolved nod + authorize keystroke; mirror of Scene 4. VO: *"Then, it automatically reads and fuses the well's complete document history — delivering a cited recommendation for operator approval."*
3. **Scene 9 (Beat 8) — Dissolve hand-off.** Standalone push-in to a glowing dashboard. VO: *"Let's dive into the live system, and see GDC analyze a struggling well at the source."*

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
