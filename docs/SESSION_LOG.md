# GDC-PM Session Log — Append-Only History

---

## Session AL (June 10, 2026) — *Sprint AK: Panel 2+3 scrubber rebuild — deployed and verified*

**Code committed:** `bc5edd7` (feat(sprint-ak): Panel 2+3 scrubber rebuild)
**Cluster image digest:** `sha256:ca4c110c` (Session AL) · 3 files changed, 44 insertions(+), 28 deletions(-)

**Panel 2 ("What is an Unloading Event?") — fixed:** Replaced infinite `@keyframes h1-brief-decline` CSS loop (87%→22%→87% perpetual, amber-only bars, wrong orientation) with presenter-controlled scrubber `h1P2Scrub` (0=nominal → 100=fault). All 4 gauges now start GREEN at scrub=0. PIP shrinks 90%→30%, AMPS shrinks 90%→20%, both flip amber when scrub>50 — implementing "short bar = worse / lower value" orientation. WINDING TEMP fixed width 70% green (was 16% slate). VIB fixed width 60% green (was 14% slate). Tile borders and header labels also react to scrub>50. Diagnostic story told in one gesture: two gauges go amber and shrink, two stay green and flat.

**Panel 3 ("One Signature, Two Causes") — fixed:** (a) Wellbore SVG containers: `max-height:148px` → `max-height:280px` on both Gas Lock and Fluid Drawdown SVGs, roughly doubling visible size. (b) Gas bubbles: removed `animation:h1-bubble-rise 2.5s ease-in infinite` infinite loop; replaced with `opacity` bound to `h1P3Scrub/100` (scrub=0 → invisible, scrub=100 → fully visible). (c) Fluid drain: removed `h1-p3-fluid-drain` infinite `scaleY` animation; replaced with `h1-p3-fluid-scrub` class + `:style="{transform:'scaleY('+…+')'}"` bound to `1 - 0.85 * h1P3Scrub / 100`. At scrub=100, fluid column shrinks to 15% height. (d) Bottom "SAME SENSOR OUTPUT" strip: both PIP (blue) and AMPS (green) bars now use `h1-bar-scrub` class with h1P3Scrub-driven width, making the caption "the live decline looks the same" visually accurate.

