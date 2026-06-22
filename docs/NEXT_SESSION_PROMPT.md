# Next Session Prompt — GDC ESP Cold-Open Video (Operational State)
Date: 2026-06-22 (Session BS+34) / branch: feature-trio-clean / docs-only (no app/cluster changes)
Git HEAD: c615c45fb142dc08ed5f6b05ec6c3b386742bcfd (uncommitted docs updated)
Image Digest: sha256:cd46caa8 (fault-trigger-ui, current)

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
cat docs/VEO_COLD_OPEN.md
```

## STEP 3: Next Implementation Task (Video production & walkthrough recording)
1. **Render Remaining Google Flow Clips:**
   - **Scene 2:** Wellhead + VFD control skid (tight push-in, schema-starved, no gauges).
   - **Scene 4:** Ambiguous alarm (operator Mark hesitates, eyes off-camera, pulsing amber warning).
   - **Scene 6:** Operator Mark Resolved (mirrors Scene 4; calm, steady green/blue screen-glow, single slow nod of approval, types final authorize key; uses same Mark Character setup & desk reference still).
2. **Assemble Video in Google Vids:**
   - Drop Scene 1, 2, 3, 4, 5 (all locked problem-half clips) on 5 scenes.
   - Drop Scene 5 GDC Hardware, Scene 6 Operator Resolved, and Scene 7 Dissolve on 3 solution-half scenes.
   - Attach per-scene VO verbatim from `docs/VEO_COLD_OPEN.md`.
3. **Record Live-Demo Walkthrough:**
   - Follow `docs/VIDEO_SCRIPT_OPS_VIDS_V4_GROUNDED.md` §2–6 and `docs/DEMO_VO_PERPANEL.md`.
   - Live demo is app-verified, number-free, and requires zero rendering.

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied — would destroy the live cluster.
- All demo changes go into templates/*.html and app.py. Slides baked into image.
- GPU scale-to-zero; `gpu-start.sh` ONLY for explicit LLM test, always paired with `gpu-stop.sh`.
