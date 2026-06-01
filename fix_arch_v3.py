#!/usr/bin/env python3
"""
Targeted fixes to the Architecture tab based on user review:
1. Pane 1 flow: remove ESP Wells + Fault Injector; rename Intake PSI → Pump Intake Pressure
2. Pane 2 stage: remove "5s telemetry cadence" and "Local field network" chips
3. Pane 3 stage: remove "6-feature sensor vector" and "No unstructured data" chips
4. Pane 4: rename Stream 1 → Model-Based RUL, Stream 3 → Operations Reports; add down-arrows between boxes
5. Pane 5: separate LLM outputs visually; remove bottom "Why the RUL Changed" callout
6. Layout: fix overflow - align-items:flex-start on flow row, overflow:hidden on stage boxes
7. CSS: fix arch-stage to not overflow parent
"""

FILE = 'gke/fault-trigger-ui/index.html'
with open(FILE, 'r') as f:
    html = f.read()

original_len = len(html)

# ── Fix 1: Pane 1 Field Sensors stage (remove ESP Wells, Fault Injector; rename Intake PSI) ──
OLD1 = '''              <div class="arch-stage stage-sensor" style="flex:1;min-width:110px">
                <div class="arch-stage-title">📡 1. Field Sensors</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-blue"><span>ESP Wells</span></div>
                  <div class="arch-chip chip-blue"><span>Intake PSI</span></div>
                  <div class="arch-chip chip-orange"><span>Winding Temp</span></div>
                  <div class="arch-chip chip-orange"><span>Vibration mm/s</span></div>
                  <div class="arch-chip chip-blue"><span>Motor Amps</span></div>
                  <div class="arch-chip chip-muted" style="opacity:0.6"><span style="font-style:italic">Fault Injector (demo)</span></div>
                </div>
              </div>'''
NEW1 = '''              <div class="arch-stage stage-sensor" style="flex:1;min-width:110px;overflow:hidden">
                <div class="arch-stage-title">📡 1. Field Sensors</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-blue"><span>Pump Intake Pressure</span></div>
                  <div class="arch-chip chip-orange"><span>Winding Temp</span></div>
                  <div class="arch-chip chip-orange"><span>Vibration mm/s</span></div>
                  <div class="arch-chip chip-blue"><span>Motor Amps</span></div>
                </div>
              </div>'''
assert OLD1 in html, "Fix 1 pattern not found"
html = html.replace(OLD1, NEW1, 1)

# ── Fix 2: Pane 1 Edge Bus stage (remove 5s / local field network chips) ──
OLD2 = '''              <div class="arch-stage stage-broker" style="flex:1;min-width:110px">
                <div class="arch-stage-title">📨 2. Edge Bus</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-orange"><span>RabbitMQ Broker</span></div>
                  <div class="arch-chip chip-muted"><span style="font-size:0.62rem">5s telemetry cadence</span></div>
                  <div class="arch-chip chip-muted"><span style="font-size:0.62rem">Local field network</span></div>
                </div>
              </div>'''
NEW2 = '''              <div class="arch-stage stage-broker" style="flex:1;min-width:110px;overflow:hidden">
                <div class="arch-stage-title">📨 2. Edge Bus</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-orange"><span>RabbitMQ Broker</span></div>
                </div>
              </div>'''
assert OLD2 in html, "Fix 2 pattern not found"
html = html.replace(OLD2, NEW2, 1)

# ── Fix 3: Pane 1 ML stage (remove extra chips) ──
OLD3 = '''              <div class="arch-stage stage-ml" style="flex:1;min-width:110px">
                <div class="arch-stage-title">⚡ 3. ML Anomaly Detection</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-orange"><span>XGBoost Health Score</span></div>
                  <div class="arch-chip chip-muted"><span style="font-size:0.62rem">6-feature sensor vector</span></div>
                  <div class="arch-chip chip-muted"><span style="font-size:0.62rem">No unstructured data</span></div>
                </div>
              </div>'''
NEW3 = '''              <div class="arch-stage stage-ml" style="flex:1;min-width:110px;overflow:hidden">
                <div class="arch-stage-title">⚡ 3. ML Anomaly Detection</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-orange"><span>XGBoost Health Score</span></div>
                </div>
              </div>'''
assert OLD3 in html, "Fix 3 pattern not found"
html = html.replace(OLD3, NEW3, 1)

