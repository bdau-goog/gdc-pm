# GDC-PM Development Decisions & Changes

This document provides a detailed overview of the recent architectural decisions, bug fixes, and system improvements implemented in the GDC-PM (Predictive Maintenance) application.

## 1. Multi-Modal RAG Document Expansion (Fix 9)
**Decision:** We expanded the `generate_dynamic_documents` function to generate realistic, simulated enterprise documents for all remaining non-ESP asset faults (`bearing_wear_glift`, `pulsation_dampener_failure`, `valve_washout`, `piston_seal_wear`, `gearbox_bearing_spalling`, and `hydraulic_leak`).
**Why:** To truly demonstrate multi-modal AI at the edge, the LLM needs a rich context window that combines structured telemetry with unstructured operational data. By dynamically injecting live sensor values (e.g., SPM, PSI, temperatures) into Maximo service histories, process historian logs, and driller shift notes, the simulated RAG pipeline perfectly mimics a complex upstream O&G environment.

## 2. Dynamic Gemma Reasoning Templates (Fix 10)
**Decision:** We transitioned the LLM "Gemma Finding" outputs from static strings to dynamic templates for `thermal_runaway`, `valve_failure`, and `bearing_wear_glift`.
**Why:** Stakeholders need to see the edge LLM actively processing live metrics. By injecting real-time values (like a climbing discharge temperature of 241°F) directly into the generated LLM assessment, the application convincingly demonstrates real-time edge inference rather than canned responses.

## 3. Fault Sessions Audit Logging (Fix 11b)
**Decision:** We introduced a full write-path for the `fault_sessions` table in AlloyDB Omni. The system now performs an `INSERT` when a fault is triggered via `/api/inject/degrade`, and an `UPDATE` when the operator resolves the fault via the `/api/agent/hitl-approve` Human-in-the-Loop endpoint.
**Why:** Predictive maintenance platforms must provide an auditable trail of interventions and savings. Tracking the exact lifecycle of a fault (injection time, resolution time, action taken, and cost avoided) allows the platform to quantify its ROI and populate the Fleet Financials Ledger accurately.

## 4. Deploy-from-Scratch Runbook
**Decision:** We authored a comprehensive deployment runbook (`docs/runbooks/deploy-from-scratch.md`) that covers the entire lifecycle from zero to a fully operational GKE cluster.
**Why:** The architecture involves stateful databases (AlloyDB), message brokers (RabbitMQ), GPU-accelerated workloads (Ollama), and custom microservices. A strict deployment order is required (e.g., RabbitMQ must precede the Event Processor to prevent CrashLoopBackOffs). The runbook ensures reliable, reproducible cluster spin-ups for future demos.

## 5. GPU Utilization & Model Registration Fix
**Decision:** We performed a global codebase patch to change the targeted LLM model from `gemma4:27b` to `gemma:27b`. 
**Why:** The init container was silently failing to pull the non-existent `gemma4:27b` model from the Ollama registry. Consequently, the main Ollama server booted with an empty memory footprint, causing the application to fall back to CPU inference and leaving the NVIDIA L4 GPU completely unutilized. Correcting the model name allowed the init script to successfully download the 15GB model, directly attaching the GPU VRAM and restoring hardware-accelerated inference.

## 6. RabbitMQ & Event Processor Resilience
**Decision:** We identified that the `event-processor` pod enters a severe `CrashLoopBackOff` if RabbitMQ is not initialized first, due to `socket.gaierror` resolution failures. 
**Why:** We documented this specific operational blocker in the runbook, establishing a strict dependency sequence. This prevents demo downtime and ensures the telemetry pipeline (Simulator -> RabbitMQ -> Processor -> DB) initializes cleanly.