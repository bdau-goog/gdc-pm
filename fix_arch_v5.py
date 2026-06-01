#!/usr/bin/env python3
"""
Architecture tab v5 + UI fixes based on final user review:
1. Gemma 27b → Gemma 4 27B (remove GPU from Pane 1 chip; update all Gemma refs in arch tab)
2. Pane 1 Context Store: restructure to show inputs feeding ↓ into AlloyDB
3. Tab nav order: How It Works → Fleet Operations → Fleet Telemetry → Fleet Financials
4. Grafana URL fix: 136.115.220.48 → 35.190.137.145
5. WAN badge → Field Link
6. Pane 2: add SCADA RTU as parallel RabbitMQ subscriber with HMI output path
"""

FILE = 'gke/fault-trigger-ui/index.html'
with open(FILE, 'r') as f:
    html = f.read()

changes = []

def replace_once(old, new, label):
    global html
    if old not in html:
        print(f"  ❌ PATTERN NOT FOUND: {label}")
        return
    html = html.replace(old, new, 1)
    changes.append(label)

def replace_all(old, new, label):
    global html
    count = html.count(old)
    if count == 0:
        print(f"  ❌ PATTERN NOT FOUND: {label}")
        return
    html = html.replace(old, new)
    changes.append(f"{label} ({count}x)")

# ─────────────────────────────────────────────────────────────
# 1. Gemma 27b → Gemma 4 27B (remove GPU chip from Pane 1 flow)
# ─────────────────────────────────────────────────────────────

# Pane 1 AI Fusion box: remove GPU from chip
replace_once(
    '<div class="arch-chip chip-purple"><span>Gemma 27b (GPU)</span></div>',
    '<div class="arch-chip chip-purple"><span>Gemma 4 27B</span></div>',
    'Pane 1 AI Fusion chip: Gemma 27b (GPU) → Gemma 4 27B'
)

# Pane 5 LLM box title
replace_all(
    'Gemma 27b (NVIDIA L4 GPU — 24GB VRAM)',
    'Gemma 4 27B (NVIDIA L4 GPU)',
    'Pane 5 LLM stage title'
)

# Pane 5 model chip
replace_all(
    '<span class="arch-chip-val">gemma:27b</span>',
    '<span class="arch-chip-val">gemma4:27b</span>',
    'Pane 5 model chip value'
)

# Pane 5 Ollama connector label
replace_once(
    'Submitted to Ollama API · gemma:27b · NVIDIA L4 GPU · on-cluster · no WAN',
    'Submitted to Ollama API · gemma4:27b · NVIDIA L4 GPU · on-cluster · no WAN',
    'Pane 5 Ollama connector label'
)

# ⓘ info panels (narrative text mentioning Gemma 27b)
replace_all(
    'Gemma 27b on the L4 GPU achieves',
    'Gemma 4 27B on the L4 GPU achieves',
    'Info panel Gemma reference'
)
replace_all('gemma:27b', 'gemma4:27b', 'API model name references')

# Pane 5 header paragraph
replace_once(
    'running on an NVIDIA L4 GPU within the edge cluster, with no WAN dependency.',
    'running on an NVIDIA L4 GPU within the edge cluster, with no internet dependency.',
    'Pane 5 header paragraph'
)

# ─────────────────────────────────────────────────────────────
# 2. Pane 1 Context Store: show inputs feeding ↓ into AlloyDB
# ─────────────────────────────────────────────────────────────
replace_once(
    '''              <div class="arch-stage stage-db" style="flex:1;min-width:110px;overflow:hidden">
                <div class="arch-stage-title">🗄 4. Context Store</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-blue"><span>AlloyDB</span></div>
                  <div class="arch-chip chip-purple"><span>RAG Manuals</span></div>
                  <div class="arch-chip chip-blue"><span>Operations Reports</span></div>
                  <div class="arch-chip chip-orange"><span>Model-Based RUL</span></div>
                </div>
              </div>''',
    '''              <div class="arch-stage stage-db" style="flex:1;min-width:110px;overflow:hidden">
                <div class="arch-stage-title">🗄 4. Context Store</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:3px">
                  <div class="arch-chip chip-purple"><span>Technical Library</span></div>
                  <div class="arch-chip chip-blue"><span>Operations Reports</span></div>
                  <div class="arch-chip chip-orange"><span>Model-Based RUL</span></div>
                </div>
                <div style="font-size:0.75rem;color:rgba(255,255,255,0.2);text-align:center;margin:3px 0">↓</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:3px">
                  <div class="arch-chip chip-blue" style="border-width:2px"><span>AlloyDB</span></div>
                </div>
              </div>''',
    'Pane 1 Context Store: inputs ↓ into AlloyDB'
)