# ── Fix 4: Pane 1 Context Store stage (rename Field Intel → Operations Reports, ML Assessments → Model-Based RUL) ──
OLD4 = '''              <div class="arch-stage stage-db" style="flex:1;min-width:110px">
                <div class="arch-stage-title">🗄 4. Context Store</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-blue"><span>AlloyDB + pgvector</span></div>
                  <div class="arch-chip chip-purple"><span>RAG Manuals</span></div>
                  <div class="arch-chip chip-blue"><span>Field Intel</span></div>
                  <div class="arch-chip chip-orange"><span>ML Assessments</span></div>
                </div>
              </div>'''
NEW4 = '''              <div class="arch-stage stage-db" style="flex:1;min-width:110px;overflow:hidden">
                <div class="arch-stage-title">🗄 4. Context Store</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-blue"><span>AlloyDB + pgvector</span></div>
                  <div class="arch-chip chip-purple"><span>RAG Manuals</span></div>
                  <div class="arch-chip chip-blue"><span>Operations Reports</span></div>
                  <div class="arch-chip chip-orange"><span>Model-Based RUL</span></div>
                </div>
              </div>'''
assert OLD4 in html, "Fix 4 pattern not found"
html = html.replace(OLD4, NEW4, 1)

# ── Fix 5: Pane 1 AI Context Fusion stage (split engine from outputs; add overflow:hidden) ──
OLD5 = '''              <div class="arch-stage stage-llm" style="flex:1;min-width:110px">
                <div class="arch-stage-title">🧠 5. AI Context Fusion</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-purple"><span>Gemma 27b (GPU)</span></div>
                  <div class="arch-chip chip-orange"><span>AI-Informed RUL</span></div>
                  <div class="arch-chip chip-green"><span>Action Recommendation</span></div>
                </div>
              </div>'''
NEW5 = '''              <div class="arch-stage stage-llm" style="flex:1;min-width:110px;overflow:hidden">
                <div class="arch-stage-title">🧠 5. AI Context Fusion</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-purple"><span>Gemma 27b (GPU)</span></div>
                </div>
                <div style="font-size:0.55rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:0.07em;margin:6px 0 3px">Outputs →</div>
                <div style="display:flex;flex-direction:column;gap:3px">
                  <div class="arch-chip chip-orange"><span>AI-Informed RUL</span></div>
                  <div class="arch-chip chip-green"><span>Action Recommendation</span></div>
                </div>
              </div>'''
assert OLD5 in html, "Fix 5 pattern not found"
html = html.replace(OLD5, NEW5, 1)

# ── Fix 6: Pane 1 flow row: align-items:stretch → align-items:flex-start ──
OLD6 = '            <div style="display:flex;gap:8px;align-items:stretch;flex-wrap:wrap;margin-bottom:18px">'
NEW6 = '            <div style="display:flex;gap:8px;align-items:flex-start;flex-wrap:wrap;margin-bottom:18px">'
assert OLD6 in html, "Fix 6 pattern not found"
html = html.replace(OLD6, NEW6, 1)

# ── Fix 7: Pane 4 Stream 1 (relabel Real-Time ML → Model-Based RUL) ──
OLD7 = '''              <!-- Stream 1: ML assessments -->
              <div class="arch-stage stage-ml">
                <div class="arch-stage-title" style="font-size:0.65rem">⚡ Stream 1 · Real-Time ML</div>
                <div style="display:flex;flex-direction:column;gap:4px;margin-top:6px">
                  <div class="arch-chip chip-orange"><span style="font-size:0.62rem">gas_lock · Health 0.34 · RUL 22.1 min</span></div>
                  <div class="arch-chip chip-muted"><span style="font-size:0.60rem">24h sensor history + prior detections</span></div>
                </div>
                <div style="font-size:0.58rem;color:var(--muted);margin-top:6px">Written continuously by Event Processor → telemetry_events table</div>
              </div>'''
NEW7 = '''              <!-- Stream 1: Model-Based RUL -->
              <div class="arch-stage stage-ml">
                <div class="arch-stage-title" style="font-size:0.65rem">⚡ Stream 1 · Model-Based RUL</div>
                <div style="display:flex;flex-direction:column;gap:4px;margin-top:6px">
                  <div class="arch-chip chip-orange"><span style="font-size:0.62rem">gas_lock · Health 0.34 · Base RUL 22.1 min</span></div>
                  <div class="arch-chip chip-muted"><span style="font-size:0.60rem">24h sensor history + prior detections</span></div>
                </div>
                <div style="font-size:0.6rem;font-weight:700;color:var(--muted);text-align:center;margin-top:8px">↓</div>
              </div>'''
