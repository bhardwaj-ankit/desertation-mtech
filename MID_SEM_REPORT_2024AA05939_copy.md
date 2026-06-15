# AN AGENTIC MULTIMODAL AI FRAMEWORK FOR AIRCRAFT TECHLOG INTELLIGENCE

**BITS ZG628T: Dissertation**

by

**Ankit Bhardwaj**
**2024AA05939**

Dissertation work carried out at

**The Emirates Group, Dubai, UAE**

Submitted in partial fulfilment of
**Master of Technology (Artificial Intelligence & Machine Learning)**
degree programme

Under the Supervision of
*[Supervisor Name]*
*[Supervisor Organisation]*

---

**BIRLA INSTITUTE OF TECHNOLOGY & SCIENCE**
**PILANI (RAJASTHAN)**

**June 2026**

---
---

## ABSTRACT

Aircraft maintenance operations at large carriers generate thousands of defect entries every month through electronic technical logbooks. Engineers working under time pressure often have to cross-reference maintenance manuals, MEL/CDL provisions, engineering orders, and previously resolved cases while moving between systems that do not talk to each other. This creates a high cognitive load, and even a delayed defect resolution can affect aircraft-on-ground time as well as operational safety.

This dissertation develops an Agentic Multimodal AI Framework, referred to throughout this report as the Techlog Copilot, to support maintenance engineers during defect investigation. The framework triages defects across eight fault categories, retrieves cited evidence from a curated knowledge corpus, predicts recurring defects on a per-tail basis, and generates explainable recommendations within safety governance constraints aligned to EASA Level 1/2 guidance.

At the mid-semester stage, I have completed the foundational data acquisition and preparation pipeline. This includes downloading and normalising four real public aviation datasets, generating a schema-consistent synthetic corpus for model training, and constructing train/validation/test splits for both the triage and recurrence tasks. The next phase will focus on implementing the RAG pipeline, training the triage and recurrence models, and integrating the agent orchestration layer.

---

*Signature of the Student: _________________ Date: _________________*

*Signature of the Supervisor: _______________ Date: _________________*

---

## CONTENTS

1. Introduction and Problem Context
2. System Architecture
3. Data Acquisition and Preparation — Work Done
4. Dataset Description and Statistics
5. Future Plan
6. Abbreviations
7. References

---

## 1. INTRODUCTION AND PROBLEM CONTEXT

The aircraft technical logbook is one of the most operationally critical records in commercial aviation. Every defect reported by a pilot, every maintenance action completed by an engineer, and every deferred item under a MEL provision is recorded there. At a large hub carrier operating several hundred aircraft, these entries can run into the thousands each week. Searching this data manually to identify patterns, retrieve the right manual section, or catch a recurring fault before it escalates is time-consuming and prone to missed connections.

The practical problem I set out to address is simple to state but difficult to implement: how can an engineer ask a maintenance question in natural language, receive a relevant evidence-backed recommendation, and still remain within the three-to-five minute turnaround window that line maintenance often demands?

Existing maintenance support tools at most carriers are largely retrieval-based. Engineers search PDF manuals by keyword, look up MEL items by ATA chapter, and rely on institutional memory for recurring fault patterns. These sources are not usually integrated, and they rarely provide a predictive view of repeat defects. The research opportunity is therefore to combine retrieval-augmented generation, multimodal deep learning, and agentic AI frameworks in a way that still respects the constraints of an airline MRO environment.

The proposed framework consists of five interacting components: a retrieval agent drawing on a knowledge corpus of approximately 1,213 documents, a triage agent classifying defects across eight ATA-aligned fault categories, a recurrence prediction agent operating on per-tail defect histories, a reasoning agent using a parameter-efficient fine-tuned LLM, and a safety layer for confidence gating, abstention, and audit logging. The safety governance approach is aligned to EASA's Concept Paper on Level 1 and Level 2 Machine Learning applications (Issue 2, 2023).

The dissertation is intended as a research prototype for academic purposes. No proprietary airline data is used at any stage; all real data comes from publicly accessible sources, and the synthetic component is clearly separated throughout.

---

## 2. SYSTEM ARCHITECTURE

