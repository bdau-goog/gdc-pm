# Next Session Prompt — GDC ESP Ops Video (Operational State)
Date: 2026-06-23 (Session BS+39) / branch: feature-trio-clean
Git HEAD: (see `git log --oneline -3` after startup) / Image: sha256:60bf5924 (fault-trigger-ui, Slide 4 v5)

## STEP 1: Run These Four Commands First
```bash
kubectl get pods -n gdc-pm --no-headers
# Expected: all 1/1 Running

kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
# Expected: 0

curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))" 2>/dev/null || echo "API unreachable"
# Expected: ollama_online: False model: offline

kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
# Expected: field_intel = 11, rag_documents = 20
```

## STEP 2: Read These Documents
```bash
cat docs/VIDS_PRODUCTION_MASTER.md   # PRIMARY REFERENCE — shot bible
# Last 3 SESSION_LOG entries for context
```

## STEP 3: Next Implementation Task — §1 H1 DISCERN

Start at `docs/VIDS_PRODUCTION_MASTER.md` §SECTION 1 (B1-P1 → B1-S6).

**Recording method (settled):** Screen Studio on BenQ 2560×1440 native full-screen (no viewport shrink, no DevTools). Cursor-driven zoom via Screen Studio. VO recorded per-scene in Screen Studio then imported to Vids.

**B3-S4 gate (pre-verified BS+39 — still valid):**
```bash
curl -s "http://gdc-pm.bdau.io/api/vizier/optimize" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); cd=d.get('constraint_doc',{}); print('found:',cd.get('found'),'title:',cd.get('title','—'))"
# Expected: found: True  title: Pad Alpha — Gas Gathering Agreement (Ref. PA-2024-GG-047)
```
If found: False → code fix needed in app.py L6530-6545 before recording B3-S4.

## Session BS+39 Key Decisions (do NOT revert)
| Decision | Detail |
|---|---|
| B0.3 sovereignty plant CUT | "both ends of that spectrum" overclaimed two hardware SKUs. Recorded VO omits this line. |
| B0.4 NEW slide added | "Two Edge Architectures — Fully On-Prem and Hybrid" — honest topology plant. Committed 115ed31. |
| "Air-gap capable" removed | Demo runs on Connected GDC; "air-gap capable" implies hardware-level isolation we don't have. Sovereignty framing = "all AI on-prem, fully sovereign" |
| BBRIDGE callback | Now points to B0.4 (not B0.3 plant). Still standalone-true. |
| B0.4 VO (locked) | "Three scenarios — two where all AI runs on-prem against local data, fully sovereign. The third reaches the cloud for one service: Vizier, Google's powerful AI optimizer." |

## Verified Live-App Facts (BS+37/39 — do NOT contradict during recording)
| Element | Actual label in live app |
|---|---|
| Nav tabs | Intro · Discern · Classify · Optimize · ⓘ Reference |
| H1/H2 view toggle | 🟡 SCADA View / 🟢 GDC Advisor |
| H1 verdict cards | ✔ GAS LOCK CONFIRMED / ⚠ FLUID DRAWDOWN CONFIRMED |
| H1 HITL | GDC Agent · Action package ready · Awaiting RTOC approval + ✔ Approve & Execute |
| H1/H2 run button | ↺ New Scenario |
| H3 run button | ⚡ Run Vizier Optimization |
| H3 comparison | Baseline Hz column vs GDC Optimal column (no toggle) |
| Close | H3 uplift card (+bbl/d, cash), then ⓘ Reference tab RTOC panel |
| Operations/Financials tabs | ❌ ORPHANED — not in nav, do not navigate there |

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied — would destroy the live cluster.
- All demo changes go into templates/*.html, app.py, and slides/*.html. Slides baked into image.
- GPU scale-to-zero; `gpu-start.sh` ONLY for explicit LLM test, always paired with `gpu-stop.sh`.
- VEO_COLD_OPEN.md has hidden-character lines — use write_to_file as fallback (not replace_in_file).
- Commit docs before ending any session — `git add docs/ && git commit -m "..."`.
