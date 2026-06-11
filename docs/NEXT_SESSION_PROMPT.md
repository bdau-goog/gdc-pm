# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 11, 2026 (Session AU — docs sprint: DEMO_STORY_AND_PATH + VIDEO_SCRIPT + DEMO_MASTER §3/§5/§6 + CLAIM_LEDGER H2 rows)
**git head:** `16667c4` (docs(session-au): DEMO_STORY_AND_PATH + VIDEO_SCRIPT + DEMO_MASTER §3/§5/§6 rewrite + CLAIM_LEDGER H2 rows)
**fault-trigger-ui image:** `sha256:2fd95932...` (unchanged — no app code deployed)
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected:** 8 pods 1/1 · ollama_online: True · gemma4:latest · field_intel: 5-6 · rag_docs: 18

---

## STEP 2: MCP Server (verify before use)

```bash
python3 -c "
from google import genai
from google.genai import types as gtypes
client = genai.Client(vertexai=True, project='gdc-pm-v2', location='us-central1')
r = client.models.generate_content(model='gemini-2.5-flash', contents='Reply: OK',
    config=gtypes.GenerateContentConfig(max_output_tokens=8192))
print(r.text)
"
```

**If "Reauthentication needed":**
```bash
gcloud auth application-default login --no-browser
gcloud auth application-default set-quota-project gdc-pm-v2
# Then: Ctrl+Shift+P → Developer: Reload Window
```

**Config:** `~/mcp/start.sh` → `~/mcp/second_opinion_server.py` · `gemini-2.5-flash` · `gdc-pm-v2` · `timeout: 120000` · results → `/tmp/mcp-results/`

---

## STEP 3: Session AU Completed — What Was Done

All 8 NEXT_SESSION_PROMPT priorities from Session AT were executed:

| Priority | Item | Status |
|---|---|---|
| P1 | `docs/DEMO_STORY_AND_PATH.md` (new — stakeholder narrative, 7 beats, all 3 horizons) | ✅ DONE |
| P2 | DEMO_MASTER §3 rewrite (STATE-vs-CONTEXT → sovereign-edge of industry-validated capability; three gaps) | ✅ DONE |
| P3 | DEMO_MASTER §5 rewrite (slug-flow → maintenance-provenance; survival test table; synthetic docs gate; screen arch) | ✅ DONE |
| P4 | DEMO_MASTER §6 update (honest Vizier hybrid framing; retired "no cloud dependency" language) | ✅ DONE |
| P5 | `docs/VIDEO_SCRIPT.md` (new — 4 narration scripts: Overview + H1 + H2 + H3 with production notes) | ✅ DONE |
| P6 | H2 briefing panels spec (embedded in DEMO_STORY_AND_PATH.md §D and DEMO_MASTER §5) | ✅ DONE |
| P7 | CLAIM_LEDGER.md H2 rows (archived slug-flow; new H2-P1–H2-C2 with tags and status) | ✅ DONE |
| P8 | Commit + handoff | ✅ THIS SESSION |

---

## STEP 4: Next Implementation Task

**The strategy is locked and all spec docs are current. Next task = BUILD.**

### PRIORITY 1: H2 Synthetic Documents (must precede any H2 code)

**Five documents total — 2 dynamic (Gemma-generated per run), 3 static seeds.** Sign off all five per G1–G6 gate before any pixel is drawn. See DEMO_MASTER §5 for full dynamic generation architecture.

| # | Document | Generation | Sign-off status |
|---|---|---|---|
| 1 | **Workover completion report** | 🔄 DYNAMIC — Gemma prompt template, randomized per run (vendor, date, fill volume) | ❌ Not yet drafted |
| 2 | **OEM fluid compatibility matrix** | 📌 STATIC SEED — Buna-N + synthetic ester = INCOMPATIBLE (Gemini confirmed chemistry) | ❌ Not yet drafted |
| 3 | **Prior pull record** | 📌 STATIC SEED — bearings: NORMAL at last pull (eliminates bearing-wear hypothesis) | ❌ Not yet drafted |
| 4 | **Shift note (recent tour)** | 🔄 DYNAMIC — Gemma prompt template, randomized operator initials/timestamps | ❌ Not yet drafted |
| 5 | **Well history extract** | 📌 STATIC SEED — workover date list, normal history pre-current-workover | ❌ Not yet drafted |

**Draft each doc text in session → run G1–G6 gate check explicitly (table format) → get user sign-off → then wire into backend.**

### PRIORITY 2: H2 Backend Endpoint (`GET /api/h2/scenario-replay`)