The framework is built as a multi-agent system orchestrated through LangGraph, with each agent responsible for a distinct function in the maintenance decision pipeline. The overall flow is shown below.

```
Engineer Query
     |
     v
Agent Orchestrator (LangGraph)
     |
     +---> Triage Agent          ---> 8-class defect label + confidence
     |     (PyTorch MLP)
     |
     +---> Recurrence Agent      ---> repeat-risk within 30 days
     |     (PyTorch LSTM)
     |
     +---> Retrieval Agent       ---> top-k cited documents from corpus
           (LangChain + Chroma)
                |
                v
          Reasoning Agent (Mistral-7B + LoRA)
                |
                v
          Safety Layer
          (confidence gate, abstention, audit log)
                |
                v
          Engineer UI (Streamlit + FastAPI)
```

**Triage agent.** The triage agent is a multimodal MLP with three input streams: the defect narrative text embedded through a sentence-transformer, structured metadata such as ATA chapter and flight phase, and 42 C-MAPSS-style sensor features based on last value and slope per sensor. The eight output classes map to the fault taxonomy derived from ATA iSpec 2200 chapter groupings.

**Recurrence agent.** The recurrence agent uses an LSTM encoder over a chronologically ordered sequence of prior defect events for each tail number. Its input features include defect category, ATA chapter, severity, and days elapsed since the last event. The binary output estimates whether the same defect category is likely to recur within a 30-day horizon.

**Retrieval agent.** The retrieval agent is implemented as a RAG pipeline using Chroma as the vector store and sentence-transformers for document embedding. At this stage, the knowledge corpus contains 1,213 documents spanning real FAA Airworthiness Directives, synthetic AMM/MEL/EO/ADV procedures, and de-identified case narratives from NASA ASRS.

**Reasoning agent.** The reasoning agent uses Mistral-7B with LoRA adapters fine-tuned on the 26,210 real defect-to-action pairs extracted from FAA Service Difficulty Reports. Given the retrieval context and triage output, it generates a ranked recommendation with citations.

**Safety layer.** The safety layer applies confidence gating, suppresses low-confidence outputs, and routes uncertain cases to a human escalation flag. Nine safety-critical question types in the QA benchmark are marked MUST_ABSTAIN, where the expected behaviour is to decline the answer rather than guess. Every decision, including abstentions, is written to an audit log.

---

## 3. DATA ACQUISITION AND PREPARATION — WORK DONE

The first major deliverable of the dissertation is a reproducible data preparation pipeline (`src/data/`). It downloads, normalises, and generates the datasets required for the modelling tasks. I kept the pipeline deterministic (`seed=42`) so that the same inputs produce the same train/validation/test splits and synthetic records each time it is run.

### 3.1 Real Public Data

Four public data sources were integrated:

**NASA C-MAPSS Turbofan Degradation Dataset.** The four sub-datasets (FD001–FD004) from the NASA Prognostics Center of Excellence were downloaded and extracted. These files contain multivariate run-to-failure time series for turbofan engines across varying operating conditions. Their schema, made up of three operational settings and 21 sensor measurements, is used directly in this project to build the signal-modality input for the triage classifier. Separate train, test, and RUL (remaining useful life) files are available for each sub-dataset. This data is real and publicly licensed.

**FAA Service Difficulty Reports (SDR), 2023–2025.** Three annual CSV exports were downloaded from the FAA's public endpoint, covering approximately 197,000 individual defect reports filed by US-registry operators. Each record follows a 76-column schema with fields such as JASC/ATA code, part name, condition, stage of operation, and a free-text Discrepancy field. In many records, that field contains both the defect description and the corrective action taken. The normalisation step maps each record onto the project's eight-class defect taxonomy using ATA chapter lookup as the primary method and keyword matching as a fallback. This produced 196,118 normalised records, of which 166,037 were successfully mapped to one of the eight classes. The remaining 30,081 records fell into an OTHER bucket. I have retained these records with their mapping method flagged, since they show a clear limitation of the current heuristic approach.

