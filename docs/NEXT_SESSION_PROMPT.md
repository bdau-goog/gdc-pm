# Next Session Prompt — GDC ESP Ops Video (Operational State)
Date: 2026-06-22 (Session BS+37) / branch: feature-trio-clean / docs-only (no app/cluster changes)
Git HEAD: 71ec245 (BS+37 Part B recording package reconciled to live app)
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

## STEP 3: Video Production Status

**Cold open (Part A):** COMPLETE — all 9 scenes produced/assembled in Vids. Final VO table locked in `docs/VEO_COLD_OPEN.md`. Scene 9 VO updated (BS+37) to bridge into the MEET GDC intro deck.

**Part B recording package:** COMPLETE AND VERIFIED (BS+37) — all four script-vs-app mismatches corrected. Record-ready.

### Part B Recording — START HERE
Use **`docs/DEMO_VO_PERPANEL.md`** as the primary per-scene recording guide (verified against the live app BS+37).
Use **`docs/VIDEO_SCRIPT_OPS_VIDS_V4_GROUNDED.md`** §2–§6 for extended narration options.
Use **`docs/RECORDING_GUIDE.md`** for capture setup (MacBook 1280×720 CSS, QuickTime → Vids).

**Demo flow (BS+37 verified):**
```
Cold open (Vids, 9 scenes) → Scene 9 "...First, a closer look at GDC itself — then we'll watch it work on a live well."
→ Intro tab (3 slides: What is GDC? / When to Consider / Deployment Models) → click ▶ View Demo →
→ Discern (H1) tab → Classify (H2) tab → Optimize (H3) tab → close on H3 uplift + ⓘ Reference tab
```

**Runtime:** ~5:50 total (Part A ~65s + Part B ~4:45) — under 6:00. Trim lever: ~10 words from H2 if needed.

**Verified live-app facts (BS+37 — do NOT contradict these during recording):**
| Element | Actual label in live app |
|---|---|
| Nav tabs | Intro · Discern · Classify · Optimize · ⓘ Reference |
| H1/H2 view toggle | 🟡 SCADA View / 🟢 GDC Advisor |
| H1 verdict cards | ✔ GAS LOCK CONFIRMED / ⚠ FLUID DRAWDOWN CONFIRMED |
| H1 HITL | GDC Agent · Action package ready · Awaiting RTOC approval + ✔ Approve & Execute |
| H1/H2 run button | ↺ New Scenario |
| H3 run button | ⚡ Run Vizier Optimization |
| H3 comparison | Baseline Hz column vs GDC Optimal column in per-well table (no toggle) |
| Close | H3 uplift card (+bbl/d, cash), then ⓘ Reference tab RTOC panel |
| Operations/Financials tabs | ❌ ORPHANED — not in nav, do not attempt to navigate there |

### Known Integrity Item
**Operations / Financials templates exist but are not wired into the nav header.** Confirmed orphaned in BS+27 and again in BS+37. The close narration has been re-pointed to H3 uplift + ⓘ Reference. **Future code task:** wire `tab_operations` and `tab_financials` into the nav header in `index.html` and the `mainTab` state in `app.js`, then verify and deploy. No urgency for the video recording — current close works on live reachable screens.

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied — would destroy the live cluster.
- All demo changes go into templates/*.html and app.py. Slides baked into image.
- GPU scale-to-zero; `gpu-start.sh` ONLY for explicit LLM test, always paired with `gpu-stop.sh`.
- VEO_COLD_OPEN.md has hidden-character lines (banner/en-dash) that defeat replace_in_file — use write_to_file as the fallback for that file (BS+29/BS+35/BS+37 lesson).
- Commit docs before ending any session — `git add docs/ && git commit -m "..."`.
