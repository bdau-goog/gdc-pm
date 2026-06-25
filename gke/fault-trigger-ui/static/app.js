console.log("=== app.js executing ===");
const { createApp } = Vue;

const SITES = {
  pad_alpha: { name:'Pad Alpha',  icon:'🛢', type:'ESP Production',      assets:['ESP-ALPHA-1','ESP-ALPHA-2','ESP-ALPHA-3','ESP-ALPHA-4','ESP-ALPHA-5','ESP-ALPHA-6'] },
  well_bravo:{ name:'Well Bravo', icon:'⚗',  type:'Gas Lift Production', assets:['GLIFT-BRAVO-1','GLIFT-BRAVO-2','GLIFT-BRAVO-3','GLIFT-BRAVO-4'] },
  rig_42:    { name:'Rig 42',     icon:'🔩', type:'Drilling Operations',  assets:['MUD-RIG42-1','MUD-RIG42-2','MUD-RIG42-3','TOPDRIVE-RIG42-1'] },
};
const ASSET_META = {
  'ESP-ALPHA-1':    {label:'ESP-A1',       site:'pad_alpha',  aclass:'esp',      type:'Electrical Submersible Pump'},
  'ESP-ALPHA-2':    {label:'ESP-A2',       site:'pad_alpha',  aclass:'esp',      type:'Electrical Submersible Pump'},
  'ESP-ALPHA-3':    {label:'ESP-A3',       site:'pad_alpha',  aclass:'esp',      type:'Electrical Submersible Pump'},
  'ESP-ALPHA-4':    {label:'ESP-A4',       site:'pad_alpha',  aclass:'esp',      type:'Electrical Submersible Pump'},
  'ESP-ALPHA-5':    {label:'ESP-A5',       site:'pad_alpha',  aclass:'esp',      type:'Electrical Submersible Pump'},
  'ESP-ALPHA-6':    {label:'ESP-A6',       site:'pad_alpha',  aclass:'esp',      type:'Electrical Submersible Pump'},
  'GLIFT-BRAVO-1':  {label:'GLIFT-B1',     site:'well_bravo', aclass:'gas_lift', type:'Gas Lift Well'},
  'GLIFT-BRAVO-2':  {label:'GLIFT-B2',     site:'well_bravo', aclass:'gas_lift', type:'Gas Lift Well'},
  'GLIFT-BRAVO-3':  {label:'GLIFT-B3',     site:'well_bravo', aclass:'gas_lift', type:'Gas Lift Well'},
  'GLIFT-BRAVO-4':  {label:'GLIFT-B4',     site:'well_bravo', aclass:'gas_lift', type:'Gas Lift Well'},
  'MUD-RIG42-1':    {label:'MUD-R42-1',    site:'rig_42',     aclass:'mud_pump', type:'Mud Pump'},
  'MUD-RIG42-2':    {label:'MUD-R42-2',    site:'rig_42',     aclass:'mud_pump', type:'Mud Pump'},
  'MUD-RIG42-3':    {label:'MUD-R42-3',    site:'rig_42',     aclass:'mud_pump', type:'Mud Pump'},
  'TOPDRIVE-RIG42-1':{label:'TD-R42-1',   site:'rig_42',     aclass:'top_drive',type:'Top Drive'},
};
const FAULT_META = {
  // ESP faults
  gas_lock:                     {label:'Gas Lock',                    color:'#f44336',desc:'Gas entrainment — pump efficiency degrading',                    aclass:'esp'},
  slug_flow:                    {label:'Slug Flow',                   color:'#ffb300',desc:'Flowline slugging — surface choke valve backpressure',            aclass:'esp'},
  sand_ingress:                 {label:'Sand Ingress',                color:'#f9a825',desc:'Formation sand erodes impeller stages',                           aclass:'esp'},
  motor_overheat:               {label:'Motor Over-Temp',             color:'#ff6d00',desc:'Winding temp climbs toward insulation failure',                   aclass:'esp'},
  // Gas Lift faults
  valve_failure:                {label:'GLV Failure',                 color:'#e53935',desc:'Gas lift valve stuck closed — injection gas blocked, well loading',aclass:'gas_lift'},
  thermal_runaway:              {label:'Thermal Runaway',             color:'#bf360c',desc:'Compression overheating — manifold temperature exceeding limits',  aclass:'gas_lift'},
  bearing_wear_glift:           {label:'Mandrel Erosion',             color:'#ff8f00',desc:'GLV mandrel erosion — formation sand cutting valve seat',          aclass:'gas_lift'},
  // Mud Pump faults
  pulsation_dampener_failure:   {label:'Dampener Failure',            color:'#ad1457',desc:'Bladder failure — pressure spikes exceed liner rating',            aclass:'mud_pump'},
  valve_washout:                {label:'Valve Washout',               color:'#c62828',desc:'Pump valve seat erosion — fluid bypassing valve, pressure loss',   aclass:'mud_pump'},
  piston_seal_wear:             {label:'Piston Seal Wear',            color:'#e65100',desc:'Liner wear — stroke efficiency declining, fluid bypass',           aclass:'mud_pump'},
  // Top Drive faults
  gearbox_bearing_spalling:     {label:'Gearbox Spalling',            color:'#b71c1c',desc:'Ring gear bearing surface pitting — vibration and torque loss',    aclass:'top_drive'},
  hydraulic_leak:               {label:'Hydraulic Leak',              color:'#e65100',desc:'Swivel seal failure — hydraulic fluid loss, torque limitation',    aclass:'top_drive'},
};
const FAULTS_BY_CLASS = {
  esp:       ['gas_lock','slug_flow','sand_ingress','motor_overheat'],
  gas_lift:  ['valve_failure','thermal_runaway','bearing_wear_glift'],
  mud_pump:  ['pulsation_dampener_failure','valve_washout','piston_seal_wear'],
  top_drive: ['gearbox_bearing_spalling','hydraulic_leak'],
};
const SENSOR_LABELS = {
  esp:       {psi:'Intake Pres. (PSI)',      temp:'Winding Temp (°F)',  vib:'Vibration (mm/s)',          s4:'Motor Current (A)'},
  gas_lift:  {psi:'Casing Pressure (PSI)',   temp:'Wellhead Temp (°F)', vib:'Valve Vibration (mm/s)',    s4:null},
  mud_pump:  {psi:'Standpipe Pres. (PSI)',   temp:'Fluid Temp (°F)',    vib:'Pump Vibration (mm/s)',     s4:'Stroke Rate (SPM)'},
  top_drive: {psi:'Hydraulic Pres. (PSI)',   temp:'Gearbox Temp (°F)',  vib:'Torque Oscillation (mm/s)',s4:null},
};
const DEMO_SCENARIOS = [
  {id:'demo_sand_ingress',name:'Sand Ingress — Supply Chain Lead Time',horizon:'Days',assetId:'ESP-ALPHA-2',faultType:'sand_ingress',faultLabel:'Sand Ingress',description:'GDC detects sand production 14 days early. SCADA sees nothing. Lab report & shift notes fused with vibration trend — SAP order must be placed today.',costAvoided:85000,dataFusion:'Lab Report + Shift Notes + Vibration',durationSec:3600},
  {id:'demo_motor_overheat',name:'Motor Over-Temp — ESP Emergency',horizon:'Hours',assetId:'ESP-ALPHA-4',faultType:'motor_overheat',faultLabel:'Motor Over-Temp',description:'67% water cut degrading downhole motor cooling. Winding temp rising at +2.1A/hr. Class H insulation failure in 18h — SCADA sees nothing until 280°F.',costAvoided:200000,dataFusion:'VFD Power Monitor + Well Test Report',durationSec:1800},
  {id:'demo_gas_lock',name:'Gas Lock — SCADA Autonomous Control',horizon:'Minutes',assetId:'ESP-ALPHA-1',faultType:'gas_lock',faultLabel:'Gas Lock',description:'Gas void fraction rising in pump intake — intake PSI declining. PNR: 25 minutes. VFD frequency adjustment available via SCADA. Sub-minute edge response.',costAvoided:150000,dataFusion:'VFD Control + SCADA Historian',durationSec:900},
];

