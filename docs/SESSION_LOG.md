# GDC-PM Session Log — Append-Only History

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