assert OLD7 in html, "Fix 7 pattern not found"
html = html.replace(OLD7, NEW7, 1)

# ── Fix 8: Pane 4 Stream 2 (add down arrow) ──
OLD8 = '''              <!-- Stream 2: RAG Documents -->
              <div class="arch-stage stage-llm" style="background:rgba(179,136,255,0.05);border-color:rgba(179,136,255,0.3)">
                <div class="arch-stage-title" style="font-size:0.65rem;color:#b388ff">📚 Stream 2 · OEM Manuals (RAG)</div>
                <div style="display:flex;flex-direction:column;gap:4px;margin-top:6px">
                  <div class="arch-chip chip-purple"><span style="font-size:0.62rem">ESP System Overview</span></div>
                  <div class="arch-chip chip-purple"><span style="font-size:0.62rem">Gas Lock — OEM Section</span></div>
                  <div class="arch-chip chip-purple"><span style="font-size:0.62rem">Motor Current Diagnostics</span></div>
                </div>
                <div style="font-size:0.58rem;color:var(--muted);margin-top:6px">18 chunks · ESP + Gas Lift + Mud Pump + Top Drive manuals</div>
              </div>'''
NEW8 = '''              <!-- Stream 2: RAG Documents -->
              <div class="arch-stage stage-llm" style="background:rgba(179,136,255,0.05);border-color:rgba(179,136,255,0.3)">
                <div class="arch-stage-title" style="font-size:0.65rem;color:#b388ff">📚 Stream 2 · OEM Manuals (RAG)</div>
                <div style="display:flex;flex-direction:column;gap:4px;margin-top:6px">
                  <div class="arch-chip chip-purple"><span style="font-size:0.62rem">ESP System Overview</span></div>
                  <div class="arch-chip chip-purple"><span style="font-size:0.62rem">Gas Lock — OEM Section</span></div>
                  <div class="arch-chip chip-purple"><span style="font-size:0.62rem">Motor Current Diagnostics</span></div>
                </div>
                <div style="font-size:0.58rem;color:var(--muted);margin-top:4px">18 chunks · 4 manual types</div>
                <div style="font-size:0.6rem;font-weight:700;color:var(--muted);text-align:center;margin-top:8px">↓</div>
              </div>'''
assert OLD8 in html, "Fix 8 pattern not found"
html = html.replace(OLD8, NEW8, 1)

# ── Fix 9: Pane 4 Stream 3 (rename Field Intelligence → Operations Reports; add down arrow) ──
OLD9 = '''              <!-- Stream 3: Field Intel -->
              <div class="arch-stage stage-sensor" style="background:rgba(30,144,255,0.05);border-color:rgba(30,144,255,0.3)">
                <div class="arch-stage-title" style="font-size:0.65rem">📋 Stream 3 · Field Intelligence</div>
                <div style="display:flex;flex-direction:column;gap:4px;margin-top:6px">
                  <div class="arch-chip chip-blue"><span style="font-size:0.62rem">Shift Note — GOR elevated</span></div>
                  <div class="arch-chip chip-blue"><span style="font-size:0.62rem">Lab Report — 8.4% free gas at intake</span></div>
                  <div class="arch-chip chip-blue"><span style="font-size:0.62rem">Work Order — Prior VFD service</span></div>
                </div>
                <div style="font-size:0.58rem;color:var(--muted);margin-top:6px">100+ rows · AI-generated, refreshed every 2–5 min per active fault</div>
              </div>'''
NEW9 = '''              <!-- Stream 3: Operations Reports -->
              <div class="arch-stage stage-sensor" style="background:rgba(30,144,255,0.05);border-color:rgba(30,144,255,0.3)">
                <div class="arch-stage-title" style="font-size:0.65rem">📋 Stream 3 · Operations Reports</div>
                <div style="display:flex;flex-direction:column;gap:4px;margin-top:6px">
                  <div class="arch-chip chip-blue"><span style="font-size:0.62rem">Shift Note — GOR elevated</span></div>
                  <div class="arch-chip chip-blue"><span style="font-size:0.62rem">Lab Report — 8.4% free gas at intake</span></div>
                  <div class="arch-chip chip-blue"><span style="font-size:0.62rem">Work Order — Prior VFD service</span></div>
                </div>
                <div style="font-size:0.58rem;color:var(--muted);margin-top:4px">100+ rows · refreshed every 2–5 min</div>
                <div style="font-size:0.6rem;font-weight:700;color:var(--muted);text-align:center;margin-top:8px">↓</div>
              </div>'''