# ─────────────────────────────────────────────────────────────
# 3. Tab nav reorder: How It Works first
# ─────────────────────────────────────────────────────────────
replace_once(
    '''      <div class="hdr-tab" :class="{active: mainTab==='operations'}" @click="mainTab='operations'">Fleet Operations</div>
      <div class="hdr-tab" :class="{active: mainTab==='financials'}" @click="mainTab='financials';fetchLedger()">Fleet Financials</div>
      <div class="hdr-tab" :class="{active: mainTab==='telemetry'}" @click="mainTab='telemetry';loadGrafana()" style="color:var(--muted);opacity:0.7">Fleet Telemetry</div>
      <div class="hdr-tab" :class="{active: mainTab==='architecture'}" @click="mainTab='architecture'">How It Works</div>''',
    '''      <div class="hdr-tab" :class="{active: mainTab==='architecture'}" @click="mainTab='architecture'">How It Works</div>
      <div class="hdr-tab" :class="{active: mainTab==='operations'}" @click="mainTab='operations'">Fleet Operations</div>
      <div class="hdr-tab" :class="{active: mainTab==='telemetry'}" @click="mainTab='telemetry';loadGrafana()">Fleet Telemetry</div>
      <div class="hdr-tab" :class="{active: mainTab==='financials'}" @click="mainTab='financials';fetchLedger()">Fleet Financials</div>''',
    'Tab nav reorder: How It Works first'
)

# ─────────────────────────────────────────────────────────────
# 4. Fix Grafana URL
# ─────────────────────────────────────────────────────────────
replace_once(
    "const grafUrl=metaTag?metaTag.content:'http://136.115.220.48';",
    "const grafUrl=metaTag?metaTag.content:'http://35.190.137.145';",
    'Grafana URL fix: 136.115.220.48 → 35.190.137.145'
)

# ─────────────────────────────────────────────────────────────
# 5. WAN badge → Field Link
# ─────────────────────────────────────────────────────────────
replace_once(
    "{{ mlops.wan_state === 'stable' ? '⚡ WAN' : mlops.wan_state === 'intermittent' ? '⚠ WAN' : '⬇ WAN' }}",
    "{{ mlops.wan_state === 'stable' ? '⚡ Field Link' : mlops.wan_state === 'intermittent' ? '⚠ Field Link' : '⬇ Field Link' }}",
    'WAN badge → Field Link'
)

