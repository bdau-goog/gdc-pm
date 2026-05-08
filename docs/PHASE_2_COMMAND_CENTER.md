# GDC-PM: Phase 2 — Command Center & Autonomous Edge AI (RAG)
**Status:** DRAFT — Requirements Gathered  

## Core Objective
Evolve the predictive maintenance demo from a single-pane visualization into a multi-tab **Autonomous Edge Command Center**. The primary technical additions are a local, air-gapped Large Language Model (Gemma) powering a Retrieval-Augmented Generation (RAG) pipeline via AlloyDB Omni `pgvector`, and a rich financial tracking system.

All features must reinforce the narrative of a **disconnected GDC deployment** — running heavy AI workloads (XGBoost + LLM + Vector DB) entirely at the edge without cloud dependency.

---

## 1. UI Restructure (The 3-Tab Architecture)

The single dense dashboard will be split into three distinct tabs, selectable from the top header:

*   **Tab 1: Operations (Live Detection):** 
    *   The current UI (Fleet Bar, Active Incidents, Inject Panel, Plotly Forecast).
    *   *Updates needed:* Ensure the layout remains clean when expanding incidents.

*   **Tab 2: Fleet Financials (The Ledger):** 
    *   A full-page data table/ledger showing historical fault events.
    *   Columns: `Timestamp`, `Asset`, `Fault Type`, `Resolution Taken`, `Cost Incurred` (for the fix), and `Savings Realized` (the avoided catastrophic failure cost).
    *   Top summary cards showing aggregate capital saved, total incidents, and operational uptime protected.

*   **Tab 3: Historical Telemetry:** 
    *   An embedded iframe pointing to the existing Grafana dashboards.
    *   Allows presenters to pivot from "AI prediction" to "deep-dive time-series analysis."

---

## 2. Autonomous Edge RAG Pipeline (Gemma + AlloyDB)

Instead of hardcoded `ai_narrative` strings or basic remediation dictionaries, the system will dynamically generate fault assessments and repair procedures using a local LLM.

### Architecture
*   **Vector DB:** Enable the `pgvector` extension in the existing AlloyDB Omni container.
*   **Knowledge Base:** Create a new directory (`docs/rag_source/`) containing markdown or text files of simulated OEM equipment manuals, maintenance procedures, and safety guidelines for ESPs, Mud Pumps, etc.
*   **Ingestion Script:** A new Python script (`scripts/ingest_manuals.py`) that chunks the documents, generates embeddings (using a lightweight local model like `all-MiniLM-L6-v2`), and inserts them into AlloyDB Omni.
*   **LLM Inference:** Deploy a lightweight LLM (e.g., `gemma-2b-it` or `llama3-8b-instruct`) using Ollama or vLLM in a new GPU-enabled GKE node pool. *Crucially, this must run entirely within the cluster to demonstrate disconnected edge capabilities.*

### Integration Point
When the XGBoost classifier in `event-processor` detects a fault:
1.  It queries AlloyDB `pgvector` using the fault type and asset class.
2.  It retrieves the top 3 relevant manual excerpts.
3.  It sends a prompt to the local Gemma container: *"You are an O&G maintenance AI. The XGBoost model detected {fault} on {asset}. Using this manual: {context}, write a 2-sentence assessment and list 2 specific resolution options."*
4.  The generated text is saved to the `ai_narrative` column.

---

## 3. Multi-Option Resolution Workflow

The current "Dispatch" modal is too simple. It will be upgraded to an **AI Recommended Actions** modal.

*   **UI Placement:** When an operator clicks "Diagnose" on an active incident, a large modal (or dedicated slide-over panel) opens.
*   **Content:** It displays the Gemma-generated RAG assessment.
*   **Actionable Choices:** It presents multiple resolution options (parsed from the LLM or structured in the DB). 
    *   *Example (Gas Lock):* 
        *   Option A: "Reduce VFD Frequency 15%" (Cost: $0, Time: Instant)
        *   Option B: "Inject Chemical Defoamer" (Cost: $1,200, Time: 2 hours)
        *   Option C: "Schedule Full Workover" (Cost: $85,000, Time: 3 days)
*   **Financial Impact:** The operator selects an option and clicks "Execute". The chosen option's cost is deducted from the "Avoided Cost" to calculate the true Net Savings, which is then written to the DB and appears on the Financials Tab.

---

## 4. Ongoing Model Stability

*   **RUL Polish:** Ensure the recent fixes to the RUL calculations (noise reduction, indexing fixes, 10-minute query windows) remain stable under the new data structures. Investigate if any further smoothing is required for the RUL display during the new multi-option resolution windows.

---

## Execution Strategy (Next Task)

1.  **Infrastructure:** Update Terraform to add the GPU node pool. Deploy Ollama/vLLM.
2.  **RAG Setup:** Enable `pgvector`, write the ingestion script, populate `docs/rag_source/`.
3.  **UI Shell:** Build the 3-tab CSS/JS framework. Move Grafana to Tab 3.
4.  **Integration:** Update `event-processor` to call the LLM and update the Dispatch Modal to handle multi-option selections.
5.  **Financials:** Build the Tab 2 Ledger pulling from the expanded `telemetry_events` table.