createApp({
  data() {
    return {
      mainTab: 'intro',
      archPane: 'overview',
      archInfoOpen: false,
      currentView: 'dashboard',
      
      // Horizon 3 (Bayesian Optimization Game)
      oilPriceSlider: 112,
      horizonSlider: 90,
      vfdFrequencySlider: 50.0,
      optTrials: [],
      optOptimalHz: null,
      optOptimalCashFlow: null,
      optScadaNominal: {},
      optRunToFailure: {},
      optVizierOptimal: {},
      optWells: [],
      optJointOptimal: {},
      optIndependentBaseline: {},
      optConstraintStack: {},
      h3ActiveConstraint: 'gas',
      constraintDoc: {},
      optCurtailment: {},
      vizierDeployed: false,
      vizierDeploying: false,
      
      // Horizon 1 State
      h1Injected: false,
      h1Resolved: false,
      h1SensorPsi: null,
      h1SensorTemp: null,
      h1SensorAmps: null,
      h1HealthScore: null,
      h1FeedItems: [],
      h1GemmaFinding: '',
      h1ForecastData: null,
      h1RawPsi: null,
      h1RawAmps: null,
      h1RawTemp: null,
      h1RawVib: null,
      h1EnvelopeHistory: [],
      h1PumpOffExcluded: false,
      h1GasLockExcluded: false,
      h1FaultType: '',
      h1Seized: false,
      h1SensorVib: null,
      h1PhasePlaneHistory: [],
      h1DetectionTime: null,
      h1AdvisorLastFeedId: null,
      h1AdvisorLastContextTime: 0,
      h1AdvisorUpdateTimers: [],
      h1ActiveSensor: 'psi',
      h1Recovering: false,
      h1Dragging: false,
      h1BriefingMode: true,     // true=show animated briefing panels; false=scenario replay
      h1BriefingPanel: 1,       // 1=This Well, 2=What is an Unload? (panels 3-6 in Sprint 2b-2e)
      introSlide: 0,            // 0-2: current intro slide index (kept; unused after iframe migration)
      h1P2Scrub: 0,             // 0=nominal → 100=fault; Panel 2 scrubber (resets on panel change)
      h1P3Scrub: 0,             // 0=nominal → 100=fault; Panel 3 scrubber (resets on panel change)
      h1SplitPercent: 56,
      h1ChartH: 140,
      h1DegPollTimer: null,
      h1LivePollTimer: null,
      // H1 Session L State — Comparative Detection Scenario
      h1SelectedWell: 'ESP-ALPHA-1', // well whose telemetry is shown in left column
      h1TargetWell: null,            // randomly injected alerting well
      h1NuisanceWells: [],           // benign disturbance wells (2 adjacent)
      h1RampSpeed: 'standard',       // 'standard' (900s) | 'accelerated' (300s)
      h1WellData: {},                // per-well telemetry cache
      h1ConsoleTab: 'scada',        // 'scada' | 'gdc' — which decision console sub-tab is shown
      h1RagRevealed: false,         // true when GDC's pgvector RAG document has been retrieved
      h1RagDoc2Shown: false,        // GOR Lab Test card (revealed ~2s after RAG)
      h1RagDoc3Shown: false,        // OEM Guide card (revealed ~3.5s after RAG)
      h1RagDoc2Timer: null,         // setTimeout handle for doc 2
      h1RagDoc3Timer: null,         // setTimeout handle for doc 3
      h1ShiftNoteModalOpen: false,  // click-through Shift Handover Note modal
      h1SonicLogModalOpen: false,   // click-through Acoustic Sonic Log modal
      h1GorModalOpen: false,        // click-through GOR/Separator Lab Report modal
      h1RagDoc3ModalOpen: false,    // click-through OEM Manual / RAG doc 3 modal (Sprint L2)
      h2DocModalOpen: false,        // click-through H2 scenario document modal (Sprint L2)
      h2DocModalItem: null,         // active H2 doc {title, text, source}
      h1OverrideModalOpen: false,   // GDC override confirmation modal (VFD trim during drawdown)
      h1ShowEvidenceTable: false,   // toggle Bayesian evidence table in Zone 1 verdict
      // Legacy evidence wall state — kept as h1EvidenceActive counter drives h1RagRevealed via watcher
      h1EvidenceWall: [
        {active: false, content: '', cat: 'Telemetry',    icon: '📡'},
        {active: false, content: '', cat: 'Field Note',   icon: '📋'},
        {active: false, content: '', cat: 'Lab Report',   icon: '🧪'},
        {active: false, content: '', cat: 'Acoustic Log', icon: '📊'},
        {active: false, content: '', cat: 'Guidelines',   icon: '📖'},
      ],
      h1EvidenceActive: 0,
      h1AdvisorHtml: '',
      h1AdvisorStreaming: false,
      h1AdvisorTimer: null,
      h1AdvisorText: '',
      h1RulHistory: [],
      h1FeedPollInterval: null,
      h1ChatInput: '',
      h1ChatMessages: [],
      h1InjectedAt: null,
      h1ElapsedMin: 0,
      h1WindowTotal: null, // Per-run thermal window (minutes) captured at first non-null forecast poll — varies every inject
      h1TopClass: null,
      h1TopClassProb: null,
      h1GvfPct: null,
      h1ElapsedTimer: null,
      h1OptA: 'wopt-viable',
      h1OptALabel: 'VIABLE',
      h1OptB: 'wopt-viable',
      h1OptBLabel: 'VIABLE',
      h1RecoveryMsg: '',
      h1RecoveryPollTimer: null,

      // ── H1 Scenario Replay state (Session Q rebuild) ──────────────────────
      h1ReplayData: null,           // full trajectory from /api/h1/scenario-replay
      h1ReplayLoading: false,       // API fetch in progress
      h1ScadaRuleFired: '',         // "Rate-of-change…" or "Static underload…" from backend
      h1CursorIdx: 0,               // scrubber position (0..N-1)
      h1Playing: false,             // auto-advance timer running
      h1PlayTimer: null,            // setInterval handle
      h1FaultTypeRevealed: false,   // true once cursor >= gdc_detect_idx
      h1RagRevealTimer: null,       // setTimeout for 1.5s RAG reveal after GDC detect
      h1RagPending: false,          // true when detect fired while paused; reveal deferred to play resume

      // Horizon 2 State
      h2Injected: false,
      h2Resolved: false,
      h2SensorVib: null,
      h2SensorTemp: null,
      h2TruckRollDispatched: false,
      h2TruckRollCountdown: 5,
      h2FeedItems: [],
      h2GemmaFinding: '',
      h2TruckRollInterval: null,
      h2DegPollTimer: null,

      // ── H2 Scenario Replay state (Session V) ─────────────────────────────
      h2ReplayData: null,          // full trajectory from /api/h2/scenario-replay
      h2ReplayLoading: false,      // API fetch in progress
      h2CursorIdx: 0,              // scrubber position (0..N-1)
      h2Playing: false,            // auto-advance timer running
      h2PlayTimer: null,           // setInterval handle
      h2VerdictRevealed: false,    // true once cursor >= gdc_detect_idx (+1.5s)
      h2RagDoc2Shown: false,       // OEM Matrix (+2s after verdict revealed)
      h2RagDoc3Shown: false,       // Prior Pull Record (+3.5s after verdict revealed)
      h2RagDoc4Shown: false,       // Field Tour Note (+5s after verdict revealed)
      h2RagDoc5Shown: false,       // Well History (+6.5s after verdict revealed)
      h2RagRevealTimer: null,      // setTimeout for 1.5s delay after GDC detect
      h2RagDoc2Timer: null,
      h2RagDoc3Timer: null,
      h2RagDoc4Timer: null,
      h2RagDoc5Timer: null,
      h2ConsoleTab: 'scada',       // 'scada' | 'gdc'
      h2SplitPercent: 56,          // left column width %
      h2PullOutcome: null,         // 'false_positive' if SCADA path chose pump pull
      h2BriefingMode: true,        // true=show 3-panel briefing; false=scenario replay
      h2BriefingPanel: 1,          // 1=The Equipment, 2=The Provenance Hook, 3=The Decision
      h3BriefingMode: true,        // true=show 3-panel briefing; false=optimization dashboard
      h3BriefingPanel: 1,          // 1=The Opportunity, 2=The Tradeoff, 3=The Optimization

      // Physics & Logic Info Panel state (Fix 10)
      showH1Info: false,
      showH2Info: false,
      showH3Info: false,
      
      // Horizon 2 Truck Roll State (legacy compat)
      truckRollDispatched: false,
      truckRollTimer: 0,
      truckRollInterval: null,
      truckRollComplete: false,
      horizonAlerts: [],
      kpis: {},
      mlops: {},
      lastRefresh: '--:--:--',
      activeDegradesMap: {},
      selectedAsset: null,
      SITES, ASSET_META, FAULT_META, FAULTS_BY_CLASS,
      demoScenarios: DEMO_SCENARIOS,
      // Deep Dive
      ddAssetId: null,
      ddFaultType: null,
      degStatus: null,
      lastSensorVals: {psi:null,temp:null,vib:null,s4:null},
      lastSensorPrev: {psi:null,temp:null,vib:null,s4:null},
      chartData: null,
      activeTab: 'psi',
      selectedFaultForInjection: null,
      injectDuration: 3600,
      injectionRunning: false,
      // Injection event popup (shows drawn params vs bounds for 5s on every inject)
      injectionPopupVisible: false,
      injectionPopupData: null,
      // Injection event log (reviewable history from /api/injection-log)
      injectionLogItems: [],
      injectionLogOpen: false,
      // Feed
      feedItems: [],
      visibleFeedCount: 0,
      gemmaFinding: '',
      feedAnimTimer: null,
      feedModalOpen: false,
      feedModalItem: null,
      // Agent
      agentMessages: [{role:'system', content:'Select a fault type, inject, then consult the Operations Agent.'}],
      agentTyping: false,
      agentTypingText: '',
      agentInput: '',
      chatHistory: [],
      hitlAction: null,
      hitlOutcome: null,
      remediationTiers: null,   // loaded from /api/resolution-actions
      selectedTierKey: null,    // which tier user clicked
      // Craft Fault Modal
      craftModalOpen: false,
      craftFaultType: null,
      craftDuration: 3600,
      // Cost Justification Modal
      justifyModalOpen: false,
      justifyData: null,
      // Financials
      ledger: [],
      totalSaved: 0,
      fleetUptime: 100.0,
      // Telemetry
      grafanaLoaded: false,
      // Copilot Resize
      copilotHeight: 360,
      // Timers
      _pollKpis: null, _pollHorizon: null, _pollMlops: null,
      _pollDeg: null, _pollChart: null,
      // Phase 15 — Asset Context Menu + Splitter
      assetContextMenu: { visible: false, x: 0, y: 0, assetId: null },
      faultTooltipFt: null,
      faultTooltipData: null,
      activityStreamWidth: 340,
      // Session 9 — Deep Dive vertical layout
      showAiFactors: false,      // toggles the AI input factors popover on the GDC chart
      // initialRulMap: per-asset map of original advance notice — persists across navigation
      // so that when you go to fleet and back, the original advance notice is preserved
      initialRulMap: {},
      // Sprint 5 v7: Side-by-side layout — chart column width (EW) and right panel heights (NS)
      compareColWidth: (() => { try { const v=sessionStorage.getItem('gdc_compareColWidth'); return v ? parseInt(v,10) : 720; } catch { return 720; } })(),
      intelPanelHeight: (() => { try { const v=sessionStorage.getItem('gdc_intelPanelHeight'); return v ? parseInt(v,10) : 260; } catch { return 260; } })(),
      agentPanelHeight: (() => { try { const v=sessionStorage.getItem('gdc_agentPanelHeight'); return v ? parseInt(v,10) : 280; } catch { return 280; } })(),
      gdcPanelHeight: (() => {
        try { const v = sessionStorage.getItem('gdc_gdcPanelHeight'); return v ? parseInt(v, 10) : 0; } catch { return 0; }
      })(),   // Sprint 5 v4: 0 = equal flex:1 split; >0 = explicit px for GDC AI chart
      // Sprint 4: Pad Alpha Digital Twin — no runtime state needed (integrated V1 only)
    };
  },

  computed: {
    wellsSortedByGor() {
      return [...(this.optWells||[])].sort((a,b) => a.gor_scf_bbl - b.gor_scf_bbl);
    },
    availableFaults() {
      if (!this.ddAssetId || !ASSET_META[this.ddAssetId]) return [];
      return FAULTS_BY_CLASS[ASSET_META[this.ddAssetId].aclass] || [];
    },
    visibleFeedItems() { return this.feedItems.slice(0, this.visibleFeedCount); },
    sensor4Label() {
      if (!this.ddAssetId) return null;
      return SENSOR_LABELS[ASSET_META[this.ddAssetId]?.aclass]?.s4 || null;
    },
    sensor4TabKey() {
      if (!this.ddAssetId) return null;
      const cls = ASSET_META[this.ddAssetId]?.aclass;
      if (cls === 'esp') return 'amps';
      if (cls === 'mud_pump') return 'spm';
      return null;
    },
    injectProgressPct() {
      if (!this.degStatus?.is_active) return 0;
      return Math.round((1 - (this.degStatus.health_score || 1)) * 100);
    },
    // ── AI input factors — sensor labels for the active fault type ────────────
    // Used by the ⓘ popover on the GDC AI chart header to list what the XGBoost
    // model is reading. No LLM involved — these are purely numerical sensor inputs.
    aiFactors() {
      if (!this.ddFaultType) return [];
      const ac = FAULT_META[this.ddFaultType]?.aclass || (ASSET_META[this.ddAssetId]?.aclass);
      if (!ac) return [];
      const labels = SENSOR_LABELS[ac] || {};
      return [labels.psi, labels.temp, labels.vib, labels.s4].filter(Boolean);
    },
    // ── Bridge bar percentage — how much lead time is remaining vs initial ────
    // Uses per-asset initialRulMap so navigating away and back doesn't reset it.
    bridgeBarPct() {
      if (!this.degStatus?.time_to_scada_minutes) return 100;
      const initial = this.ddAssetId ? this.initialRulMap[this.ddAssetId] : null;
      if (!initial) return 100;
      return Math.min(100, Math.max(2, Math.round(
        (this.degStatus.time_to_scada_minutes / initial) * 100
      )));
    },
    // ── Convenience getter for current asset's initial RUL (used in template) ──
    initialRulMinutes() {
      return this.ddAssetId ? (this.initialRulMap[this.ddAssetId] || null) : null;
    },
  },

  watch: {
    h1BriefingPanel() {
      this.h1P2Scrub = 0;
      this.h1P3Scrub = 0;
    },
    h1FeedItems(newVal, oldVal) {
      if (!this.h1Injected || this.h1Resolved || this.h1AdvisorStreaming) return;
      if (newVal.length > 0 && oldVal && oldVal.length > 0 && newVal[0].id !== oldVal[0]?.id) {
        this._triggerAdvisoryUpdate('feed', newVal[0]);
      }
    },
    h1OptALabel(newVal, oldVal) {
      if (!this.h1Injected || this.h1Resolved) return;
      if (oldVal === 'VIABLE' && newVal === 'MARGINAL') this._triggerAdvisoryUpdate('urgency', null);
      else if (oldVal === 'MARGINAL' && newVal === 'EXPIRED') this._triggerAdvisoryUpdate('critical', null);
    },
    h1EvidenceActive(val) {
      // When the second evidence item activates (2s after injection), GDC has retrieved its RAG document
      if (val >= 2 && !this.h1RagRevealed) {
        this.h1RagRevealed = true;
        // Backcompat: set the old exclusion flags (used in status banner logic)
        if (this.h1FaultType === 'fluid_drawdown') {
          this.h1GasLockExcluded = true;
        } else if (this.h1FaultType === 'gas_lock') {
          this.h1PumpOffExcluded = true;
        }
      }
    },
    // When transport resumes, fire any deferred RAG reveal (e.g. paused at gdc_detect_idx for B1-S2)
    h1Playing(val) {
      if (val && this.h1RagPending && this.h1FaultTypeRevealed && !this.h1RagRevealed) {
        this.h1RagPending = false;
        if (this.h1RagRevealTimer) clearTimeout(this.h1RagRevealTimer);
        this.h1RagRevealTimer = setTimeout(() => { this._h1DoRagReveal(); }, 1500);
      }
    },
    // ── Scenario Replay: advance state when cursor crosses detection thresholds ──
    h1CursorIdx(val) {
      if (!this.h1ReplayData) return;
      // ── Scrub BACK past GDC detect → undo all revealed state ─────────────────
      if (val < this.h1ReplayData.gdc_detect_idx && this.h1FaultTypeRevealed) {
        if (this.h1RagRevealTimer) { clearTimeout(this.h1RagRevealTimer); this.h1RagRevealTimer = null; }
        if (this.h1RagDoc2Timer)   { clearTimeout(this.h1RagDoc2Timer);   this.h1RagDoc2Timer   = null; }
        if (this.h1RagDoc3Timer)   { clearTimeout(this.h1RagDoc3Timer);   this.h1RagDoc3Timer   = null; }
        this.h1FaultTypeRevealed  = false;
        this.h1RagRevealed        = false;
        this.h1RagPending         = false;
        this.h1RagDoc2Shown       = false;
        this.h1RagDoc3Shown       = false;
        this.h1EvidenceActive     = 0;
        this.h1ShowEvidenceTable  = false;
        this.h1PumpOffExcluded    = false;
        this.h1GasLockExcluded    = false;
        // Note: h1FaultType intentionally kept (already drawn from replay data);
        // resetting it would cause the SVG wellbore to flicker during scrub.
      }
      // Cross GDC detect threshold → reveal fault type on GDC Advisor + schedule RAG reveal (1.5s)
      if (!this.h1FaultTypeRevealed && val >= this.h1ReplayData.gdc_detect_idx) {
        this.h1FaultTypeRevealed = true;
        this.h1FaultType = this.h1ReplayData.fault_type;
        if (this.h1RagRevealTimer) clearTimeout(this.h1RagRevealTimer);
        if (this.h1Playing) {
          // Transport running → reveal RAG after 1.5s (normal playback behavior)
          this.h1RagRevealTimer = setTimeout(() => { this._h1DoRagReveal(); }, 1500);
        } else {
          // Transport paused → hold amber "Retrieving" state until play resumes (B1-S2 recording window)
          this.h1RagPending = true;
        }
      }
      // Update Plotly cursor line via relayout (shape index 1 = cursor; shape[0] = alarm marker)
      this._updateH1ReplayCursor(val);
    },

    // H2 Scenario Replay: advance state when cursor crosses detection thresholds
    h2CursorIdx(val) {
      if (!this.h2ReplayData) return;
      // Cross GDC detect threshold → reveal verdict + schedule sequential doc reveals
      if (!this.h2VerdictRevealed && val >= this.h2ReplayData.gdc_detect_idx) {
        if (this.h2RagRevealTimer) clearTimeout(this.h2RagRevealTimer);
        this.h2RagRevealTimer = setTimeout(() => {
          this.h2VerdictRevealed = true;
          if (this.h2RagDoc2Timer) clearTimeout(this.h2RagDoc2Timer);
          if (this.h2RagDoc3Timer) clearTimeout(this.h2RagDoc3Timer);
          if (this.h2RagDoc4Timer) clearTimeout(this.h2RagDoc4Timer);
          if (this.h2RagDoc5Timer) clearTimeout(this.h2RagDoc5Timer);
          this.h2RagDoc2Timer = setTimeout(() => { this.h2RagDoc2Shown = true; }, 2000);
          this.h2RagDoc3Timer = setTimeout(() => { this.h2RagDoc3Shown = true; }, 3500);
          this.h2RagDoc4Timer = setTimeout(() => { this.h2RagDoc4Shown = true; }, 5000);
          this.h2RagDoc5Timer = setTimeout(() => { this.h2RagDoc5Shown = true; }, 6500);
        }, 1500);
      }
      // Update Plotly cursor line (shape index 2 in h2-replay-chart)
      if (this.h2ReplayData) {
        const t = this.h2ReplayData.t_min[val] || 0;
        try { Plotly.relayout('h2-replay-chart', { 'shapes[2].x0': t, 'shapes[2].x1': t }); } catch {}
      }
    },
  },

  methods: {
    // ── H1 RAG reveal helper — called by timer whether triggered live or deferred ──
    _h1DoRagReveal() {
      this.h1RagRevealed = true;
      this.h1EvidenceActive = 2; // triggers h1EvidenceActive watcher → sets exclusion flags
      // Sequential doc reveals: GOR Lab Test at +2s, OEM Guide at +3.5s
      if (this.h1RagDoc2Timer) clearTimeout(this.h1RagDoc2Timer);
      if (this.h1RagDoc3Timer) clearTimeout(this.h1RagDoc3Timer);
      this.h1RagDoc2Timer = setTimeout(() => { this.h1RagDoc2Shown = true; }, 2000);
      this.h1RagDoc3Timer = setTimeout(() => { this.h1RagDoc3Shown = true; }, 3500);
    },
    openDeepDive(assetId, faultType) {
      this.ddAssetId = assetId;
      this.ddFaultType = faultType;
      this.selectedFaultForInjection = faultType;
      this.currentView = 'deepdive';
      this.activeTab = 'psi';
      this.chartData = null;
      this.feedItems = [];
      this.visibleFeedCount = 0;
      this.gemmaFinding = '';
      this.agentMessages = [{role:'system', content:`Analyzing ${assetId}. Inject a fault to activate the Operations Agent.`}];
      this.hitlAction = null;
      this.hitlOutcome = null;
      this.chatHistory = [];
      this.selectedAsset = null;
      this.remediationTiers = null;
      this.selectedTierKey = null;
      const dg = this.activeDegradesMap[assetId];
      if (dg && dg.fault_type === faultType) {
        this.injectionRunning = true;
        this.fetchDegradeStatus();
        this.fetchForecastData();
        this.fetchIntelligenceFeed();
      } else {
        this.injectionRunning = false;
        // Clear the initial RUL for this asset only when no active fault
        // (if there IS an active fault, preserve the original advance notice)
        if (!dg) {
          const m = {...this.initialRulMap};
          delete m[assetId];
          this.initialRulMap = m;
        }
      }
      this.startDegPoll();
      this.$nextTick(() => { this.initCompareColResize(); this.initRowResizers(); this.initGdcScadaResize(); });
    },
    backToDashboard() {
      this.currentView = 'dashboard';
      this.stopDegPoll();
      if (this.feedAnimTimer) { clearInterval(this.feedAnimTimer); this.feedAnimTimer = null; }
      // Purge both charts — SCADA must also be purged or it leaves stale Plotly state
      Plotly.purge('forecast-chart');
      Plotly.purge('scada-chart');
      this.chartData = null;
      // NOTE: initialRulMap is intentionally NOT cleared here.
      // When the user returns to this deep dive while the fault is still active,
      // the original advance notice (time from first detection) will be preserved.
    },
    launchScenario(sc) {
      this.openDeepDive(sc.assetId, sc.faultType);
      setTimeout(() => {
        this.selectedFaultForInjection = sc.faultType;
        this.injectDuration = sc.durationSec;
        this.injectFault();
      }, 400);
    },
    selectAsset(assetId) { this.selectedAsset = this.selectedAsset === assetId ? null : assetId; },

    hasAlert(siteId) { return this.horizonAlerts.some(a => a.site === siteId); },
    isAssetActive(assetId) { return !!this.activeDegradesMap[assetId]; },
    getAssetHealthClass(assetId) {
      const dg = this.activeDegradesMap[assetId];
      if (!dg) return 'health-green';
      const hs = dg.health_score ?? 1.0;
      if (hs >= 0.8) return 'health-green';
      if (hs >= 0.3) return 'health-amber';
      return 'health-red';
    },
    formatSiteName(siteId) { return SITES[siteId]?.name || siteId; },
    faultsForAsset(assetId) { return FAULTS_BY_CLASS[ASSET_META[assetId]?.aclass] || []; },
    assetTypeLabel(assetId) { return ASSET_META[assetId]?.type || ''; },
    alertsForGroup(group) { return this.horizonAlerts.filter(a => a.horizon_label === group); },
    urgencyColor(group) { return group==='Minutes'?'#f44336':group==='Hours'?'#ff6d00':'#ffb300'; },
    interventionLabel(itype) {
      const map = {supply_chain:'SAP Supply Chain',maintenance_scheduling:'Maximo Scheduling',operational_control:'Pason EDR Control',emergency_shutdown:'Emergency Shutdown'};
      return map[itype] || itype;
    },
    formatRul(mins, group) {
      if (mins===null||mins===undefined) return '—';
      if (group==='Minutes'||mins<60) return `${Math.round(mins)}m to SCADA`;
      if (group==='Days'||mins>=1440) return `${(mins/1440).toFixed(1)}d to SCADA`;
      return `${(mins/60).toFixed(1)}h to SCADA`;
    },
    formatRulFull(mins) {
      if (mins===null||mins===undefined) return '—';
      if (mins<60) return `${Math.round(mins)} min`;
      if (mins<1440) return `${(mins/60).toFixed(1)}h`;
      return `${(mins/1440).toFixed(1)} days`;
    },
    formatTs(ts) {
      if (!ts) return '—';
      try { return new Date(ts).toLocaleString('en-US',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}); } catch { return ts; }
    },

    sensorLabel(sensor) { return (SENSOR_LABELS[ASSET_META[this.ddAssetId]?.aclass] || {})[sensor] || sensor.toUpperCase(); },
    sensorTabLabel(sensor) {
      const full = (SENSOR_LABELS[ASSET_META[this.ddAssetId]?.aclass] || {})[sensor] || sensor;
      if (sensor==='psi') return full.includes('Pres') ? 'Pressure' : 'PSI';
      if (sensor==='temp') return 'Temperature';
      if (sensor==='vib') return 'Vibration';
      return full;
    },
    sensorTabPrimary(sensor) { return this.degStatus?.primary_sensor === sensor; },
    isSensorAnomaly(sensor) {
      if (!this.injectionRunning || !this.degStatus?.is_active) return false;
      const primary = this.degStatus?.primary_sensor;
      if (!primary) return true;
      if (sensor === 's4') return primary === this.sensor4TabKey;
      return primary === sensor;
    },
    sensorTrend(sensor) {
      const curr = this.lastSensorVals[sensor], prev = this.lastSensorPrev[sensor];
      if (curr===null||prev===null) return 'stable';
      const diff = parseFloat(curr) - parseFloat(prev);
      if (Math.abs(diff) < 0.01*Math.abs(parseFloat(curr)||1)) return 'stable';
      return diff > 0 ? 'up' : 'down';
    },
    sensorTrendArrow(sensor) { const t=this.sensorTrend(sensor); return t==='up'?'↑':t==='down'?'↓':'—'; },

    async fetchKpis() { try { const r=await fetch('/api/kpis'); if(r.ok){const d=await r.json();this.kpis=d.kpis;} } catch{} },
    async fetchHorizonAlerts() {
      try {
        const r=await fetch('/api/horizon');
        if(r.ok){const d=await r.json();this.horizonAlerts=d.alerts||[];
          const dr=await fetch('/api/degrade-status'); if(dr.ok){const dd=await dr.json();this.activeDegradesMap=dd.active||{};}
        }
      } catch{}
    },
    async fetchMlopsStatus() { try { const r=await fetch('/api/mlops/status'); if(r.ok){const d=await r.json();this.mlops=d;} } catch{} },
    async fetchDegradeStatus() {
      if(!this.ddAssetId) return;
      try {
        const r=await fetch(`/api/degrade-status/${this.ddAssetId}`);
        if(r.ok){
          const d=await r.json();
          this.degStatus=d;
          if(d.is_active&&d.fault_type) this.ddFaultType=d.fault_type;
          // Capture initial RUL when the fault first becomes active for bridge bar baseline
          // Stored per-asset so navigating away and back preserves the original advance notice
          if(!this.initialRulMap[this.ddAssetId] && d.is_active && d.time_to_scada_minutes > 0) {
            this.initialRulMap = {...this.initialRulMap, [this.ddAssetId]: d.time_to_scada_minutes};
          }
        }
      } catch{}
    },
    async fetchForecastData() {
      if(!this.ddAssetId) return;
      try {
        const r=await fetch(`/api/plot/forecast-data/${this.ddAssetId}`);
        if(r.ok){const d=await r.json();
          if(d.sensors&&Object.keys(d.sensors).length>0){
            this.chartData=d;
            if(d.primary_sensor&&!this._tabManuallySelected) this.activeTab=d.primary_sensor;
            this.updateSensorVals(d);
            this.renderChart();
          }
        }
      } catch{}
    },
    async fetchIntelligenceFeed() {
      if(!this.ddAssetId||!this.ddFaultType) return;
      try {
        const r=await fetch(`/api/intelligence-feed/${this.ddAssetId}?fault_type=${this.ddFaultType}`);
        if(r.ok){const d=await r.json();this.feedItems=d.items||[];this.gemmaFinding=d.gemma_finding||'';this.visibleFeedCount=0;this.startFeedAnimation();}
      } catch{}
    },
    async fetchLedger() {
      try {
        const [lr,sr]=await Promise.all([fetch('/api/ledger'),fetch('/api/savings')]);
        if(lr.ok){const d=await lr.json();this.ledger=d.events||[];}
        if(sr.ok){const d=await sr.json();this.totalSaved=Math.round(d.total_savings||0);}
        this.fleetUptime=this.ledger.length===0?100.0:Math.max(85,(100-this.ledger.length*0.5)).toFixed(1);
      } catch{}
    },
    async fetchRemediationTiers() {
      if(!this.ddFaultType) return;
      try {
        // Use AI Fusion adjusted RUL if available, otherwise fall back to base RUL
        const rul = this.degStatus?.adjusted_rul_minutes ?? this.degStatus?.time_to_scada_minutes ?? 60;
        const r=await fetch(`/api/resolution-actions/${this.ddFaultType}?rul_minutes=${rul}`);
        if(r.ok){const d=await r.json();this.remediationTiers=d.actions||null;}
      } catch{}
    },

    updateSensorVals(d) {
      const cls=ASSET_META[this.ddAssetId]?.aclass;
      const getLastY=(sensor)=>{const s=d.sensors?.[sensor];if(!s||!s.traces||!s.traces[0])return null;const ys=s.traces[0].y;return ys&&ys.length?ys[ys.length-1].toFixed(sensor==='vib'?3:1):null;};
      this.lastSensorPrev={...this.lastSensorVals};
      this.lastSensorVals={psi:getLastY('psi'),temp:getLastY('temp'),vib:getLastY('vib'),s4:cls==='esp'?getLastY('amps'):cls==='mud_pump'?getLastY('spm'):null};
    },
    renderChart() {
      if(!this.chartData?.sensors) return;
      const s=this.chartData.sensors[this.activeTab];
      if(!s) return;
      // ── Build gdcLayout FIRST (hoisted to outer scope so SCADA block can access it) ──
      const gdcLayout = JSON.parse(JSON.stringify(s.layout));
      // Override layout to ensure dark background and no padding issues
      gdcLayout.paper_bgcolor = '#131d31';
      gdcLayout.plot_bgcolor  = '#131d31';
      gdcLayout.margin = gdcLayout.margin || {l:48,r:10,t:10,b:36};
      if (gdcLayout.annotations) {
        gdcLayout.annotations = gdcLayout.annotations.filter(a =>
          !((a.text || '').toLowerCase().includes('scada alarm') ||
            (a.text || '').toLowerCase().includes('scada a'))
        );
      }
      // ── GDC Edge AI chart — full projection + RUL markers ──────────────────
      const elGdc=document.getElementById('forecast-chart');
      if(elGdc) {
        Plotly.react(elGdc, s.traces, gdcLayout, {displayModeBar:false, responsive:true})
              .catch(()=>Plotly.newPlot(elGdc, s.traces, gdcLayout, {displayModeBar:false, responsive:true}));
      }
      // ── SCADA chart — historical data only, stops at NOW ───────────────────
      // Shows only what traditional SCADA sees: the live telemetry line and the
      // hard alarm threshold. No projection. No AI inference. No future markers.
      // Both X and Y axes are locked to match the GDC chart for visual alignment.
      const elScada=document.getElementById('scada-chart');
      if(elScada && s.traces && s.traces.length > 0) {
        // Robust trace filter: accept telemetry and threshold lines by name
        // (case-insensitive). Falls back to first trace + any non-fill line.
        let scadaTraces = s.traces.filter(t => {
          const n = (t.name || '').toLowerCase().trim();
          return n.includes('telemetry') || n.includes('threshold') ||
                 n.includes('alarm') || n.includes('historical') || n.includes('live');
        });
        // Fallback: take first trace (historical) plus any non-fill trace (threshold line)
        if (scadaTraces.length === 0) {
          scadaTraces = s.traces.slice(0, 1).concat(
            s.traces.filter((t, i) => i > 0 && !t.fill)
          );
        }
        // Deep-copy traces, trim to historical data only (x up to last real value)
        const histX = s.traces[0]?.x || [];
        const nowIdx = histX.length - 1;
        scadaTraces = scadaTraces.map(t => {
          const tc = {...t, x: t.x, y: t.y};
          // For scatter/line traces that have projection data, slice to nowIdx
          if (tc.mode && tc.mode.includes('lines') && tc.x && tc.x.length > nowIdx + 1 && !tc.name?.toLowerCase().includes('threshold') && !tc.name?.toLowerCase().includes('alarm')) {
            tc.x = tc.x.slice(0, nowIdx + 1);
            tc.y = tc.y.slice(0, nowIdx + 1);
          }
          return tc;
        });
        const scadaLayout = {
          paper_bgcolor: '#131d31',
          plot_bgcolor:  '#131d31',
          margin: {l:48, r:10, t:8, b:36},
          font: {color: '#a0b0c0', size: 11},
          xaxis: {
            ...(gdcLayout.xaxis || {}),
            range: gdcLayout.xaxis?.range,
            autorange: !gdcLayout.xaxis?.range,
            gridcolor: '#1e2a38',
            linecolor: '#1e2a38',
          },
          yaxis: {
            ...(gdcLayout.yaxis || {}),
            range: gdcLayout.yaxis?.range,
            autorange: !gdcLayout.yaxis?.range,
            gridcolor: '#1e2a38',
            linecolor: '#1e2a38',
          },
          showlegend: false,
          annotations: [],
          shapes: [],
        };

        // Add 'SCADA Blind Spot' to the empty future space if the AI chart projects into the future
        if (histX.length > 0 && gdcLayout.xaxis?.range && new Date(gdcLayout.xaxis.range[1]) > new Date(histX[nowIdx])) {
          scadaLayout.shapes.push({
            type: 'rect',
            xref: 'x', yref: 'paper',
            x0: histX[nowIdx], x1: gdcLayout.xaxis.range[1],
            y0: 0, y1: 1,
            fillcolor: 'rgba(255, 109, 0, 0.05)',
            line: { width: 0 }
          });
          
          scadaLayout.annotations.push({
            x: new Date((new Date(histX[nowIdx]).getTime() + new Date(gdcLayout.xaxis.range[1]).getTime()) / 2).toISOString(),
            y: 0.5,
            xref: 'x', yref: 'paper',
            text: '<b>SCADA BLIND SPOT</b>',
            showarrow: false,
            font: { color: 'rgba(255, 109, 0, 0.4)', size: 16, family: 'JetBrains Mono' }
          });
        }
        // Always purge and redraw to prevent Plotly "no-resize" blank state
        Plotly.purge(elScada);
        Plotly.newPlot(elScada, scadaTraces, scadaLayout, {displayModeBar:false, responsive:true})
          .then(() => { try { Plotly.Plots.resize(elScada); } catch(e){} });
      }
    },
    selectTab(tab) { this.activeTab=tab; this._tabManuallySelected=true; this.renderChart(); },

    async injectFault() {
      if(!this.selectedFaultForInjection||!this.ddAssetId) return;
      try {
        const r=await fetch('/api/inject/degrade',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({asset_id:this.ddAssetId,fault_type:this.selectedFaultForInjection,duration_seconds:this.injectDuration})});
        if(r.ok){
          const _injD = await r.json();
          if (_injD.injection_params) this.showInjectionPopup(_injD.injection_params);
          this.ddFaultType=this.selectedFaultForInjection;
          this.injectionRunning=true;
          this._tabManuallySelected=false;
          this.hitlAction=null;this.hitlOutcome=null;this.remediationTiers=null;this.selectedTierKey=null;
          this.agentMessages=[{role:'system',content:`Fault injection started: ${FAULT_META[this.ddFaultType]?.label} on ${this.ddAssetId}. Ingesting intelligence feed…`}];
          this.chatHistory=[];
          await this.fetchIntelligenceFeed();
          this.showToast(`⚡ Injecting ${FAULT_META[this.selectedFaultForInjection]?.label} on ${this.ddAssetId}`,'var(--orange)');
          this.startDegPoll();
        } else { const e=await r.json(); this.showToast(`Error: ${e.detail}`,'var(--red)'); }
      } catch(e){ this.showToast(`Network error: ${e}`,'var(--red)'); }
    },
    async resetAsset() {
      if(!this.ddAssetId) return;
      try { await fetch(`/api/cancel-degrade/${this.ddAssetId}`,{method:'POST'}); } catch{}
      this.injectionRunning=false;this.ddFaultType=null;this.degStatus=null;this.chartData=null;
      this.feedItems=[];this.visibleFeedCount=0;this.gemmaFinding='';
      this.hitlAction=null;this.hitlOutcome=null;this.remediationTiers=null;this.selectedTierKey=null;
      const nm={...this.initialRulMap}; delete nm[this.ddAssetId]; this.initialRulMap=nm;
      this.showAiFactors=false;
      this.agentMessages=[{role:'system',content:'Fault cleared. Asset reset to nominal baseline.'}];
      Plotly.purge('forecast-chart');
      Plotly.purge('scada-chart');
      this.showToast(`↺ ${this.ddAssetId} reset to normal`,'var(--green)');
    },
    async resetAllFaults() {
      try {
        await Promise.all(Object.keys(this.activeDegradesMap).map(aid=>fetch(`/api/cancel-degrade/${aid}`,{method:'POST'}).catch(()=>{})));
        this.activeDegradesMap={};this.horizonAlerts=[];
        this.showToast('↺ All faults cleared','var(--green)');
      } catch{}
    },
    executeCraftFault() {
      if(!this.craftFaultType) return;
      this.craftModalOpen=false;
      this.selectedFaultForInjection=this.craftFaultType;
      this.injectDuration=this.craftDuration;
      this.injectFault();
    },
    async fetchJustification() {
      if(!this.ddFaultType) return;
      try {
        const r=await fetch(`/api/financial-justification/${this.ddFaultType}`);
        if(r.ok){const d=await r.json();this.justifyData=d.justification;this.justifyModalOpen=true;}
        else{this.showToast('No cost justification data for this fault type','var(--muted)');}
      } catch(e){this.showToast('Error loading justification','var(--red)');}
    },

    startFeedAnimation() {
      if(this.feedAnimTimer){clearInterval(this.feedAnimTimer);this.feedAnimTimer=null;}
      if(this.feedItems.length===0) return;
      this.feedAnimTimer=setInterval(()=>{
        if(this.visibleFeedCount<this.feedItems.length){this.visibleFeedCount++;}
        else{clearInterval(this.feedAnimTimer);this.feedAnimTimer=null;}
      },1200);
    },
    openFeedModal(item){ this.feedModalItem=item; this.feedModalOpen=true; },

    consultAgent() {
      if(!this.ddFaultType||!this.ddAssetId) return;
      this.agentTyping=true;this.agentTypingText='Querying enterprise systems…';this.hitlAction=null;
      // Also fetch remediation tiers
      this.fetchRemediationTiers();
      const hs=this.degStatus?.health_score??0.7;
      const url=`/api/agent/recommend-stream?fault_type=${this.ddFaultType}&asset_id=${this.ddAssetId}&slider_health_score=${hs}&chat_history=${encodeURIComponent(JSON.stringify(this.chatHistory))}`;
      const es=new EventSource(url);
      let ruleMsg=null,llmText='';
      es.onmessage=(e)=>{
        try {
          const msg=JSON.parse(e.data);
          if(msg.type==='recommendation'){ruleMsg=msg;this.agentTypingText='AI streaming analysis…';this.agentMessages.push({role:'agent',content:`[${msg.source}] ${msg.text}`});this.$nextTick(()=>this.scrollChat());this.setHitlFromRecommendation(msg);}
          else if(msg.type==='token'){llmText+=msg.text;this.agentTypingText=llmText.slice(-80);}
          else if(msg.type==='done'){es.close();this.agentTyping=false;this.agentTypingText='';if(llmText.trim().length>20){this.agentMessages.push({role:'agent',content:llmText.trim()});this.$nextTick(()=>this.scrollChat());}if(ruleMsg)this.chatHistory.push({role:'assistant',content:ruleMsg.text});}
        } catch{}
      };
      es.onerror=()=>{es.close();this.agentTyping=false;this.agentTypingText='';};
    },
    setHitlFromRecommendation(msg) {
      const fp=this.ddFaultType, itype=msg.scenario||'maintenance_scheduling';
      const costMap={sand_ingress:85000,motor_overheat:200000,gas_lock:150000,thermal_runaway:150000,bearing_wear:85000,valve_failure:42500,pulsation_dampener_failure:500000,valve_washout:52500,piston_seal_wear:15000,gearbox_bearing_spalling:120000,hydraulic_leak:8000};
      const incurredMap={supply_chain:8500,maintenance_scheduling:0,operational_control:5000,emergency_shutdown:15000,software_command:0,workforce_scheduling:0};
      this.hitlAction={action_text:msg.text,cost_avoided:costMap[fp]||50000,cost_incurred:incurredMap[itype]||0,scenario:itype};
    },
    selectTierApprove(tierKey, tier) {
      this.selectedTierKey=tierKey;
      this.hitlAction={action_text:tier.action,cost_avoided:this.hitlAction?.cost_avoided||50000,cost_incurred:tier.cost_incurred||0,scenario:this.hitlAction?.scenario||'maintenance_scheduling'};
    },
    async approveHitl() {
      if(!this.hitlAction||!this.ddFaultType||!this.ddAssetId) return;
      try {
        const r=await fetch('/api/agent/hitl-approve',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({asset_id:this.ddAssetId,fault_type:this.ddFaultType,action_taken:this.hitlAction.action_text.substring(0,200),cost_incurred:this.hitlAction.cost_incurred||0})});
        if(r.ok){
          const d=await r.json();this.hitlOutcome=d;this.hitlAction=null;this.injectionRunning=false;
          this.agentMessages.push({role:'system',content:`✅ Intervention approved. ${d.outcome_message}`});
          this.agentMessages.push({role:'agent',content:`Action executed. $${(d.net_savings||0).toLocaleString()} net saved. The ${d.fault_label} fault on ${this.ddAssetId} has been resolved.`});
          this.$nextTick(()=>this.scrollChat());
          Plotly.purge('forecast-chart');
          Plotly.purge('scada-chart');
          this.showToast(`✅ Approved — $${(d.net_savings||0).toLocaleString()} saved`,'var(--green)');
        }
      } catch(e){ this.showToast('Error approving action','var(--red)'); }
    },
    rejectHitl() {
      this.hitlAction=null;this.selectedTierKey=null;
      this.agentMessages.push({role:'user',content:'Rejected the recommended action.'});
      this.agentMessages.push({role:'agent',content:'Understood. What concerns do you have about this recommendation? I can suggest alternatives or provide more detail.'});
      this.$nextTick(()=>this.scrollChat());
    },
    async sendAgentMessage() {
      if(!this.agentInput.trim()||this.agentTyping) return;
      const msg=this.agentInput.trim();this.agentInput='';
      this.agentMessages.push({role:'user',content:msg});this.chatHistory.push({role:'user',content:msg});
      this.$nextTick(()=>this.scrollChat());
      if(!this.ddFaultType||!this.ddAssetId) return;
      this.agentTyping=true;this.agentTypingText='Thinking…';
      const hs=this.degStatus?.health_score??0.7;
      const url=`/api/agent/recommend-stream?fault_type=${this.ddFaultType}&asset_id=${this.ddAssetId}&slider_health_score=${hs}&chat_history=${encodeURIComponent(JSON.stringify(this.chatHistory))}`;
      const es=new EventSource(url);let llmText='';
      es.onmessage=(e)=>{
        try {
          const d=JSON.parse(e.data);
          if(d.type==='token'){llmText+=d.text;this.agentTypingText=llmText.slice(-80);}
          else if(d.type==='done'){es.close();this.agentTyping=false;this.agentTypingText='';const txt=llmText.trim()||'I can help with that. Please ask again or request a specific aspect of this fault.';this.agentMessages.push({role:'agent',content:txt});this.chatHistory.push({role:'assistant',content:txt});this.$nextTick(()=>this.scrollChat());}
        } catch{}
      };
      es.onerror=()=>{es.close();this.agentTyping=false;};
    },
    scrollChat() { const el=this.$refs.chatLog; if(el) el.scrollTop=el.scrollHeight; },

    startDegPoll() {
      this.stopDegPoll();
      if(!this.ddAssetId) return;
      this._pollDeg=setInterval(()=>{this.fetchDegradeStatus();this.fetchHorizonAlerts();},5000);
      this._pollChart=setInterval(()=>this.fetchForecastData(),5000);
    },
    stopDegPoll() {
      if(this._pollDeg){clearInterval(this._pollDeg);this._pollDeg=null;}
      if(this._pollChart){clearInterval(this._pollChart);this._pollChart=null;}
    },

    async clearDispatch() {
      try { await fetch('/api/clear-dispatch',{method:'POST'});await this.fetchLedger();this.totalSaved=0;this.showToast('♻ Demo data reset','var(--blue)'); } catch{}
    },

    loadGrafana() {
      const metaTag=document.querySelector('meta[name="grafana-url"]');
      const grafUrl=metaTag?metaTag.content:'http://35.190.137.145';
      const iframe=document.getElementById('grafana-iframe');
      if(iframe){
        this.grafanaLoaded=false;
        iframe.src=grafUrl+'/d/gdc-pm-main?kiosk=tv&refresh=10s';
        iframe.onload=()=>{this.grafanaLoaded=true;};
        iframe.onerror=()=>{this.grafanaLoaded=false;};
      }
    },

    initCopilotResize() {
      const handle=this.$refs.copilotHandle;
      if(!handle) return;
      let startY=0,startH=0;
      const onMouseMove=(e)=>{const delta=startY-e.clientY;this.copilotHeight=Math.min(600,Math.max(120,startH+delta));};
      const onMouseUp=()=>{handle.classList.remove('dragging');document.removeEventListener('mousemove',onMouseMove);document.removeEventListener('mouseup',onMouseUp);document.body.style.cursor='';document.body.style.userSelect='';};
      handle.addEventListener('mousedown',(e)=>{e.preventDefault();startY=e.clientY;startH=this.copilotHeight;handle.classList.add('dragging');document.body.style.cursor='ns-resize';document.body.style.userSelect='none';document.addEventListener('mousemove',onMouseMove);document.addEventListener('mouseup',onMouseUp);});
    },

    // ── GDC AI / SCADA internal split handle — Sprint 5 v4 ────────────────
    // Drag between the GDC AI chart and the Time Bridge to redistribute
    // height between the GDC forecast and SCADA chart panels.
    // gdcPanelHeight = 0 means natural flex:1 equal split (double-click to reset).
    initGdcScadaResize() {
      const handle = this.$refs.gdcScadaHandle;
      if (!handle) return;
      if (handle.dataset.resizerInit === '1') return;
      handle.dataset.resizerInit = '1';
      let startY = 0, startH = 0;
      const minH = 60;
      const getColH = () => {
        // Use document.querySelector — this.$el may not expose querySelector in Vue 3 prod builds
        const colEl = document.querySelector('.dd-compare-col');
        return (colEl ? colEl.getBoundingClientRect().height : 0) || 600;
      };
      const onMove = (e) => {
        const colH = getColH();
        const maxH = colH - 62 - 7 - minH; // 62=bridge height, 7=handle height
        this.gdcPanelHeight = Math.min(maxH, Math.max(minH, startH + (e.clientY - startY)));
        // $nextTick ensures Vue has updated dd-gdc-panel height in the DOM before Plotly
        // measures the container — otherwise Plotly resizes to the OLD height.
        this.$nextTick(() => {
          const fg = document.getElementById('forecast-chart');
          const sc = document.getElementById('scada-chart');
          try { if (fg) Plotly.Plots.resize(fg); } catch {}
          try { if (sc) Plotly.Plots.resize(sc); } catch {}
        });
      };
      const onUp = () => {
        handle.classList.remove('dragging');
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        try { sessionStorage.setItem('gdc_gdcPanelHeight', String(this.gdcPanelHeight)); } catch {}
        if (this.chartData) this.$nextTick(() => this.renderChart());
      };
      handle.addEventListener('mousedown', (e) => {
        e.preventDefault();
        startY = e.clientY;
        // Derive startH from the actual rendered GDC panel height (getBoundingClientRect is reliable)
        const gdcPanel = document.querySelector('.dd-gdc-panel');
        const gdcH = gdcPanel ? gdcPanel.getBoundingClientRect().height : 0;
        startH = this.gdcPanelHeight || gdcH || Math.round((getColH() - 62 - 7) / 2);
        handle.classList.add('dragging');
        document.body.style.cursor = 'ns-resize';
        document.body.style.userSelect = 'none';
        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onUp);
      });
      // Double-click resets to natural equal split
      handle.addEventListener('dblclick', () => {
        this.gdcPanelHeight = 0;
        try { sessionStorage.removeItem('gdc_gdcPanelHeight'); } catch {}
        if (this.chartData) this.$nextTick(() => this.renderChart());
      });
    },

    // ── Chart column resize handle — Sprint 5 v7 ──────────────────────────
    // Dragging the handle between the chart column and the right panels adjusts
    // compareColWidth (EW). Plotly must be resized via $nextTick during drag.
    // Min 300px (both charts visible), max 85% of viewport width.
    initCompareColResize() {
      const handle = this.$refs.compareColHandle;
      if (!handle) return;
      if (handle.dataset.resizerInit === '1') return;
      handle.dataset.resizerInit = '1';
      let startX = 0, startW = 0;
      const onMove = (e) => {
        this.compareColWidth = Math.min(
          Math.round(window.innerWidth * 0.85),
          Math.max(300, startW + (e.clientX - startX))
        );
        // $nextTick: Vue must paint the new width on dd-compare-col before Plotly measures
        this.$nextTick(() => {
          const fg = document.getElementById('forecast-chart');
          const sc = document.getElementById('scada-chart');
          try { if (fg) Plotly.Plots.resize(fg); } catch {}
          try { if (sc) Plotly.Plots.resize(sc); } catch {}
        });
      };
      const onUp = () => {
        handle.classList.remove('dragging');
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        try { sessionStorage.setItem('gdc_compareColWidth', String(this.compareColWidth)); } catch {}
        if (this.chartData) this.$nextTick(() => this.renderChart());
      };
      handle.addEventListener('mousedown', (e) => {
        e.preventDefault();
        startX = e.clientX;
        startW = this.compareColWidth;
        handle.classList.add('dragging');
        document.body.style.cursor = 'ew-resize';
        document.body.style.userSelect = 'none';
        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onUp);
      });
      // Double-click resets to default 720px
      handle.addEventListener('dblclick', () => {
        this.compareColWidth = 720;
        try { sessionStorage.setItem('gdc_compareColWidth', '720'); } catch {}
        if (this.chartData) this.$nextTick(() => this.renderChart());
      });
    },

    showToast(msg, color) {
      const el=document.getElementById('toast');if(!el)return;
      el.textContent=msg;el.style.display='block';el.style.background=color||'var(--surf2)';el.style.color='#fff';el.style.border=`1px solid ${color||'var(--border)'}`;
      clearTimeout(this._toastTimer);
      this._toastTimer=setTimeout(()=>{el.style.display='none';},3000);
    },

    // ── Injection popup — shows drawn params vs bounds for 5s on every inject ──
    // Creates the DOM element lazily (no index.html dependency required).
    showInjectionPopup(params) {
      if (!params) return;
      let el = document.getElementById('inj-popup');
      if (!el) {
        el = document.createElement('div');
        el.id = 'inj-popup';
        el.style.cssText = [
          'position:fixed','top:68px','right:20px','z-index:9999',
          'background:#0d1e2e','border:1px solid #ff8c00','border-radius:8px',
          'padding:14px 18px','font-family:JetBrains Mono,monospace','font-size:11px',
          'max-width:360px','color:#d0d8e0',
          'box-shadow:0 4px 24px rgba(0,0,0,0.6)',
          'line-height:1.7','transition:opacity .3s',
        ].join(';');
        document.body.appendChild(el);
      }
      const p = params;
      const row = (label, val, lo, hi, unit='') => {
        const v = val != null ? Number(val).toFixed(1) : '—';
        const range = (lo != null && hi != null) ? `<span style="color:#2a5a6a"> [${lo}–${hi}]</span>` : '';
        return `<tr><td style="color:#4a7a8a;padding-right:14px">${label}</td><td>${v}${unit}${range}</td></tr>`;
      };
      const modeLabel = p.injection_mode === 'gradual' ? '⬆ GRADUAL RAMP' : '⚡ POINT';
      const faultLabel = (p.fault_type||'').replace(/_/g,' ').toUpperCase();
      const rampRow = p.ramp_k != null ? `<tr><td style="color:#4a7a8a;padding-right:14px">ramp k</td><td>${Number(p.ramp_k).toFixed(3)}</td></tr>` : '';
      const ampsRow = p.amps_target != null ? row('Amps target', p.amps_target, p.amps_range?.[0], p.amps_range?.[1], ' A') : '';
      el.innerHTML = `
        <div style="color:#ff8c00;font-weight:bold;margin-bottom:8px;letter-spacing:.04em">${modeLabel} · ${faultLabel}</div>
        <table style="border-collapse:collapse;width:100%">
          ${row('PSI target',  p.psi_target,  p.psi_range?.[0],  p.psi_range?.[1],  ' PSI')}
          ${row('Temp target', p.temp_target, p.temp_range?.[0], p.temp_range?.[1], '°F')}
          ${row('Vib target',  p.vib_target,  p.vib_range?.[0],  p.vib_range?.[1],  ' mm/s')}
          ${ampsRow}${rampRow}
        </table>
        <div style="color:#1a3a4a;font-size:9px;margin-top:8px">✅ Logged to injection_events · auto-dismiss 5s · <a href="#" onclick="document.getElementById('inj-popup').style.display='none';return false;" style="color:#2a5a6a">dismiss</a></div>
      `;
      el.style.display = 'block'; el.style.opacity = '1';
      clearTimeout(this._injPopupTimer);
      this._injPopupTimer = setTimeout(() => {
        if (el) { el.style.opacity='0'; setTimeout(()=>{el.style.display='none'; el.style.opacity='1';},300); }
      }, 5000);
      // Also refresh the injection log list
      this.fetchInjectionLog();
    },

    async fetchInjectionLog() {
      try {
        const r = await fetch('/api/injection-log?limit=25');
        if (r.ok) { const d = await r.json(); this.injectionLogItems = d.events || []; }
      } catch(e) {}
    },

    // ── Phase 15 — Asset Context Menu methods ──
    showAssetContextMenu(event, assetId) {
      event.stopPropagation();
      const node = event.target.closest('.asset-node');
      const rect = node ? node.getBoundingClientRect() : event.target.getBoundingClientRect();
      let x = rect.right + 10;
      let y = rect.top;
      if (x + 320 > window.innerWidth) x = rect.left - 328;
      if (y + 350 > window.innerHeight) y = window.innerHeight - 360;
      this.faultTooltipFt = null;
      this.faultTooltipData = null;
      this.assetContextMenu = { visible: true, x, y, assetId };
    },
    toggleFaultTooltip(ft) {
      if (this.faultTooltipFt === ft) {
        this.faultTooltipFt = null;
        this.faultTooltipData = null;
      } else {
        this.faultTooltipFt = ft;
        this.faultTooltipData = DEMO_SCENARIOS.find(s => s.faultType === ft) || null;
      }
    },
    scenarioCostFor(ft) {
      const sc = DEMO_SCENARIOS.find(s => s.faultType === ft);
      return sc ? sc.costAvoided : null;
    },
    launchFromContext(assetId, faultType) {
      this.assetContextMenu.visible = false;
      this.faultTooltipFt = null;
      const sc = DEMO_SCENARIOS.find(s => s.assetId === assetId && s.faultType === faultType);
      if (sc) {
        this.launchScenario(sc);
      } else {
        this.openDeepDive(assetId, faultType);
        setTimeout(() => {
          this.selectedFaultForInjection = faultType;
          this.injectDuration = 3600;
          this.injectFault();
        }, 400);
      }
    },

    // ── KPI color helpers (higher is better) ──
    kpiColor(value, greenThreshold, orangeThreshold) {
      if (value === null || value === undefined) return 'zm-neutral';
      if (value >= greenThreshold) return 'zm-green';
      if (value >= orangeThreshold) return 'zm-orange';
      return 'zm-red';
    },
    // ── KPI color helpers (lower is better — e.g., water cut) ──
    kpiColorInv(value, greenThreshold, orangeThreshold) {
      if (value === null || value === undefined) return 'zm-neutral';
      if (value < greenThreshold) return 'zm-green';
      if (value < orangeThreshold) return 'zm-orange';
      return 'zm-red';
    },
    // ── Right panel row resizers — NS drag to resize each panel independently ──
    initRowResizers() {
      this._initRowResizer(this.$refs.intelRowHandle, 'intelPanelHeight', 100, 700, 'gdc_intelPanelHeight');
      this._initRowResizer(this.$refs.agentRowHandle, 'agentPanelHeight', 100, 600, 'gdc_agentPanelHeight');
    },
    _initRowResizer(el, prop, min, max, key) {
      if (!el) return;
      if (el.dataset.resizerInit === '1') return;
      el.dataset.resizerInit = '1';
      let startY = 0, startH = 0;
      const onMove = (e) => { this[prop] = Math.min(max, Math.max(min, startH + (e.clientY - startY))); };
      const onUp = () => {
        el.classList.remove('dragging');
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        try { sessionStorage.setItem(key, String(this[prop])); } catch {}
      };
      el.addEventListener('mousedown', (e) => {
        e.preventDefault();
        startY = e.clientY;
        startH = this[prop];
        el.classList.add('dragging');
        document.body.style.cursor = 'ns-resize';
        document.body.style.userSelect = 'none';
        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onUp);
      });
      // Double-click resets to default
      el.addEventListener('dblclick', () => {
        this[prop] = prop === 'intelPanelHeight' ? 260 : 280;
        try { sessionStorage.setItem(key, String(this[prop])); } catch {}
      });
    },

    // ── Horizontal splitter between fleet canvas and activity stream ──
    // ── Horizon Tab Methods ──
    setMainTab(tab) {
      this.mainTab = tab;
      // Clear any active polling timers to prevent background leaks when navigating away
      if (this.h1DegPollTimer)   { clearInterval(this.h1DegPollTimer);   this.h1DegPollTimer   = null; }
      if (this.h1LivePollTimer)  { clearInterval(this.h1LivePollTimer);  this.h1LivePollTimer  = null; }
      if (this.h1ElapsedTimer)   { clearInterval(this.h1ElapsedTimer);   this.h1ElapsedTimer   = null; }
      if (this.h2DegPollTimer)   { clearInterval(this.h2DegPollTimer);   this.h2DegPollTimer   = null; }
      if (tab === 'horizon1') {
        // Auto-load Scenario Replay on tab open if none loaded yet (Session P)
        if (!this.h1ReplayData && !this.h1ReplayLoading) {
          this.$nextTick(() => this.loadH1Scenario());
        }
        // Always poll live telemetry for SCADA card (ticking even before fault injection)
        const _pollLive1 = async () => {
          if (this.h1Injected) return; // fault degrade thread owns sensor values when injected
          const _liveWell = this.h1SelectedWell || 'ESP-ALPHA-1';
          const r = await fetch(`/api/live-telemetry/${_liveWell}`);
          if (r.ok) { const d = await r.json();
            if (d.psi)        { this.h1SensorPsi  = d.psi.toFixed(0) + ' PSI';        this.h1RawPsi  = d.psi; }
            if (d.temp_f)     { this.h1SensorTemp = d.temp_f.toFixed(0) + '°F';       this.h1RawTemp = d.temp_f; }
            if (d.motor_amps) { this.h1SensorAmps = d.motor_amps.toFixed(1) + ' A';   this.h1RawAmps = d.motor_amps; }
          }
        };
        _pollLive1();
        this.h1LivePollTimer = setInterval(_pollLive1, 5000);
        // Fetch baseline chart on tab open (shows live data even before injection)
        if (!this.h1Injected) {
          this.$nextTick(() => {
            const _baseWell = this.h1SelectedWell || 'ESP-ALPHA-1';
            fetch(`/api/plot/forecast-data/${_baseWell}`)
              .then(r=>r.ok?r.json():null)
              .then(d=>{ if(d&&d.sensors&&!this.h1Injected){this.h1ForecastData=d;this.$nextTick(()=>this._renderH1Charts(d));} });
          });
        }
        // Fetch baseline intel docs if no fault injected
        if (!this.h1Injected && this.h1FeedItems.length === 0) {
          const _intelWell = this.h1SelectedWell || 'ESP-ALPHA-1';
          fetch(`/api/intelligence-feed/${_intelWell}?fault_type=normal`)
            .then(r=>r.ok?r.json():null).then(d=>{ if(d&&!this.h1Injected) this.h1FeedItems=d.items||[]; });
        }
        // Restart fault degrade poll if returning to an active, unresolved scenario
        if (this.h1Injected && (!this.h1Resolved || this.h1Recovering)) {
          this.h1DegPollTimer = setInterval(async()=>{
            const _tw = this.h1TargetWell || 'ESP-ALPHA-1';
            const r=await fetch(`/api/degrade-status/${_tw}`);
            if(r.ok){const d=await r.json(); if(d.is_active){
              this.h1HealthScore=(d.health_score*100).toFixed(1)+'%';
              const cs=this.activeDegradesMap[_tw]?.current_sensors||{};
              if(cs.psi) this.h1SensorPsi=cs.psi.toFixed(0)+' PSI';
              if(cs.temp) this.h1SensorTemp=cs.temp.toFixed(0)+'°F';
              if(cs.motor_amps !== undefined && cs.motor_amps !== null) this.h1SensorAmps = cs.motor_amps.toFixed(1)+' A';
            }}
            const rfd=await fetch(`/api/plot/forecast-data/${_tw}`);
            if(rfd.ok){const d=await rfd.json();if(d.sensors){
              this.h1ForecastData=d;this._renderH1Charts(d);
              if(d.class_probs){const top=Object.entries(d.class_probs).sort((a,b)=>b[1]-a[1])[0];if(top){this.h1TopClass=top[0];this.h1TopClassProb=top[1];}}
              const gvfItem=this.h1FeedItems.find(i=>(i.content||'').includes('estimated at'));
              if(gvfItem){const m=(gvfItem.content||'').match(/estimated at (\d+)%/);if(m)this.h1GvfPct=m[1]+'%';}
            }}
          }, 5000);
        }
      }
      // Auto-load H2 Scenario Replay on tab open if none loaded yet
      if (tab === 'horizon2' && !this.h2ReplayData && !this.h2ReplayLoading) {
        this.$nextTick(() => this.loadH2Scenario());
      }
      // Vizier intentionally NOT auto-fired on tab open — explicit ▶ Run button only.
      // Auto-fire created a new Vizier study (+ 15 billed trials) on every page load/tab click.
      // (removed Session BS+9 to stop unintended billing)
    },
    
    // ── Horizon 1: Pad Triage — Ingest Pad Anomalies (Comparative Detection Scenario) ──
    launchHorizon1Unloading() {
      if (this.h1Injected) return;
      // Randomly select target well from Pad Alpha (A-1 to A-6)
      const wells = ['ESP-ALPHA-1','ESP-ALPHA-2','ESP-ALPHA-3','ESP-ALPHA-4','ESP-ALPHA-5','ESP-ALPHA-6'];
      const idx = Math.floor(Math.random() * wells.length);
      this.h1TargetWell = wells[idx];
      this.h1SelectedWell = this.h1TargetWell;
      // Two adjacent wells receive benign transient disturbances (nuisance alarms)
      const prevIdx = (idx - 1 + wells.length) % wells.length;
      const nextIdx = (idx + 1) % wells.length;
      this.h1NuisanceWells = [wells[prevIdx], wells[nextIdx]];
      // Randomly select fault type — audience does not know which was injected
      const ft = Math.random() < 0.5 ? 'gas_lock' : 'fluid_drawdown';
      this.launchHorizon1(ft);
    },
    async launchHorizon1(faultType) {
      if (this.h1Injected) return;
      const ft = faultType || 'gas_lock';
      this.h1FaultType = ft;
      this.h1ConsoleTab = 'scada';   // always start on SCADA (blind) view
      this.h1RagRevealed = false;
      this.h1OverrideModalOpen = false;
      this.h1ShiftNoteModalOpen = false;
      this.h1SonicLogModalOpen = false;
      this.h1Injected = true;
      this.h1Resolved = false;
      this.h1Seized = false;
      this.h1PumpOffExcluded = false;
      this.h1GasLockExcluded = false;
      this.h1HealthScore = '82.0%';
      this.h1InjectedAt = Date.now();
      this.h1EvidenceActive = 0;
      this.h1EvidenceWall.forEach(e => { e.active = false; });
      // Dynamically configure evidence wall content for chosen fault type
      if (ft === 'fluid_drawdown') {
        this.h1EvidenceWall[0].content = 'PIP −14 PSI/min \u2193 · Amps −2.3 A/min \u2193 · 4-sensor correlated decline at 5-second cadence';
        this.h1EvidenceWall[1].content = '"06:00 sonic survey: Dynamic fluid level 150 ft above pump intake. Reservoir depleting." — Tour 2 sonic log';
        this.h1EvidenceWall[2].content = 'Separator GOR stable: 1,104 scf/bbl (nominal baseline) · Casing pressure flat at 40 PSI — no free gas migration';
        this.h1EvidenceWall[3].content = 'Acoustic survey confirms: static fluid level at critical submergence limit. Sand bridging risk on speed-down confirmed.';
        this.h1EvidenceWall[4].content = 'Field Guidelines §9.3: Speed-down during drawdown drops fluid velocity below critical lift (4.2 ft/s). VFD trim is CONTRAINDICATED.';
      } else {
        this.h1EvidenceWall[0].content = 'PIP −14 PSI/min \u2193 · Amps −2.3 A/min \u2193 · 4-sensor correlated decline at 5-second cadence';
        this.h1EvidenceWall[1].content = '"Higher than usual GVF this morning — possibly gas migration from upper zone." — 06:15 tour note';
        this.h1EvidenceWall[2].content = 'Separator gas rate 142 Mscf/d \u2191 · GOR 1,310 scf/bbl \u2191 · Casing pressure +18 PSI vs prior tour';
        this.h1EvidenceWall[3].content = 'Soft unload events × 3 in last 45 min · Power factor 0.71 \u2193 · Underload flag approaching threshold';
        this.h1EvidenceWall[4].content = 'API RP 11S §5.3: VFD speed-down is primary intervention. Class H limit: 180°C (IEEE 117). Baker Hughes: GVF >65% triggers unloading.';
      }
      this.h1AdvisorHtml = '';
      this.h1AdvisorStreaming = false;
      this.h1ChatMessages = [];
      this.h1OptA = 'wopt-viable'; this.h1OptALabel = 'VIABLE';
      this.h1OptB = 'wopt-viable'; this.h1OptBLabel = 'VIABLE';
      try {
        const _assetId = this.h1TargetWell || 'ESP-ALPHA-1';
        const _durSecs = this.h1RampSpeed === 'accelerated' ? 300 : 900;
        const _h1InjR = await fetch('/api/inject/degrade', {method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({asset_id: _assetId, fault_type: ft, duration_seconds: _durSecs})});
        if (_h1InjR.ok) { const _h1InjD = await _h1InjR.json(); if (_h1InjD.injection_params) this.showInjectionPopup(_h1InjD.injection_params); }
        this.showToast(`\u26a1 ${ft === 'fluid_drawdown' ? 'Fluid Drawdown' : 'Gas Lock'} injected on ${_assetId}`, 'var(--orange)');
        const feed = await fetch(`/api/intelligence-feed/${_assetId}?fault_type=${ft}`);
        if (feed.ok) { const d=await feed.json(); this.h1FeedItems=d.items||[]; this.h1GemmaFinding=d.gemma_finding||''; }
        if (this.h1FeedPollInterval) clearInterval(this.h1FeedPollInterval);
        this.h1FeedPollInterval = setInterval(() => {
          fetch(`/api/intelligence-feed/${_assetId}?fault_type=${ft}`)
            .then(r => r.ok ? r.json() : null)
            .then(d => { if (d && this.h1Injected && !this.h1Resolved) this.h1FeedItems = d.items || []; });
        }, 15000);
        // Activate evidence wall in sequence (200ms, 2s, 3.8s, 5.5s, 7.2s)
        const evDelays = [200, 2000, 3800, 5500, 7200];
        evDelays.forEach((delay, i) => {
          setTimeout(() => { this.h1EvidenceWall[i].active = true; this.h1EvidenceActive = i + 1; }, delay);
        });
        // LLM advisor auto-streams 3s after injection; scheduled follow-ups at T+50s and T+2min
        setTimeout(() => this._startAdvisorStream(), 3000);
        const _at1 = setTimeout(() => this._triggerAdvisoryUpdate('context', null), 50000);
        const _at2 = setTimeout(() => this._triggerAdvisoryUpdate('context', null), 120000);
        this.h1AdvisorUpdateTimers = [_at1, _at2];
        // Elapsed timer for option viability
        this.h1ElapsedTimer = setInterval(() => {
          this.h1ElapsedMin = (Date.now() - this.h1InjectedAt) / 60000;
          this._updateOptionsViability();
        }, 5000);
        // Forecast poll
        this.h1DegPollTimer = setInterval(async()=>{
          const _tw2 = this.h1TargetWell || _assetId || 'ESP-ALPHA-1';
          const r=await fetch(`/api/degrade-status/${_tw2}`);
          if(r.ok){const d=await r.json(); if(d.is_active){
            this.h1HealthScore=(d.health_score*100).toFixed(1)+'%';
            const cs=this.activeDegradesMap[_tw2]?.current_sensors||{};
            if(cs.psi) this.h1SensorPsi=cs.psi.toFixed(0)+' PSI';
            if(cs.temp) this.h1SensorTemp=cs.temp.toFixed(0)+'°F';
            if(cs.motor_amps !== undefined && cs.motor_amps !== null) this.h1SensorAmps = cs.motor_amps.toFixed(1)+' A';
          }}
          const rfd=await fetch(`/api/plot/forecast-data/${_tw2}`);
          if(rfd.ok){const d=await rfd.json();if(d.sensors){this.h1ForecastData=d;
            // Capture per-run window total on first non-null thermal deadline (failure contributor = motor-winding thermal, API RP 11S §4.2)
            if(!this.h1WindowTotal){const _tl=d.thermal_lead_time_minutes;const _sc=d.time_to_scada_minutes;
              if(_tl&&_tl>0)this.h1WindowTotal=Math.round(_tl);
              else if(_sc&&_sc>0)this.h1WindowTotal=Math.round(_sc);}
            this._renderH1PhasePlane(d);}}
        }, 5000);
      } catch(e) { this.showToast('Error injecting gas lock','var(--red)'); }
    },
    async resetHorizon1() {
      if (this.h1DegPollTimer)      { clearInterval(this.h1DegPollTimer);      this.h1DegPollTimer      = null; }
      if (this.h1LivePollTimer)     { clearInterval(this.h1LivePollTimer);     this.h1LivePollTimer     = null; }
      if (this.h1ElapsedTimer)      { clearInterval(this.h1ElapsedTimer);      this.h1ElapsedTimer      = null; }
      if (this.h1AdvisorTimer)      { clearInterval(this.h1AdvisorTimer);      this.h1AdvisorTimer      = null; }
      if (this.h1FeedPollInterval)  { clearInterval(this.h1FeedPollInterval);  this.h1FeedPollInterval  = null; }
      if (this.h1RecoveryPollTimer) { clearInterval(this.h1RecoveryPollTimer); this.h1RecoveryPollTimer = null; }
      const _cancelWell = this.h1TargetWell || 'ESP-ALPHA-1';
      try { await fetch(`/api/cancel-degrade/${_cancelWell}`,{method:'POST'}); } catch{}
      this.h1Injected=false; this.h1Resolved=false; this.h1Recovering=false;
      this.h1SensorPsi=null; this.h1SensorTemp=null; this.h1SensorAmps=null; this.h1HealthScore=null;
      this.h1FeedItems=[]; this.h1GemmaFinding=''; this.h1ForecastData=null; this.h1ActiveSensor='psi';
      this.h1EvidenceActive=0; this.h1AdvisorHtml=''; this.h1AdvisorStreaming=false; this.h1RulHistory=[];
      this.h1RawPsi=null; this.h1RawAmps=null; this.h1RawTemp=null; this.h1RawVib=null; this.h1SensorVib=null;
      this.h1PhasePlaneHistory=[]; this.h1DetectionTime=null;
      this.h1AdvisorLastFeedId=null; this.h1AdvisorLastContextTime=0;
      this.h1AdvisorUpdateTimers.forEach(t=>clearTimeout(t)); this.h1AdvisorUpdateTimers=[];
      this.h1ChatMessages=[]; this.h1ChatInput='';
      this.h1InjectedAt=null; this.h1ElapsedMin=0; this.h1WindowTotal=null;
      this.h1TopClass=null; this.h1TopClassProb=null; this.h1GvfPct=null;
      this.h1OptA='wopt-viable'; this.h1OptALabel='VIABLE';
      this.h1OptB='wopt-viable'; this.h1OptBLabel='VIABLE';
      this.h1RecoveryMsg='';
      this.h1EvidenceWall.forEach(e => { e.active = false; });
      try { Plotly.purge('h1-phase-chart'); } catch{}
      this.h1EnvelopeHistory = []; this.h1PumpOffExcluded = false;
      this.h1GasLockExcluded = false; this.h1FaultType = ''; this.h1Seized = false;
      this.h1TargetWell = null; this.h1NuisanceWells = []; this.h1WellData = {};
      this.h1SelectedWell = 'ESP-ALPHA-1';
      try { Plotly.purge('h1-envelope-chart'); } catch{}
      ['h1-spark-psi','h1-spark-amps','h1-spark-temp','h1-spark-vib'].forEach(id => { try { Plotly.purge(id); } catch{} });
      this.showToast('↺ Horizon 1 reset','var(--green)');
      const _pollLive1 = async () => {
        if (this.h1Injected) return;
        const r = await fetch('/api/live-telemetry/ESP-ALPHA-1');
        if (r.ok) { const d = await r.json();
          if (d.psi)        { this.h1SensorPsi  = d.psi.toFixed(0) + ' PSI';        this.h1RawPsi  = d.psi; }
          if (d.temp_f)     { this.h1SensorTemp = d.temp_f.toFixed(0) + '°F';       this.h1RawTemp = d.temp_f; }
          if (d.motor_amps) { this.h1SensorAmps = d.motor_amps.toFixed(1) + ' A';   this.h1RawAmps = d.motor_amps; }
        }
      };
      _pollLive1();
      this.h1LivePollTimer = setInterval(_pollLive1, 5000);
      fetch('/api/intelligence-feed/ESP-ALPHA-1?fault_type=normal')
        .then(r=>r.ok?r.json():null).then(d=>{ if(d&&!this.h1Injected) this.h1FeedItems=d.items||[]; });
    },
    // ── H1 Scenario Replay methods (Session P) ───────────────────────────────
    async loadH1Scenario() {
      this.h1Pause();
      this.h1CursorIdx = 0;
      this.h1FaultTypeRevealed = false;
      this.h1RagRevealed = false;
      this.h1FaultType = '';
      this.h1Resolved = false;
      this.h1Seized = false;
      this.h1Recovering = false;
      this.h1ScadaRuleFired = '';
      this.h1EvidenceActive = 0;
      this.h1EvidenceWall.forEach(e => { e.active = false; });
      if (this.h1RagRevealTimer) { clearTimeout(this.h1RagRevealTimer); this.h1RagRevealTimer = null; }
      if (this.h1RagDoc2Timer)   { clearTimeout(this.h1RagDoc2Timer);   this.h1RagDoc2Timer   = null; }
      if (this.h1RagDoc3Timer)   { clearTimeout(this.h1RagDoc3Timer);   this.h1RagDoc3Timer   = null; }
      this.h1RagDoc2Shown = false;
      this.h1RagDoc3Shown = false;
      this.h1RagPending   = false;
      this.h1ReplayData = null;
      this.h1ReplayLoading = true;
      // Anchored to Well A-3 (ESP-ALPHA-3) — no random well ID. Fleet scalability
      // is communicated via the narrative card, not by randomizing which well number shows.
      const ft = Math.random() < 0.5 ? 'gas_lock' : 'fluid_drawdown';
      try {
        const r = await fetch(`/api/h1/scenario-replay?fault=${ft}`);
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const data = await r.json();
        this.h1ReplayData = data;
        this.h1ScadaRuleFired = data.scada_rule_fired || '';
        this.h1ReplayLoading = false;
        this.$nextTick(() => { this._renderH1ReplayChart(); });
      } catch(e) {
        this.h1ReplayLoading = false;
        this.showToast(`Scenario load failed: ${e.message}`, 'var(--red)');
      }
    },
    h1Play(fast = false) {
      if (!this.h1ReplayData) return;
      this.h1Pause();
      this.h1Playing = true;
      // BS+23: requestAnimationFrame replaces setInterval — cursor advances are
      // locked to the display's actual frame rate (≤60fps). setInterval at 10Hz
      // was GPU-burst-firing Plotly relayout() calls independently of the display
      // refresh, causing FRC dithering chaos on HiDPI/8-bit+FRC panels full-screen.
      const interval = fast ? 30 : 100;
      let lastTs = 0;
      const step = (ts) => {
        if (!this.h1Playing) return;
        if (ts - lastTs >= interval) {
          lastTs = ts;
          if (this.h1CursorIdx >= this.h1ReplayData.n - 1) { this.h1Pause(); return; }
          this.h1CursorIdx++;
        }
        this.h1PlayTimer = requestAnimationFrame(step);
      };
      this.h1PlayTimer = requestAnimationFrame(step);
    },
    h1Pause() {
      this.h1Playing = false;
      if (this.h1PlayTimer) { cancelAnimationFrame(this.h1PlayTimer); this.h1PlayTimer = null; }
    },
    h1Reset() {
      this.h1Pause();
      this.h1CursorIdx = 0;
      this.h1FaultTypeRevealed = false;
      this.h1RagRevealed = false;
      this.h1RagDoc2Shown = false;
      this.h1RagDoc3Shown = false;
      this.h1FaultType = '';
      this.h1Resolved = false;
      this.h1Seized = false;
      this.h1Recovering = false;
      this.h1EvidenceActive = 0;
      this.h1ShowEvidenceTable = false;
      this.h1PumpOffExcluded = false;
      this.h1GasLockExcluded = false;
      this.h1EvidenceWall.forEach(e => { e.active = false; });
      if (this.h1RagRevealTimer) { clearTimeout(this.h1RagRevealTimer); this.h1RagRevealTimer = null; }
      if (this.h1RagDoc2Timer) { clearTimeout(this.h1RagDoc2Timer); this.h1RagDoc2Timer = null; }
      if (this.h1RagDoc3Timer) { clearTimeout(this.h1RagDoc3Timer); this.h1RagDoc3Timer = null; }
      this._updateH1ReplayCursor(0);
    },
    h1Scrub(idx) {
      if (!this.h1ReplayData) return;
      this.h1CursorIdx = Math.max(0, Math.min(idx, this.h1ReplayData.n - 1));
    },
    _updateH1ReplayCursor(idx) {
      if (!this.h1ReplayData) return;
      try {
        const t = this.h1ReplayData.t_min[idx] || 0;
        // shapes[0] = GDC detect (amber), shapes[1] = SCADA alarm (red), shapes[2] = cursor (grey)
        Plotly.relayout('h1-replay-chart', { 'shapes[2].x0': t, 'shapes[2].x1': t });
      } catch(e) {}
    },
    _renderH1ReplayChart() {
      const d = this.h1ReplayData;
      if (!d || !d.psi || !d.amps) return;
      const cursorT = d.t_min[this.h1CursorIdx] || 0;
      const gdcT    = d.t_min[d.gdc_detect_idx]  || 0;  // amber pre-threshold detect marker
      const scadaT  = d.t_min[d.alarm_idx]        || 0;  // red threshold alarm marker
      const xMax    = d.t_min[d.n - 1] || 30;

      // ── 4 stacked subplots sharing the same x-axis ───────────────────────
      // Each sensor gets its own row. Plotly `grid` layout with domain assignment
      // ensures equal heights. All three vertical lines (GDC, Smart-SCADA, cursor)
      // span the FULL paper height (yref:'paper', y0:0→y1:1), so they visually
      // cross all four charts — an honest representation of multivariate detection.
      const traces = [
        { x: d.t_min, y: d.psi,  name: 'PIP (PSI)',    type: 'scatter', mode: 'lines',
          line: {color:'#60a5fa', width:1.8}, xaxis:'x', yaxis:'y',  showlegend:true },
        { x: d.t_min, y: d.amps, name: 'Amps (A)',     type: 'scatter', mode: 'lines',
          line: {color:'#4ade80', width:1.8}, xaxis:'x', yaxis:'y2', showlegend:true },
        { x: d.t_min, y: d.temp, name: 'Temp (°F)',    type: 'scatter', mode: 'lines',
          line: {color:'#fb923c', width:1.8}, xaxis:'x', yaxis:'y3', showlegend:true },
        { x: d.t_min, y: d.vib,  name: 'Vib (mm/s)',   type: 'scatter', mode: 'lines',
          line: {color:'#a78bfa', width:1.8}, xaxis:'x', yaxis:'y4', showlegend:true },
      ];

      // shapes[0]=GDC detect (amber), shapes[1]=SCADA alarm (red), shapes[2]=cursor (grey)
      // All span full paper height — visually cross all 4 sensor subplots
      const shapes = [
        { type:'line', x0:gdcT,    x1:gdcT,    y0:0, y1:1, xref:'x', yref:'paper',
          line:{color:'rgba(251,191,36,0.85)',  width:2, dash:'dash'} },
        { type:'line', x0:scadaT,  x1:scadaT,  y0:0, y1:1, xref:'x', yref:'paper',
          line:{color:'rgba(239,68,68,0.88)',   width:2, dash:'dash'} },
        { type:'line', x0:cursorT, x1:cursorT, y0:0, y1:1, xref:'x', yref:'paper',
          line:{color:'rgba(148,163,184,0.6)',  width:1.5, dash:'dot'} },
      ];

      const annotations = [
        // GDC pre-threshold multivariate detect (amber) — fires before any threshold is crossed
        { x:gdcT, y:1.01, xref:'x', yref:'paper', text:'<b>GDC</b>',
          showarrow:false, xanchor:'left', yanchor:'bottom',
          font:{color:'rgba(251,191,36,0.95)', size:7.5, family:'Inter,sans-serif'},
          bgcolor:'rgba(251,191,36,0.08)', borderpad:1 },
        // SCADA threshold alarm (red) — fires when a hard setpoint is crossed
        { x:scadaT, y:1.01, xref:'x', yref:'paper', text:'<b>Threshold SCADA ▲</b>',
          showarrow:false, xanchor:'left', yanchor:'bottom',
          font:{color:'rgba(239,68,68,0.95)',   size:7.5, family:'Inter,sans-serif'},
          bgcolor:'rgba(239,68,68,0.08)',   borderpad:1 },
      ];

      const commonYAxis = {gridcolor:'#1e2a38', zeroline:false, showline:false,
                           tickfont:{size:8}, nticks:4};
      // Rolling 30-min window: after 120-step replay, x-axis slides to show last 30 min
      const xRange = xMax > 30 ? [xMax - 30, xMax] : [0, Math.max(30, xMax)];

      Plotly.newPlot('h1-replay-chart', traces, {
        paper_bgcolor:'#131d31', plot_bgcolor:'#131d31',
        font:{color:'#e0e0e0', family:'Inter,sans-serif', size:9},
        margin:{l:48, r:12, t:18, b:30},
        // 4-row grid — Plotly manages subplot spacing automatically
        grid:{rows:4, columns:1, pattern:'independent', roworder:'top to bottom',
              ygap:0.06},
        xaxis:  {gridcolor:'#1e2a38', zeroline:false, range:xRange,
                 title:{text:'Time (min)', font:{size:8, color:'#5a6a7a'}},
                 anchor:'y4', showticklabels:true, tickfont:{size:7}},
        // Each y-axis anchored to xaxis and assigned a domain row
        yaxis:  {...commonYAxis, title:{text:'Pump Intake Pressure (PSI)', font:{color:'#60a5fa',size:8}},
                 titlefont:{color:'#60a5fa'}, tickfont:{...commonYAxis.tickfont, color:'#60a5fa'},
                 anchor:'x', domain:[0.77,1.0]},
        yaxis2: {...commonYAxis, title:{text:'Motor Current (A)', font:{color:'#4ade80',size:8}},
                 titlefont:{color:'#4ade80'}, tickfont:{...commonYAxis.tickfont, color:'#4ade80'},
                 anchor:'x', domain:[0.51,0.74]},
        yaxis3: {...commonYAxis, title:{text:'Winding Temp (°F)', font:{color:'#fb923c',size:8}},
                 titlefont:{color:'#fb923c'}, tickfont:{...commonYAxis.tickfont, color:'#fb923c'},
                 anchor:'x', domain:[0.26,0.49]},
        yaxis4: {...commonYAxis, title:{text:'Vibration (mm/s)', font:{color:'#a78bfa',size:8}},
                 titlefont:{color:'#a78bfa'}, tickfont:{...commonYAxis.tickfont, color:'#a78bfa'},
                 anchor:'x', domain:[0.0, 0.23]},
        shapes, annotations,
        showlegend:false,
      }, {displayModeBar:false, responsive:true});
    },
    async approveH1VFDForce() {
      // Override path removed per design (seizure path out of scope).
      // Route directly to the standard VFD trim action.
      this.h1OverrideModalOpen = false;
      // Execute VFD trim (same as recommended path for gas lock)
      await this.approveH1VFD();
    },
    async executeH1Shutdown() {
      // Safe action during Fluid Drawdown: emergency shut-in preserves the pump
      this.h1Pause(); // lock transport on remediation
      this.h1Resolved = true;
      this.h1Recovering = false;
      this.h1OptA = 'wopt-expired'; this.h1OptALabel = 'EXECUTED';
      this.h1OptB = 'wopt-expired'; this.h1OptBLabel = 'EXPIRED';
      if (this.h1ElapsedTimer) { clearInterval(this.h1ElapsedTimer); this.h1ElapsedTimer = null; }
      const _shutWell = this.h1TargetWell || 'ESP-ALPHA-1';
      const _shutLabel = _shutWell.replace('ESP-ALPHA-','A-');
      this.h1AdvisorHtml += `<br><br><strong style="color:var(--green)">✅ Emergency shut-in command issued. Well ${_shutLabel} offline. Awaiting field confirmation — pump condition assessed on controlled restart.</strong>`;
      this.showToast('✅ Shut-in command issued — awaiting field confirmation', 'var(--green)');
      try { await fetch(`/api/cancel-degrade/${_shutWell}`, {method:'POST'}); } catch(e) {}
      // Batch D (RT-7): write remediation record to field_intel
      try {
        await fetch('/api/h1/remediation-record', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            asset_id: _shutWell,
            fault_type: this.h1FaultType || 'fluid_drawdown',
            action_label: 'emergency_shutin',
            headline: `Emergency Shut-In — Well ${_shutLabel} — operator confirmed`,
            detail: `Operator issued emergency shut-in command at T+${Math.round((this.h1CursorIdx||0)*0.25)}min. Well ${_shutLabel} taken offline. Pump condition to be assessed on controlled restart. GDC diagnostic: ${this.h1FaultType||'fluid_drawdown'} confirmed via L3 context fusion.`
          })
        });
      } catch(e) {}
    },
    async approveH1VFD() {
      this.h1Pause(); // lock transport on remediation
      // GDC Advisor view: intercept VFD trim during drawdown — show override modal instead
      if (this.h1FaultType === 'fluid_drawdown' && !this.h1Resolved && this.h1ConsoleTab === 'gdc') {
        this.h1OverrideModalOpen = true;
        return;
      }
      // SCADA blind gamble OR force-override path: if fluid_drawdown, this SEIZES the pump
      if (this.h1FaultType === 'fluid_drawdown' && !this.h1Resolved) {
        this.h1Seized = true;
        this.h1Resolved = true;
        // Write remediation record for seize path (wrong action on drawdown)
        const _seizeWell2 = this.h1TargetWell || 'ESP-ALPHA-1';
        try {
          await fetch('/api/h1/remediation-record', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
              asset_id: _seizeWell2,
              fault_type: 'fluid_drawdown',
              action_label: 'vfd_trim_contraindicated',
              headline: `VFD Trim Executed on Fluid Drawdown — Unplanned Shutdown — ${_seizeWell2}`,
              detail: `Operator executed VFD trim (52→44 Hz) during confirmed fluid drawdown. Wellbore response abnormal — well removed from production. Fluid-level recovery and engineering assessment required. GDC contraindication was not followed.`
            })
          });
        } catch(e) {}
        this.h1Recovering = false;
        if (this.h1ElapsedTimer) { clearInterval(this.h1ElapsedTimer); this.h1ElapsedTimer = null; }
        this.h1AdvisorHtml += '<br><br><strong style="color:var(--yellow)">⚠ VFD trim executed against GDC recommendation during fluid drawdown — wellbore response abnormal. Well removed from production for fluid-level recovery and engineering assessment. Production deferred. Unplanned intervention cost applies.</strong>';
        this.showToast('⚠ Unplanned outcome — well taken offline for assessment', 'var(--yellow)');
        const _seizeWell = this.h1TargetWell || 'ESP-ALPHA-1';
        try { await fetch(`/api/cancel-degrade/${_seizeWell}`, {method:'POST'}); } catch(e) {}
        return;
      }
      this.h1Resolved = true;
      this.h1Recovering = true;
      this.h1OptA = 'wopt-expired'; this.h1OptALabel = 'EXECUTED';
      this.h1OptB = 'wopt-expired'; this.h1OptBLabel = 'EXPIRED';
      if (this.h1ElapsedTimer) { clearInterval(this.h1ElapsedTimer); this.h1ElapsedTimer = null; }
      this.h1AdvisorHtml += '<br><br><strong style="color:var(--green)">↗ VFD speed-down command sent (52 → 44 Hz / 3,120 → 2,640 RPM). Recovery initiated. Monitoring wellbore response…</strong>';
      this.showToast('↗ VFD command sent — monitoring wellbore recovery','var(--green)');
      try {
        const _vfdWell = this.h1TargetWell || 'ESP-ALPHA-1';
        await fetch('/api/agent/hitl-approve',{method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify({asset_id:_vfdWell,fault_type:this.h1FaultType||'gas_lock',action_taken:'VFD reduced to 44 Hz (2,640 RPM) — free gas migrating up annulus',cost_incurred:0})});
      } catch(e) {}
      // Poll _post_approval_monitor messages every 30s
      this.h1RecoveryPollTimer = setInterval(async () => {
        const _vfdWell2 = this.h1TargetWell || 'ESP-ALPHA-1';
        try {
          const r = await fetch(`/api/recovery-status/${_vfdWell2}`);
          if (r.ok) { const d = await r.json();
            if (d.msg) { this.h1RecoveryMsg = d.msg; }
            if (d.state === 'complete') {
              this.h1Recovering = false;
              this.h1AdvisorHtml += `<br><strong style="color:var(--green)">✅ Recovery complete. ${_vfdWell2} nominal. Well responding.</strong>`;
              clearInterval(this.h1RecoveryPollTimer); this.h1RecoveryPollTimer = null;
              if (this.h1DegPollTimer) { clearInterval(this.h1DegPollTimer); this.h1DegPollTimer = null; }
            }
          }
        } catch(e) {}
      }, 30000);
      // Auto-stop chart poll after 3 min regardless
      setTimeout(() => {
        this.h1Recovering = false;
        if (this.h1DegPollTimer)      { clearInterval(this.h1DegPollTimer);      this.h1DegPollTimer      = null; }
        if (this.h1RecoveryPollTimer) { clearInterval(this.h1RecoveryPollTimer); this.h1RecoveryPollTimer = null; }
      }, 180000);
    },
    _renderH1PhasePlane(d) {
      // Extract raw sensor values from forecast data live telemetry traces
      const rawAmps = d.sensors?.amps?.traces?.[0]?.y?.slice(-1)?.[0] ?? null;
      const rawTemp = d.sensors?.temp?.traces?.[0]?.y?.slice(-1)?.[0] ?? null;
      const rawPsi  = d.sensors?.psi?.traces?.[0]?.y?.slice(-1)?.[0]  ?? null;
      const rawVib  = d.sensors?.vib?.traces?.[0]?.y?.slice(-1)?.[0]  ?? null;
      // Store for reactive gauge bindings — single source of truth (DB trace)
      if (rawAmps !== null) { this.h1RawAmps = rawAmps; this.h1SensorAmps = rawAmps.toFixed(1) + ' A'; }
      if (rawTemp !== null) { this.h1RawTemp = rawTemp; this.h1SensorTemp = rawTemp.toFixed(0) + '°F'; }
      if (rawPsi  !== null) { this.h1RawPsi  = rawPsi;  this.h1SensorPsi  = rawPsi.toFixed(0)  + ' PSI'; }
      if (rawVib  !== null) { this.h1RawVib  = rawVib;  this.h1SensorVib  = rawVib.toFixed(2)  + ' mm/s'; }
      // Detect GDC detection moment (first time health_score drops below 0.85)
      if (d.health_score && d.health_score < 0.85 && !this.h1DetectionTime) {
        this.h1DetectionTime = Date.now();
      }
      // Render the dual-axis PIP/Amps trend chart
      this._renderH1Charts(d);
    },
    _renderH1Charts(d) {
      if (!d || !d.sensors) return;
      const h = this.h1ChartH;
      // EMA smoothing (alpha=0.18): removes tick-level sensor noise while preserving trend direction.
      // Consistent with ISA-101 process trend display practices for DCS/HMI systems.
      const _ema = (vals, alpha) => {
        if (!vals || vals.length === 0) return [];
        const out = [vals[0]];
        for (let i = 1; i < vals.length; i++) out.push(alpha * vals[i] + (1 - alpha) * out[i-1]);
        return out;
      };
      const _spark = (domId, sensorKey, label, color, thresholdY, thresholdDir, unit, decimals) => {
        const el = document.getElementById(domId);
        if (!el) return;
        const sensorData = d.sensors?.[sensorKey];
        const histTrace  = sensorData?.traces?.[0];
        const projTrace  = sensorData?.traces?.[1];
        const coneTrace  = sensorData?.traces?.[2];
        const xs    = histTrace?.x || [];
        const ysRaw = histTrace?.y || [];
        // Apply EMA to smooth display (raw Gaussian noise σ≈65 PSI on ESP nominal, per fault_signatures.py)
        const ys    = _ema(ysRaw, 0.18);
        const liveVal = ys.length ? ys[ys.length - 1] : null;
        const liveStr = liveVal != null ? (liveVal.toFixed(decimals) + ' ' + unit) : '—';
        const alarmFired = liveVal != null && (thresholdDir === 'low' ? liveVal < thresholdY : liveVal > thresholdY);
        const annColor = alarmFired ? '#ef4444' : '#94a3b8';
        // Threshold line (horizontal dashed red at SCADA alarm limit)
        const shapes = [{
          type: 'line', x0: 0, x1: 1, xref: 'paper',
          y0: thresholdY, y1: thresholdY, yref: 'y',
          line: { color: 'rgba(239,68,68,0.55)', width: 1.5, dash: 'dash' }
        }];
        // NOW divider: vertical dotted line separating history from ML projection
        if (projTrace && projTrace.x && projTrace.x.length > 0) {
          shapes.push({
            type: 'line', x0: projTrace.x[0], x1: projTrace.x[0], xref: 'x',
            y0: 0, y1: 1, yref: 'paper',
            line: { color: 'rgba(100,116,139,0.5)', width: 1, dash: 'dot' }
          });
        }
        const annotations = [{
          xref: 'paper', yref: 'paper', x: 0.98, y: 0.96, xanchor: 'right', yanchor: 'top',
          text: '<b>' + liveStr + '</b>',
          font: { size: 13, color: annColor, family: 'monospace' },
          showarrow: false, bgcolor: 'rgba(0,0,0,0)'
        }];
        // Historical trace: smoothed, solid
        const traces = [{
          x: xs, y: ys, type: 'scatter', mode: 'lines', name: label,
          line: { color: color, width: 2 },
          hovertemplate: '<b>' + label + ' (live):</b> %{y:.' + decimals + 'f} ' + unit + '<extra></extra>'
        }];
        // ML Projection trace: dotted, same color — shows where sensor is predicted to go
        if (projTrace && projTrace.y && projTrace.y.length > 0) {
          traces.push({
            x: projTrace.x, y: projTrace.y, type: 'scatter', mode: 'lines', name: 'GDC Forecast',
            line: { color: color, width: 1.5, dash: 'dot' },
            hovertemplate: '<b>' + label + ' forecast:</b> %{y:.' + decimals + 'f} ' + unit + '<extra></extra>'
          });
        }
        // Confidence cone: translucent fill around projection
        if (coneTrace && coneTrace.y && coneTrace.y.length > 0) {
          const coneColorMap = {'#3b82f6':'rgba(59,130,246,0.09)','#22c55e':'rgba(34,197,94,0.09)','#f97316':'rgba(249,115,22,0.09)','#a78bfa':'rgba(167,139,250,0.09)'};
          traces.push({
            x: coneTrace.x, y: coneTrace.y, type: 'scatter', mode: 'none',
            fill: 'toself', fillcolor: coneColorMap[color] || 'rgba(100,116,139,0.08)',
            line: { width: 0 }, hoverinfo: 'skip', showlegend: false, name: 'Confidence'
          });
        }
        const layout = {
          paper_bgcolor: 'transparent', plot_bgcolor: 'rgba(15,23,42,0.25)',
          height: h,
          margin: { l: 40, r: 10, t: 4, b: 24 },
          xaxis: { tickfont: { size: 7, color: '#64748b' }, gridcolor: 'rgba(100,116,139,0.06)', showgrid: true, type: 'date' },
          yaxis: { tickfont: { size: 7, color: color }, gridcolor: 'rgba(100,116,139,0.06)', showgrid: true },
          shapes, annotations, showlegend: false, font: { family: 'monospace' },
        };
        Plotly.react(domId, traces, layout, { responsive: true, displayModeBar: false });
      };
      _spark('h1-spark-psi',  'psi',  'PIP',  '#3b82f6', 800,  'low',  'PSI',   0);
      _spark('h1-spark-amps', 'amps', 'Amps', '#22c55e', 50,   'low',  'A',     1);
      _spark('h1-spark-temp', 'temp', 'Temp', '#f97316', 280,  'high', '°F',    0);
      _spark('h1-spark-vib',  'vib',  'Vib',  '#a78bfa', 8.0,  'high', 'mm/s',  2);
    },
    _renderEnvelopeChart() { /* replaced by _renderH1Charts in Session J */ },
    _legacyEnvelopeShapes() {
      // Retained as dead stub — kept so old watcher references don't crash on rollback
      const shapes = [
        // Green safe zone
        { type: 'rect', x0: 190, x1: 238, y0: 60, y1: 88,
          fillcolor: 'rgba(34,197,94,0.08)', line: { width: 0 }, layer: 'below' },
        // Amber warning zone
        { type: 'rect', x0: 218, x1: 285, y0: 42, y1: 65,
          fillcolor: 'rgba(249,115,22,0.07)', line: { width: 0 }, layer: 'below' },
        // Red gas-lock zone
        { type: 'rect', x0: 225, x1: 308, y0: 20, y1: 58,
          fillcolor: 'rgba(239,68,68,0.10)', line: { width: 0 }, layer: 'below' },
        // SCADA low-amps alarm line (horizontal)
        { type: 'line', x0: 190, x1: 308, y0: 50, y1: 50,
          line: { color: 'rgba(239,68,68,0.55)', width: 1.5, dash: 'dot' } },
        // SCADA high-temp alarm line (vertical)
        { type: 'line', x0: 280, x1: 280, y0: 20, y1: 88,
          line: { color: 'rgba(239,68,68,0.55)', width: 1.5, dash: 'dot' } },
      ];
      const annotations = [
        { x: 210, y: 32, xref:'x', yref:'y', text: 'Gas Lock Zone ⚠',
          showarrow: false, font: { color: 'rgba(239,68,68,0.65)', size: 9 } },
        { x: 210, y: 82, xref:'x', yref:'y', text: 'Safe Operating Zone ✓',
          showarrow: false, font: { color: 'rgba(34,197,94,0.55)', size: 9 } },
        { x: 277, y: 87, xref:'x', yref:'y', text: 'SCADA 280°F',
          showarrow: false, xanchor: 'right', font: { color: 'rgba(239,68,68,0.55)', size: 8 } },
        { x: 308, y: 51.5, xref:'x', yref:'y', text: 'SCADA 50A',
          showarrow: false, font: { color: 'rgba(239,68,68,0.55)', size: 8 } },
        { x: 198, y: 75, xref:'x', yref:'y', text: '✦',
          showarrow: false, font: { color: 'rgba(100,116,139,0.6)', size: 10 } },
      ];
      const layout = {
        paper_bgcolor: '#0b1526', plot_bgcolor: '#131d2e',
        font: { color: '#94a3b8', size: 11 },
        margin: { l: 48, r: 10, t: 10, b: 38 },
        xaxis: { title: 'Motor Winding Temp (°F)', gridcolor: '#1e293b', zeroline: false, range: [190, 310] },
        yaxis: { title: 'Motor Amps (A)', gridcolor: '#1e293b', zeroline: false, range: [18, 90] },
        shapes, annotations, showlegend: false,
      };
      Plotly.react(el, traces, layout, { displayModeBar: false, responsive: true })
        .catch(() => Plotly.newPlot(el, traces, layout, { displayModeBar: false, responsive: true }));
    },
    _renderH1ScadaChart() { /* replaced by _renderH1Charts in Session J */ },
    setH1Sensor(sensor) {
      this.h1ActiveSensor = sensor;
      if (this.h1ForecastData) this._renderH1Charts(this.h1ForecastData);
    },
    initH1SplitterDrag(e) {
      e.preventDefault();
      const startX   = e.clientX;
      const startPct = this.h1SplitPercent;
      const bodyW    = (e.target.parentElement || document.body).offsetWidth;
      e.target.classList.add('dragging');
      const onMove = (ev) => {
        const dx   = ev.clientX - startX;
        const dPct = (dx / bodyW) * 100;
        this.h1SplitPercent = Math.max(25, Math.min(75, startPct + dPct));
        this.$nextTick(() => {
          try { Plotly.Plots.resize(document.getElementById('h1-replay-chart')); } catch(err) {}
        });
      };
      const onUp = () => {
        this.h1Dragging = false;
        e.target.classList.remove('dragging');
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
      };
      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
    },
    initH1CenterSplit(e, side) { this.initH1SplitterDrag(e); }, // backward-compat alias
    initH1ChartVerticalDrag(e) {
      e.preventDefault();
      const startY = e.clientY;
      const startH = this.h1ChartH;
      e.target.classList.add('dragging');
      const onMove = (ev) => {
        const dy = ev.clientY - startY;
        this.h1ChartH = Math.max(80, Math.min(320, startH + dy));
        this.$nextTick(() => {
          ['h1-spark-psi','h1-spark-amps','h1-spark-temp','h1-spark-vib'].forEach(id => {
            try { Plotly.Plots.resize(document.getElementById(id)); } catch(err) {}
          });
          if (this.h1ForecastData) this._renderH1Charts(this.h1ForecastData);
        });
      };
      const onUp = () => {
        this.h1Dragging = false;
        e.target.classList.remove('dragging');
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
      };
      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
    },
    initH1NsSplit(e) { this.initH1ChartVerticalDrag(e); }, // backward-compat alias
    _activateEvidenceWall() {
      const delays = [200, 2000, 3800, 5500, 7200];
      delays.forEach((delay, i) => {
        setTimeout(() => { this.h1EvidenceWall[i].active = true; this.h1EvidenceActive = i + 1; }, delay);
      });
    },
    async _triggerAdvisoryUpdate(type, item) {
      if (this.h1AdvisorStreaming || !this.h1Injected || this.h1Resolved) return;
      const now = Date.now();
      if (now - this.h1AdvisorLastContextTime < 38000) return;  // debounce 38s
      this.h1AdvisorLastContextTime = now;
      const elapsed = Math.max(1, Math.round(this.h1ElapsedMin));
      const d = this.h1ForecastData || {};
      const slopes = d.slopes || {};
      const pipRate = slopes.dpsi_dt != null ? Math.abs(slopes.dpsi_dt).toFixed(0) : null;
      const ampsRate = slopes.ds4_dt != null ? Math.abs(slopes.ds4_dt).toFixed(1) : null;
      const rul = d.time_to_scada_minutes;
      const adj = d.adjusted_rul_minutes;
      let message;
      if (type === 'feed' && item) {
        const detail = (item.detail || item.ai_relevance || '').slice(0, 140);
        message = `New intelligence retrieved: "${item.headline}". ${detail}. `+
          `Status at T+${elapsed}min: PIP ${this.h1SensorPsi||'N/A'}, Amps ${this.h1SensorAmps||'N/A'}. `+
          (pipRate ? `PIP declining ${pipRate} PSI/min. ` : '')+
          (rul ? `Sensor-only estimate: ${Math.round(rul)} min. Context-fused: ${adj?Math.round(adj):rul} min. ` : '')+
          `In 2 sentences: how does this document change or confirm the gas lock diagnosis?`;
      } else if (type === 'urgency') {
        message = `URGENT: T+${elapsed}min elapsed. VFD speed-down option is now MARGINAL. `+
          `PIP ${this.h1SensorPsi||'N/A'}, Amps ${this.h1SensorAmps||'N/A'}. `+
          `In 2 sentences: restate the urgency and whether the $0 option is still executable.`;
      } else if (type === 'critical') {
        message = `CRITICAL: VFD $0 option has EXPIRED at T+${elapsed}min. `+
          `In 2 sentences: what options remain and what is the expected cost?`;
      } else {
        message = `T+${elapsed}min status update. `+
          `PIP ${this.h1SensorPsi||'N/A'}, Amps ${this.h1SensorAmps||'N/A'}, Temp ${this.h1SensorTemp||'N/A'}. `+
          (pipRate ? `PIP declining ${pipRate} PSI/min, amps declining ${ampsRate||'?'} A/min. ` : '')+
          (rul && adj ? `Sensor-only: ${Math.round(rul)}min, context-fused: ${Math.round(adj)}min. ` : '')+
          `In 2 sentences: current urgency level and whether the $0 VFD option remains viable.`;
      }
      this.h1AdvisorHtml += `<br><hr style="border-color:rgba(90,143,192,0.18);margin:7px 0"><span style="font-size:0.58rem;color:var(--muted);font-style:italic">\u2500\u2500 GDC Advisor \u00b7 T+${elapsed}m \u2500\u2500</span><br>`;
      this.h1AdvisorStreaming = true;
      try {
        const r = await fetch('/api/agent/chat', {
          method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({asset_id: this.h1TargetWell||'ESP-ALPHA-1', fault_type: this.h1FaultType||'gas_lock', message, context: this.h1AdvisorText.slice(0,350)})
        });
        if (r.ok) {
          const resp = ((await r.json()).response || '').trim();
          if (resp) {
            let ci = 0;
            const tid = setInterval(() => {
              ci = Math.min(ci + 4, resp.length);
              const spans = document.querySelectorAll('.h1-advisor-body .adv-update');
              if (spans.length) spans[spans.length-1].textContent = resp.slice(0, ci);
              if (ci >= resp.length) { clearInterval(tid); this.h1AdvisorStreaming = false; }
            }, 28);
            this.h1AdvisorHtml += `<span class="adv-update"></span>`;
          } else { this.h1AdvisorStreaming = false; }
        } else { this.h1AdvisorStreaming = false; }
      } catch(e) { this.h1AdvisorStreaming = false; }
    },
    _startAdvisorStream() {
      const base = this.h1GemmaFinding ||
        `Unloading anomaly detected · confidence building on ${this.h1TargetWell||'ESP-ALPHA-1'}. ` +
        `Pump Intake Pressure declining at \u221214 PSI/min\u00b9, motor amps declining at \u22122.3 A/min\u00b9 \u2014 ` +
        `the correlated 4-sensor pattern is the diagnostic signature of gas volume fraction exceeding the pump handling threshold\u2075. ` +
        `Separator gas test confirms GOR 1,310 scf/bbl \u2014 up 19% from prior tour\u00b3. ` +
        `API RP 11S \u00a75.3 identifies VFD speed reduction as the primary intervention\u2075. ` +
        `Your $0 option is viable now. Waiting 18 minutes moves you to the $2,000 tier. Waiting 25 minutes leaves only $150,000.`;
      this.h1AdvisorText = base;
      this.h1AdvisorHtml = '';
      this.h1AdvisorStreaming = true;
      const withHtml = base
        .replace(/\u00b9/g,'<sup style="color:var(--blue);cursor:pointer" title="Source: Sensor Telemetry">[¹]</sup>')
        .replace(/\u00b3/g,'<sup style="color:var(--blue);cursor:pointer" title="Source: Separator Test">[³]</sup>')
        .replace(/\u2075/g,'<sup style="color:var(--blue);cursor:pointer" title="Source: API RP 11S §5.3">[⁵]</sup>');
      let charCount = 0;
      const rawLen = base.length;
      if (this.h1AdvisorTimer) clearInterval(this.h1AdvisorTimer);
      this.h1AdvisorTimer = setInterval(() => {
        charCount = Math.min(charCount + 4, rawLen);
        const slice = base.slice(0, charCount);
        this.h1AdvisorHtml = slice
          .replace(/\u00b9/g,'<sup style="color:var(--blue)">[¹]</sup>')
          .replace(/\u00b3/g,'<sup style="color:var(--blue)">[³]</sup>')
          .replace(/\u2075/g,'<sup style="color:var(--blue)">[⁵]</sup>');
        if (charCount >= rawLen) {
          this.h1AdvisorHtml = withHtml;
          this.h1AdvisorStreaming = false;
          clearInterval(this.h1AdvisorTimer); this.h1AdvisorTimer = null;
        }
      }, 28);
    },
    _updateOptionsViability() {
      const elapsed = this.h1ElapsedMin;
      const total = this.h1WindowTotal || 25; // fallback prevents division-by-zero before window is set
      const frac = elapsed / total;
      // 0.72 / 0.92 = fraction of per-run window at which options expire — ratios, not hardcoded minutes
      if (frac >= 0.92) { this.h1OptA = 'wopt-expired'; this.h1OptALabel = 'EXPIRED'; }
      else if (frac >= 0.72) { this.h1OptA = 'wopt-marginal'; this.h1OptALabel = 'MARGINAL'; }
      else { this.h1OptA = 'wopt-viable'; this.h1OptALabel = 'VIABLE'; }
      if (frac >= 0.92) { this.h1OptB = 'wopt-expired'; this.h1OptBLabel = 'EXPIRED'; }
      else { this.h1OptB = 'wopt-viable'; this.h1OptBLabel = 'VIABLE'; }
    },
    async sendH1Chat() {
      const q = this.h1ChatInput.trim(); if (!q) return;
      this.h1ChatInput = '';
      const uid = Date.now();
      this.h1ChatMessages.push({id: uid+'u', role:'user', text: q});
      this.h1ChatMessages.push({id: uid+'a', role:'assistant', text: '…'});
      try {
        const r = await fetch('/api/agent/chat', {method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({asset_id: this.h1TargetWell||'ESP-ALPHA-1', fault_type: this.h1FaultType||'gas_lock', message: q, context: this.h1AdvisorText.slice(0,600)})});
        if (r.ok) { const d = await r.json(); this.h1ChatMessages[this.h1ChatMessages.length-1].text = d.response || 'No response from model.'; }
        else { this.h1ChatMessages[this.h1ChatMessages.length-1].text = 'Error contacting on-site AI. Please retry.'; }
      } catch(e) { this.h1ChatMessages[this.h1ChatMessages.length-1].text = 'Error contacting on-site AI. Please retry.'; }
    },
    
    // ── Horizon 2: Slug Flow ──
    async launchHorizon2() {
      if (this.h2Injected) return;
      this.h2Injected = true;
      this.h2Resolved = false;
      this.h2TruckRollDispatched = false;
      this.h2SensorVib = '2.4 mm/s ↑';
      this.h2SensorTemp = '198°F — Nominal';
      try {
        const _h2InjR = await fetch('/api/inject/degrade', {method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({asset_id:'ESP-ALPHA-3', fault_type:'slug_flow', duration_seconds:3600})});
        if (_h2InjR.ok) { const _h2InjD = await _h2InjR.json(); if (_h2InjD.injection_params) this.showInjectionPopup(_h2InjD.injection_params); }
        this.showToast('⚡ Slug Flow injected on ESP-ALPHA-3','var(--yellow)');
        const feed=await fetch('/api/intelligence-feed/ESP-ALPHA-3?fault_type=slug_flow');
        if(feed.ok) { const d=await feed.json(); this.h2FeedItems=d.items||[]; this.h2GemmaFinding=d.gemma_finding||'🤖 AI: Vibration drift 1.1→2.4 mm/s with flat motor temperature (198°F). Flowline slugging signature — not downhole motor failure. Dispatch surface technician to adjust choke valve. Do NOT pull well.'; }
        this.h2DegPollTimer = setInterval(async()=>{
          const r=await fetch('/api/degrade-status/ESP-ALPHA-3');
          if(r.ok){const d=await r.json();if(d.is_active){const cs=this.activeDegradesMap['ESP-ALPHA-3']?.current_sensors||{};if(cs.vib)this.h2SensorVib=cs.vib.toFixed(2)+' mm/s ↑';}}
          const rfd=await fetch('/api/plot/forecast-data/ESP-ALPHA-3');
          if(rfd.ok){const d=await rfd.json();if(d.sensors)this._renderH2Charts(d);}
        }, 5000);
      } catch(e) { this.showToast('Error injecting slug flow','var(--red)'); }
    },
    async resetHorizon2() {
      if(this.h2DegPollTimer){clearInterval(this.h2DegPollTimer);this.h2DegPollTimer=null;}
      if(this.h2TruckRollInterval){clearInterval(this.h2TruckRollInterval);this.h2TruckRollInterval=null;}
      try { await fetch('/api/cancel-degrade/ESP-ALPHA-3',{method:'POST'}); } catch{}
      this.h2Injected=false; this.h2Resolved=false; this.h2TruckRollDispatched=false; this.h2TruckRollCountdown=5;
      this.h2SensorVib=null; this.h2SensorTemp=null; this.h2FeedItems=[]; this.h2GemmaFinding='';
      try { Plotly.purge('h2-gdc-chart'); Plotly.purge('h2-scada-chart'); } catch{}
      this.showToast('↺ Horizon 2 reset','var(--green)');
    },

    // ── H2 Scenario Replay methods (Session V) ────────────────────────────
    async loadH2Scenario() {
      this.h2Pause();
      this.h2CursorIdx = 0;
      this.h2VerdictRevealed = false;
      this.h2RagDoc2Shown = false;
      this.h2RagDoc3Shown = false;
      this.h2RagDoc4Shown = false;
      this.h2RagDoc5Shown = false;
      this.h2Resolved = false;
      this.h2PullOutcome = null;
      this.h2ConsoleTab = 'scada';
      if (this.h2RagRevealTimer) { clearTimeout(this.h2RagRevealTimer); this.h2RagRevealTimer = null; }
      if (this.h2RagDoc2Timer)   { clearTimeout(this.h2RagDoc2Timer);   this.h2RagDoc2Timer   = null; }
      if (this.h2RagDoc3Timer)   { clearTimeout(this.h2RagDoc3Timer);   this.h2RagDoc3Timer   = null; }
      if (this.h2RagDoc4Timer)   { clearTimeout(this.h2RagDoc4Timer);   this.h2RagDoc4Timer   = null; }
      if (this.h2RagDoc5Timer)   { clearTimeout(this.h2RagDoc5Timer);   this.h2RagDoc5Timer   = null; }
      this.h2ReplayData = null;
      this.h2ReplayLoading = true;
      try {
        const r = await fetch('/api/h2/scenario-replay');
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const data = await r.json();
        this.h2ReplayData = data;
        this.h2CursorIdx = data.scada_alarm_idx || 0;
        this.h2ReplayLoading = false;
        this.$nextTick(() => { this._renderH2ReplayChart(); });
      } catch(e) {
        this.h2ReplayLoading = false;
        this.showToast(`H2 scenario load failed: ${e.message}`, 'var(--red)');
      }
    },
    h2Play(fast = false) {
      if (!this.h2ReplayData) return;
      this.h2Pause();
      this.h2Playing = true;
      const ms = fast ? 30 : 100;
      this.h2PlayTimer = setInterval(() => {
        if (this.h2CursorIdx >= this.h2ReplayData.n - 1) { this.h2Pause(); return; }
        this.h2CursorIdx++;
      }, ms);
    },
    h2Pause() {
      this.h2Playing = false;
      if (this.h2PlayTimer) { clearInterval(this.h2PlayTimer); this.h2PlayTimer = null; }
    },
    h2Reset() {
      this.h2Pause();
      this.h2CursorIdx = 0;
      this.h2VerdictRevealed = false;
      this.h2RagDoc2Shown = false;
      this.h2RagDoc3Shown = false;
      this.h2RagDoc4Shown = false;
      this.h2RagDoc5Shown = false;
      this.h2Resolved = false;
      this.h2PullOutcome = null;
      if (this.h2RagRevealTimer) { clearTimeout(this.h2RagRevealTimer); this.h2RagRevealTimer = null; }
      if (this.h2RagDoc2Timer)   { clearTimeout(this.h2RagDoc2Timer);   this.h2RagDoc2Timer   = null; }
      if (this.h2RagDoc3Timer)   { clearTimeout(this.h2RagDoc3Timer);   this.h2RagDoc3Timer   = null; }
      if (this.h2RagDoc4Timer)   { clearTimeout(this.h2RagDoc4Timer);   this.h2RagDoc4Timer   = null; }
      if (this.h2RagDoc5Timer)   { clearTimeout(this.h2RagDoc5Timer);   this.h2RagDoc5Timer   = null; }
    },
    h2Scrub(idx) {
      if (!this.h2ReplayData) return;
      this.h2CursorIdx = Math.max(0, Math.min(idx, this.h2ReplayData.n - 1));
    },
    initH2SplitterDrag(e) {
      e.preventDefault();
      const startX   = e.clientX;
      const startPct = this.h2SplitPercent;
      const bodyW    = (e.target.parentElement || document.body).offsetWidth;
      e.target.classList.add('dragging');
      const onMove = (ev) => {
        const dx   = ev.clientX - startX;
        const dPct = (dx / bodyW) * 100;
        this.h2SplitPercent = Math.max(25, Math.min(75, startPct + dPct));
        this.$nextTick(() => {
          try { Plotly.Plots.resize(document.getElementById('h2-replay-chart')); } catch(err) {}
        });
      };
      const onUp = () => {
        e.target.classList.remove('dragging');
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
      };
      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
    },
    _renderH2ReplayChart() {
      const d = this.h2ReplayData;
      if (!d || !d.efficiency || !d.vib) return;
      const cursorT = d.t_min[this.h2CursorIdx]    || 0;
      const gdcT    = d.t_min[d.gdc_detect_idx]     || 0;
      const scadaT  = d.t_min[d.scada_alarm_idx]    || 0;
      const xMax    = d.t_min[d.n - 1]              || 8;
      const HI_VIB  = 4.0; // ISA-18.2 HI alarm (mm/s)

      // Single dual-axis chart: Efficiency % (amber, declining) + Vib mm/s (purple, rising)
      const traces = [
        { x: d.t_min, y: d.efficiency, name: 'Efficiency % (VFD-derived)', type: 'scatter', mode: 'lines',
          line: {color:'#f59e0b', width:2.0}, yaxis:'y', showlegend:true },
        { x: d.t_min, y: d.vib, name: 'Vibration (mm/s)', type: 'scatter', mode: 'lines',
          line: {color:'#a78bfa', width:2.0}, yaxis:'y2', showlegend:true },
        { x: [0, xMax], y: [HI_VIB, HI_VIB],
          name: 'ISA HI 4.0', type: 'scatter', mode: 'lines',
          line: {color:'rgba(239,68,68,0.55)', width:1.2, dash:'dash'},
          yaxis:'y2', showlegend:true, hoverinfo:'skip' },
        ...(d.roll_vib ? [{
          x: d.t_min, y: d.roll_vib,
          name: 'Rolling avg vib (SCADA trips on)',
          type: 'scatter', mode: 'lines',
          line: {color:'rgba(239,68,68,0.28)', width:1.0, dash:'dot'},
          yaxis:'y2', showlegend:true, hoverinfo:'skip'
        }] : []),
      ];

      const shapes = [
        { type:'line', x0:gdcT,    x1:gdcT,    y0:0, y1:1, xref:'x', yref:'paper',
          line:{color:'rgba(251,191,36,0.88)', width:2, dash:'dash'} },
        { type:'line', x0:scadaT,  x1:scadaT,  y0:0, y1:1, xref:'x', yref:'paper',
          line:{color:'rgba(239,68,68,0.88)',   width:2, dash:'dash'} },
        // Cursor (gray dot) — shape index 2, updated cheaply via relayout
        { type:'line', x0:cursorT, x1:cursorT, y0:0, y1:1, xref:'x', yref:'paper',
          line:{color:'rgba(148,163,184,0.6)',  width:1.5, dash:'dot'} },
      ];

      const annotations = [
        { x:gdcT,   y:1.01, xref:'x', yref:'paper',
          text:'<b>GDC \u25B2</b><br>health &lt;0.65 \u00b7 vib ~half HI limit',
          showarrow:false, xanchor:'left', yanchor:'bottom',
          font:{color:'rgba(251,191,36,0.95)', size:7.5, family:'Inter,sans-serif'},
          bgcolor:'rgba(251,191,36,0.08)', borderpad:1 },
        { x:scadaT, y:1.01, xref:'x', yref:'paper',
          text:'<b>SCADA \u25B2</b><br>single-tag 4.0\u202fmm/s crossed',
          showarrow:false, xanchor:'left', yanchor:'bottom',
          font:{color:'rgba(239,68,68,0.95)',   size:7.5, family:'Inter,sans-serif'},
          bgcolor:'rgba(239,68,68,0.08)',   borderpad:1 },
        { x:0, y:-0.20, xref:'paper', yref:'paper',
          text:'vs threshold SCADA only (~85% of wells)',
          showarrow:false, xanchor:'left', yanchor:'top',
          font:{color:'rgba(100,116,139,0.50)', size:6, family:'Inter,sans-serif'} },
      ];

      Plotly.newPlot('h2-replay-chart', traces, {
        paper_bgcolor:'#131d31', plot_bgcolor:'#131d31',
        font:{color:'#e0e0e0', family:'Inter,sans-serif', size:9},
        margin:{l:50, r:52, t:18, b:36},
        xaxis:  {gridcolor:'#1e2a38', zeroline:false, range:[0, xMax],
                 title:{text:'Weeks since last treatment', font:{size:8, color:'#5a6a7a'}},
                 tickfont:{size:7}},
        yaxis:  {gridcolor:'#1e2a38', zeroline:false,
                 title:{text:'Efficiency (%)', font:{color:'#f59e0b', size:8}},
                 tickfont:{size:8, color:'#f59e0b'}, nticks:5, side:'left'},
        yaxis2: {overlaying:'y', zeroline:false,
                 title:{text:'Vib (mm/s)', font:{color:'#a78bfa', size:8}},
                 tickfont:{size:8, color:'#a78bfa'}, nticks:5, side:'right'},
        shapes, annotations,
        showlegend:true,
        legend:{orientation:'h', x:0, y:1.07, xanchor:'left', font:{size:8},
                bgcolor:'rgba(11,12,16,0.7)'},
      }, {displayModeBar:false, responsive:true});
    },
    async dispatchTruckRoll() {
      if(this.h2TruckRollDispatched) return;
      this.h2Pause(); // lock transport on remediation
      this.h2TruckRollDispatched = true;
      this.h2TruckRollCountdown = 5;
      // Find the most recent unacknowledged slug_flow event for ESP-ALPHA-3
      let eventId = 0;
      try {
        const evResp = await fetch('/api/recent-events?limit=50');
        const evData = await evResp.json();
        const match = (evData.events || []).find(e =>
          e.asset_id === 'ESP-ALPHA-3' &&
          (e.failure_type || '').toLowerCase() === 'slug_flow' &&
          !e.acknowledged
        );
        if(match) eventId = match.id;
      } catch(e) { console.warn('truck-roll event lookup failed', e); }
      // POST to backend — writes DB entry, starts 5s resolution timer server-side
      try {
        await fetch('/api/agent/truck-roll', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({asset_id: 'ESP-ALPHA-3', event_id: eventId})
        });
      } catch(e) { console.warn('truck-roll dispatch failed', e); }
      // Start UI countdown (mirrors backend 5s timer)
      this.h2TruckRollInterval = setInterval(() => {
        this.h2TruckRollCountdown--;
        if(this.h2TruckRollCountdown <= 0) {
          clearInterval(this.h2TruckRollInterval);
          this.h2TruckRollInterval = null;
          this.h2Resolved = true;
          if(this.h2DegPollTimer){clearInterval(this.h2DegPollTimer);this.h2DegPollTimer=null;}
          fetch('/api/cancel-degrade/ESP-ALPHA-3',{method:'POST'}).catch(()=>{});
          this.showToast('✅ Choke adjustment dispatched — slug flow expected to subside','var(--green)');
        }
      }, 1000);
      this.showToast('🚛 Technician dispatched to ESP-ALPHA-3 wellsite','var(--yellow)');
    },
    _renderH2Charts(d) {
      const s=d.sensors?.vib; if(!s) return;
      const darkLayout={paper_bgcolor:'#131d31',plot_bgcolor:'#131d31',font:{color:'#a0b0c0',size:11},margin:{l:40,r:10,t:8,b:36},xaxis:{gridcolor:'#1e2a38'},yaxis:{gridcolor:'#1e2a38',title:'Vibration (mm/s)'}};
      const gdcEl=document.getElementById('h2-gdc-chart');
      if(gdcEl){ Plotly.react(gdcEl,s.traces,{...darkLayout,...(s.layout||{})},{displayModeBar:false,responsive:true}).catch(()=>Plotly.newPlot(gdcEl,s.traces,darkLayout,{displayModeBar:false,responsive:true})); }
      const scadaEl=document.getElementById('h2-scada-chart');
      if(scadaEl&&s.traces?.length>0){
        const scadaTraces=[{...s.traces[0]},{type:'scatter',x:s.traces[0]?.x||[],y:Array(s.traces[0]?.x?.length||2).fill(5.0),mode:'lines',name:'SCADA Trip (5.0 mm/s)',line:{color:'#f44336',dash:'dash',width:1.5},hoverinfo:'skip'}];
        Plotly.react(scadaEl,scadaTraces,{...darkLayout,title:{text:'SCADA: 5.0 mm/s trip limit not reached',font:{color:'var(--green)',size:11}}},{displayModeBar:false,responsive:true}).catch(()=>{});
      }
    },
    
    // ── Horizon 3: Bayesian Optimization ──
      async runVizierOptimize() {
      try {
        const r=await fetch(`/api/vizier/optimize?oil_price=${this.oilPriceSlider}&horizon_days=${this.horizonSlider}&constraint=${this.h3ActiveConstraint}`);
        if(r.ok){
          const d=await r.json();
          this.optTrials=d.trials||[];
          this.optScadaNominal=d.scada_nominal||{};
          this.optRunToFailure=d.run_to_failure||{};
          this.optVizierOptimal=d.vizier_optimal||{};
          this.optOptimalHz=d.optimal_hz;
          this.optWells=d.wells||[];
          this.optJointOptimal=d.joint_optimal||{};
          this.optIndependentBaseline=d.independent_baseline||{};
          this.optConstraintStack=d.constraint_stack||{};
          this.constraintDoc=d.constraint_doc||{};
          this.optCurtailment=d.curtailment||{};
          this.vizierDeployed=false;
          this.$nextTick(()=>this._renderVizierPareto());
        }
      } catch(e){ this.showToast('Error running Vizier optimization','var(--red)'); }
    },
    async deployVizierOptimal() {
      if(this.vizierDeployed) return;
      this.vizierDeploying=true;
      const savings=(this.optVizierOptimal.cash_flow||0)-(this.optScadaNominal.cash_flow||0);
      try {
        await fetch('/api/vizier/deploy',{method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify({oil_price:this.oilPriceSlider,horizon_days:this.horizonSlider,deployed_hz:this.optOptimalHz,net_savings:savings})});
        this.vizierDeployed=true;
        this.showToast(`✅ Vizier VFD ${this.optOptimalHz} Hz deployed. $${savings.toLocaleString()} projected savings.`,'var(--green)');
      } catch(e){ this.showToast('Error deploying recommendation','var(--red)'); }
      this.vizierDeploying=false;
    },
    _renderVizierPareto() {
      const el=document.getElementById('vizier-pareto-chart');
      if(!el||!this.optTrials.length) return;
      const failures=this.optTrials.filter(t=>t.is_failure&&!t.is_optimal);
      const successes=this.optTrials.filter(t=>!t.is_failure&&!t.is_optimal);
      const optimal=this.optTrials.filter(t=>t.is_optimal);
      const traces=[
        {type:'scatter',mode:'markers',x:successes.map(t=>t.vfd_hz),y:successes.map(t=>t.cash_flow),name:'Trial (No Burnout)',customdata:successes.map(t=>t.rul_days),hovertemplate:'<b>%{x} Hz</b><br>Cash Flow: $%{y:,.0f}<br>RUL: %{customdata}d<extra>Trial (No Burnout)</extra>',marker:{color:'rgba(30,144,255,0.7)',size:10}},
        {type:'scatter',mode:'markers',x:failures.map(t=>t.vfd_hz),y:failures.map(t=>t.cash_flow),name:'Trial (Pump Burnout)',customdata:failures.map(t=>t.rul_days),hovertemplate:'<b>%{x} Hz</b><br>Cash Flow: $%{y:,.0f}<br>RUL: %{customdata}d ⚠ BURNOUT<extra>Trial (Pump Burnout)</extra>',marker:{color:'rgba(244,67,54,0.7)',size:10,symbol:'x'}},
        {type:'scatter',mode:'markers',x:optimal.map(t=>t.vfd_hz),y:optimal.map(t=>t.cash_flow),name:'⭐ Optimal',customdata:optimal.map(t=>t.rul_days),hovertemplate:'<b>⭐ OPTIMAL: %{x} Hz</b><br>Cash Flow: $%{y:,.0f}<br>RUL: %{customdata}d<extra>Vizier Optimal</extra>',marker:{color:'#ff8c00',size:16,symbol:'star'}},
        {type:'scatter',mode:'markers',x:[this.optScadaNominal.vfd_hz],y:[this.optScadaNominal.cash_flow],name:'SCADA Nominal',customdata:[this.optScadaNominal.rul_days||0],hovertemplate:'<b>SCADA Nominal: %{x} Hz</b><br>Cash Flow: $%{y:,.0f}<br>RUL: %{customdata}d<extra>SCADA Nominal</extra>',marker:{color:'#5a6a7a',size:12,symbol:'diamond'}},
      ];
      const layout={paper_bgcolor:'#131d31',plot_bgcolor:'#131d31',font:{color:'#a0b0c0',size:11},margin:{l:60,r:20,t:20,b:50},xaxis:{title:'VFD Frequency (Hz)',gridcolor:'#1e2a38'},yaxis:{title:'Net Cash Flow ($)',gridcolor:'#1e2a38'},legend:{bgcolor:'rgba(19,29,49,0.7)',bordercolor:'#1e2a38',borderwidth:1}};
      Plotly.react(el,traces,layout,{displayModeBar:false,responsive:true}).catch(()=>Plotly.newPlot(el,traces,layout,{displayModeBar:false,responsive:true}));
    },
    
    initCanvasSplitter() {
      const splitter = this.$refs.canvasSplitter;
      if (!splitter) return;
      let startX = 0, startW = 0;
      const onMove = (e) => {
        const delta = startX - e.clientX;
        this.activityStreamWidth = Math.min(600, Math.max(180, startW + delta));
      };
      const onUp = () => {
        splitter.classList.remove('dragging');
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      };
      splitter.addEventListener('mousedown', (e) => {
        e.preventDefault();
        startX = e.clientX;
        startW = this.activityStreamWidth;
        splitter.classList.add('dragging');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onUp);
      });
    },
  },

  mounted() {
    // ── App-level font zoom: +/= zoom in, - zoom out, 0 reset ──────────────
    // Adjusts body font-size; all rem-based sizes scale proportionally.
    // Persists to localStorage — survives reload. Active only on main app
    // (slides own +/- inside their iframe and don't propagate to parent).
    const _APP_BASE_FS = 13;
    const _savedFs = parseInt(localStorage.getItem('gdc.app.fontsize') || _APP_BASE_FS, 10);
    document.body.style.fontSize = _savedFs + 'px';
    this._appZoomHandler = (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      // Cmd/Ctrl/Alt combos (native browser zoom) pass through — only intercept bare +/-/0
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      const fs = parseInt(document.body.style.fontSize || _APP_BASE_FS, 10);
      let _zoomMsg = null;
      if (e.key === '+' || e.key === '=') {
        const nv = Math.min(22, fs + 1);
        document.body.style.fontSize = nv + 'px';
        localStorage.setItem('gdc.app.fontsize', nv);
        this.showToast(`App zoom: ${Math.round(nv / _APP_BASE_FS * 100)}% (+/- to adjust, 0 = reset)`, 'var(--surf2)');
        e.preventDefault();
        _zoomMsg = 'zoom-in';
      } else if (e.key === '-' || e.key === '_') {
        const nv = Math.max(9, fs - 1);
        document.body.style.fontSize = nv + 'px';
        localStorage.setItem('gdc.app.fontsize', nv);
        this.showToast(`App zoom: ${Math.round(nv / _APP_BASE_FS * 100)}% (+/- to adjust, 0 = reset)`, 'var(--surf2)');
        e.preventDefault();
        _zoomMsg = 'zoom-out';
      } else if (e.key === '0') {
        document.body.style.fontSize = _APP_BASE_FS + 'px';
        localStorage.removeItem('gdc.app.fontsize');
        this.showToast('App zoom: 100% (reset)', 'var(--surf2)');
        e.preventDefault();
        _zoomMsg = 'zoom-reset';
      }
      // Forward zoom command to any active briefing iframes (e.g. /slides/h1.html)
      if (_zoomMsg) {
        document.querySelectorAll('iframe').forEach(function(f) {
          try { f.contentWindow.postMessage(_zoomMsg, '*'); } catch(_) {}
        });
      }
    };
    document.addEventListener('keydown', this._appZoomHandler);

    this.loadGrafana();
    this.fetchKpis();this.fetchHorizonAlerts();this.fetchMlopsStatus();
    this.fetchInjectionLog();
    this._pollKpis=setInterval(()=>{this.fetchKpis();this.lastRefresh=new Date().toLocaleTimeString();},10000);
    this._pollHorizon=setInterval(()=>this.fetchHorizonAlerts(),5000);
    this._pollMlops=setInterval(()=>this.fetchMlopsStatus(),15000);
    this.lastRefresh=new Date().toLocaleTimeString();
    this.$nextTick(()=>{
      this.initCanvasSplitter();
      // Slide postMessage handler — Session BS+10: briefing iframes hand off to Vue replay.
      // run-h1 / run-h2 / run-h3: last panel ▶ button → dismiss briefing + start scenario.
      // go-horizon1: intro deck "▶ View Demo →" → switch to H1 tab.
      this._slideMsg = (e) => {
        if      (e.data === 'run-h1')      { this.h1BriefingMode = false; this.loadH1Scenario(); }
        else if (e.data === 'run-h2')      { this.h2BriefingMode = false; this.loadH2Scenario(); }
        else if (e.data === 'run-h3')      { this.h3BriefingMode = false; this.runVizierOptimize(); }
        else if (e.data === 'go-horizon1') { this.setMainTab('horizon1'); }
      };
      window.addEventListener('message', this._slideMsg);

      // BS+22 LC-fatigue fix: pause all CSS animations when browser tab is hidden.
      // Sustained fast-cycling animations drive rapid LC voltage changes; the resulting
      // liquid-crystal orientation hysteresis causes pixel "charge" that takes 10-30s
      // to dissipate after the page navigates away.
      // body.gdc-tab-hidden rule in styles.css applies animation-play-state:paused to all.
      this._visibilityHandler = () => {
        document.body.classList.toggle('gdc-tab-hidden', document.hidden);
      };
      document.addEventListener('visibilitychange', this._visibilityHandler);
    });
  },

  beforeUnmount() {
    [this._pollKpis,this._pollHorizon,this._pollMlops].forEach(t=>t&&clearInterval(t));
    this.stopDegPoll();
    if (this._slideMsg) window.removeEventListener('message', this._slideMsg);
    if (this._appZoomHandler) document.removeEventListener('keydown', this._appZoomHandler);
    if (this._visibilityHandler) document.removeEventListener('visibilitychange', this._visibilityHandler);
  },
}).mount('#app');
console.log("=== app.js mounted successfully ===");