Per DEMO_MASTER §5 Screen Architecture:
- Returns: `efficiency[], vib[], t_min[], health_score[], gdc_detect_idx, scada_alarm_idx, gdc_verdict, doc_reveals[]`
- Asset: `ESP-ALPHA-3`, 8-week post-workover context
- Sensor pattern: efficiency decline (amber) + vibration rise (purple) — the "bearing wear" signature
- Backend uses `esp_health.ubj` for health score; flag is mechanical degradation route
- Doc reveals: workover completion report → OEM matrix → shift note → pull record (staggered timing)

### PRIORITY 3: H2 Briefing UI (3 panels, per §4.5 Briefing Pattern Spec)

Only after user has approved synthetic documents:
- Panel 1: The Equipment
- Panel 2: The Provenance Hook (timeline + 4 sensor tiles + doc stack)
- Panel 3: The Decision (GDC verdict + action cards + universal pattern close + CTA)

**Per constraints: wireframe → sign-off → HTML. No HTML without sign-off.**

### PRIORITY 4: H2 Scenario Replay UI

Same mechanics as H1. SCADA View / GDC Advisor View, same zone layout.

### PRIORITY 5 (if time): H3 tab copy fix

Fix H3 Optimize tab copy: replace any "no cloud dependency" language with honest hybrid framing per DEMO_MASTER §6.

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Briefing — all 6 panels | ✅ COMPLETE Session AQ | Deployed |
| H1 Scenario replay | ✅ WORKING | Deployed |
| H2 Briefing panels | ❌ NOT BUILT | Maintenance-provenance spec in DEMO_MASTER §5. Synthetic docs must be approved first. |
| H2 Scenario replay | ❌ NOT BUILT | Backend endpoint + UI needed after doc approval |
| H3 copy — Vizier framing | ⚠️ NEEDS COPY FIX | H3 tab may still say "no cloud dependency" — fix per Priority 5 |
| MCP gdc-second-opinion | ✅ WORKING | ~/mcp/, gemini-2.5-flash, gdc-pm-v2, timeout=120000 |
| DEMO_MASTER §3 | ✅ UPDATED Session AU | Sovereign-edge / three-gap framing |
| DEMO_MASTER §5 | ✅ UPDATED Session AU | Maintenance-provenance H2 spec |
| DEMO_MASTER §6 | ✅ UPDATED Session AU | Honest Vizier hybrid framing |
| docs/DEMO_STORY_AND_PATH.md | ✅ CREATED Session AU | Stakeholder narrative + all 3 horizon stories |
| docs/VIDEO_SCRIPT.md | ✅ CREATED Session AU | 4 narration scripts |
| CLAIM_LEDGER H2 rows | ✅ UPDATED Session AU | H2-P1–H2-C2 added; slug-flow archived |
| H2-C1 flush+reseal ~$8k–$15k | ⚠️ 🔴 NEEDS-EXPERT | Two Gemini searches — no hard public figure found. Display as soft range only. Cannot harden without field service quote from ESP OEM. |
| H2-P4 symptom onset "within weeks" | ✅ SURVIVES (softened) | Gemini search Session AV: Buna-N + phosphate ester → "days to a few weeks" for initial symptoms. 3-month documented case. Display as "within weeks of fluid fill" not a hard number. |

---

## MCP / Gemini Protocol for 🔴 NEEDS-EXPERT Items

**Rule:** Any 🔴 NEEDS-EXPERT claim MUST get a `gemini_search` pass before next session ends.
- If Gemini finds a hard number or citeable range → promote to 🟡 OUR-CODE or 🟢 TEXTBOOK with citation, update CLAIM_LEDGER
- If Gemini cannot source it (2 searches tried) → display must be softened to a range or cut; note this explicitly in CLAIM_LEDGER
- **Never ship a hard figure that has only a 🔴 tag.** Soft ranges ("a fraction of the pull cost") are acceptable display states.
- H2-C1 is the only remaining open 🔴 item. It requires a real field service quote to harden. Until then: soft range only.

**MCP server status:** `~/mcp/start.sh` is active in this workspace (autoApprove). Tools: `gemini_search` (Google Search grounded) + `gemini_second_opinion` (hostile red-team). Results saved to `/tmp/mcp-results/` — use `read_file` on the path if output truncated in Cline display.

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — do NOT use `browser_action`
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,400 lines · `index.html` ~3,200 lines · `app.js` ~2,300 lines — grep first, read targeted sections only
- **Wireframes → sign-off → HTML** (never write HTML without sign-off)
- **No H2 HTML until synthetic documents approved against G1–G6 gate**
- **No build/push/deploy without user walkthrough and verification**
- Gemini tools (gemini_search, gemini_second_opinion) on autoApprove — use freely for fact-checking; do NOT re-open locked strategy decisions