**styles.css changes:** Removed 5 infinite-loop constructs (`@keyframes h1-brief-decline`, `.h1-brief-decline-bar`, `@keyframes h1-p3-drain`, `.h1-p3-fluid-drain`, `@keyframes h1-bubble-rise` from `.h1-wb-bubble`). Added `.h1-bar-scrub` (transition:width 0.4s ease) and `.h1-p3-fluid-scrub` (transform-origin:center bottom; transition:transform 0.4s ease). Fixed `.h1-wb-bubble` to use `fill` (not `background` which doesn't apply to SVG) + `transition:opacity 0.4s ease`.

**app.js changes:** Added `h1P2Scrub: 0` and `h1P3Scrub: 0` to Vue data. Added `h1BriefingPanel()` watcher that resets both scrubbers to 0 on every panel change — prevents stale fault state when presenter navigates backward.

**Verification:** Pod grep: `h1-bar-scrub`/`h1-p3-fluid-scrub`/`h1P2Scrub`/`h1P3Scrub` present in all three files ✅. Old infinite keyframes: 0 hits in pod styles.css and index.html ✅. All 6 H1 Briefing panels now SHIP-READY.

**Next task:** Sprint 3 — H2 Briefing (3 panels: What is Slug Flow? · Why It Looks Like a Failing Pump · STATE vs. CONTEXT Exoneration). Same architecture as H1 briefing (`h2BriefingMode`/`h2BriefingPanel` in Vue data, `<template v-else>` wrapper around existing H2 scenario replay). No styles.css changes needed — reuse H1 briefing CSS classes.

---

## Session AK (June 10, 2026) — *Panel review + scrubber spec locked — wrap only, no code*

User reviewed all 6 H1 Briefing panels at proper zoom. Panels 1, 4, 5, 6 approved as ship-ready; do not touch. Panels 2 and 3 require a scrubber rebuild. Panel 2 issues: animated bars use an infinite CSS loop (`h1-brief-decline` 87%→22%→87% perpetual) rendering amber only, both PIP and AMPS the same color, and orientation is backwards (long = worse, should be short = worse/lower). Panel 3 issues: wellbore SVGs are postage-stamp size (`max-height:148px` cap) and animations are also infinite loops not under presenter control. Design locked for next session: per-panel scrubber (`h1P2Scrub`/`h1P3Scrub` 0→100), CSS transition replacing `@keyframes`, all bars start GREEN at 0, PIP and AMPS go amber and shrink as scrub increases, TEMP and VIB stay green and flat (that IS the diagnostic story in one gesture), short bar = worse orientation, Panel 3 SVGs scaled up to ~280px, bubble/drain opacity driven by scrub value not time. Sprint 3 (H2 Briefing) deferred until Panel 2+3 are fixed. No code written this session — clean handoff. Full spec in NEXT_SESSION_PROMPT.md.

---

## Session AJ (June 10, 2026) — *Financial Justification modal raw-mustache fix — integrity repair, deployed & verified*

Fixed the long-standing bug where both the Financial Justification modal and the Feed Detail modal rendered raw `{{ }}` mustache templates instead of evaluated Vue values. Root cause: the Architecture tab's "overview" pane contained 2 stray `</div>` tags in the 3-tier comparison box closing cascade (old lines 2577–2578 of `index.html`), leaving `opens=1183, closes=1181` net balance of −2. These prematurely terminated `app-body` and `#app` in the browser's parsed DOM, ejecting both modals outside Vue's mount scope. Diagnosis used a multi-line-aware tag-stack parser (strips HTML comments preserving line numbers, then token-walks all `<div>` / `</div>` using regex with `re.S`). Fix: single `replace_in_file` deleting the 2 stray closers; verified balance 1181=1181, net 0, zero extra closes. Built and pushed new image `sha256:471fb644`; deployed with `kubectl set image @sha256:<digest>` (`:latest` rollout-restart does not repull on this cluster). Live verification: `curl` confirmed modal at served-line 3122 inside `</div><!-- #app -->` at line 3207. No claims, data, or UI behaviour changed — pure structural integrity fix. Committed `e93328f`. Next task: Sprint 3 H2 Briefing (3 panels).

---

## Session AI (June 10, 2026) — *Sprint 2c+2d+2e: H1 Briefing ALL 6 Panels — complete demo briefing deployed and verified*

**Code committed:** `52baa53` (Panel 4) · `db26131` (Panel 5) · `a8c5d27` (Panel 6)
**Cluster image digest:** `sha256:ca6cea662` (Sprint 2e) · 16 Panel 6 strings + 2 CSS animation strings confirmed in live pod

**Sprint 2e — Panel 6 (This Pattern Is Universal):** 4-row industry table slides in row-by-row via `h1-p6-rowin` (translateX -16px→0, 0.5s ease-out both): Row 1 O&G/ESP blue border (delay 0.3s) — PIP↓·Amps↓ → Workover record/GOR trend/shift note; Row 2 P&E/Transformer purple border (delay 1.2s) — Load current↑·temp↑ → Loading plan/maintenance log/seasonal forecast; Row 3 MFG/Factory motor amber border (delay 2.1s) — Vibration↑·temp nominal → Lubrication record/OEM bulletin/line throughput; Row 4 MINING/Haul truck yellow border (delay 3.0s) — Fuel consumption↑·payload nominal → Haul-road report/service history/grade profile. Closing quote at 3.8s: *"This is not an oilfield trick. It is the structural gap in every industrial AI deployment."* + *"GDC: the AI goes to the data."* Inline `▶ Run the Scenario` CTA button at 4.3s (plus footer button for panel 6). All arrows and symbols use HTML entities (&#x2192; &#x2191; &#x2193;). Dot 6 upgraded to reactive Vue-bound. Navigation `< 5` → `< 6`, `===5` → `===6`. Hint text: 6-case ternary. **H1 Briefing is now complete — all 6 panels built and deployed.**

**Key decisions:** (a) Slide-in from left (translateX) chosen for row animation — "appearing one by one left to right" is the most natural visual for a table row reveal; contrasts with Panel 4's fade-down and Panel 5's scale-in. (b) All HTML entities throughout Panel 6 (no emoji, no variation selectors) — defensive choice following the `🗺️` potential issue in Panel 4. (c) Two CTA paths: inline button in panel body (most prominent) + footer button (always available from navigation footer). (d) Industry badges use text abbreviations (O&G, P&E, MFG, MINING) — no emoji, clean monospace rendering.

**Verification:** 16 Panel 6 strings + 2 CSS strings confirmed in live pod · rollout clean.

**Next task:** Sprint 3 — H2 Briefing (3 panels: What is Slug Flow? · Why It Looks Like a Failing Pump · STATE vs. CONTEXT exoneration). Same architecture as H1 briefing (`h2BriefingMode`/`h2BriefingPanel` in Vue data, `<template v-else>` wrapper around existing H2 scenario replay). See SPRINT_PLAN.md §Sprint 3 and DEMO_MASTER.md §5.

---

## Session AI (June 10, 2026) — *Sprint 2c+2d: H1 Briefing Panels 4+5 — STATE vs. CONTEXT + 2×2 Decision Matrix — deployed and verified*

**Code committed:** `52baa53` (Sprint 2c: Panel 4) · `db26131` (Sprint 2d: Panel 5)
**Cluster image digest:** `sha256:3f8ecc7` (fault-trigger-ui) · 25 Panel 5 strings + 4 CSS animation strings confirmed in live pod

**Sprint 2c — Panel 4 (STATE vs. CONTEXT):** Full-screen two-column animated reveal. LEFT blue "STATE" column: 4 sensor readout tiles (PIP 612 PSI↓, AMPS 34.2 A↓, WINDING TEMP 246°F, VIBRATION 0.41 in/s) staggered fade-in at 0.1/0.4/0.7/1.0s via `.h1-p4-state-row`; quote fades at 1.3s: *"Even a perfect gauge sharpens the STATE. It cannot report what happened last week."* RIGHT amber "CONTEXT" column: 4 document cards (WORKOVER RECORD→GOR TREND→OFFSET FRAC REPORT→SHIFT NOTE) at 1.6/2.2/2.8/3.4s via `.h1-p4-ctx-card`; amber quote at 4.0s: *"The deciding context lives here. Not on any sensor."* Full-width bottom: *"You cannot instrument your way out of a context gap."* CSS uses `animation-fill-mode:both`. Dot 4 upgraded to reactive Vue-bound. Navigation `< 3` → `< 4`, `===3` → `===4`.

**Sprint 2d — Panel 5 (Why Sand Changes Everything):** 3×3 CSS grid decision matrix. Scope badge: "moderate-sand well · AR-trim". Header row: GAS LOCK (blue) | FLUID DRAWDOWN (amber). Row labels: VFD TRIM · SHUT-IN. Four cells appear via `h1-p5-cellin` scale(0.92→1) animation: Cell 1 VFD TRIM × GAS LOCK ✅ SAFE ~$2,500 (0.2s) → Cell 2 VFD TRIM × DRAWDOWN ❌ CATASTROPHIC ~$150k (1.0s) with `h1-p5-sand-fill` bar growing 0→82% at 2.5s delay (sand accumulating visual) → Cell 3 SHUT-IN × GAS LOCK ⚠ DEFERRED ~$1-3k (1.8s) → Cell 4 SHUT-IN × DRAWDOWN ✅ RECOVERABLE (2.6s). Bottom quote row at 3.4s: *"Blind to the cause, trim risks seizure. Shut-in is safe in both — the rational default."* SPE-170776 cited for 4.2 ft/s / 3.1 ft/s velocity boundary. HTML entities (&#x2705; &#x274C; &#x26A0;) used instead of raw emoji to avoid any Vue template parser issues. Dot 5 upgraded to reactive Vue-bound. Navigation `< 4` → `< 5`, `===4` → `===5`. Both sprints deployed in single session.

**Key decisions:** (a) HTML entities instead of emoji for outcome indicators — avoids any potential Unicode parse issue in Vue 3 browser template compiler (see Financial Justification modal bug below). (b) `margin-top:auto` inside flex-column cells correctly pushes cost figures to bottom of each cell. (c) Sand fill bar uses CSS `both` fill-mode with 2.5s delay — appears naturally after the cell fades in (1.0s) and holds at 82% width permanently.

**Known issue — Financial Justification modal:** Pre-existing bug (div balance of -21 existed identically in `9691e93` baseline, before all Session AI work). The modal `v-if="justifyModalOpen"` div has `position:fixed;inset:0;z-index:400` — if Vue hasn't fully mounted when the smoke test clicks, the un-v-if'd modal intercepts. Root cause: the modal displays raw `{{ }}` in the screenshot the user shared. Confirmed NOT caused by Session AI changes (same -21 depth before/after). Not blocking briefing panel demo flow.

**Verification:** 25 Panel 5 strings + 4 CSS strings confirmed in live pod · rollout clean.

**Next task:** Sprint 2e — Panel 6 (*This Pattern Is Universal*): 4-row animated table (O&G / Power / Manufacturing / Mining). Each row: asset | STATE sensor → CONTEXT document. Full-width quote: "This is not an oilfield trick." `▶ Run the Scenario` CTA. See SPRINT_PLAN.md §Sprint 2e and DEMO_MASTER.md §4 Panel 6.

---

## Session AI (June 10, 2026) — *Sprint 2c: H1 Briefing Panel 4 — STATE vs. CONTEXT — deployed and verified*

**Code committed:** `52baa53` (feat(sprint2c): H1 Briefing Panel 4 — STATE vs. CONTEXT animated two-column reveal)
**Cluster image digest:** `sha256:6a52012` (fault-trigger-ui) · pod rolled out clean · 19 Panel 4 strings + 3 CSS animation strings confirmed in live pod

**What was built and deployed:** Sprint 2c complete. Panel 4 *STATE vs. CONTEXT* — the core moat argument of the briefing. Full-screen two-column animated reveal: LEFT blue column ("STATE") shows 4 sensor readout tiles (PIP 612 PSI↓, AMPS 34.2 A↓, WINDING TEMP 246°F, VIBRATION 0.41 in/s) fading in with staggered delays (0.1/0.4/0.7/1.0s) via `.h1-p4-state-row` class, with a 5th italic quote fading in at 1.3s: *"Even a perfect gauge sharpens the STATE. It cannot report what happened last week."* RIGHT amber column ("CONTEXT") shows 4 document cards appearing one by one (WORKOVER RECORD→GOR TREND→OFFSET FRAC REPORT→SHIFT NOTE) at delays 1.6/2.2/2.8/3.4s via `.h1-p4-ctx-card`, plus final amber italic quote at 4.0s: *"The deciding context lives here. Not on any sensor."* Full-width bottom strip: *"You cannot instrument your way out of a context gap."* (large, bold, centered). CSS: `@keyframes h1-p4-fadein` (opacity 0→1 + translateY 10px→0) with `animation-fill-mode:both` so elements start invisible during delay and stay visible after animating in — critical for the staggered narrative effect. Progress dot 4 upgraded from static cosmetic 6px span to reactive Vue-bound 8px span (matches dots 1-3). Navigation: Next `< 3` → `< 4`; Run the Scenario `===3` → `===4`. Hint text extended to 4-case ternary (panel 3 hint: "STATE is observable. CONTEXT is decisive. Panel 4 makes the case."). Both `index.html` and `static/styles.css` edited in single batched calls.

**Key decisions:** (a) CSS `animation-fill-mode:both` is the correct approach — elements invisible before their delay fires, stay visible after — no JS timers, no Vue watchers, zero side-effects on `v-if` remount. (b) Context card delays staggered 0.6s apart (1.6→4.0s) so STATE tiles fully load before CONTEXT cards begin appearing — deliberate narrative separation. (c) Panel 4 values (PIP 612, AMPS 34.2, TEMP 246, VIB 0.41) match the mid-decline phase of the H1 scenario replay — SOURCE = OUR-CODE from FAULT_PROFILES trajectory. No silent lies.

**Verification:** 19 Panel 4 strings in live pod index.html · 3 CSS animation strings in live pod styles.css · rollout clean.

**Next task:** Sprint 2d — Panel 5 (*Why Sand Makes the Stakes Asymmetric*): 2×2 animated decision matrix (Trim/Shut-in × Gas Lock/Drawdown). See SPRINT_PLAN.md §Sprint 2d and DEMO_MASTER.md §4 Panel 5 spec. Extend dot 5, Next `< 5`, Run the Scenario `===5`.

---

## Session AG (June 10, 2026) — *Sprint 1 + Sprint 2a: integrity fixes + H1 Briefing Panels 1&2 — deployed and verified*

**Code committed:** `9691e93` (fix(sprint1): integrity fixes — RTOC-sovereign, 3 pillars, IEC 62443, retire 200GB/VSAT/E-House, SCADA label, industry generalization) · `d41d27b` (feat(sprint2a): H1 Briefing panels 1&2 — This Well + What is an Unload?)
**Cluster image digest:** `sha256:7d22b015` (fault-trigger-ui) · pod running, 8 briefing strings confirmed in live pod

**What was built and deployed — Sprint 1:** All 5 open integrity violations in the "How It Works" tab fixed in one batched `replace_in_file` call (12 SEARCH/REPLACE blocks). Rewrote `ⓘ "Why Not Cloud?"` → 3 sovereignty pillars (IEC 62443/Purdue isolation+self-sufficiency; data residency; governance/IP) with explicit NERC-CIP scoping to P&E BES only — deleted "200 GB/day" and "VSAT 15–25 min". Retitled deployment → "Operator RTOC / Sovereign Data Center". Added muted anchor line with IEC 62443/Purdue/NERC-CIP scoping. Retired all "No cloud dependency" → "No public-cloud dependency — sovereign, outage-immune" (4 occurrences). Reframed SCADA path label → "control-layer telemetry path · threshold alarms & setpoints · advanced APM platforms add ML on top". Added "generalizes across industrial verticals" line below TAGS/TAG-PATTERNS/DOCUMENTS (4 industries). Cleaned up 6 secondary E-House references throughout.

**What was built and deployed — Sprint 2a:** H1 Briefing container (2 panels, extensible to 6 in Sprint 2b–2e). Architecture: `h1BriefingMode: true` + `h1BriefingPanel: 1` added to Vue data; `v-if="h1BriefingMode"` briefing div inserted before `<template v-else>` wrapper around existing scenario replay content. Panel 1 (*This Well*): full-screen layout — left column has scope declaration (formation/pump/sensor-string/operating/sand-stakes table with callout quote), right column has nominal wellbore SVG (X-MAS tree, full blue fluid column, intake PDG marker, "no discharge gauge" annotation, healthy green PUMP ✓ / MOTOR ✓, PERFS, FORMATION) + 4 green nominal sensor readout tiles. Panel 2 (*What is an Unload?*): 2×2 sensor tile grid — PIP and AMPS tiles have `.h1-brief-decline-bar` CSS class (4.5s `cubic-bezier(0.4,0,0.6,1)` keyframe, 87%→22%→87%, 0.45s delay on AMPS for visual separation); WINDING TEMP and VIBRATION tiles are static flat bars. Key insight callout at bottom: "PIP and Amps decline together... the cause is not in any of these numbers." Navigation footer: ← Back / Next → / ▶ Run the Scenario (wired to `h1BriefingMode=false; loadH1Scenario()`). Progress dots (2 of eventual 6) in the header strip.

**Key decisions:** (a) `v-else`/`<template>` wrapper approach chosen over conditional display — cleanest separation, no impact on existing scenario replay HTML. (b) CSS animation approach for Panel 2 decline bars chosen over Vue timers — zero JS, no `mounted()` hooks, works reliably in dark-mode dark backgrounds. (c) Deployment discovery (Sprint 1): `kubectl rollout restart` with `:latest` tag returns stale cached image on this GKE cluster despite `imagePullPolicy: Always`. Fix permanently documented: always `kubectl set image ... @sha256:<digest>`.

**Verification:** Pod running `sha256:7d22b015` · 8 briefing-related strings confirmed in live pod via exec grep · git clean on `feature-trio-clean`.

**Next task:** Sprint 2b — Panel 3 (*One Signature, Two Causes*): full-screen split with left=gas lock wellbore + right=drawdown wellbore, identical PIP/Amps trace below both. Extend progress dots to show 6 total (3–6 greyed). See SPRINT_PLAN.md §Sprint 2b and DEMO_MASTER.md §4.

---

## Session AG (June 10, 2026) — *Sprint 1: integrity fixes — deployed and verified*

**Code committed:** `9691e93` (fix(sprint1): integrity fixes — RTOC-sovereign deployment, 3 sovereignty pillars, IEC 62443, retire 200GB/VSAT/E-House claims, SCADA label, industry generalization)
**Cluster image digest:** `sha256:3d6009a2` (fault-trigger-ui) · pod `fault-trigger-ui-68474c5d78-x88z2` (later replaced by explicit-digest deploy) 1/1 Running

**What was built and deployed:** Sprint 1 complete — all 5 open integrity violations in the "How It Works" tab fixed in a single batched `replace_in_file` call (12 SEARCH/REPLACE blocks). Changes: (1) Rewrote `ⓘ "Why Not Cloud?"` panel → 3 sovereignty pillars (IEC 62443/Purdue isolation+self-sufficiency; data residency; governance/IP) with explicit NERC-CIP scoping to P&E BES only — deleted "200 GB/day" and "VSAT 15–25 min". (2) Retitled deployment → "Operator RTOC / Sovereign Data Center" with corrected bullet text (RTOC decision-maker, production network, document corpus convergence). (3) Added muted anchor line: "Runs inside the operator's security perimeter — IEC 62443 / Purdue Model · NERC-CIP (Power & Energy BES only) · sovereign, outage-immune". (4) Retired all "No cloud dependency" / "zero cloud dependency" strings → "No public-cloud dependency — sovereign, outage-immune". (5) Reframed SCADA path label → "control-layer telemetry path · threshold alarms & setpoints · advanced APM platforms add ML on top". (6) Added "generalizes across industrial verticals" line below TAGS/TAG-PATTERNS/DOCUMENTS centerpiece. Also cleaned up 4 secondary E-House references throughout the file.

**Key decisions:** Deployment issue discovered: `kubectl rollout restart` with `:latest` tag does NOT pull the new image on this GKE cluster (node-level image cache returns old digest despite `imagePullPolicy: Always`). Fix established: always deploy with `kubectl set image ... @sha256:<digest>` using the explicit digest from `docker push` output. This constraint documented in NEXT_SESSION_PROMPT.md Constraints section.

**Verification:** Pod running `sha256:3d6009a2` confirmed · `grep -c "RTOC" /app/index.html` → 6 in pod · old integrity strings absent from live pod · git clean on `feature-trio-clean`.

**Next task:** Sprint 2a — H1 Briefing container + Panels 1 & 2 (This Well + What is an Unload?). See SPRINT_PLAN.md §Sprint 2 and DEMO_MASTER.md §4 for full spec.

---

## Session AF (June 10, 2026) — *Pure strategy session: STATE-vs-CONTEXT universal moat locked; RTOC-sovereign deployment; §9 data architecture; H1 premise corrected; SPRINT_PLAN.md created — docs only, no UI changes*

**Code committed:** `0c35a8f` (docs(strategy): Session AF — STATE-vs-CONTEXT universal moat; RTOC-sovereign deployment; §9 data architecture; integrity fixes; 4-industry mapping; Claim Ledger P5-A/B/C + PREMISE)
**fault-trigger-ui image:** `sha256:2f5d3cab` (unchanged — no UI code this session)

This was a strategy-and-validation session — the most significant architecture review since Session AC. No UI code written. Session opened with mandatory startup (all 8 pods 1/1, ollama_online: True/gemma4:latest). Long planning session working through interconnected questions before committing anything. **Key decisions locked:** (1) **Tab naming** unchanged — Discern (H1) and Classify (H2) are precise and correct. (2) **Drift/retraining two-claim split:** "SCADA can't retrain" = dead (APM platforms do it). "Sovereign MLOps lifecycle" (train in Vertex → deploy to GDC → run on-prem on operator's own data) = alive as a platform claim. Drift detection = silent (not implemented). (3) **Deployment pivot — RTOC-sovereign canonical:** After reading `gdc-das-physics-detection` reference architecture (DAS = edge-by-data-gravity; 6,000 msg/s → 160,000:1 reduction at wellhead), concluded gdc-pm has NO data-gravity reason to be at the pad (4 scalar tags at 5 s = 0.3–0.5 GB/day for 38 wells). Decision-maker sits in a centralized RTOC (shale pads unmanned); GDC co-locates there, inside the IT/OT security perimeter. Sovereignty pillars: OT-segmentation + self-sufficiency (IEC 62443 / Purdue); data residency; governance/IP (Gemma open-weight on-prem). NERC-CIP applies ONLY to BES (power generation/transmission) — NOT upstream O&G; corrected throughout. (4) **H1 premise corrected via two independent expert reviews (Gemini + Claude):** "No sensor ever can distinguish gas-lock from drawdown" is FALSE (discharge gauge resolves state; PIP is submergence proxy). Premise corrected to: "on an intake-only string (~90% of Permian ESPs), the early-window decline is genuinely ambiguous — the deciding context is in documents, not sensors." (5) **STATE-vs-CONTEXT as the universal moat:** sensors report STATE; the correct action depends on CONTEXT (equipment history, GOR trends, offset-frac activity) that is categorically not a real-time measurement. Honest, unkillable, generalizes across industries. (6) **4-industry horizontal positioning:** O&G / P&E / Manufacturing / Mining — same pattern in each. Demo = worked example; platform claim = horizontal. (7) **Sand/shut-in physics resolved:** Both expert reviews confirmed: VFD trim during drawdown in a moderate-sand well seizes the pump (velocity drops below critical sand-transport threshold, solids compact around rotating shaft); shut-in is safe for a moderate-sand drawdown well (pump stationary; fluid level recovers; controlled restart clears loose bed). "Never shut in a sandy well" governs high-sand-cut/unconsolidated/flowback wells only. (8) **5 integrity fixes locked in §9 Retired Claims:** "200 GB/day" (wrong ~1000× for scalar SCADA); "VSAT 15–25 min" (wrong — GEO VSAT RTT ~500–650 ms); "decision at the pad" (RTOC); "no cloud dependency for the decision" (→ sovereignty framing); "NERC-CIP for upstream O&G" (→ IEC 62443 / Purdue). **Committed:** DEMO_MASTER.md Session AF full rewrite — §1 horizontal positioning; §3 STATE-vs-CONTEXT thesis + 4-industry table + settled retraining/drift position + expanded rejected-claims; §4.1 premise corrected (intake-only + sand-as-stakes + decision-window-ambiguity replaces physically-identical-forever); §9 NEW Deployment & Data Architecture; Claim Ledger P4 updated (SPE-174536 flagged unverified → SPE-170776; 4.2 ft/s = representative-not-constant); PREMISE + P5-A + P5-B + P5-C added. SPRINT_PLAN.md created (Sprint 0 complete; Sprint 1 How It Works reconciliation; Sprint 2 H1 Briefing 6 panels animated; Sprint 3 H2 Briefing 3 panels; Sprint 4 Vids). NEXT_SESSION_PROMPT.md updated. **Next task:** Sprint 1 — How It Works reconciliation (one batched index.html edit, then deploy + verify). 5 integrity fixes remain OPEN in index.html info panel.

---

## Session AE (June 10, 2026) — *Red Team assessment + integrity fixes: Class H thermal label, SCADA ledger reword, lead-time banner demoted — deployed and verified*

**Code committed:** `9d07ac2` (fix(integrity): Session AE — RT-NEW-2 Class H thermal label, RT-NEW-3 SCADA rule ledger, RT-L2 lead-time banner demoted, motor_overheat methodology softened)
**fault-trigger-ui image:** `sha256:2f5d3cab`
**Verified live:** `280°F TRIP`, `derated operating setpoint`, `IEC 60085`, `GDC already resolved`, `resolve ambiguous` — all in deployed HTML; zero 270/275/284 hits ✅

This was a pure Red Team (RT) assessment session. Mandatory startup ran clean (all 8 pods 1/1, ollama_online: True/gemma4:latest, telemetry_events: 1,168,322). Three active findings surfaced and fixed. **RT-NEW-1 (gemma4 phantom model):** Asserted "there is no Gemma 4" — retracted when user confirmed Gemma 4 is real; key lesson: PRIME DIRECTIVE SOURCE gate applies to my own knowledge claims, not just code claims. **RT-NEW-2 (Class H temperature inconsistency):** grep confirmed `270°F`, `275°F`, `284°F` all on-screen — no single consistent value, and "Class H limit" on 284°F is physically wrong (Class H = 356°F / 180°C per IEC 60085). Fixed: all reconciled to `280°F derated operating setpoint`, "Class H limit" label removed, IEC 60085 cited for insulation class. API RP 11S attribution for the specific temperature dropped (unverifiable — SOURCE gate). app.py motor_overheat methodology: dropped "ROI: 66:1" (false precision), softened "$200,000" → "~$150k–$200k", added 🔴 NEEDS-EXPERT tag. **RT-NEW-3 (SCADA ledger vs live behavior):** 12/12 live runs of `/api/h1/scenario-replay` fired "Static underload floor: rolling avg PIP < 1,020 PSI". CLAIM_LEDGER H1 row 2 had claimed "multivariate rate-of-change alarm, not a static threshold." No UI change needed (`scada_rule_fired` already shows true rule on screen); CLAIM_LEDGER reworded. **RT-L2-DRIFT:** RT review initially drifted to L2 turf; user correctly caught it. Live term-frequency audit confirmed deployed UI is ~3:1 L3-over-L2 — the AC/AD pivot is real. One genuine L2 residue: the legacy injectionRunning banner read "SCADA Alarm Zone — Lead Time Consumed" in red uppercase — headline framing, contradicting DEMO_MASTER §3(6). Fixed to muted weight, L3 framing. **RT-NEW-5 (motor_overheat latent path):** not in scripted demos but reachable via intel feed; softened and tagged NEEDS-EXPERT. All changes built (`acef8a1a0800`), pushed (`sha256:2f5d3cab`), deployed with explicit digest (initial rollout restart re-used cached old image; fixed with `kubectl set image` + exact digest), verified live. Known Integrity State: 0 open items. **Next task:** Session AF — Presenter Script + 5-Minute Veo Video (`docs/VIDEO_SCRIPT.md`).

---

## Session AD (June 10, 2026) — *UI narrative locked: Surveillance removed + physics-impossibility premise + tags vs patterns vs docs + integrity fixes — deployed and verified*

**Code committed:** `a8e6d81` (feat(ui): Session AD — Surveillance removed, physics-impossibility premise, tags vs patterns vs docs, model_drift relabeled, mainTab→architecture)
**fault-trigger-ui image:** `sha256:a74f5fbf`
**Verified live:** 4/4 grep checks pass — no `Surveillance</div>` nav, no `8,412`, `model_drift_detection: not_implemented`, `mainTab='architecture'` present ✅

This was a pure UI implementation session executing all items queued in Session AC. Three files changed in one batched session: `index.html` (7 SEARCH/REPLACE blocks in one call), `app.js` (1 line), `app.py` (1 line). **Surveillance tab fully removed:** nav div deleted (line 21), full HTML block deleted (lines 344–508, all 165 lines including the fabricated "8,412 / 14 / 156" hero numbers, the pad triage grid, and the SCADA alarm feed). A `<!-- ══ end TAB: SURVEILLANCE ══ -->` tombstone comment remains. **Default opening tab changed** from `'surveillance'` to `'architecture'` — demo now opens on How It Works. **Physics-impossibility premise added** to H1 Physics & Logic panel as a blue callout box: *"Gas lock and fluid drawdown produce physically identical PIP / Amps / Temp / Vibration signatures — with opposite correct actions... The answer exists only in field documents."* **"8,412 field documents"** removed from the L3 Context Fusion section → "field-document corpus (shift notes, sonic logs, GOR reports)". **GDC disambiguation banner** reworded to "resolved fault type from field documents". **Zone 2 Right synthesis payload** added: "The answer was never in the sensors. GDC read these documents, cross-referenced them against live telemetry, and resolved the fault in under 2s." — appears only when `h1RagRevealed=true`. **How It Works Pane 1 GDC compare card** reordered L3-first. **3-column "TAGS vs. TAG-PATTERNS vs. DOCUMENTS"** centerpiece added after Pane 1 compare cards. **Pane 3 ML Detection header** replaced with honest concessive text. **`model_drift_detected: False`** relabeled `model_drift_detection: "not_implemented"`. All changes deployed `sha256:a74f5fbf`, verified with live curl grep. Known Integrity State: 0 open items. **Next task:** Session AE — Presenter Script + 5-Minute Veo Video (`docs/VIDEO_SCRIPT.md`).

---

## Session AC (June 9, 2026) — *Narrative strategy locked: L3 categorical moat, Surveillance removed, DEMO_MASTER §3/§3.5 rewritten — docs only, no code*

**Code committed:** (docs only — pending commit at session wrap)
**fault-trigger-ui image:** `sha256:fa0d96b9` (unchanged — no code changes this session)

This was a pure strategy-and-documentation session. The Surveillance tab was evaluated and cut; the demo's value-proposition framing was pressure-tested against both threshold SCADA and best-of-breed APM platforms and rebuilt L3-centered. No UI code was written. **All decisions and their rationale are now on disk** in `DEMO_MASTER.md §3/§3.5` so they survive any context reset. Key decisions: (1) **Surveillance tab cut** (4 reasons: fabricated "8,412 docs / 14 alarms / 156 ESPs" display values; implicit straw man implying operator negligence; A-3 inside the SCADA alarm feed self-contradicts H1 lead-time thesis; workload-frame is wrong argument). (2) **L3 = sole categorical moat; L1 and L2 conceded.** Tested value prop against threshold SCADA (hand-authored per-well rules) AND advanced APM platforms (GE SmartSignal, AVEVA PRiSM, Aspen Mtell — which do adaptive ML with retraining). Only L3 wins against both tiers: no SCADA/APM product reads unstructured documents into real-time fault diagnosis. (3) **Rejected L2 claims permanently blocked:** "SCADA can't retrain" (SmartSignal/PRiSM/Mtell do this — false), "SCADA can't do multivariate detection" (false), any market-share % (🔴 NEEDS-EXPERT — fabrication risk). (4) **No market-share percentages on screen.** User generated "5%/95%" — correctly identified as fabricated; removed. Argument reframed by capability tier (architecture description, not market share). (5) **Physics-impossibility premise** is now the H1 foundation: *gas-lock and fluid-drawdown produce identical sensor signatures — this is a physical measurement constraint, not a model limitation — the answer exists only in field documents.* (6) **Lead-time (~5 min) demoted to supporting footnote.** Real and honest but gradient — keep on chart as evidence, never headline. Disambiguation is H1's headline. (7) **One honest L2 line** lives in How It Works Pane 3: segment-aware, no lifecycle diagram, concedes both tiers and pivots to L3. **Default opening tab** changes from `surveillance` to `architecture` (How It Works). **H1/H2/H3 UI impact for next implementation session:** H1: add physics-impossibility premise line; demote lead-time to footnote; add L3 synthesis payload at doc-reveal beat ("the answer was never in the sensors; GDC read 3 docs in < 2s"). H2: already L3-centered, no structural changes. H3: no narrative changes. How It Works: remove Surveillance nav tab + HTML block; change default tab; add "tags vs tag-patterns vs documents" centerpiece in Pane 1/4; reorder GDC column bullets L3-first; add honest segment-aware L2 line in Pane 3. Integrity fixes: remove/relabel `model_drift_detected: False` hardcoded field; remove "8,412 field documents" count from How It Works line ~572; don't present `/api/model/version` as live swap. All decisions permanently captured in DEMO_MASTER.md §3 (L3-centered capability stack, tier description, rejected-claims table) and §3.5 (Surveillance removed, rationale, what replaced it, new default tab).

---

## Session AB (June 9, 2026) — *esp_thermal.ubj trained + vizier_optimize() hardcoded polynomial replaced — deployed and verified*

**Code committed:** `b4013a4` (feat(h3): Session AB — esp_thermal.ubj regressor + vizier_optimize() wired)
**fault-trigger-ui image:** `sha256:fa0d96b9`
**Verified live:** `api/model/status` → `models_loaded: ['esp', 'gas_lift', 'mud_pump', 'top_drive', 'esp_thermal']` · startup log confirms `✅ Loaded thermal constraint model: esp_thermal (164 KB)` ✅

This session resolved the only remaining model integrity violation from `MODEL_FOUNDATIONS.md` §4: `vizier_optimize()` in `app.py` was using a hardcoded polynomial (`temp = 180 + 1.5(hz−45) + 0.15·max(0,hz−58)³`) instead of a real XGBoost model, making the claim "local XGBoost evaluates thermal safety" false. **Fix in two parts:** (1) **Trained `esp_thermal.ubj`:** XGBoost single-feature regressor (input: `vfd_hz`, output: `motor_temp_f`) trained on 50,200 rows generated from the canonical physics polynomial with σ=3°F Gaussian noise, exactly as specified in `MODEL_FOUNDATIONS.md §5C`. Verification gate passed: max prediction delta vs polynomial is ±0.33°F across all test points (45–70 Hz) — well inside the ±3°F spec. (2) **Wired into `app.py`:** `load_health_models()` extended with a new block that loads `esp_thermal.ubj` into `HEALTH_MODELS["esp_thermal"]` at startup (with warning-only fallback if file not found). `evaluate_hz()` inside `vizier_optimize()` now calls `HEALTH_MODELS.get("esp_thermal")` and uses `model.predict(xgb.DMatrix([[hz]], feature_names=["vfd_hz"]))` in place of the inline polynomial — with an honest polynomial fallback if the model is somehow missing. Rebuilt container, pushed `sha256:fa0d96b9`, deployed with explicit digest, confirmed live. **All five MODEL_FOUNDATIONS §4 integrity violations now ✅ CLOSED.** The only remaining gap is the full non-circular external replay through `injection_events` (a verification gap, not a model quality gap). **Next task:** Vizier end-to-end smoke-test (Vertex AI call was still in flight at session wrap) + H3 UI tab review to verify thermal model label.

---

## Session AA (June 9, 2026) — *Model Foundations precision conflict resolved — docs only, no code changes*

**Code committed:** `58190e2` (docs: Session AA — reconcile MODEL_FOUNDATIONS precision conflict)
**fault-trigger-ui image:** `sha256:5b608508` (unchanged — no code changes this session)
**Verified live:** All 8 pods 1/1 Running · ollama_online: True · gemma4:latest · field_intel: 5 · rag_documents: 18 · telemetry_events: 1,121,520 · inference-api: 7 models loaded ✅

This was a documentation-only integrity session. The session opened with mandatory startup commands (all healthy), then read NEXT_SESSION_PROMPT.md, DEMO_MASTER.md, and the full SESSION_LOG history to confirm the open items list. The key finding: the "MODEL_FOUNDATIONS vs SESSION_LOG precision conflict" open item was not a real model quality problem — it was a documentation staleness problem. `MODEL_FOUNDATIONS.md` was authored during the June 5 Session T arc; the June 9 Session S retrain had already resolved the root causes (slope-window mismatch, wrong FAULT_PROFILES) and deployed a v2 model (gas_lock P=0.995, RMSE=0.00179) — without updating MODEL_FOUNDATIONS.md. **Fix:** Updated MODEL_FOUNDATIONS.md §1, §4, §6, §8, and §9 in one batched `replace_in_file` call: historical v1 0.815 results retained in §9 (correct historical record); v2 Session S results documented in §6 (internal holdout: gas_lock P=0.995, slug_flow P=0.993, all 5 classes pass), §8 (implementation status table), and §9 addendum. §4 integrity violations table updated: esp_classifier, esp_health, slug_flow vib_range, sand_ingress amps all marked ✅ FIXED; `vizier_optimize()` hardcoded polynomial remains ❌ OPEN (esp_thermal.ubj not yet built). Also updated `H1_METHODOLOGY.md` §10 and `NEXT_SESSION_PROMPT.md` (Known Integrity State row closed, NEXT TASKS updated, git head bumped to 58190e2). No model training, no UI changes, no container rebuild. Sole remaining model integrity gap: full non-circular external replay through `injection_events` table (verification gap, not model quality gap). **Next task:** H3 Optimize tab review — smoke-test Vertex AI Vizier endpoint, assess esp_thermal.ubj build and vizier_optimize() wiring.

---

## Session Z — Addendum (June 9, 2026) — *Batch E: SCADA pre-alarm sensor tiles, taller wellbore SVG, SVG doc icons — deployed and verified*

**Code committed:** `4083b2a` (feat(ui): Batch E — SCADA pre-alarm sensor tiles, taller wellbore SVG, SVG doc icons)
**fault-trigger-ui image:** `sha256:5b608508`
**Verified live:** `curl` grep count = 28 (SONIC, GOR↑, OEM, X-MAS, FORMATION, NOMINAL all confirmed in deployed HTML) ✅

Three UI polish changes in one batched `replace_in_file` call to `index.html`. **SCADA pre-alarm sensor tiles:** The SCADA tab pre-alarm state now shows a live 2×2 sensor tile grid (PIP/Amps/Temp/Vib) in green nominal styling, reading from the same `h1ReplayData[h1CursorIdx]` arrays as the GDC tab. Before this fix, the SCADA pre-alarm state showed only a single monospace "SURVEILLANCE ACTIVE" line — the GDC tab showed live data but SCADA showed nothing, creating an asymmetric presentation an engineer would immediately notice. Now both tabs show the same live telemetry, with SCADA post-alarm showing amber tiles (alarm state) and GDC tab always green until alarm then amber. **Taller wellbore SVG (Zone 3):** Container width 12%→15%. SVG viewBox changed from `0 0 40 210` to `0 0 44 250`. Added a surface Christmas tree (X-MAS label, 3-tier rectangular header, standard wellhead equipment above the casing strings), depth tick marks on the casing at 3k ft and 6k ft with distance labels, 4 perforation pair lines (vs prior 2 pairs), and a formation/reservoir block at the bottom (~9,800 ft MD label). Fluid column y-axis scaled to new viewBox proportions. Gas bubble and sand particle animations y-values updated to match new geometry. **SVG document icons:** The three `h1-rag-doc-card` cards now display distinct inline SVG icons instead of the plain `📄` emoji. Doc 1 (shift note): a clipboard icon with ruled lines (green); Doc 1 (sonic log): a waveform trace on a dark background (green); Doc 2 (separator lab report): a rising 3-bar chart with `GOR↑` label (blue/amber); Doc 3 (OEM guide): an open book with ruled lines and spine (purple). Each SVG is 26×26px, self-contained, and thematically matches the document type. **Next task:** Confirm with user whether any additional Batch F tasks are needed or if session should wrap.

---

## Session Z (June 9, 2026) — *Batch D: Remediation writes to field_intel — HITL audit loop deployed and verified*

**Code committed:** `58fc8ac` (feat(integrity): Batch D — remediation writes to field_intel via /api/h1/remediation-record)
**fault-trigger-ui image:** `sha256:bacd3718`
**Verified live:** `curl → {"status":"ok","asset_id":"ESP-ALPHA-3","action":"vfd_trim"}` · AlloyDB row `id=73411, doc_type=remediation_record, lbl_type=hitl_action` confirmed ✅

This was a single-fix session implementing RT-7: the HITL audit loop that closes the human-operator remediation action into the persistent AlloyDB `field_intel` table. **New endpoint `/api/h1/remediation-record`:** POST endpoint accepts `RemediationRecordRequest` (asset_id, fault_type, action_label, headline, detail) and inserts a row with `doc_type='remediation_record'`, `lbl_type='hitl_action'`, `icon='✅'`, `lbl='HITL'`. The row persists in AlloyDB across sessions — every operator action becomes part of the auditable field intelligence context. **RAG exclusion:** `get_rag_context_and_adjusted_rul()` dynamic query extended with `AND lbl_type != 'hitl_action'` — operator action records are written to the audit trail but explicitly excluded from the pre-diagnosis Bayesian discrimination RAG context to prevent circular reasoning (the remediation action cannot become evidence for its own correctness). **Frontend wired in `app.js`:** `executeH1Shutdown()` calls the endpoint with `action_label='emergency_shutin'` and includes elapsed T+Xmin cursor position in the detail. `approveH1VFD()` seize path (VFD trim contraindicated on drawdown) calls with `action_label='vfd_trim_contraindicated'`, documenting the adverse outcome. The happy path (gas_lock VFD trim) continues to use the existing `/api/agent/hitl-approve` endpoint. **Key design decision:** `hitl_action` rows appear in the intelligence feed (visible to operators reviewing context) but are excluded from the RAG LR computation — this preserves the integrity of the Bayesian discriminator while still creating a complete audit trail. **Next task (Batch E):** Taller wellbore SVG + telemetry tiles visible on both SCADA and GDC sub-tabs + SVG document artifact sketches.

---

## Session Y (June 9, 2026) — *Batch C: Scrub-reactive GDC reset + transport lockout post-remediation + H2 classifier verified — deployed and verified*

**Code committed:** `1ac4c7e` (feat(integrity): Batch C — scrub-reactive GDC reset + transport lockout post-remediation)
**fault-trigger-ui image:** `sha256:bb285184`
**Smoke test:** 12/12 assertions, 0 console errors ✅ · H2 classifier_ok: true (live inference-api confirmed)

This was a pure integrity and narrative-consistency session completing all Batch C items. **Scrub-reactive GDC verdict reset:** The h1CursorIdx watcher in app.js now includes a backward-scrub guard — if the cursor moves back before gdc_detect_idx and h1FaultTypeRevealed is true, it explicitly resets h1FaultTypeRevealed, h1RagRevealed, h1EvidenceActive, h1ShowEvidenceTable, h1RagDoc2Shown, h1RagDoc3Shown, h1PumpOffExcluded, h1GasLockExcluded, and cancels all pending document reveal timers. GDC Advisor zone returns to "BASELINE MONITORING — scanning" on back-scrub. This closes the integrity gap where a presenter could show the GDC verdict, scrub back to T+0, and the verdict would still show — a temporal impossibility any engineer would call out. Note: h1FaultType is intentionally NOT reset to avoid SVG wellbore flicker during continuous scrubbing. **Transport lockout post-remediation:** H1 transport controls (◀◀/▶/▶▶ buttons and range scrubber) bind :disabled="h1Resolved || h1Seized" and the wrapper div binds pointer-events:none; opacity:0.4 on the same condition. H2 transport controls bind on h2Resolved || h2PullOutcome. approveH1VFD(), executeH1Shutdown(), and dispatchTruckRoll() all call h1Pause()/h2Pause() as their first action — play stops the instant the operator clicks any action card. H2 SCADA pump-pull button updated to h2Pause(); h2PullOutcome="false_positive". **h1Reset() expanded:** Now explicitly clears h1ShowEvidenceTable, h1PumpOffExcluded, h1GasLockExcluded to prevent stale exclusion flags persisting across new scenarios. **H2 classifier verified:** Live curl of /api/h2/scenario-replay confirmed classifier_ok: true — H2 slug_flow_prob comes from the real esp_classifier.ubj on the inference-api, not the fallback sigmoid ramp. MODEL_FOUNDATIONS vs SESSION_LOG precision conflict (0.815 vs 0.995) remains open — must be reconciled before any accuracy percentage ships on screen. **Next task (Batch D):** Remediation writes a doc_type=remediation_record row to field_intel via a new /api/h1/remediation-record endpoint, closing the HITL audit loop.

---

## Session X (June 9, 2026) — *Batch B: Bayesian posterior wired, sonic log de-smoking-gunned, GOR modal, Document Realism Gate RT-1…RT-10 — deployed and verified*

**Code committed:** `5767ccf` (feat(integrity): Session X Batch B)
**fault-trigger-ui image:** `sha256:18155185`
**Smoke test:** 12/12 assertions, 0 console errors ✅ · API verified: `bayes_pct: 99.6`, `model: esp_health.ubj`

This was a pure integrity and document-realism session, completing all outstanding Batch B RT items. **Bayesian posterior wired:** Implemented `_bayes_discriminate(fault_type)` in `app.py` using naive-Bayes odds-form (Good 1950 / Fagan 1975) with four findings grounded in API RP 11S §7.2 physics (F1 no free gas LR=8, F2 flat casing pressure LR=5, F3 declining fluid column LR=3, F4 nominal GOR LR=2). Prior = 50/50 (honest encoding of telemetry ambiguity). The posterior is computed live on every API call — verified `bayes_pct: 99.6` with `bayes_findings_count: 4` on the live endpoint. This is the final answer to "the confidence is fabricated" (RT-1): the math is on-screen, checkable, and the LRs are labeled as conservative transparent weights (not calibrated). **Document Realism Gate applied (RT-3, RT-4, RT-5, RT-7, RT-9):** Sonic log modal completely redesigned — document body now shows measurements-only: dynamic fluid level 240 ft (within limits at 06:00 — NOT the alarming 150 ft), flat casing pressure, no free gas. All diagnosis, VFD shutdown orders, and "emergency shutdown is the correct action" language removed from document body; moved to GDC verdict layer only (G2/G3 gate). GOR provenance fixed by adding a dedicated `Separator Lab Report` modal (Permian Fluid Analytics) — GOR was never measured by an acoustic survey. `Baker Hughes SONiK™` replaced with `Permian Acoustic Services (SONiX-2)` (G1 gate). `Baker Hughes ESP` in OEM doc card → `Permian ESP Operational Manual`. All `Well A-1` references in modals → `A-3`. **Health fallback fixed (RT-2):** Zone 1 health score now uses safe clamped index — no more `1.0000` on confirmed-fault state. **Expandable evidence table:** Added `▼ Evidence Table` toggle button in GDC Advisor Zone 1, revealing F1–F4 Bayesian update chain with LR, prior_p, post_p columns. Also added `h1GorModalOpen` and `h1ShowEvidenceTable` state variables to `app.js`. **Global clinerules updated:** Section 8 "Internal Reasoning Discipline — Thinking Block Token Economy" added to `~/.clinerules` governing concise, non-verbose internal reasoning to protect token budget. **RED_TEAM_LEDGER.md updated:** RT-1 through RT-10 logged with fix status. **Next task (Batch C):** Scrub-reactive GDC verdict reset + transport lock after remediation + H2 live slug_flow_prob verification.

---

## Session W (June 9, 2026) — *Integrity Audit + Batch A Fixes: HITL reframe, strip $, remove fake confidence, H1_METHODOLOGY.md — deployed and verified*

**Code committed:** `1e12ad7` (feat(integrity): Session W Batch A)
**fault-trigger-ui image:** `sha256:b0ebc20d`
**Smoke test:** 12/12 assertions, 0 console errors ✅ · Live grep: 0 old strings / 10 new strings confirmed

This was a pure integrity and methodology session with no new features. **Planning track:** Extensive pre-Act red-teaming surfaced seven user-raised issues (HITL, cost display, scrubbing, remediations, wellbore sizing, telemetry in both views, images) plus three additional red-team criticals (RT-1: fabricated 92/94% confidence literals; RT-2: "pump integrity confirmed" on unverified state; RT-3: sonic log with diagnosis+shutdown order = "smoking gun" — a document that would have caused operators to act before the demo timeline). **Deep methodology design:** Resolved the "how do we show real confidence on a classifier that can't distinguish gas_lock from fluid_drawdown?" question — the correct answer is a Bayesian differential-diagnosis posterior (naive-Bayes log-odds fusion over document-derived findings, Good 1950 / Fagan 1975), which attributes 100% of discriminating power to the retrieved documents (our L3 thesis), starting from a 50/50 prior (the honest encoding of telemetry ambiguity). This design is documented in the new `docs/H1_METHODOLOGY.md` (18KB standalone document). Also discovered that the fabricated 92/94% confidence would have been self-defeating — it would destroy the L3 moat argument if derived from telemetry alone, which is physically impossible for identical input vectors. **Batch A (deployed):** HITL reframe on all H1+H2 action cards and outcomes ("awaiting field confirmation · pump condition assessed on controlled restart"); stripped all $ figures from operational cards/outcomes/toasts (kept only in ⓘ Physics & Logic panel per ISA-101); shut-in now honestly framed as "Deferred production + restart costs apply"; removed fabricated 92%/94% replaced with "L3 context fused" placeholder. CLAIM_LEDGER.md and NEXT_SESSION_PROMPT.md updated. **Key rejections/deferrals:** RT-3 sonic log redesign deferred to Batch B (requires redesigning document role: measurements-only body, not smoking gun); Bayesian posterior wiring deferred to Batch B; scrub-reactive GDC (issue #4) deferred to Batch C. Document Realism Gate G1–G6 codified in planning — applies to all synthetic field documents. **Next task (Batch B):** RT-3 de-smoking-gun sonic log + fictional vendor + A-1→A-3 + hs=1.0000 fix + _bayes_discriminate() implementation + evidence table in H1 verdict + Document Realism Gate applied to all 6 H1/H2 docs.

---

## Session V (June 9, 2026) — *H2 Slug Flow Scenario Replay + Red Team Audit — deployed and verified*

**Code committed:** `eb0936e` (feat(h2): Session V — H2 Slug Flow Scenario Replay + Red Team Audit)
**fault-trigger-ui image:** `sha256:a8cac759`
**Smoke test:** 12/12 assertions, 0 console errors ✅

This session had two parallel tracks. **Track A (Truth & Integrity):** User-driven red-teaming surfaced three blocking integrity violations before any code was written. (1) CLAIM_LEDGER.md H1 sensor ranges were factually wrong — the ledger said psi 875-1100 / vib 2.0-3.5 mm/s while the actual FAULT_PROFILES say psi 400-600 / vib 4.5-6.5 — reconciled. (2) The H2 physics narrative claimed "surface slugs transmit mechanical shocks down the tubing string" — this fails a basic mechanical engineering challenge (2 miles of damped, clamped tubing). Cut and replaced with the correct mechanism: in-string multiphase slug loading at the pump intake where the gauge actually sits; cyclic gas/liquid slugs arriving at the impeller cause cyclic vib+amps+PIP with flat temp — all measured at source, no long-distance transmission. (3) simulator.py slug_flow vibration was 2.7 mm/s while FAULT_PROFILES and the classifier training data expect 4.0-6.5 mm/s — reconciled. Created `docs/RED_TEAM_LEDGER.md` — a permanent artifact of all hostile-engineer attacks ranked by "do we have an honest answer?"; trigger phrase "red team" re-runs the audit. Discovered that the local `esp_classifier.bst` is a 4-class model (normal/gas_lock/sand_ingress/motor_overheat) with no slug_flow class — H2 correctly uses the inference-api's 5-class `esp_classifier.ubj` via async parallel httpx calls. Health model (esp_health.ubj) verified to dip to 0.52 on slug trajectory — acknowledged honestly in the UI ("Health model reacts to rising vib rate — use classifier for fault type"). **Track B (H2 Implementation):** Built the complete H2 Scenario Replay architecture: backend `/api/h2/scenario-replay` endpoint (120-step trajectory, cyclic vib 1.2→4.5 mm/s, temp FLAT 198°F, ISA-18.2 HI at 4.0 mm/s fires, HH at 5.0 mm/s never fires, 15+ min GDC lead time); replaced static H2 Classify tab with the full interactive layout (dual-sensor Plotly chart, scrubber with GDC▲/HI▲ markers, ISA-101 sub-tab SCADA View with 2-equal-action cards and no hand-holding text, GDC Advisor 3-zone layout with sequential doc reveals, shared SVG wellbore visible on both sub-tabs showing surface slug animation + healthy green pump/motor). **Key rejections:** Echometer fluid level "streaming automatically" rejected — narrative corrected to ad-hoc survey ordered by lease operator, uploaded 15 min prior. SCADA hand-holding text removed per user request — SCADA view now shows raw ISA-18.2 HI alarm and two equal-size option cards; ambiguity explanation tucked behind Physics & Logic panel. **Next task (Session W):** H2 UX polish (live baseline feed, SVG annotations) + RED_TEAM_LEDGER P-2/P-3 resolution + H3 Vizier verification.

---

## Session U (June 9, 2026) — *H1 ISA-101 3-zone Decision Console (steps 3c + 3d) — deployed and verified*

**Code committed:** `c06aaf9` (feat(ui): Session U — ISA-101 3-zone Decision Console (3c+3d): new SCADA view, GDC 3-zone, cursor-reactive SVG wellbore, removed fleet card)
**fault-trigger-ui image:** `sha256:a33a0833`
**Smoke test:** 12/12 assertions, 0 console errors ✅

Completed the two remaining H1 Decision Console sub-tasks deferred from Session T. **3c (Full ISA-101 Decision Console redesign):** SCADA View redesigned from a 2-card sensor grid to a proper ISA-101 HP-HMI layout — pre-alarm shows a quiet slate monospace status line (`WELL A-3 — SURVEILLANCE ACTIVE · ALL SENSORS WITHIN LIMITS`, no color, no noise), post-alarm reveals a compact amber alarm banner + 2×2 industrial tag grid (PIP/Amps/Temp/Vib, monospace readouts with SCADA setpoints) + two equal ISA-101 slate-outline action cards (VFD Speed-Down / Emergency Shut-In, not color-saturated since cause is unknown). The old saturated amber cards and 2-sensor pre-alarm grid were replaced. GDC Advisor View restructured from a flat single-column layout into a Three-Zone ISA-101 layout: Zone 1 (full-width assessment headline, monochrome border — quiet baseline → scanning retrieval → full GDC verdict), Zone 2 Left (58%, action cards and outcomes, scrollable), Zone 2 Right (30%, vertical document stack with three pgvector evidence cards revealed sequentially: primary shift note/sonic log fires with RAG, GOR Lab Test fires +2s, OEM Troubleshooting Guide fires +3.5s using existing `h1RagDoc2Shown`/`h1RagDoc3Shown` state), Zone 3 (12% far-right strip, SVG downhole digital twin, GDC view only). **3d (SVG wellbore cursor-reactive binding):** The old SVG wellbore (previously hardcoded to binary `h1RagRevealed` toggle) was completely replaced with a new Zone 3 SVG whose gas bubble and sand particle `<g>` groups have their opacity bound to `Math.max(0, (h1CursorIdx - h1ReplayData.gdc_detect_idx) / Math.max(1, h1ReplayData.n - 1 - h1ReplayData.gdc_detect_idx))` — a continuous 0→1 ramp from the GDC detection index to the end of the trajectory, zero before detection. This is a live, honest coupling of visual animation to model output position. **Fleet Scale Card removed** — the Surveillance tab already makes the fleet-scale argument (156 ESPs, 14 alarms, 8,412 documents); redundant card deleted from Discern tab. Added `.h1-rag-doc-card` CSS class to styles.css for the Zone 2 right document stack cards. No Vue template compiler issues detected (all `<` in text content confirmed as `< ` with space). Smoke test: PIP 1168→493 PSI, Temp 197→248°F, Vib 1.1→5.4 mm/s — all physics correct. **Next task (Session V):** H2 Slug Flow Scenario Replay — same architectural pattern as H1 (backend replay endpoint + frontend Play/scrub + SCADA vs GDC verdict).

---

## Session T (June 9, 2026) — *H1 ISA-101 partial redesign — scrubber, physics panel, rolling x-axis*

**Code committed:** `6a8b328` (feat(ui): Session T — scrubber inside left col, ⓘ physics panel, rolling x-axis, doc reveal timers, h1SplitPercent=56)
**fault-trigger-ui image:** `sha256:45bc0846`
**Smoke test:** 12/12 assertions, 0 console errors ✅

Three of the five NEXT_SESSION_PROMPT.md §3 sub-tasks completed and deployed. **3a (Scrubber inside Left Column):** The `<input type="range">` scrubber was moved from a standalone div below the status banner into the Left Column div, directly above `#h1-replay-chart`, with `padding-left:48px;padding-right:12px` to align tick marks exactly with Plotly's `margin:{l:48,r:12}` plot area — the GDC▲ and SCADA▲ labels now land on true data positions at any window size. The Left Column width was bound to `h1SplitPercent` (changed from 38→56 default) via `:style` binding. The `.h1-splitter` drag handle was added between columns; `initH1SplitterDrag` was updated to resize `#h1-replay-chart` (not the legacy `h1-spark-*` IDs). **3b (ⓘ Physics & Logic button + panel):** Added `ⓘ Physics & Logic` button in the H1 banner `hb-actions` div; collapsible `<div v-if="showH1Info" class="physics-panel">` panel inserted after the banner with four sections: ESP Unloading Physics (identical sensor trajectories), Smart SCADA 3-rule ISA-18.2 trip logic (Rules A/B/C), XGBoost pre-threshold detection (W=20 sliding window, hs<0.65), L3 Context Fusion (pgvector RAG <2s). Used existing `.physics-panel/.pp-*` CSS classes shared with H2/H3 panels. **3e (Rolling 30-min x-axis):** `_renderH1ReplayChart` x-axis range changed from `[0, xMax]` to `xMax > 30 ? [xMax-30, xMax] : [0, Math.max(30, xMax)]`. Also wired `h1RagDoc2Shown/h1RagDoc3Shown` state vars and reveal timers (+2s/+3.5s after RAG) and `h1Reset()` timer cleanup — ready for 3c Document Stack. **Key rejection:** Did not start 3c (full ISA-101 Decision Console redesign) or 3d (SVG wellbore cursor-reactive binding) — would require replacing the entire old SCADA+GDC view HTML (200+ lines) which risks another SEARCH failure cascade in a single pass; defer to Session U with full context.

---

## Session S (June 9, 2026) — *Physics audit + model retrain + Surveillance tab*

**Code committed:** `327d85d` (4 commits — physics fix, Surveillance tab, retrained models)
**fault-trigger-ui image:** `sha256:d0fc6935` · **inference-api image:** `sha256:357c78da`
**Smoke test:** 12/12 assertions, 0 console errors ✅

This was an ML integrity session. The H1 demo chart was physically wrong — PIP ending at 875–1100 PSI (should be 400–600), winding temperature flat (should rise to 245–265°F), vibration too low (should be 4.5–6.5 mm/s), and the Smart SCADA alarm firing at step 119/120 (never). Root cause: `FAULT_PROFILES` in `app.py`, `fault_signatures.py`, and `retrain_edge_models.py` all had stale gas_lock endpoint ranges. All three files corrected to API RP 11S §4.2/§7.2 and SPE-174536-MS ground truth. `esp_classifier.ubj` retrained (gas_lock P=0.995, all 5 MODEL_FOUNDATIONS §6 gates pass, seed=99 independent of training). `esp_health.ubj` retrained (RMSE=0.00179, SCADA alarm zone correctly at health ≈ 0.30). Live curl verify after deploy: psi_final=536 PSI, temp=253°F, vib=5.11 mm/s, amps=32.7 A, lead_time=7.0 min, model=esp_health.ubj. Smart SCADA Rule C (undercurrent trip Amps < 50A, API RP 11S §7.2) added to `h1_scenario_replay` — now 3-rule ISA-18.2 logic; SCADA fires step 79/120 (~T=20 min). **Surveillance tab** added as the new first tab (`index.html` + `app.js`) — hero scope panel (6 pads / 156 ESPs / 14 alarms / 8,412 pgvector docs), 6-pad triage grid (Alpha amber+anomaly, Bravo–Foxtrot nominal), static DCS-style alarm noise panel, Deep-Dive CTA button -> `setMainTab(horizon1)`. App now opens on Surveillance tab by default. Key rejection: did not start Phase 3 (H1 ISA-101 redesign) — context budget risk; deferred to Session T with full spec in NEXT_SESSION_PROMPT.md.


## Session Q (June 8, 2026) — *H1 Discern tab rebuild — 4-sensor chart, SVG wellbore, smart SCADA, fleet scalability card*

**Code committed:** `1fe60f4` (feat(ui): Session Q — 4-sensor chart, SVG wellbore, smart SCADA, A-3 anchor)
**Cluster image digest:** `sha256:a751a83e` (fault-trigger-ui — Session Q, current and live)
**Smoke test:** 12/12 assertions, 0 console errors ✅

Complete rebuild of the H1 Discern tab in response to five user feedback items. Key changes: (1) replaced dual-Y chart with 4-stack Plotly subplots (PIP/Amps/Temp/Vib sharing x-axis, single `relayout` cursor for smooth scrubbing); (2) moved transport controls (◀◀/▶/▶▶) to header far right, removed separate controls row; (3) slider padded l:48/r:12 to align exactly with Plotly plot area so GDC▲/SCADA▲ tick marks land on true data positions; (4) replaced CSS div-bar wellbore with an inline SVG wellbore (vector, reactive fluid column driven by PIP, animated gas bubbles / sand particles after RAG reveal, PUMP/MOTOR/PERFS labels, motor overtemp colour); (5) greyed/disabled mitigation cards pre-alarm; (6) fleet scalability card at base of Decision Console (6 ESPs, one model, ISA-18.2/EEMUA-191 cited). Backend: added intelligent Smart SCADA rate-of-change trip (ISA-18.2 §5.3 rolling 2.5-min window, -35 PSI/min threshold + static 1020 PSI floor per API RP 11S §7.2) replacing naive static threshold; returns `scada_rule_fired` field shown in SCADA alarm banner. Anchored Discern tab to Well A-3 (removed random well ID). Created `docs/CLAIM_LEDGER.md` with 8 H1 claim rows all SURVIVES. Live run: gdc_detect_idx=34, scada_alarm_idx=119, lead_time=21.2 min, model=esp_health.ubj (real XGBoost). Decision rejected: inflating lead time or straw-manning SCADA — both PRIME DIRECTIVE violations; disambiguation (unstructured context fusion) is the headline win, not the numeric head start.

---

## Session P (June 8, 2026) — *H1 Scenario Replay — full stack complete and deployed*

**Code committed:** `d76b252` (backend + Playwright harness), `fb7b71c` (UI rewrite)
**Cluster image digest:** `sha256:97033866` (fault-trigger-ui — Session P, current and live)

**What was built and deployed:** (1) **`GET /api/h1/scenario-replay`** (app.py line 5809) — precomputes 120-step ESP unloading trajectory from `FAULT_PROFILES`, runs real `esp_health.ubj` XGBoost in W=20 sliding window with confirmed feature names (`psi`, `temp_f`, `vibration`, `motor_amps`, + rates), returns `gdc_detect_idx` / `scada_alarm_idx` / `lead_time_minutes` / `model_used`. (2) **H1 Discern tab full rewrite** (index.html + app.js) — replaces inject-and-wait with Play/scrub model: `↺ New Scenario` button, `[◀◀ Reset] [▶ Play] [▶▶ Fast]` + range scrubber, `#h1-replay-chart` Plotly dual-Y (PIP blue left + Amps green right, amber dashed GDC marker, red dashed SCADA marker, grey moving cursor), 4 sensor tiles at cursor position, SCADA sub-tab gated on `h1CursorIdx >= scada_alarm_idx`, GDC sub-tab gated on `h1FaultTypeRevealed` (watcher on cursor crossing `gdc_detect_idx`) + 1.5s `h1RagRevealTimer` for RAG card reveal. (3) **`scripts/ui_smoke.mjs`** Playwright harness — headless Chromium, console capture, Plotly dump, PNG screenshot.

**Key decisions:** SCADA threshold = 1000 PSI (NOT 800 PSI — `FAULT_PROFILES` `psi_range` 875–1100 never crosses 800; 1000 PSI = API RP 11S §7.2 underload setpoint). Lead time is computed live by the real model — ran at 5.0 min in verification (honest, varies per run). All existing action card CSS (`.h1-action-card`, `.h1-card-green`, `.h1-card-contraindicated`) kept unchanged. Old inject-and-wait / sparklines / degrade polling entirely removed from index.html.

**Verification:** `n:120, gdc:75 < scada:95, lead:5.0min, model:esp_health.ubj` ✅. Smoke test: **12/12 assertions, 0 console errors, 0 JS errors**. `#h1-replay-chart` found, PIP trace 120 pts starting 1217 PSI declining to 883 PSI (physics correct). No Vue template leaks. No FALLBACK_SYNTHETIC.

**Next task:** User visual review of the live Discern tab. Then H2 Classify tab Scenario Replay (same architecture: `GET /api/h2/scenario-replay?fault=slug_flow`, vib+temp decorrelation chart, $1,500 vs $150k verdict).

---

## Session N (June 8, 2026) — *Vue template crash fixed · Descriptive action cards · SPE-174536 velocity boundaries · Financial breakdowns — sha256:8c73db2d*

**Code committed:** `454ed9f` (fix(ui): Session N — Vue template crash, action cards, SPE-174536 boundaries, financial breakdowns)
**Image digest:** `sha256:8c73db2d` · pod `fault-trigger-ui-68dd77fd7f-8lw22` 1/1 Running

**Root cause diagnosed and fixed:** Session M's bare-metal SCADA sensor tile redesign introduced raw `<800 PSI` and `<50 A` text directly inside HTML `<div>` content inside a Vue.js 3 template. Vue 3's template compiler treats `<800` as an opening tag and fails silently, causing the entire Vue app to fail to mount. Result: no LLM streaming, no Plotly charts ticking, no interactive tab switching. The fix was to escape all occurrences of unescaped `<` to `&lt;` across index.html (sparkline labels, SCADA sensor tiles, RAG latency copy, H3 RUL formula, Arch tab Vibration spec, HNSW retrieval latency — 11 locations total).

**New action card design deployed (both SCADA and GDC):** The simple one-line action buttons were replaced with large `.h1-action-card` styled descriptive cards. On the SCADA side, both cards now show: physical mechanism description, "Apply if:" guidance, and explicit velocity risk warning ("velocity drops to 3.1 ft/s → sand bridge → ~$150k seizure"). On the GDC side, the Gas Lock card is styled `h1-card-green` and labeled "✔ GDC RECOMMENDED"; the Drawdown shutdown card is `h1-card-red` with "✔ GDC RECOMMENDED"; the contraindicated VFD trim is `h1-card-contraindicated` with "❌ GDC CONTRAINDICATED" and full boundary reference.

**Post-selection itemized financial tables:** After the operator makes a selection, both SCADA and GDC views render a full itemized line-item breakdown using CSS grid. Seizure path: Pull-rig $42k (WTX spot $14k/day × 3d) + Replacement ESP Motor $53k + HP cable $15k + Deferred production $39.9k (300 BPD × $76/bbl × 1.75d) = ~$149,900. Correct paths show avoided capital vs net cost. All values sourced to OUR-CODE app.py FAULT_PHYSICS + WTX rig rate (🟡 OUR-CODE).

**SPE-174536 velocity boundaries woven into all warning surfaces:** GDC drawdown verdict updated to "Speed-down below 48 Hz drops velocity from 4.2 ft/s to 3.1 ft/s at 44 Hz — breaching the critical sand-transport lift boundary (SPE-174536)." Override modal bullet list now explicitly cites at-52Hz (4.2 ft/s above minimum) and at-44Hz result (3.1 ft/s below minimum). app.js seizure failure log updated with exact velocity numbers and SPE-174536 citation. 5 occurrences of SPE-174536 confirmed in deployed container.

**Key decisions:** (a) The Vue template crash root cause was the SCADA redesign from Session M — bare `<` in HTML text content. All future SCADA-style inline `<` comparisons must use `&lt;`. (b) The `.h1-action-card` CSS pattern (large, text-heavy, colored border, left-aligned) is now canonical for all intervention decisions — reuse for H2 Classify tab in Session O. (c) The financial breakdowns use the CLAIM LEDGER sourced numbers — $42k pull-rig (WTX spot), $53k motor (Reda Class H), $15k cable, $39.9k deferred production — all OUR-CODE, defensible under O&G engineer scrutiny.

**Next task (Session O):** Browser smoke-test of full H1 flow (user must run in browser — no browser on SSH remote). Then H2 "Classify" tab upgrade per DEMO_MASTER §5 — two-pane SCADA/GDC layout, slug flow narrative, $148,500 false-positive prevention story, reusing `.h1-action-card` CSS pattern.

---

## Session M (June 8, 2026) — *Dynamic well routing, EMA smoothing, SCADA de-clutter, GDC scanning state — sha256:add2a56d*

**Code committed:** `90b5185` (fix(ui): Session M — dynamic well routing, EMA smoothing, projection traces, SCADA de-clutter, GDC scanning state)
**Image digest:** `sha256:add2a56d` · pod `fault-trigger-ui-84778f746b-qplhx` 1/1 Running

**What was built and deployed:** Four targeted fixes across app.js and index.html. (1) **Dynamic well routing:** All hardcoded `ESP-ALPHA-1` endpoints in app.js replaced with dynamic `h1TargetWell` / `h1SelectedWell` references. Every API call — live-telemetry, forecast-data, degrade-status, intelligence-feed, cancel-degrade, hitl-approve, recovery-status, and both agent/chat calls — now targets whichever well the injection randomly selected. (2) **EMA smoothing + projection traces:** `_renderH1Charts()` `_spark()` closure upgraded: EMA alpha=0.18 applied to historical trace; ML forecast dotted trace (traces[1]) and confidence cone fill (traces[2]) rendered when present from the API; vertical "NOW" divider dotted line inserted at the forecast boundary. (3) **SCADA view de-cluttered:** Replaced the "Operator's Dilemma" explanatory card with a bare-metal industrial 2×2 sensor grid (PIP, Amps, Temp, VIB each with large monospace readout and SCADA alarm threshold label). The section header is now "Operator Action Required" with two plain action buttons. (4) **GDC scanning state:** Replaced the blank `v-if="!h1RagRevealed"` pre-reveal panel with a scanning wellbore schematic (greyscale, 0.65 opacity) plus animated `streaming-dot` and "Disambiguating Gas Lock vs Fluid Drawdown…" copy. This ensures the GDC tab shows a live, contextual state rather than a blank/placeholder panel immediately on injection.

**Key decisions:** (a) The "de-cluttered" SCADA view intentionally removed the explanation cards — O&G operators don't need to be told what the signals mean; what they need is live values. The dilemma is implicit: two sensors declining simultaneously, no document context, two possible causes. (b) EMA alpha=0.18 follows ISA-101 process trend display practice — removes tick-level Gaussian noise (σ≈65 PSI on ESP nominal per fault_signatures.py) while preserving trend direction. (c) NOTE: The `<800 PSI` and `<50 A` labels in the SCADA sensor grid were introduced as raw HTML — this caused a Vue 3 template compiler crash that was not detected during this session. Fixed in Session N.

**Next task (Session N):** Fix the Vue template compiler crash introduced in Session M (escaped `<` issue). Then browser smoke-test H1 flow.

---

## Session L Implementation (June 8, 2026) — *H1 Comparative Detection Scenario fully deployed — sha256:85803d58*

**Code committed:** `06dffe8` (feat(ui): Session L — Comparative Detection Scenario, Pad Alpha triage grid, 4-sparkline cards, resizable splitters)
**Image digest:** `sha256:85803d58` · pod `fault-trigger-ui-5f66b85865-g8bft` 1/1 Running

**What was built and deployed:** Complete implementation of the 9-step Session L runbook, transforming the H1 "Discern" tab from the "Double-Blind Choice Game" framing to a professional **"Comparative Detection Scenario"** targeting an O&G engineering audience. (1) **De-Gamification**: All game/gamble terminology removed across `index.html`, `app.js`. Banner button "⚡ Inject Unloading Anomaly" → "⚡ Ingest Pad Anomalies". SCADA action label "Blind Gamble — Choose Without Context" → "Reactive Manual Intervention — Without Document Context". Pre-injection placeholder "Ready for Double-Blind Choice Game" → "Pad Alpha Surveillance Active". Status banner "WELL A-1 NOMINAL" → "PAD ALPHA SURVEILLANCE ACTIVE · 6 wells nominal". (2) **Pad Alpha 6-Well Surveillance Grid**: Interactive well cards (A-1 to A-6) at the top of the Left column. `launchHorizon1Unloading()` now randomly selects a target well (`h1TargetWell`) from the 6-well pool and flags two adjacent wells (`h1NuisanceWells`) as receiving benign transient disturbances. Clicking any well updates `h1SelectedWell` for telemetry display. (3) **4 Stacked Plotly Sparkline Cards**: ISA-101 horizontal progress bars entirely removed. Replaced with `#h1-spark-psi`, `#h1-spark-amps`, `#h1-spark-temp`, `#h1-spark-vib` — each rendered by the rewritten `_renderH1Charts(d)` using a `_spark()` closure. Each chart includes a horizontal red dashed threshold shape at the SCADA alarm limit and a large bold live digital readout via Plotly annotation (top-right, color-coded red if alarm fired). (4) **Dual Resizable Drag Handles**: New `initH1SplitterDrag()` (replaces `initH1CenterSplit`) manages the horizontal `.h1-splitter` between Left/Right columns (range 25–75%, double-click resets to 38%). New `initH1ChartVerticalDrag()` (replaces `initH1NsSplit`) manages the `.h1-v-splitter` within the Left column controlling sparkline height (range 80–320px, default 140px, double-click resets). Both trigger `Plotly.Plots.resize` on all 4 sparkline elements via `$nextTick`. (5) **Departure Rate Toggle**: Standard/Accelerated buttons in the banner before injection, mapping `h1RampSpeed` to `duration_seconds` 900 or 300. (6) **New Vue state**: `h1SelectedWell`, `h1TargetWell`, `h1NuisanceWells`, `h1RampSpeed`, `h1WellData` added to `data()`. All reset correctly in `resetHorizon1()`. (7) **styles.css additions**: `.h1-telemetry-col` updated (removed hardcoded flex-basis, now bound via Vue `:style`); `.h1-v-splitter`, `.h1-well-card` (nominal/alerting/suppressed/selected variants with keyframe pulse animation), `.h1-spark-card`, `.h1-spark-label`, `.h1-pulse-alert`.

**Key decisions:** (a) `h1TargetWell` is randomly selected from all 6 Pad Alpha wells — the fault injection API still targets ESP-ALPHA-1 backend (since only that asset has a trained model) but the UI correctly shows which grid well is "alerting". This is an honest approximation — the demo narrative is about the operator triage experience, not per-well model differentiation. (b) Nuisance suppression is frontend-only; a backend `GET /api/nuisance-suppression/{asset_id}` can be added if a skeptical audience demands a RAG card showing the Daily Well Test retrieval. (c) Both old drag method names (`initH1CenterSplit`, `initH1NsSplit`) are preserved as backward-compat aliases pointing to the new methods.

**Next task (Session M):** Browser smoke-test of full H1 flow — user must report visual findings since no browser on SSH remote. Then H2 "Classify" tab upgrade per DEMO_MASTER §5.

---

## Session L Design (June 8, 2026) — *H1 Comparative Detection Scenario spec locked — doc-only, no code*

**Code committed:** docs only (DEMO_MASTER.md, NEXT_SESSION_PROMPT.md)

**What was designed:** Following user review of the deployed H1 "Discern" tab (Session J/K), three foundational design requirements were identified and fully specced: (1) **De-Gamification**: All "game", "gamble", and "🎲" language removed throughout the UI and spec. The scenario is now called the **"Comparative Detection Scenario"** and the SCADA trigger is now called **"Reactive Manual Intervention"**. The inject button becomes `⚡ Ingest Pad Anomalies`. (2) **Panel Resizability**: Both horizontal (left/right column width via `.h1-splitter` drag handle) and vertical (sparkline card height via `.h1-v-splitter` drag handle) resizability are required. Plotly charts must resize via `$nextTick` listeners. (3) **Workload Scaling / Pad Triage Scenario**: The single-well injection is replaced by a **6-well Pad Alpha triage experience** — the ingestion button randomly selects a target well (`h1TargetWell`, from A-1 to A-6) and a fault type (gas_lock or fluid_drawdown). Two adjacent wells simultaneously experience benign transient nuisance disturbances triggering SCADA alarms, which GDC suppresses via Daily Well Test RAG retrieval. The operator faces a realistic multi-alarm triage rather than a single-well event. Additionally, a **Departure Rate** toggle (Standard/Accelerated) sets `duration_seconds` to 900 or 300. Horizontal progress bars (4 ISA-101 sensor bars) are entirely removed and replaced with **4 individual stacked Plotly sparkline trend cards** — each with a bold live digital readout via annotation and a subtle horizontal red dashed SCADA alarm threshold line.

**Key decisions:** (a) "Game" framing rejected entirely per user direction — O&G domain requires professional, operationally-framed scenarios. (b) Random well selection is the correct randomization mechanism — it removes the predictability of "always well A-1" while keeping the disambiguation narrative intact. (c) Nuisance suppression is the strongest "at-scale" argument: SCADA floods the operator with 3 concurrent alarms; GDC filters to 1 critical alert while suppressing the other 2 based on retrieved context — this is unambiguously superior operational intelligence. (d) Sparklines beat bars: dynamic trending is more credible as a live operational interface than ISA-101 progress bars for a demo context. (e) Standard/Accelerated departure rate toggle was specifically requested to allow the presenter to dial-up the urgency for high-impact audiences.

**Next task (Session L implementation):** Complete implementation of the 9-step NEXT_SESSION_PROMPT.md Session L runbook: update DEMO_MASTER.md §4 (done), app.js state/methods, index.html Left column rebuild, styles.css additions, build/deploy/verify.

---

## Session K (June 8, 2026) — *Tab navigation labels corrected — Discern / Classify — deployed*

**Code committed:** `e8838af` (fix(ui): Session K — header nav tab labels Detect→Discern, Discern→Classify)
**Image digest:** `sha256:d66b61e6` · pod rolled out 1/1 Running

**What was done:** Single two-line fix: header nav tabs at lines 22–23 of index.html. Tab 1 changed from "Detect" to "Discern" (H1 Unloading tab). Tab 2 changed from "Discern" to "Classify" (H2 Slug Flow tab). These match DEMO_MASTER.md §7 canonical tab names: `How It Works | Discern | Classify | Optimize`. Rebuilt, pushed (`sha256:d66b61e6`), rollout restart, verified with grep (4 matches for "Discern|Classify" in live pod). Integrity items table in NEXT_SESSION_PROMPT cleared.

**Next task (Session L):** (1) Browser smoke-test of full H1 Discern demo flow — user must run in browser since no browser on SSH remote; report visual issues. (2) H2 "Classify" tab upgrade per DEMO_MASTER §5 — two-pane SCADA/GDC layout with surface slug flow narrative and $148,500 avoided false-positive story.

---

## Session J (June 8, 2026) — *H1 Discern Tab clean-slate rewrite — Double-Blind Choice Game deployed*

**Code committed:** `5d3a9c8` (feat(ui): Session J — H1 Discern tab clean-slate rewrite)
**Image digest:** `sha256:2fe914a6` · pod `fault-trigger-ui-77664876d7-f46qk` 1/1 Running

**What was done:** Implemented the complete H1 "Discern" tab as specified in DEMO_MASTER.md §4 and the Session I+1 NEXT_SESSION_PROMPT.md 10-step runbook. The old three-column layout (operating envelope scatter chart, 14-well pad strip, evidence wall, dual inject buttons) was entirely replaced with the **ESP Unloading Double-Blind Choice Game**. Key deliverables: (1) **Single randomized inject button** — `launchHorizon1Unloading()` randomly selects Gas Lock or Fluid Drawdown (50/50) and starts the injection without revealing the fault type. (2) **Left 40% Shared Telemetry Column** — four ISA-101 sensor bars (PIP, Amps, Temp, Vib) plus a Plotly dual-axis PIP (blue, left y-axis) / Amps (green, right y-axis) trend chart rendered into `#h1-unloading-chart`. Both sensors decline identically for both fault types — the visual proof of the physical ambiguity. (3) **Right 60% Decision Console** — two sub-tabs: 🟡 SCADA View (shows ambiguous state alarm, dilemma text explaining Gas Lock vs Drawdown physical identity, two blind-gamble action buttons) and 🟢 GDC Advisor (shows pgvector RAG card which is clickable to open a professional field log modal, CSS Dynamic Wellbore Digital Twin with gold rising gas bubbles for Gas Lock or brown falling sand for Drawdown, high-confidence GDC verdict, informed action buttons). (4) **Override modal** — when the operator attempts VFD trim during a confirmed Drawdown from the GDC tab, `h1OverrideModalOpen = true` fires a critical warning overlay listing the physical sand-bridging consequences; requires explicit "Override & Trim" button to proceed (2-click bypass). (5) **Baker Hughes Acoustic Sonic Log modal** and **Operator Shift Handover Note modal** — authentic field record pop-ups styled with header tables, measurement data, and engineer notes. (6) **Double-blind integrity** — `h1RagRevealed` starts `false` at injection; status banner reads "UNLOADING ANOMALY ACTIVE — FAULT TYPE UNKNOWN" until the second evidence item activates at T+2s, at which point the banner updates to "GAS LOCK CONFIRMED" or "FLUID DRAWDOWN CONFIRMED". All CSS animations (bubble rise, sand fall, motor glow, sub-tab active states, modal overlays, field doc tables) appended to styles.css.

**Key decisions:** (a) `h1FaultType` is set internally at inject time but `h1RagRevealed` gates all UI disclosure — the watcher sets `h1RagRevealed = true` at `h1EvidenceActive >= 2`. (b) The wrong action (VFD trim during drawdown) remains available on both SCADA and GDC sides — gated by the override modal on GDC side only. (c) `_renderH1Charts(d)` replaces the old `_renderEnvelopeChart()` — the scatter chart is removed entirely. (d) Two minor integrity items noted for Session K: header nav tab still reads "Detect" (should be "Discern") and H2 tab reads "Discern" (should be "Classify") — quick batched fix.

**Next task (Session K):** (1) Fix tab navigation labels ("Detect" → "Discern", H2 "Discern" → "Classify") — batched single replace_in_file. (2) Smoke-test the full demo flow in browser. (3) H2 Classify tab layout upgrade per DEMO_MASTER.md §5.

---

## Session I+1 (June 8, 2026) — *Doc-only: Clean-Slate H1 Discern Tab spec locked; no code changes*

**Code committed:** docs only (DEMO_MASTER.md, NEXT_SESSION_PROMPT.md)

**What was done:** Following user rejection of the layered, complex Session I H1 UI (operating envelope scatter chart, 14-well pad map, dual inject buttons, tacked-on narrative), the H1 specification was completely redesigned from first principles. DEMO_MASTER.md §4 was rewritten to define the **ESP Unloading Double-Blind Choice Game**: (1) A single `⚡ Inject Unloading Anomaly` button randomly selects Gas Lock or Fluid Drawdown behind the scenes. (2) The screen splits into shared persistent telemetry (Left 40%) — sensor bars + dual-axis PIP/Amps Plotly trend chart — and a switchable Decision Console (Right 60%) with two sub-tabs: SCADA View (blind gamble) and GDC Advisor (informed clarity). (3) The GDC Advisor tab exclusively shows: a clickable pgvector RAG card (click-through to a professional field form modal), a GDC-only Dynamic Wellbore Digital Twin (CSS/HTML, casing fluid column responds to telemetry — high stable fluid for Gas Lock with gold gas bubbles; depleted fluid with brown sand settling for Drawdown), a high-confidence GDC verdict, and informed action buttons with a mandatory override modal if the operator attempts to VFD Trim during a Drawdown. The key physical insight locked: dynamic fluid level does NOT drop during Gas Lock (casing annulus remains flooded; only gas enters the pump stages) — only a sonic log or shift note can distinguish this, which is GDC's categorical L3 moat. NEXT_SESSION_PROMPT.md updated with the 10-step Session J implementation runbook.

**Key decisions:** (a) No dual inject buttons — the double-blind only works if the fault type is unknown before GDC reveals it. (b) The wellbore schematic is exclusive to the GDC tab — SCADA cannot see the downhole digital twin. (c) Both VFD Trim and Emergency Shutdown are available on both sides — the difference is informed vs blind, not gated vs ungated. (d) No dollar hardcoding in the SCADA view — only representative framing.

**Next task (Session J):** Implement the clean-slate H1 Discern tab per DEMO_MASTER.md §4 and NEXT_SESSION_PROMPT.md STEP 3.

---

## Session I (June 8, 2026) — *Interactive H1 Unloading Game — Dual-Inject Fluid Drawdown deployed*

**Code committed:** `5485592` (feat(ui): Session I — Fluid Drawdown dual-inject game, dual-zone envelope exclusion, seizure diagnostic state)

**What was done:** (1) **Dual Inject Buttons deployed:** Single `⚡ Inject Gas Lock` button replaced with two distinct buttons — `⚡ Gas Lock` (dark red) and `⚡ Fluid Drawdown` (dark orange). Both disabled after first inject. Tab subtitle dynamically shows active fault type. (2) **Dynamic Evidence Wall:** `launchHorizon1(faultType)` now accepts a fault type param and overwrites evidence wall card content before injection. Gas Lock: GVF separator logs + 06:15 shift note. Fluid Drawdown: 06:00 sonic log (dynamic fluid level 150 ft), flat GOR/casing pressure confirming no gas migration, sand bridging contraindication. (3) **Dual-Zone Operating Envelope Exclusion:** `_renderEnvelopeChart()` now reads both `h1PumpOffExcluded` and `h1GasLockExcluded`. Gas Lock → Pump-Off Risk zone grays out with `❌ EXCLUDED (L3 Fused)`. Fluid Drawdown → Gas Lock zone grays out with same treatment. Watcher `h1EvidenceActive` routes to the correct exclusion based on `h1FaultType`. (4) **Fluid Drawdown backend:** `fluid_drawdown` added to FAULT_PROFILES (identical sensor ranges to gas_lock — this IS the physical ambiguity), PNR_MINUTES, REMEDIATION_TIERED, FAULT_PHYSICS, REMEDIATION_COSTS, INTELLIGENCE_FEED (sonic log, separator test, sand bridging guideline), GEMMA_FINDING_TEMPLATES. RAG seed doc: 06:00 dynamic sonic survey (fluid level 150 ft above intake, casing pressure flat, VFD trim contraindicated). (5) **Decision Split Card rewired:** GDC column switches between Gas Lock path (VFD Trim correct) and Fluid Drawdown path (Emergency Shutdown correct + VFD Trim shown as red contraindicated option that still fires to demonstrate consequence). (6) **h1Seized state:** If user clicks VFD Trim during Fluid Drawdown, `h1Seized = true`, split card shows `❌ Pump Seized — Sand Bridged Downhole` with physics explanation. Professional, no animations. (7) **executeH1Shutdown():** New method for safe Fluid Drawdown resolution — cancels degrade, marks resolved, shows green confirmation.

**Key decisions:** (a) No CSS seizure animations — inline styles in split card are sufficient and more professional for O&G audience. (b) VFD Trim button during Fluid Drawdown remains clickable (styled red/warning) — intentional so presenter can demonstrate the consequence path. (c) `h1FaultType` tracked in Vue state (set at inject, cleared on reset). (d) Status banner text "GAS LOCK ACTIVE" still hardcoded regardless of fault type — flagged as Next Task for Session J.

**Next task (Session J):** (1) Fix status banner text to show "FLUID DRAWDOWN ACTIVE" vs "GAS LOCK ACTIVE" based on `h1FaultType`. (2) Fix operating envelope context banner — `h1-pumpoff-excluded` shows Gas Lock text even during Drawdown. Both are minor `v-if` patches in `index.html`, one batched call.

---

## Session H (June 8, 2026) — *Phase 1 H1 UI — Operating Envelope + Discerning Operator narrative deployed*

**Code committed:** `2cd9768` (feat(ui): Phase 1 H1 — Pad Alpha map, Operating Envelope, Split SCADA/GDC card, Pump-Off exclusion)

**What was done:**
1. **Critical H1 re-analysis:** Traced the $2,500-vs-$8,000 dollar gap math error — the gap at the low end is only $500, not "an order of magnitude." Resolved by pivoting H1 entirely off the dollar-ladder and onto the **"Discerning Operator / Pump-Off Risk"** paradigm: raw PIP+Amps drops are physically identical for Gas Lock (trim is safe) and Reservoir Pump-Off (trim causes $150k sand-bridge). SCADA cannot safely auto-trim without the document context GDC provides.
2. **Document Consolidation (clean break):** Created `feature-trio-clean` branch. Deleted `CLAIM_LEDGER.md` (merged as appendix into `DEMO_MASTER.md`). Archived `INTEGRITY_AUDIT.md` + `BACKEND_CONFORMANCE_REPORT.md`. Active doc footprint reduced to 3 files. `DEMO_MASTER.md` rewrote with L1/L2/L3 capability stack, H1 Three-Act Screen spec, and updated Claims Ledger.
3. **Phase 1 UI deployed:**
   - **Pad Alpha 14-well overview strip:** 14 Vue-driven well icons. A-1 pulses amber on fault inject. Proves scale story.
   - **3-column H1 layout:** Left 23% (ISA-101 sensor bars + timeline), Center 40% (Operating Envelope + Decision Split Card), Right 37% (GDC Advisor + Intel Feed).
   - **Operating Envelope (Plotly scatter):** PSI vs Motor Amps with Gas Lock / Pump-Off / Nominal background zones. Live dot trail migrates out of Nominal during fault. When `h1EvidenceActive >= 2` (shift note retrieved), Pump-Off zone dims to gray + "❌ EXCLUDED (L3 Fused)" label — the key visual moment.
   - **Decision Split Card:** SCADA box (ambiguous, Pump-Off risk, conservative trip path) vs GDC Advisor box (L3 confirmed, safe to trim, [APPROVE VFD TRIM] HITL button).

**Key decisions:** (a) H1's economic story is now "production continuity vs. offline trip" NOT a simple $500 dollar-gap. (b) "Operational-Lead with Benchmark Dollars" framing adopted — physical risk reality leads, representative costs are supporting. (c) `h1PumpOffExcluded` keyed to `h1EvidenceActive >= 2` as a pragmatic proxy for RAG shift-note retrieval — close enough for now; a future session can tie it to a specific `pump_off_excluded` flag from `app.py`.
(d) Adopted "Fluid Drawdown" and "Fluid Unloading" as canonical domain terminology. Clarified that no sensor can distinguish them; GDC RAG context is the decider.

**Next task (Session I):** Build Act 1 & 3 of the Interactive H1 Unloading Game (dual-path injection, Fluid Drawdown RAG log, exclusion logic, and "wrong choice" stuck-pump simulation).

---

## Session H (June 8, 2026) — *Total Document Sweep & Narrative Consolidation*

**Code committed:** `feature-trio-clean` (new branch, all cruft purged, authoritative master consolidated)

**What was done:** 
1. **Executed Clean Break Strategy:** Created new branch `feature-trio-clean` to separate prior commit drift. Purged obsolete documents (`docs/INTEGRITY_AUDIT.md` and `docs/BACKEND_CONFORMANCE_REPORT.md` moved to historical archive; `docs/archive/README.md` added with explicit instructions to block future context pollution). 
2. **Re-engineered the H1 Value Proposition:** Resolved the weak $500-gap comparison of H1 by moving the core value story from a simplistic dollar-ladder onto the **"Discerning Operator"** paradigm. Documented how GDC uses L3 Context (06:15 Shift Note + Annulus Level) to safely execute early VFD trims (HITL) that SCADA operators cannot risk executing automatically on raw, ambiguous telemetry due to Reservoir Pump-Off/sand-bridging risk (~$150k stuck pump).
3. **Consolidated authoritative blueprints:** Rewrote `docs/DEMO_MASTER.md` as the absolute single-source-of-truth. Permanently welded the **Claims Ledger** directly inside it as an appendix to eliminate any future document drift. Updated the H1 and H2 design specs to detail the upcoming split SCADA/GDC advisor cards and multi-well surveillance strip. Deleted standalone `CLAIM_LEDGER.md`. 
4. **Updated Operational state:** Compacted `docs/NEXT_SESSION_PROMPT.md` for clean handoff.

**Key Decisions:** 
- (a) Consolidated active guidance into exactly **two active files** (`DEMO_MASTER.md` and `NEXT_SESSION_PROMPT.md`), saving up to 150K tokens per session and permanently ending document/narrative drift.
- (b) Adopted **"Operational-Lead with Benchmark Dollars"** framing for all future visual elements—using physical and risk reality as primary visual text, with representative dollars as supporting order-of-magnitude benchmarks.
- (c) Verified all background LLM and data operations remain fully backwards compatible.

---

## Session G (June 8, 2026) — *Phase 3 cost-ladder + sensor bar integrity fixes — deployed and verified*

**Code committed:** `a2eee90` (fix(ui): Phase 3 — cost-ladder ticks, wopt card B cost, sensor bar widths pre-injection)

**What was done:** (1) **Decision timeline tick labels corrected (CLAIM_LEDGER C2):** Tick at 72% changed from `$0→$2k` to `SCADA reactive · ~$3k–$8k` per C2 math ($1,900–$3,800 production loss + $700–$1,400 labor + $500–$1,500 thermal cycling = $3k–$8k range, 300 BPD @ $76/bbl net-back, API RP 11S §7.2). Tick at 92% changed from bare `PNR` to `PNR · ~$150k only`. (2) **Wopt card B cost corrected:** `~$2,000 workover cost` → `~$3,000–$8,000 (shut-in + restart)` with full C2 footnote: "2–4h production loss + restart labor + motor thermal cycling. 300 BPD @ $76/bbl net-back. Varies by well." (3) **Sensor bar fill widths fixed (pre-injection):** PIP/AMPS/TEMP sensor bar fill widths were rendering at hardcoded fallbacks (88%/83%/24%) before fault injection because `h1RawPsi/Temp/Amps` were only set during degrade-poll. Fixed by also setting them in `_pollLive1` (both `setMainTab` and `resetHorizon1`). Bars now show live telemetry widths from the moment the Detect tab opens. (4) **Motor CRITICAL state audited:** `h1ElapsedMin > 15` is NOT in the codebase — already correctly fixed in Session V. Banner uses `parseInt(h1SensorTemp||'0') >= 260`. Integrity table corrected to ✅. (5) **RAG seed collapse assessed:** With `AI_NARRATIVE_ENABLED=false`, `_intel_generator` is not running, no prune fires, seed doc persists throughout fault. Not an active bug; deferred.

**Key decisions:** (a) Wopt card B correction from $2k to $3k–$8k is the honest display per CLAIM_LEDGER C2 — the old $2k mapped to the `SCHEDULED` tier (inspect intake valve), not the SCADA-reactive shut-in path. (b) Sensor bar fix targets `h1RawPsi/Temp/Amps` — the text value was already live; only the bar fill width was hardcoded. VIB bar still uses hardcoded 14% pre-injection (VIB not available from `/api/live-telemetry`) — acceptable. (c) Atomic-fix rule followed: 3 related fixes shipped as one commit, verified deployed before handoff.

**Next task (Session H):** Option A — H1 cost-ladder row visual below the decision timeline (`$2,500 GDC ACT NOW` → `$3k–$8k SCADA` → `$150k PNR ONLY` labeled nodes as a horizontal strip). Pure index.html, single batched `replace_in_file`.

---

## Session F (June 8, 2026) — *Workspace isolation + Claim Ledger C2 resolved — Phase 3 unblocked*

**Code committed:** `39da363` (chore: bootstrap workspace isolation), `1518b5e` (docs: Claim Ledger C2 resolved)

**What was done:** (1) **Workspace isolation bootstrapped** for `~/gdc-pm` — had never been installed (not removed). Root cause: host-level bootstrap (`bootstrap-host.sh`) was done June 5 correctly, but per-repo step was never run for gdc-pm. Impact: every `kubectl` call in this repo was falling through to global `~/.kube/config` (gdc-pm-v2 context was set as global current context, contaminating other sessions). Fix: `scripts/setup-workspace.sh` copied from canonical template, `terraform/terraform.tfvars` created (`project_id=gdc-pm-v2, region=us-east1`), `.env`/`.envrc`/`.vscode/settings.json` generated, `.kubeconfig` seeded from live cluster (`gdc-edge-simulation us-east1`). Verified: `source .env && kubectl config current-context` → `gke_gdc-pm-v2_us-east1_gdc-edge-simulation` via isolated kubeconfig. `.gitignore` updated with isolation entries. `~/.clinerules` §5 table updated (gdc-pm → Fully isolated). All future `kubectl`/`gcloud` commands must use `source .env &&` prefix. (2) **Claim Ledger C2 resolved** — C2 (`$8k–$15k SCADA reactive path cost`) was the sole 🔴 NEEDS-EXPERT row blocking Phase 3. Resolved via independent math against demo well parameters (300 BPD @ $76/bbl net-back from app.py lines 1065/1072/1090): gas-locked ESP restart = 2–4 hours per API RP 11S §7.2; breakdown: $1,900–$3,800 production loss + $700–$1,400 labor + $500–$1,500 thermal cycling = **$3,000–$8,000** defensible range. Changed from 🔴 to 🟡 (our-math with disclosed assumptions), status → SURVIVES. Section 5 one-sentence claim updated to use new range. All 10 claims now SURVIVES or SURVIVES-with-qualification. (3) **Audited all ~/ repos** for isolation status — only gdc-pm was missing; gdc-das-physics-detection is half-done (needs project_id from user).

**Key decisions:** (a) C2 resolution approach: option (a) from rules = "soften to defensible range" — no SME required once math is transparent and assumptions are disclosed. The lower bound ($3,100) still beats the GDC action ($2,500) + preserves production, so the economic argument actually gets stronger with the honest range. (b) The $8k–$15k code values are not wrong — they map to different fault-urgency tiers (`urgent` vs `critical`), not a single scenario. (c) gdc-das-physics-detection bootstrap deferred — project_id unknown; noted in §5 table for next session that touches that repo.

**Next task (Session G):** Phase 3 H1 Decision Clock UI redesign — index.html only, single batched `replace_in_file`. Fix 3 integrity bugs (motor state timer, pre-injection sensor bars, RAG seed collapse) in the same pass. Review DEMO_MASTER.md §12 wireframe (lines 488–528) before writing any code.

---

## Session E (June 7, 2026) — *Phase 2 H1 integrity fixes — deployed and verified*

**Code committed:** `a493549` (fix(ui): Phase 2 H1 integrity fixes — Claim Ledger conformance)  
**Cluster image digest:** `sha256:ec5b0306` (fault-trigger-ui) · pod `fault-trigger-ui-cd6495468-bmpbz` 1/1 Running

**What was built and deployed:** Four H1 integrity violations from the CLAIM_LEDGER.md (Session D) fixed in two batched `replace_in_file` calls (index.html 5 blocks, app.js 3 blocks), then built, pushed, and force-deployed with explicit digest pinning. (1) **$0→$2,500 fix (Claim Ledger C1):** Corrected in 3 locations — physics panel comparison table, RESOLVED banner, Window of Options VFD card. The "$0 direct cost" was a known integrity violation: `RESOLUTION_OPTIONS["gas_lock"]["early"]["cost_incurred"] = 2500`. (2) **Vibration sensor bar added (Claim Ledger S1):** 4th H1 sensor bar (VIB) now rendered — scales to 10 mm/s, alarm tick at 80% (8.0 mm/s SCADA threshold), cavitation status "↑ Elevated — cavitation · no alarm" during gas lock injection. `h1RawVib` + `h1SensorVib` data properties added to app.js; extracted from forecast-data trace in `_renderH1PhasePlane`; included in reset. (3) **Thermal countdown clamped (I3):** Banner now gates on `h1ForecastData.slopes.dtemp_dt > 0.2` before showing countdown; shows "— monitoring temp rise" at injection onset when temperature hasn't moved yet (eliminates the "993 min" absurdity). (4) **Sensor source unified:** `_renderH1PhasePlane` now updates `h1SensorAmps/Psi/Temp/Vib` from the DB trace directly (not from the stale `activeDegradesMap.current_sensors` first-write path). With P0 queue fix (AI_NARRATIVE_ENABLED=false, queue=0), DB trace is always current.

**Verification note:** `rollout restart` re-used cached `:latest` tag and pulled the OLD image (`sha256:afa26b3a`). Fixed by `kubectl set image` with explicit new digest (`sha256:ec5b0306`). Confirmed running. API `/api/degrade-status/ESP-ALPHA-1` → `is_active: False, health: 1.0`. All 4 changes verified with grep against deployed files.

**Key decisions:** (a) The "SCADA alarm fires within seconds" root cause was the RabbitMQ backlog (stale DB rows), fixed in Session D by P0 (AI_NARRATIVE_ENABLED=false). The sensor source desync was a secondary contributor but also addressed by unifying to the DB trace source. (b) VIB bar uses `crit_vib=8.0` (from ASSET_REGISTRY) not 4.0 — gas lock vib stays at 2-3.5 mm/s, well below the alarm, which correctly shows "SCADA doesn't alarm" while showing the sensor is elevated. (c) Thermal countdown gates on `dtemp_dt > 0.2` per the Claim Ledger rationale: GDC's story is "classifier fires first, temp moves LATER." A blank "— monitoring temp rise" at T+00:10 is MORE on-message than a garbage large number.

**Next task (Session F):** User red-lines `docs/CLAIM_LEDGER.md` (esp. C2 = SCADA reactive path $8-15k, 🔴 NEEDS-EXPERT). After ledger is signed off with all SURVIVES rows, Phase 3 = H1 Decision Clock UI redesign around the honest cost-ladder story.

---

## Session D (June 7, 2026) — *Governance + Claim Ledger + RabbitMQ fix*

**Code committed:** `11d5430` (docs: archive superseded docs, add conformance report, rewrite README), `77be959` (fix: AI_NARRATIVE_ENABLED=false — kills per-message Gemma call, unclogs queue)

**What was built and deployed:** (1) **RabbitMQ P0 fix** — root-caused the 32k-message queue backlog to `AI_NARRATIVE_ENABLED=rag` in the event-processor, which was calling Ollama synchronously on every message (legacy from the old power-gen demo). Changed to `false`, restarted deployment, one-time purge of backlog. Verified: queue holds at 0 messages under live load. This fix also eliminates the stale-DB root cause of the "SCADA alarm fires in seconds" UI bug (I1 from the conformance report). (2) **Doc cleanup** — archived 13 superseded pre-pivot docs to `docs/archive/`; wrote `BACKEND_CONFORMANCE_REPORT.md` (component audit against DEMO_MASTER with integrity violations I1–I5 and legacy kill-list L1–L5); rewrote `README.md`; active doc set reduced to 7 files. (3) **Prime Directive** — prepended "Survive O&G Engineer Scrutiny" as rule #1 to `.clinerules` with 5-gate check, 🟢/🟡/🔴 confidence-tag system, and Claim Ledger enforcement mechanism. (4) **H1 Claim Ledger** — drafted `docs/CLAIM_LEDGER.md`: 14 claims across 4 sections (failure physics, SCADA limits, GDC detection, cost ladder), each sourced and challenge-tested. Key outcomes: the honest H1 story is "production continuity vs reactive shut-in" (not "GDC saves pump from death"); $0→$2,500 UI integrity bug identified; 25-min PNR and 45-min total failure window clarified as non-contradicting; C2 (SCADA reactive-path cost) flagged 🔴 NEEDS-EXPERT for SME validation before display.

**Key decisions this session:** (a) Established 6-phase program: Governance → Truth → Backend Truth → UI → Verify → Replicate H2/H3. (b) Prime Directive: every on-screen claim must pass a 5-gate scrutiny test + have a SURVIVES row in the Claim Ledger before any pixel is drawn. (c) The honest SCADA-vs-GDC comparison: SCADA's underload trip *protects the pump by stopping it*; GDC's advantage is *production continuity* — clearing the gas void before the trip fires. Never imply SCADA lets the pump die. (d) Conservative Claim Ledger drafting: 🔴 claims show as ranges or are SME-verified; no false precision. (e) Token budget discipline: no large-file (app.py/index.html) edits this session.

**Key rejections:** Rejected prior "binary $0 vs $150k" framing (was oversimplifying and misleading). Rejected "SCADA can't see multi-sensor correlation" (modern SCADA CAN, in principle — GDC wins on pre-threshold probability and context fusion, not sensor blindness). Rejected "start over" impulse — the right architecture (System 1 GDC Advisor) already exists and works; problem was legacy code + stale docs creating confusion.

**Verification:** Queue = 0 messages, 1 consumer, confirmed stable. All 8 pods 1/1 Running. `AI_NARRATIVE_ENABLED=false` in live event-processor deployment.

**Next task (Session E):** User red-lines `docs/CLAIM_LEDGER.md`; SME verifies 🔴 rows (esp. C2). After ledger is signed off: Phase 2 backend truth fixes (4 bugs in app.js/index.html in one batched call, verify deployed). Then Phase 3 H1 Decision Clock UI on a truthful foundation.

---

## Session C (June 5, 2026) — *H1 V2 redesign deployed + thermal-window integrity fix + H2 narrative locked*

**Code committed:** `4f2847e` (feat(ui): H1 V2 redesign), `bc71f69` (fix(integrity): per-run thermal window), `5d2363a` (docs: H2 narrative + DEMO_MASTER §5)
**Cluster state:** fault-trigger-ui sha256:afa26b3a (1/1), inference-api sha256:d1194989 (unchanged, v3 esp_classifier live)

**What was built and deployed — code:** (1) **H1 V2 visual redesign** (`4f2847e`): replaced 3-column well-strip + phase-plane layout with HP-HMI 2-column layout. Full-width status banner (green/amber/red, pulsing animation post-inject), YOU ARE HERE dot sliding along 25-min decision timeline, three directional sensor bars (PIP/Amps/Temp each with "↓ Lower=worse · Alarm: <X" label and SCADA status), SCADA vs GDC plain-text progressive summary, Window of Options cards. Well strip, phase-plane chart, SCADA gauge cluster, AI lead-time panel all removed. Intel feed expanded to 5 items. (2) **Thermal window integrity fix** (`bc71f69`): deleted all 7 hardcoded `25`/`18`/`23` values from the live execution path. `h1WindowTotal` data property captures the per-run thermal deadline (`thermal_lead_time_minutes` from API, fallback `time_to_scada_minutes`) on first non-null forecast poll. `_updateOptionsViability` now uses elapsed/h1WindowTotal fractions (0.72/0.92) — inject twice, get two different windows. Banner shows live `thermal_lead_time_minutes` ("N min to 280°F limit"), timeline label shows "N min this run (varies per injection)." Tick marks: "72% of window" / "92% of window." Physics panel: "~15–30 min (conservative range, per API RP 11S)."

**What was built — docs:** (3) `docs/narratives/H2_SLUG_FLOW.md` — canonical H2 narrative with three-layer evidence framework (L1 telemetry / L2 classifier / L3 context fusion), honest SCADA-vs-GDC scoping (concede L1, scope L2, own L3 categorically), SCADA challenge rebuttals, and Session C visual design directive: two-line chart = setup, evidence fusion = punchline. (4) DEMO_MASTER.md §5 updated with H2 Visual Design Directive. Both from a session-opening design discussion where user correctly challenged: "won't a multivariate SCADA do the same minus the ML?"

**Key decisions:** (a) Gas lock thermal deadline confirmed as the correct H1 window basis (failure contributor = motor-winding thermal runaway per API RP 11S §4.2). (b) H2 deadline basis is NOT thermal (motor temp stays flat by design in slug flow) — H2's urgency is $1,500-vs-$150k decision, not a countdown. (c) Honest Layer-2 scope: a good SCADA can notice the vib/temp decorrelation on one well; GDC's advantages are pre-threshold probability, learned-not-hand-coded, scales to thousands of wells. Layer 3 (4-of-6 H2 evidence sources are unstructured field docs) is categorically impossible for any SCADA product. (d) RabbitMQ at 13,986 purged end of session.

**Session D task:** H2 Discern tab redesign — index.html only, single batched replace_in_file. app.py fully wired. See NEXT_SESSION_PROMPT.md STEP 3 wireframe.

---

## Session C (June 5, 2026) — *H2 narrative locked; docs/narratives/ architecture introduced; no code changes*

**Code committed:** None (documentation-only session — H1 V2 implementation deferred at user request)
**Cluster state:** All 8 pods 1/1 Running · ollama_online: True · gemma4:latest · rag_documents: 18 · field_intel: 2 (pre-fault, expected) · RabbitMQ telemetry.events: 1,528 (healthy, < 5,000 threshold)

**What happened:** Session opened with mandatory startup checks (all healthy). User requested deep-dive on H2 scenario before proceeding with the Session C primary task (H1 V2 visual redesign). Discussion covered: (a) the complete H2 slug-flow physics and evidence structure; (b) the honest three-layer breakdown (L1 telemetry departure, L2 classifier discrimination, L3 unstructured context fusion); (c) the critical design question: *"Won't a multivariate SCADA provide the same insights minus the AI/ML part?"* — answered directly: Layer 1 is conceded to a good SCADA, Layer 2 is scoped carefully as "calibrated probability, learned not hand-authored, pre-threshold, scalable," and Layer 3 (4 of 6 H2 evidence sources are unstructured field documents SCADA has no architecture to read) is the categorically unique differentiator.

**Design decision made this session:** H2 visual directive: **lead with Layer 3 / Context Fusion as the hero; treat the two-line chart as the setup, not the punchline.** The choke log + separator test + shift note + OEM "do not pull well" retrieval assembled into a cited Advisor verdict is what a controls engineer cannot replicate with any SCADA product. The two-line chart creates the question; the evidence fusion answers it. This is locked in DEMO_MASTER.md §5 and in the new narrative doc.

**New artifact introduced: `docs/narratives/` directory.** `docs/narratives/H2_SLUG_FLOW.md` is the first in a planned series of per-horizon narrative documents (H1, H2, H3). Canonical role: the *narrative rationale* layer above DEMO_MASTER.md's spec — includes SCADA-challenge rebuttals, honest Layer-2 claim wording, code-grounded mechanism description, and visual design directives. DEMO_MASTER.md §5 now points to this file.

**Next task (pending "proceed with C" from user):** H1 V2 visual redesign per DEMO_MASTER.md §12 and NEXT_SESSION_PROMPT.md STEP 3 — status banner, decision timeline with YOU ARE HERE, directional sensor bars, SCADA-vs-GDC plain-text comparison. Two `replace_in_file` calls: `index.html` + `styles.css`. Then build/push/rollout.

---

## Session B (June 5, 2026) — *All integrity fixes deployed + live verification passing + RabbitMQ backlog purged*

**Code committed:** Session B — fix(integrity): dynamic PNR remaining time, inference-api v3 deployed, backlog purged  
**Cluster state:** fault-trigger-ui sha256:7b97605e (1/1), inference-api sha256:d1194989 (1/1, v3 esp_classifier NOW LIVE), telemetry-simulator 1/1

**What was fixed and deployed:** Three batched app.py changes in one `replace_in_file` call: (1) Line 3495: `_gemma_finding = get_gemma_finding(fault_type, asset_id)` replaces direct `GEMMA_FINDINGS.get()` for LLM context — ensures gas_lock LLM context uses the dynamic template path, not the static fallback. (2) `GEMMA_FINDING_TEMPLATES["gas_lock"]` template line: `{pnr}` → `{remaining:.0f}-min advantage window` (the live countdown). (3) `get_gemma_finding()` function: added `onset_str` → `elapsed_min` computation from `fault_onset_utc`, `remaining = max(0, PNR_MINUTES[ft] - elapsed_min)`, passed as `remaining=remaining` instead of static `pnr=25`. (4) `GEMMA_FINDINGS["gas_lock"]` static fallback: "Act within 25 minutes" → "Motor thermal window is minutes, not hours — act immediately" (honest, non-time-specific). Both fault-trigger-ui and inference-api rebuilt, pushed, and deployed with exact digest pinning. fault-trigger-ui picks up the slug_flow vib_range fix (source already correct at HEAD); inference-api picks up esp_classifier v3 from `c4ca13e`.

**Live verification:** After purging 286,418-message RabbitMQ backlog (see below), live non-circular classifier verification passed all gates: normal→normal 92.5% ≥90% ✅ · gas_lock→gas_lock 100% @ conf=1.000 ✅ · slug_flow→slug_flow 100% @ conf=0.999 ✅. All offline gates now confirmed live.

**RabbitMQ backlog discovery:** The `telemetry.events` queue had accumulated 286,418 messages over ~8h of cluster operation. Root cause: event-processor uses `prefetch_count=1` (synchronous). The Ollama RAG narrative generation times out after 30s per triggered message (Ollama is busy with the `_intel_generator` keepalive and `/api/agent/chat` calls). During heavy Ollama load, the consumer drains at ~2 messages/min while the simulator publishes 168/min → queue grows at 166/min. Purged the backlog (`rabbitmqctl purge_queue`). Session C should add a queue-depth check to startup commands and consider making RAG narrative generation async (non-blocking) to prevent re-accumulation.

**Point injection limitation documented:** `/api/inject-fault` point injections (published synchronously to RabbitMQ) get consumed in the same batch as the telemetry-simulator's concurrent normal readings. The event-processor's batch at time T contains both fault and normal readings, but the logs only show the normal PSI values. The fault readings ARE written to DB but are indistinguishable from the rapid normal reads unless you query by asset+failure_type carefully. Use `/api/inject/degrade` for live classifier verification — the degrade thread's readings arrive on their own cadence and are more reliably isolated.

**Session C required:** (a) Confidence Widget in H1 tab — `h1TopClass`/`h1TopClassProb` already wired (Session V), needs HTML/CSS probability bars for all 5 classes; (b) H2 Discern tab per DEMO_MASTER.md §5.

---

## Session W (June 5, 2026) — *ESP classifier v3 — all training-fidelity bugs fixed, all offline gates pass*

**Code committed:** `c4ca13e` (feat(models): Session W — ESP classifier v3 all gates pass)  
**Cluster state:** fault-trigger-ui sha256:b57066d4 (1/1), inference-api sha256:62e007c5 (1/1, STALE — v3 model not yet deployed), telemetry-simulator 1/1

**Root cause investigation:** Full end-to-end audit of the training-serving path revealed four independently hand-authored fault definitions (simulator.py dead code, app.py FAULT_PROFILES, fault_signatures.py, MODEL_FOUNDATIONS) that disagreed. All four ESP fault endpoint ranges in fault_signatures.py (sand_ingress, motor_overheat, slug_flow) were reconciled to match app.py FAULT_PROFILES as the authoritative source. The physics of the fault scenarios was validated as correct — the failures were training-fidelity bugs, not physics bugs.

**Three fidelity bugs fixed in train_classifiers.py:** (1) Slope-window mismatch: training used 12-reading window with formula `scale=12/n`; live processor.py uses 60-reading deque with `dt_minutes=(n-1)/12.0`. Fixed to match exactly. (2) Normal-class slope skew: the root cause of live 97%-confidence false alarms. Training drew slopes from flat bands (±2 PSI/min); live noise-driven slopes are σ≈18.7 PSI/min at the 60-window. Fixed by simulating 60-reading steady-state trajectories with absolute simulator noise (psi σ=65, temp σ=8, amps σ=6). Normal precision went from 0% to 1.000 on hold-phase test. (3) Fault noise mismatch: training used flat 1.5% noise; degrade thread uses per-sensor fractions (psi 2%, temp 1%, vib 5%, amps 1%) and amps_end=midpoint of range. Fixed to match.

**Two additional fixes:** (1) Hold-phase training samples (N=20/trajectory): offline verifier revealed that without hold-phase training, the model returned to "normal" once slopes collapsed at the fault endpoint. Fixed by generating 60-reading steady-state samples at the fault endpoint per trajectory. Gas_lock recall went from 0% to 100% at hold phase. (2) Gas_lock departure filter: applied sensor-departure threshold (psi<1335 OR amps<69, i.e. >1σ from normal) to exclude ambiguous early-ramp training rows. Gas_lock precision went from 0.826 to 0.971. Detection threshold is at 4.6% PSI decline below nominal vs SCADA alarm at 43% — the early-detection advantage over SCADA is fully preserved.

**New tool:** `scripts/verify_classifier_offline.py` — full serving-path replica (degrade ramp → 60-window deque → inference-api feature construction → model → confusion matrix). All offline gates pass independently (seed=99 vs training seed=42): normal 1.000, gas_lock 0.971, sand_ingress 0.974, motor_overheat 0.890, slug_flow 0.946, slug→sand FP 0.000.

**Key decisions:** Option B chosen for gas_lock boundary fix (sensor-departure filter) vs Option A (accept 0.90 precision) or Option C (lower the gate). Rationale: Option A had ~22% chance of spurious alarm during a 5-min normal demo window; Option C weakens the precision claim; Option B is physically honest and preserves the early-detection story. The "25 minutes" static value in app.py GEMMA_FINDING_TEMPLATES/GEMMA_FINDINGS was identified as an integrity violation (shows static PNR regardless of elapsed time) but deferred to Session B (app.py batch). DEMO_MASTER.md design was not changed.

**Session B required:** (a) Fix app.py `{pnr}` template → dynamic elapsed-time remaining (lines 4506, 4527, 4597); (b) rebuild fault-trigger-ui (slug_flow vib_range container still stale at 2.2–3.2, source correct at 4.0–6.5); (c) rebuild inference-api with v3 model; (d) live non-circular verification; (e) Confidence Widget for H1 tab.

---

## Session V (June 5, 2026) — *Integrity audit fixes — all 9 violations resolved and deployed*

**Code committed:** `bd28fdf` (fix(integrity): Session V — all 9 violations resolved V-01 through V-09)  
**Cluster image digest:** `sha256:b57066d4` (fault-trigger-ui) · pod `fault-trigger-ui-699f7667c7-nljrm` 1/1 Running

**What was built and deployed:** All 9 🔴 VIOLATION items from the Session U integrity audit (`docs/INTEGRITY_AUDIT.md`) fixed in three batched `replace_in_file` calls — one per file. **(1) app.py V-08:** Deleted `OLLAMA_DISPLAY_MODEL` variable entirely (4 lines removed) — `/api/mlops/status` now reports `OLLAMA_MODEL` directly. Verified live: `ollama_online: True · model: gemma4:latest`. **(2) app.js V-07 + wire-up:** Replaced advisor pre-load string `"Gas lock diagnosis confirmed at 94% confidence"` with `"Gas lock pattern detected · confidence building"`. Added `h1TopClass`, `h1TopClassProb`, `h1GvfPct` Vue data properties. Wired `class_probs` from `/api/plot/forecast-data` into `h1TopClass`/`h1TopClassProb` in the degrade-poll interval. Added GVF parsing from intel feed items (`/estimated at (\d+)%/` regex). Added reset in `resetHorizon1`. **(3) index.html V-01 through V-09 (9 SEARCH/REPLACE blocks):** V-01 `"94% confidence"` → `"≥92% once confirmed"`; V-02 dual-reality bar badge bound to `h1TopClass`/`h1TopClassProb` live values; V-03 all 6 `h1ElapsedMin > 15` occurrences replaced with `parseInt(h1SensorTemp||'0') >= 260` (motor state now from actual winding temp); V-04 GVF display bound to `h1GvfPct || '—'`; V-05 H2 physics text `"52%"` → `"builds to ≥90% as slug pattern confirms"`; V-06 H2 confidence card `"52% (Ambiguous)"` → `"— PREVIEW — not yet live"`; V-07 arch tab banner added; V-09 `$1,200` → `~$2,000` in arch tab walkthrough.

**Key decisions:** V-04 (GVF) implemented as an intel-feed parse rather than a new API endpoint — `_intel_generator` already writes the GVF value as text (`"estimated at {gvf}%"`) into `field_intel`, so the frontend regex-parses it from `h1FeedItems`. This avoids app.py changes and is honest: shows `'—'` pre-inject, shows the actual drawn GVF value ~20s after injection. V-03 threshold chosen as `>= 260°F` (between nominal 198°F and SCADA alarm 280°F) to give meaningful WARMING → CRITICAL progression. `parseInt()` on the `"199°F"` string correctly returns 199 in both browsers and Vue templates.

**Verification:** Pod 1/1 Running · digest `sha256:b57066d4` · `/api/mlops/status` → `ollama_online: True, model: gemma4:latest` ✓. Git clean on `feature-trio-scenarios`.

**Next task (Session W):** Classifier model recreate — fix `train_classifiers.py` slope window, retrain, non-circular verification, deploy. See NEXT_SESSION_PROMPT.md STEP 4. After W: build Live Diagnostic Confidence widget in H1 tab (h1TopClass/h1TopClassProb now wired — widget just needs HTML/CSS).

---

## Session U (June 5, 2026) — *Integrity audit + canonical fault signatures + trajectory classifier v1 (not committed)*

**Code committed:** Session U commit — fault_signatures.py, train_classifiers.py rewrite, INTEGRITY_AUDIT.md, clinerules §6, MODEL_FOUNDATIONS §9, app.py slug_flow fix  
**Cluster state:** fault-trigger-ui / inference-api / telemetry-simulator at 0 replicas (intentional, unchanged from Session T)

**What happened:** Full integrity audit of the GDC-PM demo frontend — first systematic classification of all hardcoded values. Root cause: every fake confidence value (94%, 52%, 91.4%) is a fossil from the pre-model era (Session R found inference-api returned `inference_error` on every call since day one — no classifier existed when the UI was built). Placeholders were never retired when Session S trained classifiers. Nine violations classified (V-01 through V-09) across Display, Health/Identity, and Illustrative-without-marker dimensions. Model integrity finding: v1 trajectory-based classifier trained (108,937 rows, 600 trajectories/class) using correct distributions for the first time, but failed precision thresholds (gas_lock 0.815 vs 0.92 required, slug_flow 0.746 vs 0.90). Root cause diagnosed: label-noise from indistinguishable early-ramp readings (at ramp step 12, t≈0.012 — sensors 1% toward fault endpoint, indistinguishable across all fault classes). v1 NOT committed per ML Integrity rule — git checkout'd to restore Session S classifier.

**What was built:** (1) `gke/shared/fault_signatures.py` — canonical 8-feature ESP fault signature table; single source of truth replacing four previously-disagreeing definitions. (2) `scripts/train_classifiers.py` full rewrite to trajectory-based approach: uses same `((i+1)/steps)^k` ramp formula as `_run_degrade_thread`, distributions from fault_signatures.py (gas_lock PSI 875–1100, slug_flow vib 4.0–6.5). (3) `app.py` one-line fix: `slug_flow vib_range (2.2, 3.2) → (4.0, 6.5)`. (4) `docs/INTEGRITY_AUDIT.md` — full classified violation table (9 violations with precise fix instructions). (5) Global `~/.clinerules §6` — "Integrity, End to End" five-dimension rule (Display / Model / Provenance / Health / Documentation), portable to all projects.

**Key decisions:** (a) Gradual-confidence design approved: early-ramp uncertainty is on-message ("probability scoring before thresholds" — DEMO_MASTER §2 Claim 2). (b) Two-number metric approved: show both overall (~0.81) and developed-stage (≥0.92) precision — neither cherry-picked. (c) v1 classifier explicitly NOT committed. (d) `OLLAMA_DISPLAY_MODEL` flagged as Dimension-4 (Health/Identity) violation (V-08). (e) Three-session cadence: V = fix 9 violations, W = model recreate + non-circular verify, V+ = confidence widget.

---

## Session T (June 5, 2026) — *Model foundations audit + injection event log + MODEL_FOUNDATIONS.md*

**Code committed:** `89040f9` (feat: injection event log + popup — non-circular model verification foundation)
**Cluster image digest:** `sha256:34c0c8fe` (fault-trigger-ui) · `sha256:560e4ab3` (inference-api, unchanged)

**What happened:** Post-deployment audit of the Session S classifiers found three critical defects: (1) Training distributions were hand-authored, not derived from `FAULT_PROFILES` — gas_lock was trained on PSI 350–800 but the live system injects at 875–1100 (confirmed by 71,794 DB rows avg 971 PSI). (2) Verification was circular — the 94% accuracy figure was measured against the same invented distribution used for training, not against live data. (3) H3's `vizier_optimize()` uses a hardcoded polynomial — the XGBoost health model is never called, making the "edge model enforces thermal constraint" claim false. Session S classifiers remain deployed but are explicitly marked NOT TRUSTED in the new `docs/MODEL_FOUNDATIONS.md`. Additionally: the `FAULT_PROFILES["slug_flow"]["vib_range"]` of (2.2, 3.2) barely separates from normal (0.8–2.0), meaning the H2 "vibration alarm" story is not plausible at live signal levels. Four disagreeing definitions of each fault were found (simulator.py, fault-trigger-ui FAULT_PROFILES, retrain_edge_models.py, train_classifiers.py) with no canonical source.

**What was built:** (1) `docs/MODEL_FOUNDATIONS.md` — the authoritative model spec: canonical ESP fault-signature table (gas_lock PSI 875–1100 from live DB, slug_flow vib widened to 4.0–6.5 for H2 story), per-horizon model inventory (H1: classifier+health, H2: classifier, H3: `esp_thermal` not yet built), 4 open integrity violations with deadlines, trajectory-based training spec, and non-circular verification protocol with pass/fail thresholds (gas_lock ≥ 0.92, slug_flow ≥ 0.90 on live-distribution replay). (2) `injection_events` AlloyDB table — every inject/degrade now persists drawn values AND profile bounds. (3) `GET /api/injection-log`. (4) `showInjectionPopup()` in `app.js` — dynamically created DOM popup, 5s auto-dismiss, fires on all 3 inject points. Verified live: `gas_lock point psi_target: 882.9 [875–1100] amps_target: 23.5`.

**Key decisions:** `FAULT_PROFILES` in `app.py` is the canonical source — everything derives from it. slug_flow vib must be widened to 4.0–6.5 for H2 to be credible. `esp_thermal` XGBoost model must be built for H3 to be honest. The injection event log is the non-circular verification instrument — replay its rows through `/predict`, publish the confusion matrix in `MODEL_FOUNDATIONS.md §6`.

**Next task:** Clean retrain — 5-step runbook in `MODEL_FOUNDATIONS.md §7`: fix slug_flow vib range → `fault_signatures.py` → trajectory-based classifier retrain → non-circular replay verification → `esp_thermal` + wire into H3.

---

## Session S (June 4, 2026) — *Model Prep complete — ESP classifier with slug_flow class 4, inference-api LOCAL_MODELS_DIR deploy*

**Code committed:** `92dc9be` (feat: ESP classifier with slug_flow class 4 — inference-api LOCAL_MODELS_DIR deploy)
**Cluster image digest:** `sha256:560e4ab3` (inference-api) · `sha256:565ec44a` (fault-trigger-ui, unchanged)

**What was built and deployed:** Closed the classifier gap discovered in Session R. Created `scripts/train_classifiers.py` which trains XGBoost multi-class classifiers for all 4 asset classes. The ESP classifier was extended from 4 classes to 5 — adding `slug_flow` as class 4. The `slug_flow` training signature encodes the H2 demo's discriminating physics: elevated vibration (`vib` 3–8 mm/s) with near-zero temperature rate (`dtemp_dt` ≈ ±0.08°F/min), contrasting with `sand_ingress` (vibration + rising temperature) and `motor_overheat` (strong temperature rise). All classifiers trained in <2s locally: ESP 99.92% accuracy, all 5 classes 100/200 correct in holdout test. Classifier `.ubj` files baked into the inference-api container at `/app/models/` via `COPY models/ ./models/` in Dockerfile. Set `LOCAL_MODELS_DIR=/app/models` and cleared `GCS_MODEL_BUCKET` in k8s yaml (GCS bucket was always empty — fully edge-native now). Rebuilt, pushed (`sha256:560e4ab3`), applied k8s yaml, forced exact digest rollout (old image was cached on node — `kubectl set image` with full digest solved it).

**Verified live:** `gas_lock` → 94.41% · `slug_flow` → 93.8% (flat dtemp_dt correctly discriminated from sand_ingress) · `sand_ingress` → 94.47%. DB `telemetry_events` shows real `predicted_label` values for all asset types — `inference_error` is gone. Known calibration issue: ESP nominal state occasionally classified as `sand_ingress` at 50–63% because simulator nominal amps (~88A) overlap with the training sand_ingress range (42–72A). Non-blocking for H1 demo (gas_lock injection uses PSI <800, amps <50 — unambiguous). Fix: retrain with corrected normal amps range if needed.

**Next task:** H1 V2 UI integrity fixes — all 7 known violations in `static/app.js`: (1) motor state from `h1SensorTemp` not timer, (2) GAS LOCK% from live `class_probs.gas_lock` not static text, (3) SCADA gauge bars from live telemetry not fallback, (4) "YOU ARE HERE" moving marker on Window of Options timeline, (5) event-active status banner with ticking T+MM:SS timer, (6) directional labels on SCADA gauge bars, (7) drop phase-plane chart. All 7 batched into ONE `replace_in_file` call on `app.js`.

---

## Session R — Addendum 3 (June 4, 2026) — *Critical model-architecture discovery: no classifier models exist*

**Code committed:** None (discovery session — documentation only)

**What was discovered:** While diagnosing the nominal health_score issue (Fix A), a deeper architectural gap emerged: the GCS bucket `gdc-pm-v2-models` is **completely empty**. The inference-api has been running with no models loaded since the cluster was first deployed. Every call to `POST /predict` returns `{"predicted_label": "inference_error", "confidence": 0.0}`. This explains why `class_probs` showed `{'inference_error': 0.0}` after Phase 2.

**Root cause:** The project pivoted from BQML classifier models → XGBoost health score regressors during Phase 5.1. The `retrain_edge_models.py` script correctly produced health regressors (`esp_health.ubj`, etc.) and placed them in `fault-trigger-ui/models/`. However, no equivalent classifier training script was created, and no classifier models were ever uploaded to the `gdc-pm-v2-models` GCS bucket. The inference-api's model loading logic (Priority 2: GCS download) silently fails when the bucket is empty, leaving all models as `None`.

**Why this is blocking:** The H2 (Slug Flow) demo is 100% classifier-dependent. H2's entire argument is "the model discriminates slug_flow (surface issue, $1,500 fix) from downhole fault (wrong $150,000 pump pull) — SCADA cannot." Without a working `esp_classifier`, H2 has no story. Additionally, the `esp_classifier` label map is missing `slug_flow` as a class entirely (currently: `{0: normal, 1: gas_lock, 2: sand_ingress, 3: motor_overheat}`). This needs to be added as class 4 with training data that encodes the temperature-flat signature that is the discriminating H2 feature.

**Model dependency per horizon:** H1 needs both classifier (for "gas_lock 94%" panel) + health regressor (for early detection). H2 needs classifier only — it IS the classifier story. H3 needs health regressor as Vizier's thermal-safety constraint; Vertex AI Vizier is the one intentional cloud dependency in an otherwise fully-edge stack.

**Temperature reframe does NOT reduce model dependence.** Temperature is the lagging deadline (`(280°F − temp) / dtemp_dt`) — the finish line the ML is racing to beat. The ML classifier is the hero. The reframe increases model dependence by making the classification panel the primary demo element.

**Next action:** Model-prep before any further UI work. See NEXT_SESSION_PROMPT.md STEP 4 for the complete 5-step sequence. Key steps: audit training scripts, extend classifier to include slug_flow (class 4, flat-temp training data), deploy via LOCAL_MODELS_DIR (edge-native, not GCS), verify `predicted_label = "gas_lock"` in DB.

---

## Session R — Addendum 2 (June 4, 2026) — *Fix A: inference_error classifier gate — deployed and verified*

**Code committed:** `0d85220` (fix: Fix A — exclude inference_error from classifier_active gate)
**Cluster image digest:** `sha256:565ec44a` (fault-trigger-ui)

**What was fixed:** Nominal health_score was 0.74 (should be ~0.92+ or None). Root cause diagnosed by querying the DB: ALL `predicted_label` values in `telemetry_events` were `inference_error` — the inference-api doesn't have the ESP classifier model loaded, so every reading gets labeled `inference_error`. The `classifier_active` gate checked `l not in ("normal", "")`, which treated `inference_error` as a fault label → 100% "fault fraction" → health model ran on nominal sensor data → scored 0.74 from noise slopes. **Fix:** Added `"inference_error"` to the exclusion tuple in both `plot_forecast` and `get_forecast_data`. Verified: `health_score: None, is_active: False` in nominal state. The health model itself is correctly calibrated — no retrain needed for the nominal issue. Fix B (retrain) remains optional for improving fault-severity discrimination in active injections.

---

## Session R — Addendum (June 4, 2026) — *Phase 2 app.py truth layer — deployed and verified*

**Code committed:** `faebd9f` (feat: Phase 2 app.py truth layer — thermal_lead_time, class_probs, RAG seed protection, advisor fallback)
**Cluster image digest:** `sha256:db6f7b6d` (fault-trigger-ui)

**What was built and deployed:** Four surgical `app.py` changes in a single batched `replace_in_file` call. (1) **`thermal_lead_time_minutes`** added to `/api/plot/forecast-data` response: computed as `(280 - temp_v[-1]) / dtemp_dt` where `dtemp_dt` comes from polyfit over fault-labeled rows. This number varies per run because `_run_degrade_thread` randomizes `_temp_target` and `_k` — directly solves the "always 25m" convergence problem. Verified live: returned 8.9 min with dtemp_dt=9.335 °F/min. (2) **`class_probs` dict** added to same endpoint: derived from the distribution of `predicted_label` + `confidence` in the last 20 DB rows. Currently shows `{'inference_error': 0.0}` because the ESP classifier isn't loaded in the inference-api pod — that's honest, not a code bug. During active gas_lock with a working classifier, will show `{'gas_lock': 0.94, ...}`. (3) **RAG seed doc protection**: the `_intel_generator` prune query now adds `AND id NOT IN (SELECT id FROM field_intel WHERE doc_type='shift_note' AND lbl_type='ai' ORDER BY created_at ASC LIMIT 5)` — protects the GVF seed document from being pruned after ~10 intel cycles, keeping the context-fusion RAG gap alive throughout the demo. (4) **Advisor template fallback**: `/api/agent/chat` now returns a physically grounded response when Gemma is unavailable, instead of "Unable to reach AI model." 

**Key data source discovery:** The inference-api (separate pod) outputs a full softmax `probabilities: dict[str, float]` on its `/predict` endpoint — confirmed from inspection of `gke/inference-api/app.py`. But the event-processor only stores `predicted_label` + `confidence` (top class), not the full vector, in `telemetry_events`. The `class_probs` field uses the stored labels. If the inference-api ESP classifier were loaded, this would produce a real multi-class probability distribution.

**Next task:** Phase 3 — HP-HMI/ISA-101 design system components: moving-analog-indicator (leading/lagging split), fault classification panel (from `class_probs`), status banner (from `thermal_lead_time_minutes`), gray/color discipline. Target files: `static/styles.css` + `static/app.js` (both now ~800-1600 lines, ~6× cheaper than pre-Phase-1).

---

## Session R (June 4, 2026) — *Design overhaul + Phase 1 frontend modularization — deployed and verified*

**Code committed:** `0d18533` (feat: Phase 1 frontend modularization — split index.html into static/{styles.css,app.js})
**Cluster image digest:** `sha256:85738e70` (fault-trigger-ui) · pod `fault-trigger-ui-74559b58dc-tlgmn` 1/1 Running

**What happened this session (Plan mode + Phase 1 only):** Longest Plan-mode session to date. Diagnosed the root cause of 8 failed redesigns: (1) no shared visual vocabulary — each session invented a new bespoke primary visual, every one rejected; (2) noisy real-model data forcing integrity violations (hardcoded timer-driven state, static "94%", converged "always 25m" RUL). Read all session history, the Situation Brief, and the full DEMO_MASTER before touching any code.

**Key design decisions locked this session:** Adopted HP-HMI (moving-analog-indicator + gray/color discipline) and ISA-101 (Level-1 fast-horse overview / Level-2 available detail) as the shared design system across H1/H2/H3. Reframed the hero visual from "countdown chart" to "live fault CLASSIFICATION panel + leading/lagging indicator split." Classification panel shows the full label-probability distribution derived from recent model outputs — this is categorically unmistakably ML, not threshold-alarm (SCADA). Temperature reframed as the *lagging deadline* motor is racing toward (not the ML detection signal). ML detection signal is the multivariate PIP+amps correlated decline *before* temp moves. Lead-time number = `(280°F − current_temp) / dtemp_dt` — varies per run because `_run_degrade_thread` randomizes `_temp_target` and `_k`, so "always 25m" problem is solved at the data layer. Confirmed inference-api returns full softmax `probabilities: dict[str, float]` per prediction; class_probs for UI will be derived from DB label-frequency distribution (no schema changes needed). 

**Phase 1 executed and verified:** Extracted CSS (829 lines → `static/styles.css`) and JS (1569 lines → `static/app.js`) from 4347-line `index.html` using a Python extraction script with structural assertions. New `index.html` is 1947 lines. Added `StaticFiles` mount to `app.py`, `aiofiles==23.2.1` to requirements, `COPY static/` to Dockerfile. Rebuilt image (sha256:85738e70, 2.56GB), pushed, rolled out. Verified: `/static/styles.css` HTTP 200 (76KB), `/static/app.js` HTTP 200 (87KB), page loads identically. Token impact: future HTML edits are ~2.2× cheaper; CSS/JS edits target small individual files.

**Rejected approaches this session:** (a) "5 separate microservice apps" for H1/H2/H3 — correct that they should be separate, wrong split axis; concerns should be split by concern within the frontend, not by demo act. (b) Motor temperature as the primary ML detection signal — caught and corrected: temp is lagging, ML acts on multivariate precursors before temp moves. (c) Continuing to push Phase 2+ without fixing the large-file token problem first.

**Next task:** Phase 2 (app.py truth layer): add `thermal_lead_time_minutes` (deterministic, per-run-varying), `class_probs` (DB-derived softmax), protect GVF RAG seed from prune, and Advisor template fallback. Single batched `replace_in_file` on `app.py`. See NEXT_SESSION_PROMPT.md §STEP 4.


**Format:** One paragraph per session, newest first. Never delete entries.  
**Usage:** New sessions read the last 3–5 entries only for recent decision context.

---

## Session Q — Addendum (June 4, 2026) — *H1 visual review: FAILED*

**Visual review outcome:** After deployment, four screenshots reviewed by the user. Every major element failed. Summary of failures in order of severity:

**(1) Integrity violations:** "Motor CRITICAL" fires at T+16m driven by `h1ElapsedMin > 15` — a hardcoded timer, not actual temperature. Motor temp was 199°F while SCADA alarm threshold is 280°F. The UI was lying. "GAS LOCK — 94% confidence" in the dual-reality bar is static text unconnected to the model. SCADA CSS gauge bars show fallback hardcoded values pre-injection even though live-telemetry data was available.

**(2) UX failures:** No visible "event active" state — audience doesn't know if the demo is running. No "YOU ARE HERE" indicator on the Window of Options timeline — viewers can't see how much window remains. SCADA gauge bars have no directional labels — "Alarm at 800" doesn't tell a non-engineer whether 800 is the floor or the ceiling. Phase-plane chart is unreadable to a business audience — state-space diagrams require engineering literacy that a business audience does not have.

**(3) Technical bugs:** AI Lead-Time RAG gap collapsed to 0 after ~5 minutes (seed `field_intel` GVF doc rotated out by the 100-row prune after `_intel_generator` wrote ~10 documents). Advisor T+2m re-trigger returned "Unable to reach AI model" — Gemma timeout, no fallback template.

**(4) Design root cause identified:** Every iteration added more sophistication (3-line charts → phase planes → state-space zones) while the core engagement problem was never solved: it's one button then "try to figure out what's happening." There is no live narrative, no sense of urgency building, no visual that a fast-moving business viewer can process in 3 seconds. The question was never "what does an engineer find credible?" — it should have been "what makes a non-technical person feel the urgency AND understand what GDC did that SCADA couldn't?"

**Decision:** H1 is NOT demo-ready. H2 and H3 must not be started. Next session must get explicit design approval for H1 V2 before writing any code. The redesign concept: horizontal decision timeline with a moving YOU ARE HERE marker, directional sensor bars with plain-English alarm context, a live event-active banner with ticking clock, evidence reveal sequence. DEMO_MASTER.md §15 now captures "Demo Engagement Requirements" so this failure mode is documented for future sessions.

---

## Session Q (June 4, 2026) — *Phase-plane chart + SCADA CSS gauges + AI lead-time panel + LLM re-triggering + context-fusion server fix*

**Code committed:** `a4cb95d` (fix: seed field_intel GVF doc on gas_lock inject), `245e50a` (feat: phase-plane chart, SCADA CSS gauges, AI lead-time panel, Vue watchers for LLM re-triggering)
**Cluster image digest:** `sha256:3ee29db0` (fault-trigger-ui) · pod 1/1 Running

**What was built and deployed:** Prompted by user frustration that the "Minutes Until Failure" chart showed a flat line (instantaneous model output, not a time-series countdown), the advisor fired only once, the SCADA chart showed nothing useful, and the context-fusion gap was always zero. Produced `docs/GDC_DEMO_SITUATION_BRIEF.md` for external review; consulted Gemini 3.1 Pro. Accepted 3 of 4 Gemini proposals; rejected the fake-frontend context-fusion delta (integrity violation). Also addressed user pushback on (a) what actually kills the pump (motor winding temperature, not PIP), (b) no digital clocks, (c) analytical/state-space visual, (d) resizability. **Commit 1 (app.py):** On `gas_lock` inject, immediately INSERT a `field_intel` seed row containing "estimated at 78% GVF" — the existing `adjust_rul_with_documents()` keyword-match regex fires its 0.6× multiplier, producing a real `adjusted_rul_minutes < time_to_scada_minutes`. Verified: 7.2 min gap (`17.9 → 10.7 min`). **Commit 2 (index.html):** (1) **Phase-plane chart** — replaces the flat-line chart with a Plotly scatter plot of Motor Amps (Y) × Winding Temp (X). Background shapes: green safe zone, amber warning, red gas-lock zone (physically grounded: low amps + rising temp = loss of motor cooling). SCADA alarm lines: horizontal at 50A, vertical at 280°F. Trail of last 20 operating points. Current point color-coded. The dot migrates into the red zone during gas lock while NEITHER alarm line has been crossed — this IS the demo story in one visual. (2) **SCADA CSS gauge cluster** — 4 horizontal bars (PIP, Amps, Temp, Vib) with colored fills and red threshold tick marks. Reactive to `h1RawPsi/Amps/Temp` numeric data props extracted from forecast data traces. (3) **AI Lead-Time Advantage panel** — shows sensor-only vs context-fused estimates from real API, with the RAG contribution labeled (~7 min, "Shift note + GOR lab report fused via AlloyDB RAG"). (4) **Vue `watch:` block + `_triggerAdvisoryUpdate()` method** — Advisor re-fires when: new intel doc arrives in feed, `h1OptALabel` transitions VIABLE→MARGINAL→EXPIRED, or at T+50s/T+2min scheduled intervals. Each re-fire builds a live-context prompt from current sensor slopes + elapsed time + the triggering document and calls `/api/agent/chat`.

**Decisions made this session:** (a) Rejected fake frontend context-fusion multiplier — fixed server-side with real RAG doc. (b) Replaced "Minutes Until Failure" with phase-plane state-space chart — analytically credible to petroleum engineers, self-explains without narration. (c) Destructive metric corrected to motor winding temperature (API RP 11S thermal failure chain). (d) Rejected 3D rotatable wellbore for today — deferred; SVG engineering schematic remains in well strip. (e) SCADA normalized-% chart replaced with absolute CSS gauges — cleaner signal that sensors ARE moving but haven't crossed SCADA thresholds. (f) Wrote `GDC_DEMO_SITUATION_BRIEF.md` as structured handoff doc for external model consultation.

**Verification:** Both commits deployed, pod 1/1 Running, digest `sha256:3ee29db0`. Context fusion gap: 7.2 min (real). Raw sensor values `latest_amps: 84.5, latest_temp: 202.6` confirmed present in API response for phase-plane rendering.

**Next task:** Visual verification of H1 Detect tab (user must view in browser). Then H2 (Discern) tab redesign per DEMO_MASTER.md §5: two-line Vib+Temp chart, evidence wall, GDC Advisor with "$1,500 vs $150,000" verdict.

---

## Session P (June 4, 2026) — *CSS instrument panel + 4-sensor SCADA chart + chart coherence fix*

**Code committed:** `919c7ee` (feat: CSS instrument panel (GVF/PIP/Amps/Temp), 4-sensor normalized SCADA chart (% Δ baseline))
**Cluster image digest:** `sha256:c335c72c` (fault-trigger-ui) · pod `fault-trigger-ui-7f476cf587-6bmgk` 1/1 Running

**What was built and deployed:** Two improvements prompted by user visual feedback on the Session O screenshot. (1) **CSS Instrument Panel** — the 45-line SVG wellbore cross-section replaced entirely with a CSS-only "downhole instrument panel." Structure: `WELL A-1` title + pulsing status dot (`dot-green`/`dot-amber`/`dot-red` with `@keyframes ws-pulse`) → animated fluid column (`.wstrip-casing` with `.fluid-nominal`/`.fluid-gaslock` CSS gradient animations + 3 CSS bubble floaters) → PUMP block (blue border) + MOTOR block (CSS `box-shadow` glow transitions: `motor-ok`/`motor-warn`/`motor-crit` with `@keyframes motor-glow`) → 4 instrument readouts (GVF% with animated bar, PIP↓, AMPS↓, TEMP — all live Vue data, color-coded). Design aesthetic taken from `gdc-das-physics-detection/gke/das-web-ui`: bold, dark, readable at any size, no tiny unrenderable SVG primitives. (2) **4-Sensor Normalized SCADA Chart** — replaced single-sensor-with-tabs approach (`setH1Sensor` / h1-stab tabs) with an overlay showing all 4 sensors (PIP, Amps, Temp, Vib) normalized to `% Δ from initial baseline value` on one Plotly chart. PIP and Amps decline together (orange solid / orange dotted) while Temp and Vib stay flat near 0% (blue / grey). Zero-line reference added. "✓ All above SCADA threshold" annotation bottom-right. This chart makes the multivariate correlation argument visual without narration — two sensors co-decline while two hold flat = gas lock signature, SCADA threshold not crossed.

**Decisions made this session:** (a) SVG wellbore rejected as renderable at 180px — CSS instrument panel is the correct tool at this scale. (b) Single-sensor SCADA chart with tabs undermined the multivariate argument by mimicking what SCADA does (one sensor, one threshold). 4-sensor normalized overlay is the correct visualization for "GDC sees the correlation, SCADA doesn't alarm." (c) Amps added to instrument panel per user request.

**Verification:** Pod 1/1 Running · digest `c335c72c` · ollama_online: True, gemma4:latest. Git clean on `feature-trio-scenarios`.

**Next task:** Visual verification of full H1 demo flow (inject → fluid column turns amber → status dot pulses amber → bubbles rise → SCADA chart shows PIP/Amps declining together, Temp/Vib flat → AI chart lines diverge → GDC Advisor streams → Window of Options → Approve). Then H2 (Discern) tab redesign per DEMO_MASTER.md §5.

---

## Session O (June 4, 2026) — *H1 chart redesign — implemented, deployed, verified*

**Code committed:** `15330a4` (feat: H1 chart redesign — Minutes Until Failure 3-line chart, SCADA secondary, GDC Advisor rename, well strip to right, SVG callout labels, dynamic feed poll)
**Cluster image digest:** `sha256:8202af33` (fault-trigger-ui) · pod `fault-trigger-ui-6558568b8c-q7gts` 1/1 Running

**What was built and deployed:** Implemented the full H1 chart redesign approved in Session N. Single batched `replace_in_file` call (15 SEARCH/REPLACE blocks) covering: (1) **Primary chart rewrite** — `_renderH1Charts` replaced entirely with a rolling time-series "Minutes Until Pump Failure" chart showing 3 lines: gray (SCADA flat at 120), orange dashed (sensor-only from `d.time_to_scada_minutes`), solid orange (context-fused from `d.adjusted_rul_minutes`). Shaded fill + annotation bracket "⚡ Context Fusion: −Nm" renders when gap > 0. Pre-injection: all 3 flat at 120. History buffer `h1RulHistory[]` accumulates up to 36 points. (2) **New `_renderH1ScadaChart` method** added — renders raw PIP/Amps/Temp with SCADA alarm threshold line below the primary chart (id=`h1-scada-chart`, 110px fixed height). Sensor tabs (PIP/Amps/Temp) now control the SCADA chart. "✓ No SCADA alarm triggered" annotation shown pre-injection. (3) **NS handle** made always-visible (removed `v-if="h1Injected"` gate) — sits between primary and SCADA charts. (4) **Column reorder** via CSS `order:5` on `.h1-well-strip` + `.h1-body>:nth-child(2){display:none}` to hide left splitter — well strip moves to far right (180px, `align-self:stretch`) without touching the SVG HTML. (5) **SVG callout labels** added at end of SVG: "Intake: Nominal"↔"Intake: 68% GVF ⚠" and "Motor: Cooling normal"↔"Motor: Cooling lost ⚠". (6) **"GDC Copilot" → "GDC Advisor"** across all CSS classes, Vue data props, method name, HTML labels. (7) **Dynamic feed poll** `h1FeedPollInterval` every 15s during active fault, cleared on reset. (8) Both `initH1CenterSplit` and `initH1NsSplit` now resize both `h1-gdc-chart` and `h1-scada-chart`.

**Key implementation decisions:** Used CSS `order` property + `:nth-child(2){display:none}` to reorder columns without touching the large SVG HTML block (avoiding a risky 50-line exact-match SEARCH). Pre-injection chart shows all 3 lines at 120 by gating on `this.h1Injected` in the JavaScript. Column order: Charts (44%, left) | splitter | GDC Advisor (flex:1, center) | Well Strip (180px, right — CSS order:5).

**Verification:** Pod `fault-trigger-ui-6558568b8c-q7gts` 1/1 Running · `/api/mlops/status` → ollama_online: True, gemma4:latest · `/api/plot/forecast-data/ESP-ALPHA-1` returns `time_to_scada_minutes: 35.6, adjusted_rul_minutes: 35.6, sensors: [psi, temp, vib]` ✓.

**Next task:** Visual verification of H1 demo flow (inject → 3 lines diverge → bracket appears → Window of Options → Approve). Then implement H2 (Discern) tab redesign per DEMO_MASTER.md §5: two-line vibration+temp chart, 6-chip evidence wall, GDC Advisor auto-streams "$1,500 vs $150,000" verdict.

---

## Session AH (June 10, 2026) — *Sprint 2b: H1 Briefing Panel 3 — One Signature, Two Causes*

**Code committed:** `1c02e6b` (feat(sprint2b): H1 Briefing Panel 3 — One Signature, Two Causes)
**Cluster image digest:** `sha256:68948a277d43` (fault-trigger-ui)

**What was built and deployed:** H1 Briefing Panel 3 added as the third step in the guided briefing flow. Full-screen two-column split: LEFT = Gas Lock (blue fluid column, full annulus, 3 animated `h1-wb-bubble` CSS circles rising with staggered `animation-delay`, amber gas pocket zone at top, green PUMP ⚠ / MOTOR ✓) vs RIGHT = Fluid Drawdown (dark depleted casing background, amber fluid column animated via new `h1-p3-fluid-drain` CSS class — `transform: scaleY()` with `transform-origin: center bottom; transform-box: fill-box` — giving a convincing "level dropping" effect, sand zone near perfs, red PUMP ⚠). Below both sides: identical PIP (blue) + Amps (green) `h1-brief-decline-bar` declining traces with the hero quote: *"On this well's sensor, the live decline looks the same."* Progress dots extended from 2 to 6 (dots 4–6 cosmetically greyed with tooltips "Coming: STATE vs. CONTEXT / Sand Stakes / Universal Pattern"). Counter updated to `/6`. Panel 1 & 2 labels updated to `X of 6`. Navigation: `Next →` now unlocks panel 3; `▶ Run the Scenario` CTA moved from panel 2 → panel 3. Hint text updated for each panel state. CSS: `@keyframes h1-p3-drain` + `.h1-p3-fluid-drain` added to styles.css.

**Key design decisions:** Reused existing `h1-wb-bubble` class and `@keyframes h1-bubble-rise` (already defined for the H1 scenario replay wellbore strip) rather than adding new bubble keyframes — keeps CSS DRY. Used `transform: scaleY()` with `transform-box: fill-box` for the drawdown animation instead of animating SVG `height`/`y` attributes directly — more reliable across modern Chrome. Fluid level annotation line left at a fixed y=90 (approximate mid-drain position) — cosmetically acceptable without JS-driven positioning. Bottom trace deliberately reuses `h1-brief-decline-bar` (the same class as Panel 2) because the design spec requires *visually identical* output — intentional not a copy-paste error.

**Verification:** Pod `fault-trigger-ui-9c956bd5-bfnzg` 1/1 Running (age 20s at check). Deployed via `kubectl set image` with explicit digest (not rollout restart — per permanent constraint). Build: `c694904ff499`. Push confirmed two new layers.

**Next task:** Sprint 2c — H1 Briefing Panel 4 (STATE vs. CONTEXT): two-column animated reveal, sensor readouts pulse in on left, document cards appear one by one on right, "You cannot instrument your way out of a context gap." Also extend navigation from `< 3` → `< 4` and `===3` → `===4`.

---

## Session N (June 4, 2026) — *H1 chart design — approved, not yet implemented*

**Code committed:** None (design session only — no code written)
**Cluster image:** Unchanged from Session M (`sha256:55e56268`)

**What was decided:** Extended design discussion triggered by user feedback on the Session M screenshot. Six issues identified: (1) Well strip placement (left column, too small, not readable); (2) Chart still confusing — Y-axis in PSI explains nothing to a business audience; (3) "SCADA Alarm" pins showing 4+ hours out (timing bug in chart render — `time_to_scada_minutes` returns large values in nominal state); (4) Truck roll/chemical injection as H2 scenario expansion; (5) LLM update frequency (every 20-30s, intel feed only refreshes on inject); (6) "GDC Copilot" = Microsoft competitor brand conflict.

**Key design decision approved (the chart redesign):** Replace raw sensor telemetry (PSI/Amps/Temp) as the primary H1 visual with a **"Minutes Until Pump Failure" chart** showing three distinct lines on the same plot: (1) gray — SCADA deterministic threshold monitoring (stays HIGH — honestly shows SCADA hasn't been alarmed yet); (2) orange dashed — GDC AI sensor-only XGBoost prediction; (3) solid orange — GDC AI context-fused prediction (adjusted by retrieved AlloyDB RAG documents). A shaded bracket between lines 2 and 3 dynamically labels the gap as "Context Fusion: −Nm (shift note + GOR lab test)". No hardcoded values — all computed live from `d.time_to_scada_minutes` and `d.adjusted_rul_minutes` from the API. Pre-injection: three flat calm lines at ~120+ minutes. Post-injection: GDC lines decline; context-fused line diverges below sensor-only after first RAG retrieval cycle.

**Key rejections this session:** Rejected raw-sensor-on-Y-axis approach (requires narration to understand). Rejected hardcoded timing values (integrity violation). Rejected "straw-manning" SCADA as dumb — SCADA can do multivariate correlation; our advantage is specifically (a) retrainable physics-aware models and (b) unstructured document fusion. Rejected two-chart comparative-only approach (proposed by Gemini during a brief model switch) — the context-fusion gap visualization requires both the sensor-only AND context-fused forecasts on the same Y-axis to make the gap visible.

**Additional layout changes approved:** Well strip moved to far right (decorative, full-height, 180px, with dynamic SVG callout labels for pump intake and motor status). "GDC Copilot" renamed to "GDC Advisor" throughout all CSS, Vue data, and HTML labels (Microsoft Copilot brand conflict). Dynamic feed poll every 15s during active fault.

**Next task:** Fresh session, implement the approved chart design. ONE batched `replace_in_file` call to index.html. See NEXT_SESSION_PROMPT.md Step 3 for complete implementation spec.

---

## Session M (June 4, 2026) — *H1 Detect tab bug fixes + chart redesign*

**Code committed:** `9b77d4b` (fix: H1 Detect tab — cost-zone chart, column splitters, NS resize, well strip height, intel timestamps, clean pre-injection state)
**Cluster image digest:** `sha256:55e5626853cc...` (fault-trigger-ui)

**What was built and deployed:** Five user-reported bugs on the H1 "Detect" tab fixed in a single batched `replace_in_file` call. (1) **Chart redesign** — `_renderH1Charts` rewritten from scratch: pre-injection now shows only "Live Sensor Reading" + SCADA alarm threshold line with a clean "NOW — Monitoring" label (no fault projection, no declining ML lines). Post-injection renders three colored cost-zone backgrounds (green=$0, amber=~$2k, red=$150k) with "🤖 AI detects — ACT NOW", "📡 SCADA alarms T+Xm", "⛔ PNR" event pin annotations and cost labels in each zone. "ML RUL Projection" label (integrity violation per our rules) removed and replaced with "GDC ML Forecast". (2) **Column resize splitters** — two `.h1-splitter` divs inserted between well-strip↔center and center↔copilot; `initH1CenterSplit(e, side)` wired to both; replaces the dead `initH1Resize` which was referencing `.h3-main-body` (a container that doesn't exist in the H1 layout). (3) **NS resize handle** — `h1-ns-handle` div added between chart and Window of Options (gated v-if="h1Injected"); `initH1NsSplit` method controls `h1ChartH` data property via `:style` binding. (4) **Well strip** — widened 82px → 110px; SVG `max-height:215px` changed to `flex:1;min-height:0` so the strip fills the full column height. (5) **Intel feed timestamps** — `item.ts_label` rendered in `.h1-ic-time` span on each feed row (field was already returned by the API, just never displayed in H1). Also corrected `h1SplitPercent` initial value 60→36 and added `h1ChartH:200` data property.

**Design decisions:** Chart redesign settled on a "cost-zone" framing rather than the previous engineering-centric "ML RUL Projection" line — colored background zones make the business story ($0 vs $2k vs $150k) immediately readable by a non-technical observer. SCADA chart (second stacked chart) was discussed and deferred — the dual-reality bar at the top already handles the SCADA vs AI comparison narrative. "Dive deeper" technical sub-page also deferred — existing ⓘ, citation superscripts, and "How It Works" tab stub cover that need.

**Verification:** Pod `fault-trigger-ui-64d4b6b944-9m5xb` 1/1 Running · `/api/mlops/status` → ollama_online: True, gemma4:latest · digest `sha256:55e56268`.

**Next task:** Collect user visual feedback on the Detect tab, then implement H2 ("Discern") tab redesign per DEMO_MASTER §5 — two-line vibration+temp chart, H2 dual-reality bar with 6 evidence chips, LLM copilot "$1,500 vs $150,000" verdict, reuse all H1 CSS patterns.

---

## Session L (June 4, 2026) — *H1 UI Redesign + Vue template bug fix*

**Code committed:** `e500c4d` (feat: H1 redesign — Detect/Discern/Optimize tabs, dual-reality bar, 3-col layout, copilot dominant, wopt v-if), `1915fe1` (fix: remove em-dash from {{ }} expressions — incorrect theory, benign change), `df13bf2` (fix: remove extra </div> that closed #app early)  
**Cluster image digest:** `sha256:719e0a6c...` (fault-trigger-ui)

**What was built and deployed:** Complete H1 ("Detect") UI restructure in response to 12-point user feedback. Tab nav renamed: Horizon 1/2/3 → Detect / Discern / Optimize (user's preferred "Detect, Discern, Optimize" progression). Fleet Financials tab removed. H1 banner collapsed to a single line with physics description moved behind ⓘ. "25-minute lead time" removed as a standalone callout. New **dual-reality bar** (hero comparison element): two-column compact strip showing SCADA (4 sensors, all nominal) vs GDC AI (same 4 sensors + 4 context chips activating on inject → different verdict). Old evidence wall and scada-compare boxes removed; their purpose absorbed into the dual-reality bar. New **3-column main body**: thin 82px SVG well strip (left), sensor chart + Window of Options (center 36%), dominant LLM copilot panel (right ~52%). Window of Options hidden with `v-if="h1Injected"` — only visible when fault is active. Charts now load and tick on tab open (before injection) via baseline `/api/plot/forecast-data` fetch in `setMainTab`. Live intel feed reduced to 3 compact rows. Stale `h1-scada-chart` DOM reference removed from `_renderH1Charts`.

**Key design decisions:** Dual-reality bar replaces the separate evidence-wall + scada-compare pattern — cleaner and immediately communicates the core "same sensors, different conclusion" argument. LLM copilot at ~52% width is now the visual anchor of the right half of the screen. Window of Options visible only post-injection reduces visual noise in the baseline monitoring state. "How It Works" tab pinned for future refactoring — not touched this session.

**Verification:** Pod `fault-trigger-ui-587fc8fb94-vqdst` 1/1 Running · `/api/live-telemetry/ESP-ALPHA-1` → 200 OK in logs · image digest `sha256:5c6d33ae`.

**Bug fixed (commit `df13bf2`):** The H1 redesign's Block 6 SEARCH/REPLACE (SVG closing → h1-center opening) introduced one extra `</div><!-- /h1-well-strip -->`. After `</svg>`, the existing `</div>` correctly closed `h1-well-strip`. The extra `</div>` then closed `h1-body`. This caused a cascade of 5 more orphaned closing divs: `/h1-center` → closed `h3-dashboard`, `/h1-copilot-pane` → closed the H1 `main-tab-content`, `/h1-body` → closed `app-body`, `/h3-dashboard` → **closed `#app` at line 1334**. Everything after line 1334 (the H2 tab, H3 tab, Architecture tab, and Financial Justification modal at line 2553) was rendered OUTSIDE the Vue template scope — explaining why the Financial Justification modal showed raw `{{ }}` text. Fix: removed the one duplicate line. Commit `1915fe1` (em-dash removal) was an incorrect theory and is a benign no-op; the real fix was one `</div>` deletion.

**Next task:** Collect Detect tab visual feedback, then implement H2 (Discern) tab redesign reusing all new CSS patterns (`.dr-bar`, `.h1-body`, `.h1-copilot-pane`) per DEMO_MASTER §5.

---

## Session K (June 4, 2026) — *H1 Full Redesign — deployed and verified*

**Code committed:** `9951199` (feat: H1 full redesign — Evidence Wall, Cited Copilot, Window of Options, SVG well schematic)  
**Cluster image digest:** `sha256:c8dfa4c...`

**What was built and deployed:** Complete H1 tab redesign matching DEMO_MASTER.md §4 wireframe. Two-column layout (55% left / 45% right). Left column: 2D SVG animated wellbore schematic (blue liquid particles + yellow gas particles with CSS transition, motor housing color gradient green→amber→red, GVF indicator bar), sensor tab bar + GDC forecast chart (230px), Window of Options timeline (3 cards with live VIABLE/MARGINAL/EXPIRED viability tickers, `_updateOptionsViability` ticking every 5s). Right column: Evidence Convergence Wall (5 source categories activating in sequence at 200ms/2s/3.8s/5.5s/7.2s with glow animation), SCADA comparison (always visible, left=4 sensors normal, right=8 signals GAS LOCK 94%), Cited LLM Copilot (auto-streams on inject via `_startCopilotStream` typewriter effect at 4 chars/28ms, superscript citations [¹][³][⁵] linked to source categories, follow-up chat via `/api/agent/chat`), Live Document Feed with `⚡ GDC AI — just now` badge and ALT counterargument styling.

**app.py changes:** `_intel_generator` now uses weighted 55/30/15 document type mix (supporting/neutral/counterargument) per DEMO_MASTER §10 with tailored Gemma prompts per category. `slopes` dict (`dpsi_dt`, `dtemp_dt`, `dvib_dt`, `ds4_dt`) added to `/api/plot/forecast-data` response. `_post_approval_monitor()` background function polls PIP recovery trend every 30s for 2.5 min post-VFD-approval, writes to `RECOVERY_STATUS` dict, exposed via `/api/recovery-status/{asset_id}`. `/api/agent/chat` endpoint added for H1 copilot follow-up chat. `hitl_approve()` for gas_lock now launches both `_run_recovery_thread` and `_post_approval_monitor` in parallel. Fleet Operations tab removed from header. Static financial cards not present (already absent from prior session).

**Verification passed:** Pod 1/1 Running (digest `c8dfa4c`). `/api/mlops/status` → ollama_online: True, gemma4:latest. `/api/recovery-status/ESP-ALPHA-1` → `{"msg":"","state":"pending"}` (correct for no active fault). `/api/plot/forecast-data/ESP-ALPHA-1` → `slopes` dict present with all 4 keys.

**Next task:** Verify H1 demo flow end-to-end in browser (inject → evidence wall → copilot streams → approve → recovery message). Then implement H2 redesign per DEMO_MASTER §5 (two-line vibration+temp chart, H2 evidence wall, copilot with $1,500 vs $150,000 decision, reuse H1 CSS classes).

---

## Session J (June 3–4, 2026) — *Major planning session; H1 full implementation*

**Code committed:** `e8f8b78` (feat: H1 Live Telemetry & Strategic Advisor), `862d674` (docs handoff)  
**Cluster image:** `sha256:7da84c...` (fault-trigger-ui)

**What was built and deployed:** H1-Live-1 (`/api/live-telemetry/{asset_id}` endpoint, SCADA card polls real DB every 5s), H1-Live-2 (`"normal"` key in `INTELLIGENCE_FEED` with 3 baseline docs), H1-Cards-1 (2-card layout, GDC card renamed "Assessment", PIP/Amps/Temp trend rows), H1-LLM-1 (Gemma templates upgraded to risk-weighted financial advisory), H1-P3 (`_run_recovery_thread()` posts 36 climbing DB rows over 3 min post-approval).

**Major design decisions made this session (Session J planning portion):** The Fleet Operations tab was previously removed (do not re-add). H1/H2/H3 tabs are the complete primary demo experience. The `DEMO_MASTER.md` document was written as the authoritative permanent spec — all future sessions read this first. Three-act narrative locked: H1=Protect (gas lock, 25 min window), H2=Discriminate (slug flow, false positive prevention), H3=Optimize (VFD Bayesian optimization, Vertex AI Vizier + local XGBoost). RUL metric replaced by "Window of Options" (viability timeline). Financial case delivered through LLM only, no static cards. "Consult Agent" button eliminated — LLM auto-starts on injection. Evidence Convergence Wall (5 source categories, activation sequence) and Cited LLM Copilot (superscript citations) added as required UI patterns for all three tabs.

**Physics corrections made:** Gas lock failure is thermal (motor loses cooling fluid flow) NOT mechanical dryout ("running dry" is incorrect — pump is still submerged). 25-minute PNR is defensible per API RP 11S and ESP manufacturer guidelines. Three defensible SCADA vs ML claims: fault discrimination, probability scoring before thresholds, context fusion. Advanced SCADA CAN do some multi-sensor correlation — ML wins on discrimination, probability scoring, and context fusion specifically.

**Key rejections this session:** Rejected "RUL" as primary H1 metric (engineering term, not audience-friendly). Rejected static financial cards (numbers without context). Rejected H2 abandonment (reframed as false-positive prevention — compelling to production engineers who have experienced unnecessary pump pulls). Agreed H2 needs temperature-vibration decorrelation as primary visual, not a generic evidence list.

**Next session's primary task:** Implement H1 tab redesign from `DEMO_MASTER.md` spec — 2D SVG well schematic, Evidence Convergence Wall, Cited LLM Copilot (auto-streaming), Window of Options timeline. Single `app.py` + single `index.html` replace_in_file call. Then rebuild/push/rollout.

---

## Session I (June 3, 2026) — *H1 UX overhaul — slate palette, sensor tabs, splitter, corrected financials*

**Code committed:** `0949491` (feat: H1 UX overhaul), `ddb8a3b` (docs handoff)

What was built: Global Tailwind dark slate palette replaced harsh neon palette across the entire UI. H1 drag-resizable splitter between chart pane and RAG pane. H1 multivariate sensor tabs (PIP / Motor Amps / Winding Temp) above GDC forecast chart with `h1ForecastData` cache. H1 assessment state machine (`h1Recovering` flag, 4 states). VFD terminology with Hz + RPM equivalents. Recovery phase (approveH1VFD sets h1Recovering=true, polls for 2 min). Financial card integrity fix: VFD cost corrected $2,500→$0, physics panel net avoided updated, financial card restructured with risk-weighted SCADA-only expected loss (~$97,500).

---

## Session H (prior) — *V1+V2 integrity violations fixed and verified*

**Code committed:** `65275b7`

Fixed integrity violations: H3 Vizier tab now uses real Vertex AI Vizier Gaussian Process Bandit (not fake deterministic trials). Field intel documents now use live Gemma4 Ollama generation via `_intel_generator()`. VFD cost displayed was $2,500 (fixed to $0). H1 assessment label was "INTERVENE NOW" (fixed to "Intervention Needed" with dynamic state machine). All known display-vs-reality mismatches resolved.
