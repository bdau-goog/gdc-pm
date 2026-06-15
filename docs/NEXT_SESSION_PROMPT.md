# Next Session Prompt — GDC Edge AI Demo (Operational State)
Session BS wrap — June 15, 2026 / git head: `a929afb` / image: `sha256:37763297ef8a0b9d3d8712123a190984d234828b5f665f8d5b2879f1fd4b0e8b` / branch: `feature-trio-clean`

## STEP 1: Run These Four Commands First

```bash
# 1. GPU node pool at 0 (no idle billing)
kubectl get nodes -l cloud.google.com/gke-accelerator=nvidia-tesla-t4 --no-headers | wc -l
# Expected: 0 (Autopilot deprovisions T4 node ~2-3 min after scaling down)

# 2. Cluster health
kubectl get pods -n gdc-pm --no-headers 2>/dev/null | awk '{print $3}' | sort | uniq -c
# Expected: 1 Completed + 7 Running (Ollama at 0 replicas - correct default)

# 3. Ollama replicas
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
# Expected: 0 (correct dev default, stood down via gpu-stop.sh)

# 4. API status
curl -s --max-time 2 http://gdc-pm.bdau.io/api/mlops/status | \
  python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:', d.get('ollama_online'))" \
  2>/dev/null || echo "API offline"
# Expected: ollama_online: False (correct dev default)
```

## STEP 2: Read DEMO_MASTER.md

```bash
cat /home/brian/gdc-pm/docs/DEMO_MASTER.md
```

## STEP 3: Next Implementation Task

The sovereign self-hosting fix for Vue and Plotly has been fully deployed, verified, and committed. The blank-screen / `v-cloak` lock issue is completely resolved. The next step is to record the demo videos as specified in `docs/VIDEO_SCRIPT.md`.

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied (would destroy live cluster)
- No `browser_action` (SSH remote, no browser)
- Batch all edits to same file in ONE `replace_in_file` call
- `feature-trio-clean` branch — do NOT merge to main
- No GPU start without announcing cost (~$0.35/hr T4) and getting confirmation
- Deploy sequence: `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status`
- Artifact Registry only — NOT gcr.io
- All Ollama API calls MUST include `"think": False` — do not omit this