Corrective action extraction from SDR free text was one of the noisier parts of the pipeline. The Discrepancy field often combines defect narrative and action text in a single block, separated by phrases such as "CORRECTIVE ACTION:", "C/A", or "RECTIFICATION". I used a regex-based splitter for these markers and extracted 26,210 defect-to-action pairs where a parseable corrective action was present. These pairs provide the primary supervised signal for fine-tuning the reasoning agent.

**NASA ASRS Report Sets.** Three curated report-set PDFs were downloaded from NASA's Aviation Safety Reporting System, covering maintenance technician reports, fuel management issues, and cabin fumes/smoke incidents. Each PDF contains 50 de-identified safety reports submitted voluntarily by aviation personnel. The PDFs were parsed using `pypdf`, with individual report blocks segmented by ACN (Accession Number) markers. Metadata fields such as aircraft type, component, flight phase, and anomaly type were extracted from the structured header of each report, while the free-text Narrative section was parsed separately. This produced 150 structured records that were added to the knowledge corpus as CASE-type documents.

**FAA Airworthiness Directives.** 500 AD rules were retrieved via the Federal Register API, with full text for 49 of these fetched from govinfo.gov. The remaining 451 carry only the abstract text, as the Federal Register's raw text endpoint is behind access controls. All 500 AD documents are included in the RAG corpus.

### 3.2 Synthetic Data

A schema-consistent synthetic corpus was generated to complement the real public data. I treated the synthetic component as supporting material, not as a replacement for real data. Its main role is to provide labelled training material for modelling tasks where public aviation data does not exist in the required form.

**Synthetic techlogs.** 4,425 electronic techlog records were generated across 70 tail numbers styled on an Emirates-style A6- registry fleet (A320, A321, A330, A350, B737, B777, B787 types). Each record includes the defect category, ATA chapter, component, severity, flight phase, station, and two versions of the defect narrative: a raw form with shorthand abbreviations typical of real techlog language, for example "Gen CB tripped repeatedly dur approach PLS ADV", and a clean normalised form. Per-tail histories are internally consistent, with recurrence flags assigned using 30-day lookback logic across the chronological sequence.

**Knowledge corpus.** 563 synthetic documents were generated across six document types: 42 AMM procedure snippets, 16 MEL deferral entries, 40 AD documents, 35 Engineering Orders, 30 operational advisories, and 400 prior-case documents. Each document references a specific defect category and ATA chapter, and the component-to-ATA-chapter pairing was validated programmatically (zero mismatches). The 500 real FAA ADs and 150 ASRS reports were appended to this base corpus, bringing the total to 1,213 retrievable documents.

**C-MAPSS-style signal windows.** 3,915 signal windows were generated following the NASA C-MAPSS schema (3 operational settings + 21 sensor measurements). Each window is associated with a techlog record and has a defect-category-specific degradation signature injected: pressure drift for hydraulic and landing gear faults, flow anomaly for fuel system faults, temperature rise for bleed air faults, and similar patterns for the remaining categories. A sensor summary file provides fusion-ready per-sensor last-value and slope features for each window.

**QA benchmark.** 189 question-answer pairs covering all eight defect categories were generated with a safety-aware taxonomy: 163 MUST_CITE items (answer requires citing a specific corpus document), 17 CAN_ANSWER items (answerable from general knowledge), and 9 MUST_ABSTAIN items (safety-critical authority questions where the correct response is to decline and escalate). This benchmark will be used to evaluate retrieval Recall@k, nDCG, citation correctness, hallucination rate, and abstention precision/recall.

### 3.3 Train/Val/Test Splits

Splits were generated chronologically to prevent temporal leakage. This is especially important for the recurrence task, where using future events to predict past ones would give artificially inflated metrics. The train set covers the earliest 80% of dates, the validation set the next 10%, and the test set the final 10%.

For triage: 3,540 train / 442 validation / 443 test records. Class balance in the training set is roughly uniform across the eight categories (400–480 per class). 3,888 of the total examples carry the signal modality.

For recurrence: 3,470 train / 372 validation / 373 test records. Positive rate (recurrence within 30 days) is approximately 37% in the training set.

---

## 4. DATASET DESCRIPTION AND STATISTICS

