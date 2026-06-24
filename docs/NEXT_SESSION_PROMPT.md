# Next Session Prompt — GDC ESP Ops Video (Operational State)
Date: 2026-06-24 (Session BS+47 wrap) / branch: feature-trio-clean
Git HEAD: d3b9dc1 / Image: sha256:ff5f96d1c4c2e5d71bd76eb867336c8d388a9e8db15b8a8a207236c5fbc7ff98

## STEP 1: Run These Four Commands First
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

## STEP 2: Read These Documents
```bash
cat docs/SESSION_LOG.md | head -60   # last 2 entries for context
```

## STEP 3: PRIME DIRECTIVE — Start by listing remaining H1 scenes

**The user's instruction:** *"Start that session by listing the remaining H1 scenes with VO and direction."*

**B1-S4 is DONE ✅.** The remaining H1 scenario scenes are:

| Scene | Status | Note |
|---|---|---|
| **B1-S5** | ⏳ TO RECORD | HITL Approve — Autonomy Policy badge |
| **B1-S6** | ⏳ RECORD-IF-BUDGET | Outcome — VFD dispatched |

Output the full scene cards for B1-S5 and B1-S6 from VIDS_PRODUCTION_MASTER.md (the cards are already updated with smoothed VOs from BS+47). Then continue with BBRIDGE and H2.

**After H1, recording order:**
| Section | Scenes | Status |
|---|---|---|
| BBRIDGE | H2→H3 Sovereignty Bridge | ⏳ TO RECORD |
| H2 CLASSIFY | B2-P1 through B2-S4 | ⏳ TO RECORD |
| H3 OPTIMIZE | B3-P1 through B3-S5 | ⏳ TO RECORD |
| BCLOSE | H3 Uplift + Reference tab | ⏳ TO RECORD |

**All VOs are locked and smoothed in VIDS_PRODUCTION_MASTER.md (commit d3b9dc1).**

## STEP 4: What BS+47 Shipped

### Code change deployed (sha256:ff5f96d1):
- **tab_h1.html L302+L392:** "Gas interference in pump stages" (stated-as-fact) replaced with the inference chain:
  - Zone 1: `"Casing pressure rising · GOR elevated · annulus submerged — free gas inferred at pump intake (GVF ~18% estimated from surface evidence)"`
  - Action card: `"Casing pressure rising + GOR elevated → GVF ~18% estimated at intake. Early interference, pre-gas-lock threshold. Annulus submerged. VFD trim safe."`
  - Physics: PIP drops (pump intake pressure = the SCADA signal on chart). Casing annulus pressure (wellhead) RISES in gas lock (gas accumulates above pump). These are distinct tags. The app says "Casing pressure rising" (correct for engineers). VO uses "gas accumulating in the annulus" (clearer for mixed audience).

### VO locks (docs only, commit d3b9dc1):
- **B1-S2:** `"GDC flags the developing event — ahead of any SCADA hard limits fire — and begins retrieving unstructured field context."` (LOCKED)
- **B1-S3:** `"Further into the event, the SCADA threshold fires — it sees the unloading signature, as it should. But the cause is ambiguous, and on a sandy well, the wrong choice here destroys the pump."` (LOCKED)
- **B1-S4 GAS LOCK:** User's version — *"GDC retrieves the well's latest documents — the gas-to-oil ratio rising at the separator, gas is accumulating in the annulus — and concludes that free gas is reaching the pump stages. It's gas interference, not fluid drawdown. It's best to ease the speed and keep the well online."* (~15s real-pace, LOCKED)
- **B1-S5 through BCLOSE:** All smoothed for natural delivery cadence (commit d3b9dc1)

### Recording progress:
- ✅ B1-P1 through B1-P5 DONE
- ✅ B1-S1 through B1-S4 DONE
- ⏳ B1-S5, B1-S6, BBRIDGE, H2, H3, BCLOSE still to record

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
- VEO_COLD_OPEN.md has hidden-character lines — use write_to_file not replace_in_file
- B1-P1 through B1-S4 VO locked: recorded, match bible ✅
- B2-S5: ❌ CUT — do not record
- BBRIDGE VO: "all AI local, no cloud required" (not "air-gap capable")
- **Autonomy numeric knob: ❌ BLOCKED** — IEC 61511 FAILS. Deploy action-class policy badge only (done).
- **GAS LOCK VO physics:** PIP drops (SCADA signal). Casing annulus pressure rises (gas lock evidence). These are different tags. App says "Casing pressure rising" (correct). VO says "gas accumulating in the annulus" (mechanism, clearer for mixed audience). Do NOT change either without this note.
