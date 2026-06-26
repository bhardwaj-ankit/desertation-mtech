---
title: "Agentic Multimodal AI Framework for Aircraft Techlog Intelligence"
subtitle: "Outline Viva Presentation"
author: "Ankit Bhardwaj | BITS ID: 2024AA5039"
date: "May 2026"
---

# Project Context

- Aircraft maintenance teams rely on eTechlogs, maintenance records, advisories, manuals, and prior defect history.
- Much of this information is unstructured, distributed, and time-sensitive.
- Engineers often need to identify recurring defects, relevant MEL/CDL references, troubleshooting history, and operational risk quickly.
- The project proposes an AI-assisted maintenance copilot for evidence-grounded techlog intelligence.

::: notes
Start by explaining that the project is motivated by real maintenance workflow challenges: large volumes of technical text, fragmented information sources, and strict operational timelines. The focus is decision support, not autonomous aircraft maintenance decisions.
:::

# Problem Statement

- Manual techlog analysis increases cognitive workload and response time.
- Conventional keyword search may miss context, similarity, and historical defect patterns.
- General LLM responses may hallucinate unless grounded in trusted evidence.
- Aviation maintenance requires traceability, explainability, confidence control, and human oversight.

::: notes
Emphasize that the problem is not only information retrieval. The core challenge is combining retrieval, prediction, explanation, and safety constraints in a way suitable for aviation maintenance support.
:::

# Objectives

- Study AI approaches for maintenance intelligence, RAG, conversational systems, and predictive maintenance.
- Design an agentic multimodal framework for aircraft techlog analysis.
- Implement a RAG-based Techlog Copilot with evidence citation.
- Develop predictive models for recurring defect patterns and early-warning indicators.
- Add safety-constrained decision support using confidence, abstention, escalation, and audit logging.
- Evaluate retrieval quality, prediction performance, latency, hallucination reduction, and audit completeness.

::: notes
This slide maps directly to the submitted abstract. Keep it crisp: the project is both research-oriented and prototype-oriented.
:::

# Scope

- Academic prototype, not a production deployment.
- Data sources include public industrial defect datasets, synthetic techlog data, aviation advisories, and simulated operational signals.
- Core components include RAG, vector search, conversational AI, predictive modeling, multimodal fusion, and safety governance.
- Evaluation will use retrieval, prediction, response quality, latency, and auditability metrics.

::: notes
Mention that sensitive airline production data is outside the declared academic scope unless separately approved. The prototype can still be realistic using public and synthetic sources.
:::

# Proposed Framework

- Techlog Copilot for evidence-grounded question answering.
- Retrieval agent for manuals, MEL/CDL extracts, advisories, engineering orders, and prior cases.
- Predictive agent for recurring defect and risk pattern detection.
- Multimodal fusion layer combining text, metadata, and simulated health signals.
- Safety layer for confidence scoring, abstention, escalation, and audit trail generation.

::: notes
Explain the agentic structure as a coordinated set of specialized components. The key idea is that each component has a clear responsibility rather than one black-box model doing everything.
:::

# Methodology

1. Literature review and problem refinement.
2. Dataset preparation using public, synthetic, and simulated maintenance data.
3. Knowledge ingestion, chunking, embedding generation, and vector indexing.
4. RAG-based conversational assistant implementation.
5. Predictive modeling for recurring defect patterns.
6. Multimodal fusion and safety-constrained recommendation layer.
7. Experimental evaluation, benchmarking, and ablation studies.

::: notes
Use this as the main walkthrough slide. The methodology is staged so the examiner can see a feasible path from data preparation to evaluation.
:::

# Data and Knowledge Sources

- FAA Service Difficulty Reports and aviation safety resources.
- NASA C-MAPSS prognostics dataset for health signal simulation.
- NASA ASRS safety narratives for operational incident-style text.
- Public aviation advisories and maintenance-related documents.
- Synthetic techlog records representing defect narratives, metadata, and maintenance actions.