| Dataset | Type | Path | Volume |
|---------|------|------|--------|
| NASA C-MAPSS FD001–FD004 | Real | `data/raw/nasa_cmapss/` | 14 files (train/test/RUL per sub-dataset) |
| FAA SDR 2023–2025 | Real | `data/raw/faa_sdr/real/` | ~197,000 rows, 76 columns |
| NASA ASRS (3 report sets) | Real (de-identified) | `data/raw/nasa_asrs/report_sets/` | 3 PDFs, 150 parsed reports |
| FAA Airworthiness Directives | Real | `data/raw/faa_ad/real/` | 500 metadata records, 49 full-text |
| Synthetic Techlogs | Synthetic | `data/raw/techlogs/` | 4,425 records, 70 tail histories |
| Knowledge Corpus | Mixed | `data/raw/knowledge_corpus/` | 1,213 documents total |
| C-MAPSS-style Signal Windows | Synthetic | `data/raw/cmapss_signals/` | 3,915 windows, 117,450 cycle-rows |
| Triage Splits | Processed | `data/processed/triage/` | 3,540 / 442 / 443 |
| Recurrence Splits | Processed | `data/processed/recurrence/` | 3,470 / 372 / 373 |
| SDR Normalised Records | Processed | `data/processed/` | 196,118 records |
| Defect-Action Pairs | Processed | `data/processed/` | 26,210 pairs |
| QA Benchmark | Processed | `data/processed/` | 189 items |

**Table 1: Dataset Summary**

A few observations from working with this data are worth noting. The FAA SDR free text is genuinely noisy: it comes in upper case, uses heavy abbreviations, and often runs the defect and corrective action together without a clean separator. The regex-based splitter handles the majority of cases, but approximately 10% of records with corrective actions were not cleanly separable and were excluded from the pairs file. Given the overall volume, this is an acceptable loss for the current stage.

The ASRS PDF structure is generally well-suited to automated extraction. Each report follows a consistent tabular layout with explicit field labels, and the Narrative section is clearly delimited. The main challenge was that `pypdf` occasionally merged adjacent text blocks when the original PDF layout was column-based. A few reports therefore had malformed metadata fields, although the narrative text was consistently recoverable.

The 30,081 records that fell into the OTHER taxonomy bucket represent a real limitation of the heuristic ATA mapping approach. Many of these cover ATA chapters not in the project's 15-chapter scope (e.g., ATA 25 cabin equipment, ATA 45 central maintenance system). These records are preserved in the normalised output with the mapping_method field flagged as "unmapped", so future work could apply an ML-based classifier to recover them.

---

## 5. FUTURE PLAN

| Sl No | Phase | Start Date – End Date | Work to be Done | Status |
|-------|-------|-----------------------|-----------------|--------|
| 1 | Dissertation Outline | 05 May 2026 – 10 May 2026 | Literature review and prepare Dissertation Outline | COMPLETED |
| 2 | Data Acquisition & Preparation | 10 May 2026 – 15 Jun 2026 | Download public datasets; generate synthetic corpus; build train/val/test splits | COMPLETED |
| 3 | RAG Pipeline & Vector Store | 16 Jun 2026 – 05 Jul 2026 | Embed knowledge corpus into Chroma; implement retrieval agent; evaluate Recall@k and nDCG on QA benchmark | IN PROGRESS |
| 4 | Triage & Recurrence Models | 06 Jul 2026 – 20 Jul 2026 | Train multimodal MLP triage classifier (text + metadata + signals); train LSTM recurrence model; ablation baseline comparison | PENDING |
| 5 | LLM Fine-tuning & Agent Integration | 21 Jul 2026 – 06 Aug 2026 | LoRA fine-tune Mistral-7B on defect-action pairs; integrate triage, recurrence, retrieval, and reasoning agents in LangGraph; implement safety layer with confidence gating and abstention | PENDING |
| 6 | API, UI & Evaluation | 07 Aug 2026 – 13 Aug 2026 | FastAPI backend; Streamlit engineer UI; full system evaluation against all metrics (AUROC, nDCG, hallucination rate, latency p95) | PENDING |
| 7 | Dissertation Review & Submission | 14 Aug 2026 – 19 Aug 2026 | Submit dissertation to Supervisor and Additional Examiner for review; final corrections and submission | PENDING |

