# Next Session Prompt — GDC ESP Ops Video (Operational State)
Date: 2026-06-23 (Session BS+41) / branch: feature-trio-clean
Git HEAD: e34bf91 / Image: sha256:d2dfa64a (fault-trigger-ui, H1-P5 cross-industry reframe — identical framing removed)

## STEP 1: Run These Four Commands First
```bash
kubectl get pods -n gdc-pm --no-headers
# Expected: all 1/1 Running (7 pods)

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

## STEP 3: FIRST TASK — Record B1-P5, then B1-S1 → B1-S6

**H1-P5 card fix: ✅ DONE (Session BS+41)**
- P&U line 571: "Thermal alarm fires. Safe action — isolate now or ride through peak demand — depends on context the sensor stream cannot supply."
- Maritime line 593: "Vibration alarm fires — block vibration rising, fuel consumption up, RPM flat. Combustion knock and early bearing wear both produce this pattern; opposite responses required."
- ISO 10816 removed. "identical" removed. Committed e34bf91. Live at sha256:d2dfa64a.

**Recording order:**
1. B1-P5 — VO in bible (VIDS_PRODUCTION_MASTER.md §B1-P5). Cursor O&G → P&U → MARITIME → pull wide. ~24s.
2. B1-S1 → B1-S2 → B1-S3 → B1-S4 (A/B branch) → B1-S5 → B1-S6 (OPTIONAL)

B1-P1 ✅ B1-P2 ✅ B1-P3 ✅ B1-P4 ✅ B1-P5 card fixed ✅ — ready to record B1-P5.

## STEP 4: Continue Recording — B2 → BBRIDGE → B3 → BCLOSE (after B1 done)

All B1-Sx VOs are in the bible and have not changed this session — safe to proceed.

## STEP 5: Update Runtime Ledger

Actual runtime with updated VOs (~145 wpm pace):
| Section | Real est |
|---|---|
| Part A cold open | ~68s |
| Intro B0.1–B0.4 | ~55s |
| H1 Discern B1-P1→S5 | ~2:46 (core) |
| H2 Classify B2-P1→S4 | ~1:05 |
| BBRIDGE | ~19s |
| H3 Optimize B3-P1→S5 | ~1:06 |
| BCLOSE | ~13s |
| **TOTAL core VO** | **~7:32** |
| Finished (add 10–15% overhead) | **~8:00–8:30** |

The bible runtime ledger still shows the old ~5:45 estimate — update it.

## Current Deployed State
- App: http://gdc-pm.bdau.io
- Image: sha256:d2dfa64a (fault-trigger-ui, H1-P5 cross-industry reframe — identical/ISO10816 removed)
- Slides committed: h1.html — P3 redesigned (3-card), P5 Observational State reframed (e34bf91)
- VIDS_PRODUCTION_MASTER.md: B1-P1→P4 marked DONE; B1-P5 slide fixed and VO updated — ready to record

## Key Decisions This Session (do NOT revert)
| Decision | Detail |
|---|---|
| B1-P3 3-card redesign | VFD Speed-Down / Managed Step-Down + Hold / Emergency Shut-In; closes false-binary hole for sandy drawdown |
| B1-P3 title | "All Three Responses Have a Trap." |
| LAST RESORT removed | Replaced with "SAFE · DEFERS PRODUCTION" on clean-drawdown / shut-in row |
| "Indistinguishable" dropped from B1-P2 VO | Replaced with "the cause and the safe action are not in these numbers" |
| "Needless for gas" replaced in B1-P3 VO | "for gas, the simple speed-down already worked" |
| P5 labels | "Oil & Gas" / "Power & Utilities" / "MARITIME" (full names) |
| P5 text sizes bumped | badges 0.82, headlines 0.85, descriptions 0.70, resolution 0.76rem |
| P5 analogies: BOTH FAIL RT | "identical signature" framing is false; fix before recording B1-P5 |

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- GPU scale-to-zero; `gpu-start.sh` ONLY for explicit LLM test
- VEO_COLD_OPEN.md has hidden-character lines — use write_to_file not replace_in_file