::: notes
Clarify that the project avoids dependency on confidential production data for the academic prototype. Synthetic records are useful for controlled experiments and repeatable benchmarking.
:::

# AI Components

- Retrieval-Augmented Generation for grounded answers and citations.
- LLM-based conversational interface for engineer-facing interaction.
- Embedding and vector database pipeline for semantic retrieval.
- Predictive models for recurring defect classification and early-warning signals.
- Multimodal learning to combine defect text, structured metadata, and operational signals.
- Explainability methods for evidence traceability and decision transparency.

::: notes
This is the technical core. Explain that RAG handles evidence-based Q&A, while predictive modeling handles pattern detection and risk indicators.
:::

# Safety and Governance

- Human-in-the-loop decision support.
- Confidence thresholds before recommendations are shown.
- Abstention when evidence or confidence is insufficient.
- Escalation paths for safety-critical or ambiguous cases.
- Evidence citation for retrieved sources and generated recommendations.
- Audit logging for traceability and post-review.
- Alignment with EASA Level 1/Level 2 AI guidance and AI risk management principles.

::: notes
Stress that the system is designed to assist engineers, not replace certified maintenance judgment. This is important for aviation acceptability.
:::

# Progress So Far

- Problem statement, objectives, and scope have been finalized.
- Submitted the abstract and outline report.
- Identified literature areas: RAG, predictive maintenance, multimodal AI, agentic systems, explainable AI, and aviation AI governance.
- Identified candidate datasets and knowledge sources.
- Defined high-level architecture and core modules.
- Defined initial evaluation metrics for retrieval, prediction, latency, recommendation quality, and auditability.

::: notes
Since this is outline viva, present this as current dissertation progress. Avoid claiming implementation results unless you have already built them.
:::

# Key Findings From Initial Study

- Techlog intelligence needs both semantic retrieval and predictive analysis.
- Evidence-grounded RAG is better suited than standalone LLM generation for maintenance use cases.
- Multimodal inputs can capture patterns that text-only analysis may miss.
- Safety-critical domains require abstention, traceability, and human oversight by design.
- Evaluation must cover both technical metrics and operational usefulness.

::: notes
Frame these as findings from the initial literature and problem analysis. They justify the selected architecture and evaluation plan.
:::

# Evaluation Plan

- Retrieval performance: Recall@k, nDCG, citation relevance.
- Generation quality: hallucination reduction against parametric-only LLM baseline.
- Prediction performance: AUROC, AUPRC, F1-score, and early-warning precision.
- Multimodal value: comparison against text-only and metadata-only baselines.
- Operational metrics: p95 response latency and task completion quality.
- Governance metrics: confidence coverage, abstention correctness, and audit completeness.

::: notes
Examiners often ask how success will be measured. This slide shows that evaluation is planned across retrieval, prediction, usability, and governance.
:::

# Future Work Plan

- Weeks 3-5: dataset collection, synthetic data generation, preprocessing, and requirements.
- Weeks 6-8: RAG pipeline, vector database, and Techlog Copilot prototype.
- Week 8: mid-semester review and prototype demonstration.
- Weeks 9-12: multimodal fusion, predictive modeling, and safety layer.
- Weeks 13-14: testing, benchmarking, and ablation studies.
- Weeks 15-16: dissertation review, final corrections, submission, and viva preparation.

::: notes
This mirrors the submitted work plan. Present it as the execution roadmap from outline viva to final dissertation.
:::

# Expected Contribution

- A structured framework for aircraft techlog intelligence.
- Evidence-grounded maintenance Q&A with source citation.
- Predictive support for recurring defect pattern identification.
- Multimodal analysis combining text, metadata, and simulated operational signals.
- Safety-constrained decision support aligned with aviation AI governance expectations.

::: notes
End by restating the contribution in a confident but measured way. The expected outcome is a research prototype and evaluation, not direct operational deployment.
:::
