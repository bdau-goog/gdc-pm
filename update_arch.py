import re

file_path = 'gke/fault-trigger-ui/index.html'
with open(file_path, 'r') as f:
    html = f.read()

new_block = """    <!-- ══ TAB: ARCHITECTURE ══ -->
    <div id="tab-architecture" class="main-tab-content" :class="{active: mainTab==='architecture'}">
      <div class="arch-container">
        <div class="arch-header">
          <div class="arch-title">GDC Predictive Maintenance — How It Works</div>
          <div class="arch-subtitle">Production deployment architecture · Fully localized on-premises edge AI</div>
        </div>
        
        <div class="arch-diagram">
          
          <!-- TIER 1: INPUT -->
          <div class="arch-tier">
            <div class="arch-tier-title">1. Data Sources</div>
            
            <div class="arch-node arrow-right">
              <div class="arch-node-title">📡 Field Sensors</div>
              <div class="arch-node-desc">ESP, Compressor, Turbine, Transformer</div>
              <div class="path-label path-blue">Live Telemetry</div>
            </div>
            
            <div class="arch-node arrow-right">
              <div class="arch-node-title">📄 Operations Records</div>
              <div class="arch-node-desc">Shift Notes, Work Orders, Lab Reports</div>
              <div class="path-label path-purple">Context Vectorized</div>
            </div>
            
            <div class="arch-node arrow-right">
              <div class="arch-node-title">📚 Industry Corpus</div>
              <div class="arch-node-desc">ISO Standards, OEM Manuals</div>
              <div class="path-label path-purple">RAG Knowledge Base</div>
            </div>
            
            <div class="arch-node node-demo" style="margin-top:24px">
              <div class="arch-node-title">⚙️ Fault Injector</div>
              <div class="arch-node-desc">(Demo Only)</div>
              <div style="font-size:0.6rem;color:var(--muted);margin-top:6px;font-style:italic">Simulates sensor degradation</div>
            </div>
          </div>
          
          <!-- TIER 2: EDGE INGESTION & ML -->
          <div class="arch-tier">
            <div class="arch-tier-title">2. Edge Ingestion & ML</div>
            
            <div class="arch-node">
              <div class="arch-node-title">SCADA</div>
              <div class="arch-node-desc">Legacy Threshold Monitoring</div>
              <div style="margin-top:8px;font-size:0.68rem;color:var(--text2)">
                <div style="margin-bottom:3px">• Operator HMIs</div>
                <div>• Threshold-Based RUL</div>
              </div>
            </div>
            
            <div style="font-size:0.55rem; font-weight:700; color:var(--muted); text-align:center; text-transform:uppercase; letter-spacing:0.08em; margin: 4px 0">
              ▲ Shared Telemetry ▼
            </div>
            
            <div class="arch-box" style="flex:1">
              <div class="arch-box-title">GDC EDGE CLUSTER</div>
              
              <div class="arch-node arrow-down" style="margin-top:auto">
                <div class="arch-node-title">RabbitMQ</div>
                <div class="arch-node-desc">Real-Time Telemetry Bus</div>
              </div>
              
              <div class="arch-node node-ml arrow-right" style="margin-top:16px; margin-bottom:auto">
                <div class="arch-node-title">⚡ XGBoost ML (GPU)</div>
                <div class="arch-node-desc">Multivariate Health Score & Fault Probability</div>
                <div class="path-label path-orange">Detects Anomaly</div>
              </div>
            </div>
          </div>
          
          <!-- TIER 3: DATA STORE & GEN AI -->
          <div class="arch-tier">
            <div class="arch-tier-title">3. Data Store & Gen AI</div>
            
            <div class="arch-box" style="flex:1; margin-top: 120px">
              <div class="arch-box-title">UNIFIED CONTEXT</div>
              
              <div class="arch-node node-db arrow-down" style="margin-top:auto">
                <div class="arch-node-title">AlloyDB Omni</div>
                <div class="arch-node-desc">PostgreSQL + pgvector<br/>Unified Asset Data Store</div>
                <div style="display:flex; gap:4px; flex-wrap:wrap; margin-top:8px">
                  <div class="path-label path-blue">telemetry_events</div>
                  <div class="path-label path-orange">ml_detections</div>
                  <div class="path-label path-purple">rag_documents</div>
                </div>
              </div>
              
              <div class="arch-node node-llm arrow-right" style="margin-top:16px; margin-bottom:auto">
                <div class="arch-node-title">⚡ Gemma 27b (GPU)</div>
                <div class="arch-node-desc">Edge LLM + RAG Synthesis</div>
                <div style="display:flex; gap:4px; flex-wrap:wrap; margin-top:8px">
                  <div class="path-label path-purple">Reads Ops Records</div>
                  <div class="path-label path-orange">Enhances RUL</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- TIER 4: OUTPUT -->
          <div class="arch-tier">
            <div class="arch-tier-title">4. Operator Interface</div>
            
            <div class="arch-node">
              <div class="arch-node-title">AI-Informed RUL</div>
              <div class="arch-node-desc">vs. Legacy SCADA Estimate</div>
              <div class="path-label path-orange">Context-Aware</div>
            </div>
            
            <div class="arch-node">
              <div class="arch-node-title">Recommended Action</div>
              <div class="arch-node-desc">Human-in-the-Loop (HITL) Approval</div>
              <div class="path-label path-green">Actionable Insight</div>
            </div>
            
            <div class="arch-node">
              <div class="arch-node-title">Financial Ledger</div>
              <div class="arch-node-desc">ROI Tracking & Cost Avoided</div>
              <div class="path-label path-green">Business Value</div>
            </div>
            
            <div class="arch-node" style="margin-top:16px">
              <div class="arch-node-title">Asset Chatbot</div>
              <div class="arch-node-desc">Operator Q&A & Investigations</div>
              <div class="path-label path-purple">RAG Empowered</div>
            </div>
          </div>
          
        </div>
      </div>
    </div>"""

pattern = re.compile(r'<!-- ══ TAB: ARCHITECTURE ══ -->\s*<div id="tab-architecture".*?</div>\s*</div>\s*</div>', re.DOTALL)
new_html, count = pattern.subn(new_block, html, 1)

if count > 0:
    with open(file_path, 'w') as f:
        f.write(new_html)
    print("Replaced successfully")
else:
    print("Pattern not found")
