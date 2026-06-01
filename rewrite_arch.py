#!/usr/bin/env python3
"""
Rewrite the Architecture tab in index.html with:
- Narrative text moved to ⓘ info modals (on-demand)
- Full-width diagrams in all 6 panes
- Pane 1: sensor chips, ML Anomaly Detection label, E-House narrative
- Pane 2: Field-of-Pads (6 pads, 38 wells total)
- Pane 4: Parallel-stream layout into AlloyDB
- archInfoOpen state added to Vue data()
"""
import re

FILE = 'gke/fault-trigger-ui/index.html'

with open(FILE, 'r') as f:
    html = f.read()

# ──────────────────────────────────────────────────────────────────────────────
# 1. Add archInfoOpen: false to Vue data()
# ──────────────────────────────────────────────────────────────────────────────
html = html.replace(
    "archPane: 'overview',",
    "archPane: 'overview',\n      archInfoOpen: false,"
)

# ──────────────────────────────────────────────────────────────────────────────
# 2. Replace the entire Architecture tab block
# ──────────────────────────────────────────────────────────────────────────────

NEW_ARCH_TAB = r"""        <!-- ══ TAB: ARCHITECTURE ══ -->
    <div id="tab-architecture" class="main-tab-content" :class="{active: mainTab==='architecture'}">
      <div class="arch-outer">

        <!-- Sub-tab navigation bar -->
        <div class="arch-sub-nav">
          <div class="arch-sub-tab" :class="{active: archPane==='overview'}" @click="archPane='overview';archInfoOpen=false">
            <span class="ast-num">1</span> System Overview
          </div>
          <div class="arch-sub-tab" :class="{active: archPane==='ingestion'}" @click="archPane='ingestion';archInfoOpen=false">
            <span class="ast-num">2</span> Data Ingestion
          </div>
          <div class="arch-sub-tab" :class="{active: archPane==='detection'}" @click="archPane='detection';archInfoOpen=false">
            <span class="ast-num">3</span> ML Detection
          </div>
          <div class="arch-sub-tab" :class="{active: archPane==='context'}" @click="archPane='context';archInfoOpen=false">
            <span class="ast-num">4</span> Context Fusion
          </div>
          <div class="arch-sub-tab" :class="{active: archPane==='reasoning'}" @click="archPane='reasoning';archInfoOpen=false">
            <span class="ast-num">5</span> AI Reasoning
          </div>
          <div class="arch-sub-tab" :class="{active: archPane==='operator'}" @click="archPane='operator';archInfoOpen=false">
            <span class="ast-num">6</span> Operator Value
          </div>
        </div>

        <!-- ── Pane 1: System Overview ── -->
        <div class="arch-pane" :class="{active: archPane==='overview'}">
          <div class="arch-pane-hdr" style="display:flex;align-items:flex-start;gap:12px">
            <div style="flex:1">
              <h2>GDC Edge AI — Complete Pipeline</h2>
              <p>End-to-end view of how sensor telemetry becomes actionable maintenance intelligence, entirely on-cluster with no public cloud dependency.</p>
            </div>
            <button class="arch-info-btn" @click="archInfoOpen=!archInfoOpen" title="Technical Details">ⓘ</button>
          </div>

          <!-- ⓘ Info Panel: Pane 1 -->
          <div v-if="archInfoOpen && archPane==='overview'" class="arch-info-panel">
            <div class="arch-info-close" @click="archInfoOpen=false">✕ Close</div>
            <div class="arch-info-section">
              <div class="arch-info-title">🌐 Deployment Location: Multi-Well Pad E-House</div>
              <ul>
                <li>GDC Software Only runs on customer-provided ruggedized hardware (e.g. Dell PowerEdge XR, HPE Edgeline) installed inside the climate-controlled <strong>E-House (Electrical House)</strong> on the well pad.</li>
                <li>The E-House already houses the VFDs, motor control centers, and PLCs — the GDC server shares this protected, powered environment.</li>
                <li>All sensors stream to the GDC server over the <strong>local hardwired field network</strong> at 5-second cadence — no WAN required for data acquisition.</li>
                <li>Only low-bandwidth insights (health scores, alerts, recommendations) are transmitted over the slow VSAT/LTE backhaul to central SCADA/headquarters.</li>
              </ul>
            </div>
            <div class="arch-info-section">
              <div class="arch-info-title">⚙️ GKE Cluster Components (On-Prem)</div>
              <ul>
                <li><strong>RabbitMQ</strong> — Durable message broker; survives pod restarts without data loss</li>
                <li><strong>Inference API</strong> — XGBoost ML model serving via FastAPI; deterministic, explainable anomaly detection</li>
                <li><strong>AlloyDB Omni</strong> — PostgreSQL + pgvector; unified store for telemetry, ML outputs, and RAG documents</li>
                <li><strong>Ollama + Gemma 27b</strong> — Local LLM on NVIDIA L4 GPU; RAG synthesis and fault reasoning</li>
                <li><strong>Fault Trigger UI</strong> — Demo control console + live operator interface</li>
                <li><strong>Event Processor</strong> — RabbitMQ consumer; routes telemetry to ML inference and AlloyDB</li>
              </ul>
            </div>
            <div class="arch-info-section">
              <div class="arch-info-title">🔒 Why Not Cloud?</div>
              <ul>
                <li>38-well fleet generates ~200GB/day of raw telemetry — economically infeasible to backhaul over VSAT at $0.015/MB</li>
                <li>Gas Lock point-of-no-return: 25 minutes. VSAT round-trip latency: 15–25 minutes. Cloud analytics cannot deliver the alert in time.</li>
                <li>Production rates and reservoir pressure data are commercially sensitive — must remain on-premises</li>
                <li>WAN outages occur regularly offshore and in remote land operations. GDC continues monitoring through any network interruption.</li>
              </ul>
            </div>
          </div>

          <div class="arch-pane-body" style="display:block">
            <!-- Full-width flow diagram -->
            <div style="display:flex;gap:8px;align-items:stretch;flex-wrap:wrap;margin-bottom:18px">

              <div class="arch-stage stage-sensor" style="flex:1;min-width:110px">
                <div class="arch-stage-title">📡 1. Field Sensors</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-blue"><span>ESP Wells</span></div>
                  <div class="arch-chip chip-blue"><span>Intake PSI</span></div>
                  <div class="arch-chip chip-orange"><span>Winding Temp</span></div>
                  <div class="arch-chip chip-orange"><span>Vibration mm/s</span></div>
                  <div class="arch-chip chip-blue"><span>Motor Amps</span></div>
                  <div class="arch-chip chip-muted" style="opacity:0.6"><span style="font-style:italic">Fault Injector (demo)</span></div>
                </div>
              </div>

              <div style="display:flex;align-items:center;color:rgba(255,255,255,0.2);font-size:1.4rem;padding-top:10px">→</div>

              <div class="arch-stage stage-broker" style="flex:1;min-width:110px">
                <div class="arch-stage-title">📨 2. Edge Bus</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-orange"><span>RabbitMQ Broker</span></div>
                  <div class="arch-chip chip-muted"><span style="font-size:0.62rem">5s telemetry cadence</span></div>
                  <div class="arch-chip chip-muted"><span style="font-size:0.62rem">Local field network</span></div>
                </div>
              </div>

              <div style="display:flex;align-items:center;color:rgba(255,255,255,0.2);font-size:1.4rem;padding-top:10px">→</div>

              <div class="arch-stage stage-ml" style="flex:1;min-width:110px">
                <div class="arch-stage-title">⚡ 3. ML Anomaly Detection</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-orange"><span>XGBoost Health Score</span></div>
                  <div class="arch-chip chip-muted"><span style="font-size:0.62rem">6-feature sensor vector</span></div>
                  <div class="arch-chip chip-muted"><span style="font-size:0.62rem">No unstructured data</span></div>
                </div>
              </div>

              <div style="display:flex;align-items:center;color:rgba(255,255,255,0.2);font-size:1.4rem;padding-top:10px">→</div>

              <div class="arch-stage stage-db" style="flex:1;min-width:110px">
                <div class="arch-stage-title">🗄 4. Context Store</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-blue"><span>AlloyDB + pgvector</span></div>
                  <div class="arch-chip chip-purple"><span>RAG Manuals</span></div>
                  <div class="arch-chip chip-blue"><span>Field Intel</span></div>
                  <div class="arch-chip chip-orange"><span>ML Assessments</span></div>
                </div>
              </div>

              <div style="display:flex;align-items:center;color:rgba(255,255,255,0.2);font-size:1.4rem;padding-top:10px">→</div>

              <div class="arch-stage stage-llm" style="flex:1;min-width:110px">
                <div class="arch-stage-title">🧠 5. AI Context Fusion</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-purple"><span>Gemma 27b (GPU)</span></div>
                  <div class="arch-chip chip-orange"><span>AI-Informed RUL</span></div>
                  <div class="arch-chip chip-green"><span>Action Recommendation</span></div>
                </div>
              </div>

              <div style="display:flex;align-items:center;color:rgba(255,255,255,0.2);font-size:1.4rem;padding-top:10px">→</div>

              <div class="arch-stage stage-ui" style="flex:1;min-width:110px">
                <div class="arch-stage-title">👤 6. Operator</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-green"><span>HITL Decision</span></div>
                  <div class="arch-chip chip-green"><span>ROI Ledger</span></div>
                </div>
              </div>

            </div><!-- flow row -->

            <!-- Key differentiator comparison -->
            <div class="arch-compare-row">
              <div class="arch-compare-card acc-scada">
                <div class="acc-title acc-title-scada">🛢 Traditional SCADA Only</div>
                <ul class="acc-items">
                  <li class="no">Single-threshold alarm only</li>
                  <li class="no">15-min downsampled WAN poll</li>
                  <li class="no">No unstructured data fusion</li>
                  <li class="no">Reactive emergency dispatch</li>
                </ul>
              </div>
              <div class="arch-compare-card acc-gdc">
                <div class="acc-title acc-title-gdc">⚡ GDC Edge AI (E-House)</div>
                <ul class="acc-items">
                  <li class="yes">Multivariate ML detection</li>
                  <li class="yes">5s local stream — no WAN needed</li>
                  <li class="yes">OEM manuals + ops records fused</li>
                  <li class="yes">Scheduled proactive intervention</li>
                </ul>
              </div>
            </div>
          </div>
        </div><!-- pane overview -->

        <!-- ── Pane 2: Data Ingestion ── -->
        <div class="arch-pane" :class="{active: archPane==='ingestion'}">
          <div class="arch-pane-hdr" style="display:flex;align-items:flex-start;gap:12px">
            <div style="flex:1">
              <h2>Data Ingestion — Regional Field Network to Edge Bus</h2>
              <p>High-frequency telemetry from 38 ESP wells across 6 pads flows over the local field-mesh network to the RabbitMQ edge broker every 5 seconds, completely bypassing the slow WAN backhaul to central SCADA.</p>
            </div>
            <button class="arch-info-btn" @click="archInfoOpen=!archInfoOpen" title="Technical Details">ⓘ</button>
          </div>

          <!-- ⓘ Info Panel: Pane 2 -->
          <div v-if="archInfoOpen && archPane==='ingestion'" class="arch-info-panel">
            <div class="arch-info-close" @click="archInfoOpen=false">✕ Close</div>
            <div class="arch-info-section">
              <div class="arch-info-title">📡 Sensor Physics</div>
              <ul>
                <li><strong style="color:var(--blue)">Intake PSI</strong> — Pump inlet pressure. Drop below 180 PSI indicates gas lock or low reservoir pressure. Nominal: 220–280 PSI.</li>
                <li><strong style="color:var(--orange)">Winding Temp °F</strong> — Motor insulation health. Class H limit: 284°F. Gas lock causes heat buildup as the motor runs dry.</li>
                <li><strong style="color:var(--orange)">Vibration mm/s</strong> — Impeller/bearing wear indicator. Nominal: <0.05 mm/s. Failure threshold: >0.50 mm/s (ISO 10816-3).</li>
                <li><strong style="color:var(--blue)">Motor Amps</strong> — VFD current draw. Rising trend = increasing mechanical resistance (sand ingress, scale buildup).</li>
              </ul>
              <div class="arch-callout callout-blue">All 4 sensors are correlated simultaneously by the XGBoost model. No single sensor in isolation is sufficient to detect faults early — it's the pattern across all four that matters.</div>
            </div>
            <div class="arch-info-section">
              <div class="arch-info-title">🔌 Why RabbitMQ?</div>
              <ul>
                <li>Durable queues survive pod restarts without data loss — critical for unattended well-pad operations</li>
                <li>Topic exchange allows multiple consumers (ML inference, SCADA historian, Grafana) from the same message stream</li>
                <li>Tested at 12 messages/second sustained throughput per pod on this cluster</li>
              </ul>
            </div>
            <div class="arch-info-section">
              <div class="arch-info-title">📶 Local Field Network vs. WAN</div>
              <ul>
                <li>The 5s telemetry stream is pulled over a local high-speed field-mesh network within the pad facility — no WAN link involved in data acquisition</li>
                <li>Central SCADA in headquarters polls over a VSAT/LTE backhaul — typically receiving 15-minute averages only due to bandwidth constraints</li>
                <li>GDC protects the WAN link by transmitting only insights (kilobytes), not raw telemetry (gigabytes)</li>
              </ul>
            </div>
          </div>

          <div class="arch-pane-body" style="display:block">
            <!-- Regional field network -->
            <div class="arch-stage stage-sensor" style="margin-bottom:12px">
              <div class="arch-stage-title">📡 Regional Field Network — 38 ESP Wells Aggregated</div>
              <div class="arch-stage-body" style="flex-wrap:wrap;gap:6px">
                <div class="arch-chip chip-blue"><span class="arch-chip-label">Pad Alpha</span><span class="arch-chip-val">6 Wells</span></div>
                <div class="arch-chip chip-blue"><span class="arch-chip-label">Pad Bravo</span><span class="arch-chip-val">8 Wells</span></div>
                <div class="arch-chip chip-blue"><span class="arch-chip-label">Pad Charlie</span><span class="arch-chip-val">4 Wells</span></div>
                <div class="arch-chip chip-blue"><span class="arch-chip-label">Pad Delta</span><span class="arch-chip-val">6 Wells</span></div>
                <div class="arch-chip chip-blue"><span class="arch-chip-label">Pad Echo</span><span class="arch-chip-val">8 Wells</span></div>
                <div class="arch-chip chip-blue"><span class="arch-chip-label">Pad Foxtrot</span><span class="arch-chip-val">6 Wells</span></div>
              </div>
              <div style="font-size:0.6rem;color:var(--muted);margin-top:8px;font-style:italic">GDC Software Only on customer hardware · E-House at Central Battery · Local field-mesh network (no WAN)</div>
            </div>

            <div class="arch-connector">↓ <span class="arch-connector-label">High-speed local field-mesh · 5s continuous telemetry stream · bypasses slow WAN backhaul</span></div>

            <!-- Telemetry payload -->
            <div class="arch-stage stage-db" style="margin-bottom:12px">
              <div class="arch-stage-title">📦 Telemetry Payload (per reading, per well)</div>
              <div class="arch-stage-body">
                <div class="arch-chip chip-blue"><span class="arch-chip-label">Intake</span><span class="arch-chip-val">PSI</span></div>
                <div class="arch-chip chip-orange"><span class="arch-chip-label">Winding</span><span class="arch-chip-val">Temp °F</span></div>
                <div class="arch-chip chip-orange"><span class="arch-chip-label">Vibration</span><span class="arch-chip-val">mm/s</span></div>
                <div class="arch-chip chip-blue"><span class="arch-chip-label">VFD</span><span class="arch-chip-val">Motor Amps</span></div>
                <div class="arch-chip chip-muted"><span class="arch-chip-label">Source</span><span class="arch-chip-val">asset_id</span></div>
                <div class="arch-chip chip-muted"><span class="arch-chip-label">Type</span><span class="arch-chip-val">fault_label</span></div>
              </div>
            </div>

            <div class="arch-connector">↓ <span class="arch-connector-label">Published to sensor.reading routing key</span></div>

            <!-- Broker -->
            <div class="arch-stage stage-broker" style="margin-bottom:12px">
              <div class="arch-stage-title">📨 RabbitMQ Edge Broker</div>
              <div class="arch-stage-body">
                <div class="arch-chip chip-orange"><span class="arch-chip-label">Exchange</span><span class="arch-chip-val">telemetry (topic)</span></div>
                <div class="arch-chip chip-orange"><span class="arch-chip-label">Queue</span><span class="arch-chip-val">telemetry.events</span></div>
                <div class="arch-chip chip-muted"><span class="arch-chip-label">Durability</span><span class="arch-chip-val">Persistent</span></div>
                <div class="arch-chip chip-muted"><span class="arch-chip-label">Consumers</span><span class="arch-chip-val">Event Processor</span></div>
              </div>
            </div>

            <div class="arch-connector">↓ <span class="arch-connector-label">Consumed by Event Processor pod</span></div>

            <!-- Demo note -->
            <div class="arch-stage stage-scada" style="opacity:0.75;border-style:dashed">
              <div class="arch-stage-title" style="color:var(--muted)">⚙️ Fault Injector (Demo Only)</div>
              <div class="arch-stage-body">
                <div class="arch-chip chip-muted"><span>Overrides nominal sensor values to simulate fault conditions</span></div>
                <div class="arch-chip chip-muted"><span>Simulates gas_lock, sand_ingress, overheat signatures</span></div>
                <div class="arch-chip chip-muted"><span>In production: replaced by real VFD/PLC OPC-UA feed</span></div>
              </div>
            </div>
          </div>
        </div><!-- pane ingestion -->

        <!-- ── Pane 3: ML Detection ── -->
        <div class="arch-pane" :class="{active: archPane==='detection'}">
          <div class="arch-pane-hdr" style="display:flex;align-items:flex-start;gap:12px">
            <div style="flex:1">
              <h2>ML Anomaly Detection — XGBoost Health Scoring</h2>
              <p>A trained XGBoost model ingests 6 input features (4 sensor readings + 2 rolling rate-of-change slopes) and outputs a Health Score from 1.0 (nominal) to 0.0 (failure). This model operates purely on numerical sensor data — no documents.</p>
            </div>
            <button class="arch-info-btn" @click="archInfoOpen=!archInfoOpen" title="Technical Details">ⓘ</button>
          </div>

          <!-- ⓘ Info Panel: Pane 3 -->
          <div v-if="archInfoOpen && archPane==='detection'" class="arch-info-panel">
            <div class="arch-info-close" @click="archInfoOpen=false">✕ Close</div>
            <div class="arch-info-section">
              <div class="arch-info-title">🤖 How XGBoost Works Here</div>
              <ul>
                <li>Trained on 10,000+ labelled fault signatures per asset class</li>
                <li>Gradient-boosted decision trees — deterministic, explainable, not a neural network black-box</li>
                <li>One model per asset class: <code style="font-family:var(--mono)">esp_health.ubj</code>, <code style="font-family:var(--mono)">gas_lift_health.ubj</code>, etc.</li>
                <li>Health Score of 0.34 = 66% degraded. SCADA single-threshold alarm not triggered yet.</li>
                <li>Key: SCADA uses absolute thresholds. XGBoost uses correlated trends across all 4 sensors simultaneously.</li>
              </ul>
              <div class="arch-callout callout-orange">PSI at 185 is "normal" in isolation. PSI declining at 2.4 PSI/min while temp and amps rise simultaneously is a gas_lock signature. XGBoost detects the pattern; SCADA cannot.</div>
            </div>
            <div class="arch-info-section">
              <div class="arch-info-title">📐 RUL Calculation</div>
              <ul>
                <li>Health Score is converted to RUL via fault-physics degradation curves calibrated per fault type</li>
                <li>Exponential weighted average (EWA) over 10 readings smooths out sensor noise</li>
                <li>Base RUL = time until Health Score would reach the SCADA alarm threshold (0.15)</li>
                <li>This Base RUL is then refined by the Edge LLM in Pane 5 using retrieved context</li>
              </ul>
            </div>
          </div>

          <div class="arch-pane-body" style="display:block">
            <!-- Input features -->
            <div class="arch-stage stage-sensor" style="margin-bottom:12px">
              <div class="arch-stage-title">📥 Model Input — 6 Features per Reading</div>
              <div class="arch-sensor-grid" style="margin-top:4px">
                <div class="arch-sensor-row">
                  <div class="asr-label">Intake PSI</div>
                  <div class="asr-val asr-anomaly">185 PSI <span class="asr-trend">↘</span></div>
                </div>
                <div class="arch-sensor-row">
                  <div class="asr-label">Winding Temp</div>
                  <div class="asr-val asr-anomaly">218 °F <span class="asr-trend">↗</span></div>
                </div>
                <div class="arch-sensor-row">
                  <div class="asr-label">Vibration</div>
                  <div class="asr-val asr-anomaly">0.41 mm/s <span class="asr-trend">↗</span></div>
                </div>
                <div class="arch-sensor-row">
                  <div class="asr-label">Motor Amps</div>
                  <div class="asr-val asr-anomaly">63.2 A <span class="asr-trend">↗</span></div>
                </div>
                <div class="arch-sensor-row">
                  <div class="asr-label">dPSI/dt (slope)</div>
                  <div class="asr-val asr-anomaly">−2.4 PSI/min</div>
                </div>
                <div class="arch-sensor-row">
                  <div class="asr-label">dTemp/dt (slope)</div>
                  <div class="asr-val asr-anomaly">+1.8 °F/min</div>
                </div>
              </div>
            </div>

            <div class="arch-connector">↓ <span class="arch-connector-label">XGBoost inference — Inference API pod (FastAPI) · deterministic · explainable</span></div>

            <!-- Model output -->
            <div class="arch-stage stage-ml" style="margin-bottom:12px">
              <div class="arch-stage-title">⚡ XGBoost Model Output</div>
              <div class="arch-stage-body">
                <div class="arch-chip chip-orange"><span class="arch-chip-label">Fault Label</span><span class="arch-chip-val">gas_lock</span></div>
                <div class="arch-chip chip-red"><span class="arch-chip-label">Health Score</span><span class="arch-chip-val">0.34</span></div>
                <div class="arch-chip chip-orange"><span class="arch-chip-label">Confidence</span><span class="arch-chip-val">91.4%</span></div>
                <div class="arch-chip chip-blue"><span class="arch-chip-label">Base RUL</span><span class="arch-chip-val">22.1 min</span></div>
              </div>
            </div>

            <div class="arch-connector">↓ <span class="arch-connector-label">Written to AlloyDB telemetry_events + triggers context retrieval in Pane 4</span></div>

            <!-- SCADA comparison -->
            <div class="arch-compare-row">
              <div class="arch-compare-card acc-scada">
                <div class="acc-title acc-title-scada">SCADA Alarm at same time</div>
                <ul class="acc-items">
                  <li class="no">PSI: 185 PSI — Within normal range ✓</li>
                  <li class="no">Temp: 218°F — Within normal range ✓</li>
                  <li class="no">Vib: 0.41mm — Within normal range ✓</li>
                  <li class="no">NO ALARM TRIGGERED</li>
                </ul>
              </div>
              <div class="arch-compare-card acc-gdc">
                <div class="acc-title acc-title-gdc">GDC ML at same time</div>
                <ul class="acc-items">
                  <li class="yes">Correlated 4-sensor degradation pattern</li>
                  <li class="yes">Rising rate-of-change on 3 of 4 sensors</li>
                  <li class="yes">91.4% gas_lock confidence</li>
                  <li class="yes">22 min advance warning issued</li>
                </ul>
              </div>
            </div>
          </div>
        </div><!-- pane detection -->

        <!-- ── Pane 4: Context Fusion ── -->
        <div class="arch-pane" :class="{active: archPane==='context'}">
          <div class="arch-pane-hdr" style="display:flex;align-items:flex-start;gap:12px">
            <div style="flex:1">
              <h2>Context Fusion — Three Streams into AlloyDB</h2>
              <p>AlloyDB Omni unifies three independent data streams: real-time ML assessments, static OEM manual embeddings (RAG), and dynamically-generated field intelligence. The LLM draws from all three simultaneously.</p>
            </div>
            <button class="arch-info-btn" @click="archInfoOpen=!archInfoOpen" title="Technical Details">ⓘ</button>
          </div>

          <!-- ⓘ Info Panel: Pane 4 -->
          <div v-if="archInfoOpen && archPane==='context'" class="arch-info-panel">
            <div class="arch-info-close" @click="archInfoOpen=false">✕ Close</div>
            <div class="arch-info-section">
              <div class="arch-info-title">🔍 pgvector Similarity Search</div>
              <ul>
                <li>All manual sections are pre-embedded using <code style="font-family:var(--mono)">all-MiniLM-L6-v2</code> (384-dim vectors) at ingestion time</li>
                <li>At query time: fault label + asset class is embedded, then cosine-similarity search retrieves top-3 relevant sections (<code style="font-family:var(--mono)">embedding <-> query_vec</code>)</li>
                <li>HNSW index on AlloyDB ensures <10ms retrieval as document count scales</li>
              </ul>
              <div class="arch-callout callout-purple">Keyword search for "gas lock" returns all gas lock entries. pgvector semantic search returns the sections most contextually relevant to the specific sensor profile of this fault instance.</div>
            </div>
            <div class="arch-info-section">
              <div class="arch-info-title">🏭 Field Intel Generation</div>
              <ul>
                <li>A background thread generates realistic shift notes, lab reports, and work orders every 2–5 minutes, correlated to the active fault type and live sensor readings</li>
                <li>This simulates the real-world context an operator would have: recent documentation from the field that augments the static OEM manuals</li>
                <li>In production, this layer would be replaced by actual CMMS records (SAP PM, IBM Maximo) and real lab reports</li>
              </ul>
            </div>
          </div>

          <div class="arch-pane-body" style="display:block">

            <!-- Three parallel input streams -->
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:12px">

              <!-- Stream 1: ML assessments -->
              <div class="arch-stage stage-ml">
                <div class="arch-stage-title" style="font-size:0.65rem">⚡ Stream 1 · Real-Time ML</div>
                <div style="display:flex;flex-direction:column;gap:4px;margin-top:6px">
                  <div class="arch-chip chip-orange"><span style="font-size:0.62rem">gas_lock · Health 0.34 · RUL 22.1 min</span></div>
                  <div class="arch-chip chip-muted"><span style="font-size:0.60rem">24h sensor history + prior detections</span></div>
                </div>
                <div style="font-size:0.58rem;color:var(--muted);margin-top:6px">Written continuously by Event Processor → telemetry_events table</div>
              </div>

              <!-- Stream 2: RAG Documents -->
              <div class="arch-stage stage-llm" style="background:rgba(179,136,255,0.05);border-color:rgba(179,136,255,0.3)">
                <div class="arch-stage-title" style="font-size:0.65rem;color:#b388ff">📚 Stream 2 · OEM Manuals (RAG)</div>
                <div style="display:flex;flex-direction:column;gap:4px;margin-top:6px">
                  <div class="arch-chip chip-purple"><span style="font-size:0.62rem">ESP System Overview</span></div>
                  <div class="arch-chip chip-purple"><span style="font-size:0.62rem">Gas Lock — OEM Section</span></div>
                  <div class="arch-chip chip-purple"><span style="font-size:0.62rem">Motor Current Diagnostics</span></div>
                </div>
                <div style="font-size:0.58rem;color:var(--muted);margin-top:6px">18 chunks · ESP + Gas Lift + Mud Pump + Top Drive manuals</div>
              </div>

              <!-- Stream 3: Field Intel -->
              <div class="arch-stage stage-sensor" style="background:rgba(30,144,255,0.05);border-color:rgba(30,144,255,0.3)">
                <div class="arch-stage-title" style="font-size:0.65rem">📋 Stream 3 · Field Intelligence</div>
                <div style="display:flex;flex-direction:column;gap:4px;margin-top:6px">
                  <div class="arch-chip chip-blue"><span style="font-size:0.62rem">Shift Note — GOR elevated</span></div>
                  <div class="arch-chip chip-blue"><span style="font-size:0.62rem">Lab Report — 8.4% free gas at intake</span></div>
                  <div class="arch-chip chip-blue"><span style="font-size:0.62rem">Work Order — Prior VFD service</span></div>
                </div>
                <div style="font-size:0.58rem;color:var(--muted);margin-top:6px">100+ rows · AI-generated, refreshed every 2–5 min per active fault</div>
              </div>
            </div>

            <!-- Converging arrow -->
            <div class="arch-connector" style="text-align:center">↓ <span class="arch-connector-label">All three streams unified in AlloyDB · semantic query via pgvector (all-MiniLM-L6-v2)</span></div>

            <!-- AlloyDB unified store -->
            <div class="arch-stage stage-db" style="margin-bottom:12px">
              <div class="arch-stage-title">🗄 AlloyDB Omni — Unified Context (PostgreSQL + pgvector)</div>
              <div class="arch-stage-body">
                <div class="arch-chip chip-orange"><span class="arch-chip-label">Table</span><span class="arch-chip-val">telemetry_events</span></div>
                <div class="arch-chip chip-purple"><span class="arch-chip-label">Table</span><span class="arch-chip-val">rag_documents (18 rows)</span></div>
                <div class="arch-chip chip-blue"><span class="arch-chip-label">Table</span><span class="arch-chip-val">field_intel (100+ rows)</span></div>
                <div class="arch-chip chip-muted"><span class="arch-chip-label">Index</span><span class="arch-chip-val">HNSW · <10ms retrieval</span></div>
              </div>
            </div>

            <div class="arch-connector">↓ <span class="arch-connector-label">Top-3 semantically relevant sections retrieved via cosine similarity · assembled into LLM prompt</span></div>

            <!-- Retrieved context assembled -->
            <div class="arch-stage stage-llm">
              <div class="arch-stage-title">📄 Context Assembled for Gemma Prompt</div>
              <div class="arch-stage-body" style="flex-direction:column;gap:5px">
                <div class="arch-chip chip-purple"><span>📚 [OEM Manual] Gas Lock — causes pump cavitation via gas void fraction exceeding 30%...</span></div>
                <div class="arch-chip chip-blue"><span>📋 [Shift Note] Operator noted elevated GOR on ESP-A1 during previous afternoon tour...</span></div>
                <div class="arch-chip chip-blue"><span>📋 [Lab Report] Fluid analysis shows 8.4% free gas at pump intake, trending up from 5.1% last week...</span></div>
              </div>
            </div>
          </div>
        </div><!-- pane context -->

        <!-- ── Pane 5: AI Reasoning ── -->
        <div class="arch-pane" :class="{active: archPane==='reasoning'}">
          <div class="arch-pane-hdr" style="display:flex;align-items:flex-start;gap:12px">
            <div style="flex:1">
              <h2>AI Reasoning — Gemma 27b Edge LLM</h2>
              <p>The assembled context (sensor data + ML prediction + retrieved documents) is submitted to Gemma 27b, running on an NVIDIA L4 GPU within the edge cluster, with no WAN dependency.</p>
            </div>
            <button class="arch-info-btn" @click="archInfoOpen=!archInfoOpen" title="Technical Details">ⓘ</button>
          </div>

          <!-- ⓘ Info Panel: Pane 5 -->
          <div v-if="archInfoOpen && archPane==='reasoning'" class="arch-info-panel">
            <div class="arch-info-close" @click="archInfoOpen=false">✕ Close</div>
            <div class="arch-info-section">
              <div class="arch-info-title">💡 Why Edge LLM Matters</div>
              <ul>
                <li>Cloud LLM APIs (Vertex AI, OpenAI) require a WAN connection and introduce 2–5 second network latency — assuming the link is up</li>
                <li>A wellsite with 4G failover may have packet loss during a storm — exactly when you need the AI most</li>
                <li>Sensitive operational data (well test reports, production rates, lab results) never leaves the E-House premises</li>
              </ul>
              <div class="arch-callout callout-purple">Gemma 27b on the L4 GPU achieves comparable reasoning quality to Gemini Flash for structured O&G fault diagnosis, with zero cloud dependency and full offline operation.</div>
            </div>
            <div class="arch-info-section">
              <div class="arch-info-title">🎯 What the LLM Actually Does</div>
              <ul>
                <li>It is <strong style="color:var(--text)">not</strong> doing ML inference — the XGBoost model does that in Pane 3</li>
                <li>It synthesizes structured sensor data with unstructured text documents to produce a <strong style="color:var(--text)">human-readable diagnosis and action recommendation</strong></li>
                <li>It adjusts the Base RUL when retrieved context reveals conditions the ML model's training data didn't capture (e.g., accelerating free-gas trend from the lab report)</li>
                <li>The recommendation is Gemma's output — not a hardcoded rule</li>
              </ul>
            </div>
          </div>

          <div class="arch-pane-body" style="display:block">
            <!-- Prompt assembly -->
            <div class="arch-stage stage-db" style="margin-bottom:12px">
              <div class="arch-stage-title">📝 Prompt Assembly</div>
              <div style="display:flex;flex-direction:column;gap:5px;margin-top:4px">
                <div class="arch-chip chip-orange" style="font-size:0.65rem"><span><strong>FAULT:</strong> gas_lock on ESP-ALPHA-1 · Health: 34% · Base RUL: 22.1 min</span></div>
                <div class="arch-chip chip-orange" style="font-size:0.65rem"><span><strong>SENSORS:</strong> PSI 185↘ · Temp 218°F↗ · Vib 0.41mm↗ · Amps 63.2A↗</span></div>
                <div class="arch-chip chip-purple" style="font-size:0.65rem"><span><strong>STATIC CORPUS:</strong> [3 OEM manual sections — gas lock, motor current, system overview]</span></div>
                <div class="arch-chip chip-blue" style="font-size:0.65rem"><span><strong>FIELD INTEL:</strong> Shift note (GOR elevated) + Lab report (8.4% free gas at intake)</span></div>
              </div>
            </div>

            <div class="arch-connector">↓ <span class="arch-connector-label">Submitted to Ollama API · gemma:27b · NVIDIA L4 GPU · on-cluster · no WAN</span></div>

            <!-- GPU box -->
            <div class="arch-stage stage-llm" style="margin-bottom:12px">
              <div class="arch-stage-title">🧠 Gemma 27b (NVIDIA L4 GPU — 24GB VRAM)</div>
              <div class="arch-stage-body">
                <div class="arch-chip chip-purple"><span class="arch-chip-label">Model</span><span class="arch-chip-val">gemma:27b</span></div>
                <div class="arch-chip chip-purple"><span class="arch-chip-label">Backend</span><span class="arch-chip-val">Ollama (on-cluster)</span></div>
                <div class="arch-chip chip-muted"><span class="arch-chip-label">Latency</span><span class="arch-chip-val">< 8 seconds</span></div>
                <div class="arch-chip chip-muted"><span class="arch-chip-label">WAN required</span><span class="arch-chip-val" style="color:var(--green)">None</span></div>
              </div>
            </div>

            <div class="arch-connector">↓ <span class="arch-connector-label">Streaming response token-by-token</span></div>

            <!-- LLM Output -->
            <div class="arch-stage stage-ml" style="margin-bottom:12px">
              <div class="arch-stage-title">📤 LLM Output (AI-Informed Analysis)</div>
              <div style="display:flex;flex-direction:column;gap:6px;margin-top:4px">
                <div class="arch-chip chip-orange"><span><strong>Assessment:</strong> "Intake PSI of 185 is declining at 2.4 PSI/min. Combined with lab report confirming 8.4% free gas at intake, this matches early-stage gas void fraction exceeding pump design limits..."</span></div>
                <div class="arch-chip chip-red"><span class="arch-chip-label">AI-Informed RUL</span><span class="arch-chip-val">14.2 min</span></div>
                <div class="arch-chip chip-green"><span><strong>Action:</strong> "Reduce VFD frequency from 52Hz to 44Hz immediately to allow gas to break out through the annulus before pump cavitation occurs."</span></div>
              </div>
            </div>

            <div style="padding:10px 14px;border-radius:7px;background:rgba(179,136,255,0.07);border:1px solid rgba(179,136,255,0.25);font-size:0.67rem;color:var(--text2)">
              <strong style="color:#b388ff">🔑 Why the RUL Changed:</strong> The base ML model estimated 22.1 min. After retrieving the lab report showing 8.4% free gas (vs. 5.1% last week — a +64% increase), Gemma assessed the degradation is accelerating faster than the XGBoost model's training data assumed. Adjusted RUL: 14.2 min.
            </div>
          </div>
        </div><!-- pane reasoning -->

        <!-- ── Pane 6: Operator Value ── -->
        <div class="arch-pane" :class="{active: archPane==='operator'}">
          <div class="arch-pane-hdr" style="display:flex;align-items:flex-start;gap:12px">
            <div style="flex:1">
              <h2>Operator Interface — Human-in-the-Loop & ROI</h2>
              <p>The AI recommendation is presented to the operator with full financial context. The human retains final control — but now has expert-level intelligence to inform every decision.</p>
            </div>
            <button class="arch-info-btn" @click="archInfoOpen=!archInfoOpen" title="Technical Details">ⓘ</button>
          </div>

          <!-- ⓘ Info Panel: Pane 6 -->
          <div v-if="archInfoOpen && archPane==='operator'" class="arch-info-panel">
            <div class="arch-info-close" @click="archInfoOpen=false">✕ Close</div>
            <div class="arch-info-section">
              <div class="arch-info-title">🤝 Human-in-the-Loop Design</div>
              <ul>
                <li>The AI recommends — the <strong style="color:var(--text)">operator decides</strong>. There is no automated actuation without human approval.</li>
                <li>Three tiered options give the operator financial and time trade-offs before they commit</li>
                <li>Every approved action is audit-logged to the <code style="font-family:var(--mono)">fault_sessions</code> table in AlloyDB for compliance and ROI tracking</li>
              </ul>
              <div class="arch-callout callout-green">HITL is not just a safety feature — it's what makes the ROI case credible. The financial ledger records what the operator chose, and what it saved. This is a provable, reproducible financial outcome.</div>
            </div>
            <div class="arch-info-section">
              <div class="arch-info-title">💵 The ROI Equation</div>
              <ul>
                <li><strong style="color:var(--g-red)">Without GDC:</strong> SCADA alarms when the motor is already at risk. Emergency pull: $150,000 + 48hr downtime at $45k/day = <strong style="color:var(--g-red)">$366,000</strong></li>
                <li><strong style="color:var(--g-green)">With GDC:</strong> Operator adjusts VFD 14 minutes early. Motor preserved. <strong style="color:var(--g-green)">Cost: $0</strong></li>
                <li>Annualised ROI across 38-well field at current fault frequency: <strong style="color:var(--g-green)">$7.8M+</strong></li>
              </ul>
            </div>
          </div>

          <div class="arch-pane-body" style="display:block">
            <!-- Alert -->
            <div class="arch-stage stage-ml" style="margin-bottom:12px">
              <div class="arch-stage-title">⚡ AI Detection Alert</div>
              <div class="arch-stage-body">
                <div class="arch-chip chip-orange"><span class="arch-chip-label">Asset</span><span class="arch-chip-val">ESP-ALPHA-1</span></div>
                <div class="arch-chip chip-red"><span class="arch-chip-label">Fault</span><span class="arch-chip-val">Gas Lock</span></div>
                <div class="arch-chip chip-red"><span class="arch-chip-label">AI-Informed RUL</span><span class="arch-chip-val">14.2 min</span></div>
                <div class="arch-chip chip-muted"><span class="arch-chip-label">SCADA</span><span class="arch-chip-val" style="color:var(--green)">No Alarm</span></div>
              </div>
            </div>

            <div class="arch-connector">↓ <span class="arch-connector-label">Operator opens Deep Dive → consults Operations Agent</span></div>

            <!-- Remediation tiers -->
            <div class="arch-stage stage-db" style="margin-bottom:12px">
              <div class="arch-stage-title">📋 Remediation Options (AI-Generated)</div>
              <div style="display:flex;flex-direction:column;gap:6px;margin-top:4px">
                <div style="background:rgba(0,230,118,0.06);border:1px solid rgba(0,230,118,0.3);border-radius:6px;padding:10px 13px;display:grid;grid-template-columns:1fr auto;gap:8px">
                  <div>
                    <div style="font-size:0.64rem;font-weight:700;color:var(--green)">IMMEDIATE</div>
                    <div style="font-size:0.68rem;color:var(--text2);margin-top:2px">Reduce VFD to 44Hz — allow gas breakout through annulus</div>
                  </div>
                  <div style="text-align:right">
                    <div style="font-size:0.7rem;font-weight:700;font-family:var(--mono);color:var(--green)">$0</div>
                    <div style="font-size:0.57rem;color:var(--muted)">Instant</div>
                  </div>
                </div>
                <div style="background:rgba(255,179,0,0.05);border:1px solid rgba(255,179,0,0.3);border-radius:6px;padding:10px 13px;display:grid;grid-template-columns:1fr auto;gap:8px">
                  <div>
                    <div style="font-size:0.64rem;font-weight:700;color:var(--yellow)">SCHEDULED</div>
                    <div style="font-size:0.68rem;color:var(--text2);margin-top:2px">Inspect intake valve + gas separator</div>
                  </div>
                  <div style="text-align:right">
                    <div style="font-size:0.7rem;font-weight:700;font-family:var(--mono);color:var(--yellow)">$1,200</div>
                    <div style="font-size:0.57rem;color:var(--muted)">4 hours</div>
                  </div>
                </div>
                <div style="background:rgba(244,67,54,0.05);border:1px solid rgba(244,67,54,0.25);border-radius:6px;padding:10px 13px;display:grid;grid-template-columns:1fr auto;gap:8px;opacity:0.6">
                  <div>
                    <div style="font-size:0.64rem;font-weight:700;color:var(--red)">EMERGENCY (SCADA PATH)</div>
                    <div style="font-size:0.68rem;color:var(--text2);margin-top:2px">Emergency pull & full motor replacement</div>
                  </div>
                  <div style="text-align:right">
                    <div style="font-size:0.7rem;font-weight:700;font-family:var(--mono);color:var(--red)">$150,000</div>
                    <div style="font-size:0.57rem;color:var(--muted)">48 hours</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="arch-connector">↓ <span class="arch-connector-label">Operator selects Immediate tier → Approve & Execute</span></div>

            <!-- Financial outcome -->
            <div class="arch-stage stage-ui">
              <div class="arch-stage-title">💰 Fleet Financials Ledger Update</div>
              <div class="arch-stage-body">
                <div class="arch-chip chip-green"><span class="arch-chip-label">Capital Preserved</span><span class="arch-chip-val">$150,000</span></div>
                <div class="arch-chip chip-muted"><span class="arch-chip-label">Cost Incurred</span><span class="arch-chip-val">$0</span></div>
                <div class="arch-chip chip-green"><span class="arch-chip-label">Advance Warning</span><span class="arch-chip-val">14.2 min</span></div>
                <div class="arch-chip chip-green"><span class="arch-chip-label">Outcome</span><span class="arch-chip-val">Unplanned downtime avoided</span></div>
              </div>
            </div>
          </div>
        </div><!-- pane operator -->

      </div><!-- arch-outer -->
    </div><!-- tab-architecture -->"""

