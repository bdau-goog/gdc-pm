# Next Session Prompt — GDC ESP Ops Demo (Operational State)
Date: 2026-06-25 (Session BS+55) / branch: feature-trio-clean
Git HEAD: 42e0d5b / Image: sha256:5033abd8449c0c87581417ca1d031070777acc53b51d932f10be4538b0df0197

⚠ NOTE: 9 commits ahead of origin/feature-trio-clean — push before next session if needed.

## STEP 1: Run Four Startup Commands
```bash
kubectl get pods -n gdc-pm --no-headers
# Expected: all 1/1 Running (7 pods)

kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
# Expected: 0

curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
# Expected: ollama_online: False model: offline

kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
# Expected: field_intel = 11, rag_documents = 20
```

## STEP 2: Read DEMO_MASTER.md + DECISION_DOSSIER.md
```bash
cat docs/DECISION_DOSSIER.md   # §2 is H2 spec; §2.6 physics; Bill Barna SME confirmation
cat docs/SESSION_LOG.md | head -80
```

## STEP 3: Next Tasks — H2 Recording + H3 Iterative Vizier

### H2 UI — FULLY DEPLOYED (sha256:5033abd8) ✅
All layout/content fixes from BS+54 and BS+55 shipped and verified:
| Fix | Commit | Verified |
|---|---|---|
| Wellbore SVG clip | 42c6089 | ✅ viewBox 315, position:absolute |
| Dollar figures removed | 42c6089 | ✅ "major workover" / "low-cost surface" in live HTML |
| 3-col drag resize handles | 42c6089 | ✅ h2StartDrag + sessionStorage |
| Annotation overlap (legend) | 42c6089 | ✅ y:0.97 inside chart |
| SVG absolute positioning | 42e0d5b | ✅ position:absolute;top:0;left:0 |
| SCADA annotation clip | 42e0d5b | ✅ xanchor:'right' |
| Scrubber label overlap | 42e0d5b | ✅ translateX(-100%) + T+max label removed |
| WAX ZONE contrast | 42e0d5b | ✅ dark text on amber |

### ⭐ NEXT TASK: RECORD H2 (B2-P1 through B2-S4 + B2-S3.5)
Scene order: B2-P1 → B2-P2 → B2-P3 → B2-S1 → B2-S2 → B2-S3 → B2-S3.5 → B2-S4

**Pre-recording checklist:**
1. Open http://gdc-pm.bdau.io → Classify tab
2. Column widths: reset sessionStorage if needed (`sessionStorage.clear()` in DevTools) → defaults 44/22/32%
3. Click ↺ New Scenario → confirm loads at alarm state (VIB-HI banner active)
4. Confirm wellbore: WH at top, wax band visible, PUMP/PROT/MOTOR visible below
5. Confirm chart: GDC▲ (~week 4) and SCADA▲ (~week 7) annotations visible, no clipping
6. Confirm 3 doc cards appear on GDC Advisor tab after ~2s, ~4s, ~5.5s
7. Vib at gdc_detect_idx = 1.94 mm/s (drag scrubber to GDC▲ to confirm)

**Key VO anchors (from VIDS_PRODUCTION_MASTER.md §SECTION 2):**
- B2-S3.5 closing line: "Act on the drift, not the alarm." — pause after; let it land
- B2-S4 closing line: "The pull is averted, because the documents separated the symptom from the cause."
- B2-S5: ❌ CUT — do not record

### H3 — Iterative Vizier loop fix (blocking H3 recording)
- **File:** `app.py` — `suggest_trials(count=15)` at L6734 is a single batch, NOT iterative
- **Fix needed:** Wrap in 3-round loop (3×5 trials → score → re-suggest) so "searches and learns" is literally true
- **Pattern** already in app.py: look for the 3-round fallback loop in `_FALLBACK_VECS` — the LIVE Vizier path needs the same structure
- After fix: deploy + verify `vizier_algorithm` returns `GAUSSIAN_PROCESS_BANDIT` (not `deterministic_convergence_demo`)
- Then record B3-P1 → B3-S5

## Recording Progress
- ✅ B0.1–B0.4 (Intro) DONE
- ✅ B1-P1–P5 + B1-S1–S6 (H1 scenario) DONE
- ⏳ H2 (B2-P1 through B2-S4 + B2-S3.5) — UI deployed, **record now**
- ⏳ BBRIDGE — record after H2
- ⏳ H3 (B3-P1 through B3-S5) — panels deployed; iterative Vizier fix needed first
- ⏳ BCLOSE — record last

## Deploy Command (permanent reference)
```bash
cd gke/fault-trigger-ui
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest .
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
```
**Registry:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/` (NOT gcr.io)

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- GPU scale-to-zero; `gpu-start.sh` ONLY for explicit LLM test (~$0.65/hr)
- B2-S5: ❌ CUT — do not record
- BBRIDGE VO: "all AI local, no cloud required" (not "air-gap capable")
- **Autonomy numeric knob: ❌ BLOCKED** — IEC 61511 FAILS
- **GAS LOCK VO physics:** PIP drops / casing annulus pressure rises — do NOT change
- **H3 MUST-NOT-SAY:** See DECISION_DOSSIER.md §3.7
- **Why-GDC MUST-NOT-SAY:** See DECISION_DOSSIER.md §4.5
- **H2 early-detect claim:** threshold SCADA only — never "earlier than APM" (dossier §2.3)
- **H2 wax band:** "schematic · wax inferred from PIP" — displayed, not a measurement
- **live_vizier=True: announce before calling** — creates a billable Vizier study
