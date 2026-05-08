# GDC-PM Phase 2 — Deployment & Validation Session Summary
**Date:** 2026-05-08

## Accomplishments

1. **Successful Full-Stack Phase 2 Deployment**
   - Deployed the complete Phase 2 architecture to the `gdc-edge-simulation` GKE Autopilot cluster using `scripts/deploy-phase2.sh`.
   - Executed AlloyDB schema migrations, adding the `cost_incurred` column and pgvector structures.
   - Built and pushed updated container images for `fault-trigger-ui`, `event-processor`, and `inference-api`.
   - All 8 pods across the stack were successfully brought up to healthy `1/1 Running` states.

2. **RAG Pipeline & Edge LLM Activation**
   - Provisioned an Ollama server running the Gemma 2B model on an NVIDIA T4 GPU node.
   - Successfully ingested 11 context chunks from 4 OEM equipment manuals into the AlloyDB pgvector store via `scripts/ingest_manuals.py`.
   - Verified the end-to-end RAG pipeline: the event processor successfully correlates live fault telemetry with manual extracts, and Ollama generates asset-specific diagnostic narratives with multi-option resolution recommendations.

3. **Inference & RUL Enhancements Validated**
   - Verified that the `inference-api` correctly loads and serves predictions across all 7 asset classification models simultaneously.
   - Validated the RUL (Remaining Useful Life) stability fix. Injected a 3600-second gradual `sand_ingress` fault on an ESP; observed a smooth, stable decline in RUL (staying tightly within a 28–31 minute range) without the erratic 0/600 flipping seen in previous phases.

4. **Financial Ledger & UI Verified**
   - Confirmed the 3-tab UI layout (Operations, Fleet Financials, Historical Telemetry) is active.
   - Verified the dispatch acknowledgment flow: operator selections correctly deduct `cost_incurred` and calculate net `cost_avoided`.
   - Validated the `clear-dispatch` utility securely resets the ledger savings ticker to $0 without generating negative values.

## Key Decisions & Fixes Applied During Deployment

* **Event Processor Configuration:** Fixed the `event-processor.yaml` manifest by changing `AI_NARRATIVE_ENABLED` from `rule_based` to `rag`, and increased the memory limit to `1Gi` to accommodate the `sentence-transformers` and PyTorch overhead.
* **Inference API Workload Identity:** Restored the critical `iam.gke.io/gcp-service-account` annotation on the `ml-inference-ksa` service account to ensure the API could pull model artifacts from the GCS bucket (`gdc-pm-v2-models`).
* **GPU Provisioning:** GKE Autopilot Warden required a specific `cloud.google.com/gke-accelerator` nodeSelector. Initially requested an L4 GPU, but due to capacity constraints in `us-central1-a`, dynamically pivoted the selector to `nvidia-tesla-t4` (16GB VRAM), which successfully provisioned the `n1-highmem-2` instance.

## Edge Hardware Portability Context (GDC SWO)

* Evaluated the target hardware for GDC Software-Only deployment: **3x NVIDIA A2 GPUs**.
* **Conclusion:** The A2 (Ampere, 10GB VRAM, 250 INT8 TOPS, 60W TDP) is excellently suited for Edge AI inference. Gemma 2B at Q4_0 quantization only requires ~1.7GB of VRAM, leaving extensive headroom.
* **Required Manifest Change for GDC SWO:** 
  The GKE-specific `cloud.google.com/gke-accelerator` nodeSelector must be removed or commented out in `gke/ollama/k8s/ollama.yaml` when deploying to the physical GDC edge nodes. The existing `nvidia.com/gpu: 1` resource request is sufficient for the NVIDIA GPU Operator to handle scheduling.

## Active Context / Next Steps

* Phase 2 is considered **Code Complete and Deployed**.
* The cluster is in a stable, observable state suitable for live demonstrations of multi-asset degradation tracking, AI RAG diagnostics, and edge financial ledgers.
* Ready to transition to new tasks or Phase 3 initiatives.