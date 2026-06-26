# Next Session Prompt — GDC ESP Ops Demo (Operational State)
Date: 2026-06-26 (Session BS+58) / branch: feature-trio-clean
Git HEAD: 0a30ee1 / Image: sha256:f733483fca110fab4d0b9902b8f023349c0b1216b1addbfe375fce3212198a3d
⚠ NOTE: All pods scaled to 0. Push origin/feature-trio-clean before or after next session.

## STEP 1: Run Four Startup Commands
```bash
kubectl get pods -n gdc-pm --no-headers
# Expected: No resources found (all scaled to 0)

kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
# Expected: 0

# API unavailable while pods are down — skip curl + psql until pods are scaled back up
# To restore: kubectl scale deployment -n gdc-pm --all --replicas=1
#             kubectl scale statefulset -n gdc-pm --all --replicas=1
```

## STEP 2: Read DEMO_MASTER.md + DECISION_DOSSIER.md
```bash
cat docs/DECISION_DOSSIER.md   # §2 H2 spec; §3 H3 spec; §3.7 Must-NOT-SAY
cat docs/SESSION_LOG.md | head -30
```

## STEP 3: Current State — All Recordings Completed
All recordings are done:
- ✅ B0.1–B0.4 (Intro) DONE
- ✅ B1-P1–P5 + B1-S1–S6 (H1) DONE
- ✅ B2-P1–P3 + B2-S1 + B2-S3 + B2-S3.5 + B2-S4 (H2) DONE
- ✅ BBRIDGE DONE
- ✅ H3 (B3-P1 through B3-S5) DONE
- ✅ BCLOSE DONE
- ✅ BWHY (Why GDC tab) DONE

### Iterative Vizier Loop: RESOLVED (was stale blocker)
The iterative 3-round × 5-trial Vizier loop was already implemented at app.py L6740-6786 (committed in Session BS+51). The NEXT_SESSION_PROMPT blocker from BS+57 was stale. Verified live: endpoint returns 15 trials across 3 rounds ({1, 2, 3}). `vizier_algorithm` returns `GAUSSIAN_PROCESS_BANDIT` (live) / `deterministic_convergence_demo` (fallback) at L6943.

### Uncommitted H3 UI Changes: COMMITTED (0a30ee1)
Three files committed this session:
- `slides/h3.html`: New Slide 3 "CORPORATE OPTIMIZATION — Vizier at Portfolio Scale" (now 4 slides total)
- `static/app.js`: h3SubTab, h3LiveVizier, vizierAlgorithm state + live_vizier API parameter
- `templates/tab_h3.html`: Cloud/edge sub-tab layout refactor

### Next Tasks (post-recording)
- Video editing / post-production (outside Cline scope)
- Any final UI polish if needed after video review
- Push feature-trio-clean to origin

## Deploy Command (permanent reference)
```bash
cd gke/fault-trigger-ui
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest .
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
```
**Registry:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/` (NOT gcr.io)

## Restore Cluster (when needed)
```bash
kubectl scale deployment -n gdc-pm --all --replicas=1
kubectl scale statefulset -n gdc-pm --all --replicas=1
kubectl get pods -n gdc-pm -w   # wait for all Running
```

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- GPU scale-to-zero; `gpu-start.sh` ONLY for explicit LLM test (~$0.65/hr)
- **live_vizier=True: announce before calling** — creates a billable Vizier study
- **H3 MUST-NOT-SAY:** See DECISION_DOSSIER.md §3.7
- **Why-GDC MUST-NOT-SAY:** See DECISION_DOSSIER.md §4.5