# ─────────────────────────────────────────────────────────────
# 6. Pane 2: add SCADA RTU as parallel RabbitMQ subscriber
# ─────────────────────────────────────────────────────────────
replace_once(
    '''            <div class="arch-connector">↓ <span class="arch-connector-label">Consumed by Event Processor pod</span></div>

            <!-- Demo note -->
            <div class="arch-stage stage-scada" style="opacity:0.75;border-style:dashed">
              <div class="arch-stage-title" style="color:var(--muted)">⚙️ Fault Injector (Demo Only)</div>
              <div class="arch-stage-body">
                <div class="arch-chip chip-muted"><span>Overrides nominal sensor values to simulate fault conditions</span></div>
                <div class="arch-chip chip-muted"><span>Simulates gas_lock, sand_ingress, overheat signatures</span></div>
                <div class="arch-chip chip-muted"><span>In production: replaced by real VFD/PLC OPC-UA feed</span></div>
              </div>
            </div>''',
    '''            <!-- Two parallel consumers -->
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:4px">

              <!-- Path A: GDC AI -->
              <div>
                <div class="arch-connector" style="margin-bottom:8px">↓ <span class="arch-connector-label">GDC Edge AI path</span></div>
                <div class="arch-stage stage-ml">
                  <div class="arch-stage-title" style="font-size:0.65rem">⚡ Event Processor (GDC)</div>
                  <div class="arch-stage-body" style="flex-direction:column;gap:4px;margin-top:4px">
                    <div class="arch-chip chip-orange"><span style="font-size:0.62rem">XGBoost inference → AI-Based RUL</span></div>
                    <div class="arch-chip chip-purple"><span style="font-size:0.62rem">RAG context → Gemma 4 27B</span></div>
                  </div>
                </div>
              </div>

              <!-- Path B: SCADA HMI -->
              <div>
                <div class="arch-connector" style="margin-bottom:8px">↓ <span class="arch-connector-label">SCADA path (legacy)</span></div>
                <div class="arch-stage stage-scada" style="opacity:0.85">
                  <div class="arch-stage-title" style="font-size:0.65rem">🖥 SCADA RTU Subscriber</div>
                  <div class="arch-stage-body" style="flex-direction:column;gap:4px;margin-top:4px">
                    <div class="arch-chip chip-muted"><span style="font-size:0.62rem">Downsampled 15-min averages</span></div>
                    <div class="arch-chip chip-muted"><span style="font-size:0.62rem">Threshold alarms → Operator HMI</span></div>
                  </div>
                </div>
              </div>

            </div>

            <!-- Demo note -->
            <div class="arch-stage stage-scada" style="opacity:0.65;border-style:dashed;margin-top:12px">
              <div class="arch-stage-title" style="color:var(--muted)">⚙️ Fault Injector (Demo Only)</div>
              <div class="arch-stage-body">
                <div class="arch-chip chip-muted"><span>Overrides nominal sensor values to simulate fault conditions</span></div>
                <div class="arch-chip chip-muted"><span>In production: replaced by real VFD/PLC OPC-UA feed</span></div>
              </div>
            </div>''',
    'Pane 2: SCADA RTU as parallel RabbitMQ subscriber + GDC path'
)

# ─────────────────────────────────────────────────────────────
# Also: Pane 4 ⓘ info panel update (field_intel → ops_reports, Gemma)
# ─────────────────────────────────────────────────────────────
replace_once(
    'Ollama + Gemma 27b</strong> — Local LLM on L4 GPU',
    'Ollama + Gemma 4 27B</strong> — Local LLM on L4 GPU',
    'Info panel Ollama+Gemma ref'
)
replace_all('Gemma 27b', 'Gemma 4 27B', 'Remaining Gemma 27b text references')

# ─────────────────────────────────────────────────────────────
# Write and verify
# ─────────────────────────────────────────────────────────────
with open(FILE, 'w') as f:
    f.write(html)

print("SUCCESS — Changes applied:")
for c in changes:
    print(f"  ✅ {c}")

# Spot checks
spots = [
    ('Gemma 4 27B', 'Gemma 4 27B present'),
    ('gemma4:27b', 'gemma4 model name'),
    ('How It Works</div>', 'How It Works tab first'),
    ('35.190.137.145', 'Grafana URL fixed'),
    ('Field Link', 'WAN → Field Link'),
    ('SCADA RTU Subscriber', 'SCADA subscriber present'),
    ('Technical Library', 'Technical Library in Context Store'),
    ('Gemma 27b', 'Gemma 27b REMOVED'),
    ('gemma:27b', 'gemma:27b REMOVED'),
]
with open(FILE, 'r') as f:
    v = f.read()
for term, label in spots:
    if label.endswith('REMOVED'):
        status = '✅ ABSENT' if term not in v else '❌ STILL PRESENT'
    else:
        status = '✅' if term in v else '❌ MISSING'
    print(f"  {status}  {label}")
