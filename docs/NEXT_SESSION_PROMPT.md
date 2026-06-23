# Next Session Prompt — GDC ESP Ops Video (Operational State)
Date: 2026-06-23 (Session BS+40) / branch: feature-trio-clean
Git HEAD: 650956b / Image: sha256:c2165139 (fault-trigger-ui, B1-P5 labels + text size bump)

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

## STEP 3: FIRST TASK — Fix H1-P5 Cross-Industry Cards (BLOCKING — do before any recording)

**Red-team result (Session BS+40, MCP gdc-second-opinion):** Both P&U and Maritime analogies in H1 Slide 5 FAIL.

**Root cause:** "SCADA thermal alarm — identical on overload or insulation failure" is FALSE. An expert reads disproportionate rate-of-change from sensors alone; DGA is a *primary* diagnostic, not a tie-breaker. Same problem for Maritime: combustion knock and bearing wear have distinct frequency spectra; "identical" is falsifiable.

**Approved fix (Plan Mode only, user to approve draft before code):**
Reframe from "identical sensor signature" → "alarm fires; the *safe action* depends on context off the telemetry stream." Drop ISO 10816 from Maritime (no replacement standard needed). Name both causes in Maritime (currently only has one explicit cause — inconsistent with P&U which names both).

**Implementation steps:**
1. Draft revised P5 card text + B1-P5 VO in Plan mode → get approval
2. Edit `gke/fault-trigger-ui/slides/h1.html` P5 section — rewrite "Observational State" and "Documented Context" blurbs; remove ISO 10816 citation
3. Rebuild + push + rollout restart (standard deploy pipeline)
4. Re-record B1-P5 with revised VO

**Specific lines to target in h1.html (grep to confirm):**
```bash
grep -n "SCADA thermal alarm\|ISO 10816\|identical on" gke/fault-trigger-ui/slides/h1.html
```

**Revised framing (start here — refine with user):**
- P&U: "A transformer SCADA thermal alarm — winding temperature rising, load current rising. Whether to isolate (incipient internal fault) or ride through (explained peak-demand overload) requires documents: the DGA oil lab report confirms or rules out internal arcing; the regional grid demand forecast explains the load. Without both, the correct action is unknown."
- Maritime: "Engine block vibration rising with fuel consumption up, RPM flat. Whether to switch fuel tanks under way (high-asphaltene combustion knock) or initiate controlled shutdown (early main bearing wear) requires the fuel bunkering assay and OEM combustion service bulletin. Both causes; opposite actions; the decision lives in the documents."

## STEP 4: Resume Recording — B1-S1 → B1-S6 (after P5 is fixed)

B1-P1 ✅ B1-P2 ✅ B1-P3 ✅ B1-P4 ✅ recorded this session.
B1-P5 needs re-record after P5 card fix above.
Then proceed: B1-S1 → B1-S2 → B1-S3 → B1-S4 (A/B) → B1-S5 → B1-S6 (OPTIONAL).

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
- Image: sha256:c2165139 (fault-trigger-ui, H1-P5 text bumped + Oil & Gas / Power & Utilities labels)
- Slides committed: h1.html — P3 redesigned (3-card, "All Three Responses Have a Trap."), P5 text bumped
- VIDS_PRODUCTION_MASTER.md: B1-P1→P4 marked DONE; B1-P5 card has revised VO but needs re-record after slide fix

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
