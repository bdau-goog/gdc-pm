# Next Session Prompt — GDC ESP Ops Video (Operational State)
Date: 2026-06-23 (Session BS+38) / branch: feature-trio-clean / docs-only this session
Git HEAD: 975d012 (BS+38 VIDS_PRODUCTION_MASTER.md — shot bible, sovereignty spine, 40 scenes)
Image Digest: sha256:65e1f258 (fault-trigger-ui, current — deployed and verified BS+37)

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

## STEP 2: Read DEMO_MASTER.md and the shot bible
```bash
cat docs/DEMO_MASTER.md
cat docs/VIDS_PRODUCTION_MASTER.md   # ← PRIMARY REFERENCE for next session
```

## STEP 3: Next Session — Part B Recording Walkthrough

**Primary task:** Walk through building Part B (live screen-recording demo) scene by scene, using `docs/VIDS_PRODUCTION_MASTER.md` as the directing document.

**Start here — Section 0 (MEET GDC):**
- `docs/VIDS_PRODUCTION_MASTER.md` §"SECTION 0 — MEET GDC" (scenes B0.1 → B0.3)
- Key: B0.3 VO is EXTENDED from prior scripts — new line: *"You'll see both ends of that spectrum today."* This is the sovereignty PLANT.

**Then proceed in order:**
- §"SECTION 1 — H1 DISCERN" (B1-P1 → B1-S6) — note B1-S2 is a NEW scene (pre-threshold detect)
- §"SECTION 2 — H2 CLASSIFY" (B2-P1 → B2-S5)
- §"SOVEREIGNTY BRIDGE" (BBRIDGE) — NEW scene, callback to Intro Slide 3
- §"SECTION 3 — H3 OPTIMIZE" (B3-P1 → B3-S5) — note B3-S4 is CONDITIONAL (see code task below)
- §"CLOSE" (BCLOSE)

**Before recording B3-S4 (H3 constraint provenance):**
```bash
# Verify the RAG constraint query returns found=true consistently
curl -s "http://gdc-pm.bdau.io/api/vizier/optimize" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); cd=d.get('constraint_doc',{}); print('found:',cd.get('found'),'title:',cd.get('title','—'))"
# Expected: found: True  title: <midstream contract document title>
# If found: False → code fix needed in app.py L6530-6545 before recording B3-S4
```

**Recording setup reference:** `docs/RECORDING_GUIDE.md`
- MacBook · Chrome DevTools 1280×720 CSS · QuickTime record-then-import · Vids crop 16:9 · export 1440p Rec.709

**Part A status (cold open):**
- Scenes 1–7, 9: DONE
- Scene 8 (A8 — operator authorized, lamp-out): **TO RENDER** — fresh cold render, NOT Extend, use A7A still-frame as ingredient. Prompt in `docs/VEO_COLD_OPEN.md` Beat 7.

## Verified live-app facts (BS+37 — do NOT contradict these during recording)
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
| Operations/Financials tabs | ❌ ORPHANED — not in nav, do not navigate there |

## Known Integrity Items
| Item | Fix needed |
|---|---|
| B3-S4 constraintDoc reliability | Verify app.py L6530–6545 RAG query returns `found=true`; fix if not before recording |
| Operations/Financials orphaned tabs | Wire into nav header + mainTab state (future code task, no urgency for video) |
| Part A Scene A8 | Fresh cold Veo render (lamp-out dominant event; NOT Extend; use A7A still as ingredient) |

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied — would destroy the live cluster.
- All demo changes go into templates/*.html and app.py. Slides baked into image.
- GPU scale-to-zero; `gpu-start.sh` ONLY for explicit LLM test, always paired with `gpu-stop.sh`.
- VEO_COLD_OPEN.md has hidden-character lines — use write_to_file as fallback (not replace_in_file).
- Commit docs before ending any session — `git add docs/ && git commit -m "..."`.