assert OLD9 in html, "Fix 9 pattern not found"
html = html.replace(OLD9, NEW9, 1)

# ── Fix 10: Pane 4 AlloyDB table labels (field_intel → ops_reports) ──
OLD10 = '                <div class="arch-chip chip-blue"><span class="arch-chip-label">Table</span><span class="arch-chip-val">field_intel (100+ rows)</span></div>'
NEW10 = '                <div class="arch-chip chip-blue"><span class="arch-chip-label">Table</span><span class="arch-chip-val">ops_reports (100+ rows)</span></div>'
assert OLD10 in html, "Fix 10 pattern not found"
html = html.replace(OLD10, NEW10, 1)

# ── Fix 11: Pane 5 LLM Output section — separate outputs, remove bottom callout ──
OLD11 = '''            <!-- LLM Output -->
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
            </div>'''
NEW11 = '''            <!-- LLM Assessment -->
            <div class="arch-stage stage-ml" style="margin-bottom:12px">
              <div class="arch-stage-title">📤 LLM Assessment</div>
              <div style="margin-top:4px">
                <div class="arch-chip chip-orange" style="font-size:0.65rem"><span>"Pump Intake Pressure of 185 is declining at 2.4 PSI/min. Lab report confirms 8.4% free gas at intake — matches early-stage gas void fraction exceeding pump design limits..."</span></div>
              </div>
            </div>

            <!-- Outputs -->
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
              <div style="background:rgba(255,109,0,0.08);border:1px solid rgba(255,109,0,0.4);border-radius:8px;padding:12px 14px">
                <div style="font-size:0.6rem;font-weight:700;color:var(--orange);text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px">📊 Output — AI-Informed RUL</div>
                <div style="font-family:var(--mono);font-size:1.2rem;font-weight:700;color:var(--orange)">14.2 min</div>
                <div style="font-size:0.6rem;color:var(--muted);margin-top:4px">Refined from Model Base RUL (22.1 min) using retrieved lab report context</div>
              </div>
              <div style="background:rgba(0,230,118,0.06);border:1px solid rgba(0,230,118,0.35);border-radius:8px;padding:12px 14px">
                <div style="font-size:0.6rem;font-weight:700;color:var(--green);text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px">✅ Output — Action Recommendation</div>
                <div style="font-size:0.7rem;color:var(--text2);line-height:1.4">"Reduce VFD frequency from 52Hz to 44Hz immediately to allow gas to break out through the annulus before pump cavitation occurs."</div>
              </div>
            </div>'''
assert OLD11 in html, "Fix 11 pattern not found"
html = html.replace(OLD11, NEW11, 1)

# ── Fix 12: Also update Pane 5 ⓘ info title from "Field Intel" to "Operations Reports" ──
OLD12 = '              <div class="arch-info-title">🏭 Field Intel Generation</div>'
NEW12 = '              <div class="arch-info-title">🏭 Operations Reports Generation</div>'
# Only update the one in Pane 4's info panel
html = html.replace(OLD12, NEW12, 1)

# ── Write back ──
with open(FILE, 'w') as f:
    f.write(html)

print(f"SUCCESS: {original_len} → {len(html)} chars")

# Verify
checks = [
    ('Pump Intake Pressure', 'Intake PSI renamed'),
    ('RabbitMQ Broker</span></div>\n                </div>', 'Edge Bus simplified'),
    ('XGBoost Health Score</span></div>\n                </div>', 'ML stage simplified'),
    ('Operations Reports', 'Field Intel renamed'),
    ('Model-Based RUL', 'ML Assessments relabeled'),
    ('Outputs →', 'Pane 5 outputs labelled'),
    ('AI-Informed RUL\n                <div style="font-family', 'Pane 5 RUL output box'),
    ('align-items:flex-start', 'Flow row overflow fixed'),
]
with open(FILE, 'r') as f:
    v = f.read()
for term, label in checks:
    status = '✅' if term in v else '❌ MISSING'
    print(f"  {status} {label}: '{term[:40]}'")
