# GDC-PM Demo Narrative & Value Proposition

## The Vision
The core objective of the GDC-PM (Predictive Maintenance) application is to demonstrate the power of **Google Distributed Cloud (GDC) at the edge**. In remote and harsh environments like upstream Oil & Gas (O&G) operations—where connectivity is intermittent and latency is critical—relying on centralized cloud infrastructure for real-time operational decisions is often impossible or cost-prohibitive.

GDC-PM showcases a fully localized, self-contained AI platform operating on a GKE cluster with attached GPU acceleration, proving that heavy-duty machine learning and generative AI workloads can run robustly at the tactical edge.

## How the Design Supports the Narrative

### 1. Multi-Modal AI Fusion
**The Challenge:** Traditional SCADA systems only trigger alerts when a single metric (like temperature or vibration) crosses a static, critical threshold. By then, the equipment is often already damaged. Furthermore, operators must manually cross-reference these alarms with offline systems like maintenance schedules or lab reports.

**The GDC-PM Solution:** We have implemented a multi-modal RAG (Retrieval-Augmented Generation) pipeline. The architecture seamlessly fuses:
- **Structured Data:** Live, high-frequency IoT telemetry ingested via RabbitMQ and evaluated by an XGBoost regressor.
- **Unstructured Data:** Shift notes, Maximo service records, fluid analysis lab reports, and historic process logs stored in AlloyDB.

**The Narrative Impact:** By dynamically generating non-generic documents (Fix 9) and feeding them to an edge-deployed LLM (Gemma), the demo shows that GDC doesn't just read sensors—it "reads" the entire operational context. The AI can predict a failure (like a valve washout or thermal runaway) long before the SCADA system throws a hard alarm.

### 2. Edge LLM Reasoning (Gemma)
**The Challenge:** Running large language models requires massive compute power, typically forcing operations back to the public cloud.

**The GDC-PM Solution:** By deploying `gemma:27b` via an Ollama pod directly onto an NVIDIA L4 GPU within the edge cluster, we completely eliminate the dependency on a WAN connection. We resolved a critical configuration issue (Fix 10 & Model Typo Fix) to ensure the LLM properly loads into GPU memory. 

**The Narrative Impact:** When the user injects a "thermal runaway" fault, the Gemma model responds *instantaneously* with dynamic findings that interpolate live metrics (e.g., "Discharge temp 241°F is trending up"). This proves to stakeholders that GDC provides true autonomy and low-latency intelligence, even in fully air-gapped scenarios.

### 3. Quantifiable ROI & Human-in-the-Loop (HITL)
**The Challenge:** Enterprise buyers need to see immediate financial justification for adopting edge AI.

**The GDC-PM Solution:** The application records every fault injection and subsequent operator resolution into an auditable `fault_sessions` table (Fix 11b). We use a Human-in-the-Loop (HITL) approval system where the AI recommends an action (e.g., "Reduce VFD Frequency 15%"), but the operator makes the final call. 

**The Narrative Impact:** This directly supports the "Self-Justifying Demo" feature. When the operator acknowledges the AI's recommendation, the system calculates the "Cost Avoided" (e.g., saving $150,000 by preventing an ESP motor burnout). The Fleet Financials Ledger updates in real-time, showing stakeholders exactly how edge AI pays for itself by turning catastrophic, unplanned downtime into scheduled, inexpensive maintenance.

## Conclusion
The recent developments solidify the GDC-PM demo as a premier showcase of edge autonomy. By resolving the GPU deployment blocker and extending the dynamic documentation to cover all asset classes, the demo now reliably presents a cohesive story: **GDC brings cloud-native, multi-modal AI directly to the operational edge, preventing failures, protecting capital assets, and driving undeniable ROI.**