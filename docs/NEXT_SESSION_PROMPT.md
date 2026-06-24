# Next Session Prompt — GDC ESP Ops Video (Operational State)
Date: 2026-06-24 (Session BS+46 wrap) / branch: feature-trio-clean
Git HEAD: 22611e6 / Image: sha256:8b3411d2fc1caf69efdff994bc507fe950f53e82fc7c665bc7590d12dc2ee47b

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

## STEP 3: Next Implementation Tasks

**B1-S4 HOLD IS LIFTED** — all Tasks 1–4 resolved, Autonomy badge added, HITL reworded. Ready to record.

### RECORDING ORDER (resume here)

| Scene | Status | Notes |
|---|---|---|
| B1-S4 | ✅ **CLEARED TO RECORD** | "GAS INTERFERENCE CONFIRMED", Autonomy badge, Doc 1 modal on camera ~3s |
| B1-S5 | ✅ CLEARED | "Approve & Dispatch to SCADA" button; show Autonomy Policy badge |
| B1-S6 | ✅ CLEARED (optional) | "VFD SETPOINT DISPATCHED — awaiting wellbore response" |
| BBRIDGE | ✅ CLEARED | Sovereignty bridge H2→H3 |
| B2-S1–S4 | ✅ CLEARED (B2-S5 ❌ CUT) | H2 CLASSIFY paraffin scenario |
| B3-S1–S3 | ✅ CLEARED | H3 OPTIMIZE Vizier → table → uplift |
| B3-S4 | CONDITIONAL | Verify constraintDoc.found=True before recording |

### Verify B3-S4 gate before recording:
```bash
curl -s "http://gdc-pm.bdau.io/api/vizier/optimize" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print('constraintDoc.found:', d.get('constraint_doc', {}).get('found'))"
# Expected: constraintDoc.found: True
```

---

### TASK A — Autonomy Envelope Roadmap (next session — NOT this session)
**Context:** The "autonomy threshold knob" idea (confidence-based auto-execute) was RT-tested
(gdc-second-opinion BS+46) — numeric confidence threshold FAILS (IEC 61511, not PHA-grounded).
The correct design is an **action-class Autonomy Policy** (operator defines per-action-class
whether GDC may act or must escalate; high-stakes/contraindicated actions always require
human approval regardless of confidence).

**What was shipped:** Static "⛭ Autonomy Policy: VFD setpoint → ALWAYS REQUIRE APPROVAL
(operator-set)" badge on the H1 HITL panel — defensible, honest, survives hostile engineer.

**What's deferred for future session:**
- Full operator-configurable autonomy envelope (action-class matrix, low-risk action delegation)
- Calibrated confidence display (requires precision/recall/Brier score against real outcomes
  before any numeric threshold goes on screen per PRIME DIRECTIVE)
- DEMO_MASTER roadmap entry added this session — see §5 notes.

---

## STEP 4: What BS+46 Shipped (already deployed, do not re-do)

**Image sha256:8b3411d2 — committed 22611e6**

### Code changes (tab_h1.html + app.py):
- **Task 2 (terminology):** `✔ GAS LOCK CONFIRMED` → `✔ GAS INTERFERENCE CONFIRMED — free gas in pump stages`; cause-term sweep. Internal `gas_lock` enums untouched.
- **Task 3 (GVF):** `GVF 78%` → `GVF ~18% at intake — early interference, below the 20–25% sharp-drop threshold` (UI + shift note seed + field_intel inject text + nm_1 nominal card 42%→12%). Source: MCP-grounded, API RP 11S / SLB / Baker Hughes (Session BS+46).
- **Task 4 (Doc 3 integrity):** Doc 3 card label now dynamically bound to `rag_sections[2].title` — kills the No-Silent-Lies hardcode.
- **Task 6 (HITL):** Button → `✔ Approve & Dispatch to SCADA — VFD Trim` / sub `Supervisory setpoint · 52 → 44 Hz · SCADA retains regulatory control`. Post-press → `✅ VFD SETPOINT DISPATCHED — 52 → 44 Hz · awaiting wellbore response` (replaces both RECOVERING instances). Source: gdc-second-opinion RT SURVIVES.
- **Autonomy Policy badge:** Static badge `⛭ Autonomy Policy: VFD setpoint → ALWAYS REQUIRE APPROVAL (operator-set)` on gas_lock HITL panel. RT on numeric threshold FAILS (IEC 61511); badge is defensible.
- **GVF consistency sweep:** 60–65% contradictory threshold strings fixed in app.py (L2967/2971, L5014/5015/5018); nm_1 nominal card 42%→12%; all now align with OEM bulletin 20–25% threshold (L1256 — untouched, correct).
- **DB re-seed:** Tour 2 Shift Note deleted pre-rollout; `_seed_l3_scenario_docs_bg()` thread re-inserts with `~18%%` on startup.

### Docs sweep:
- DEMO_MASTER §2 table: "Gas Lock or Fluid Drawdown" → "Gas Interference or Fluid Drawdown"
- DEMO_MASTER §4.1: updated to reflect Gas Interference as cause-term + GVF ~18% early-interference window + API RP 11S / SLB citation
- DEMO_MASTER G5 note: GVF 78% note updated to confirm resolved (BS+46)
- VIDS B1-S4: cause-term → "gas interference, preventing gas lock"; Autonomy badge choreography; Task 5 modal open (Doc 1, ~3s on camera)
- VIDS B1-S5: button label + Autonomy Policy badge in app state
- VIDS B1-S6: outcome label updated

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
- B1-P1 through B1-P5 VO locked: recorded, match bible verbatim ✅
- B2-S5: ❌ CUT — do not record
- BBRIDGE VO: "all AI local, no cloud required" (not "air-gap capable")
- B1-S4: ✅ **HOLD LIFTED** — all integrity fixes deployed, verified live (BS+46)
- **Autonomy numeric knob: ❌ BLOCKED** — gdc-second-opinion: 4 FAILS (IEC 61511, not PHA-grounded, cherry-picked, automation bias). Deploy action-class policy badge only (done). Numeric threshold gates on precision/recall/Brier calibration.