**Table 2: Project Plan**

---

## 6. ABBREVIATIONS

| Abbreviation | Full Form |
|---|---|
| AD | Airworthiness Directive |
| AHM | Aircraft Health Monitoring |
| AMM | Aircraft Maintenance Manual |
| ASRS | Aviation Safety Reporting System (NASA) |
| ATA | Air Transport Association (chapter numbering standard) |
| AUPRC | Area Under Precision-Recall Curve |
| AUROC | Area Under the Receiver Operating Characteristic Curve |
| BITE | Built-In Test Equipment |
| CDL | Configuration Deviation List |
| C-MAPSS | Commercial Modular Aero-Propulsion System Simulation |
| CMC | Central Maintenance Computer |
| EASA | European Union Aviation Safety Agency |
| EGT | Exhaust Gas Temperature |
| EO | Engineering Order |
| FAA | Federal Aviation Administration |
| GPU | Graphics Processing Unit |
| JASC | Joint Aircraft System/Component |
| LLM | Large Language Model |
| LoRA | Low-Rank Adaptation |
| LSTM | Long Short-Term Memory (recurrent neural network variant) |
| MEL | Minimum Equipment List |
| MLP | Multilayer Perceptron |
| MRO | Maintenance, Repair and Overhaul |
| nDCG | Normalised Discounted Cumulative Gain |
| NLP | Natural Language Processing |
| QA | Question Answering |
| RAG | Retrieval-Augmented Generation |
| RUL | Remaining Useful Life |
| SDR | Service Difficulty Report |
| SRM | Structural Repair Manual |

---

## 7. REFERENCES

[1] Lewis, P., Perez, E., Piktus, A., et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." *NeurIPS*, 2020.

[2] Vaswani, A., Shazeer, N., Parmar, N., et al. "Attention Is All You Need." *NeurIPS*, 2017.

[3] Hu, E. J., Shen, Y., Wallis, P., et al. "LoRA: Low-Rank Adaptation of Large Language Models." *ICLR*, 2022.

[4] Dettmers, T., Pagnoni, A., Holtzman, A., and Zettlemoyer, L. "QLoRA: Efficient Finetuning of Quantized LLMs." *NeurIPS*, 2023.

[5] Schick, T., Dwivedi-Yu, J., Dessi, R., et al. "Toolformer: Language Models Can Teach Themselves to Use Tools." *NeurIPS*, 2023.

[6] Devlin, J., Chang, M-W., Lee, K., and Toutanova, K. "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding." *NAACL*, 2019.

[7] Ouyang, L., Wu, J., Jiang, X., et al. "Training language models to follow instructions with human feedback." *NeurIPS*, 2022.

[8] EASA Concept Paper: First Usable Guidance for Level 1 & 2 Machine Learning Applications, Issue 2, European Union Aviation Safety Agency, 2023.

[9] IATA Guidance Material for Electronic Technical Logbooks (ELB) and Aircraft Health Monitoring (AHM), International Air Transport Association.

[10] FAA Service Difficulty Reporting System. Federal Aviation Administration. Available: https://av-info.faa.gov/sdrx/

[11] NASA ASRS Aviation Safety Reporting System Database. Available: https://asrs.arc.nasa.gov/

[12] NASA C-MAPSS Turbofan Degradation Simulation Data Set. Prognostics Data Repository, NASA Ames Research Center. Available: https://www.nasa.gov/content/prognostics-center-of-excellence-data-set-repository

[13] Saxena, A., Goebel, K., Simon, D., and Eklund, N. "Damage Propagation Modeling for Aircraft Engine Run-to-Failure Simulation." *1st International Conference on Prognostics and Health Management (PHM08)*, Denver, 2008.

[14] NIST AI Risk Management Framework (AI RMF 1.0), National Institute of Standards and Technology, 2023.

[15] MITRE ATLAS Adversarial Threat Landscape for AI Systems. Available: https://atlas.mitre.org/