# Match the old arch tab from the comment through the closing tag
pattern = re.compile(
    r'        <!-- ══ TAB: ARCHITECTURE ══ -->.*?    </div><!-- tab-architecture -->',
    re.DOTALL
)

new_html, count = pattern.subn(NEW_ARCH_TAB, html, count=1)

if count == 0:
    print("ERROR: Pattern not found — no changes made.")
else:
    with open(FILE, 'w') as f:
        f.write(new_html)
    print(f"SUCCESS: Replaced arch tab block. ({count} substitution)")
    # Quick sanity check
    with open(FILE, 'r') as f:
        verify = f.read()
    checks = [
        ('archInfoOpen', 'archInfoOpen state added'),
        ('Regional Field Network', 'Pane 2 field-of-pads updated'),
        ('Pad Alpha', 'Pad chips present'),
        ('Intake PSI', 'Sensor chips present'),
        ('ML Anomaly Detection', 'ML label corrected'),
        ('E-House', 'E-House narrative present'),
        ('Stream 1', 'Parallel streams in Pane 4'),
        ('arch-info-btn', 'Info button present'),
        ('arch-info-panel', 'Info panel present'),
    ]
    for term, label in checks:
        status = '✅' if term in verify else '❌ MISSING'
        print(f"  {status} {label}: '{term}'")
