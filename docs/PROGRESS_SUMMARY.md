# Progress Summary: Agentic Multimodal AI Framework for Aircraft Techlog Intelligence

**Student:** Ankit Bhardwaj · **BITS ID:** 2024AA05939  
**Course:** AIMLCZG628T — Dissertation / Project Work  
**Supervisor:** Alla Venkatesh Rao  
**Carried out at:** The Emirates Group, Dubai, UAE  
**Last Updated:** 2026-06-27

---

## Dissertation Phase Tracker

| # | Phase | Dates | Status |
|---|---|---|---|
| 1 | Dissertation outline & literature review | 05 May – 10 May 2026 | ✅ **Complete** |
| 2 | Data acquisition & preparation | 10 May – 15 Jun 2026 | ✅ **Complete** |
| 3 | **RAG pipeline & vector store** | 16 Jun – 05 Jul 2026 | 🚧 **In progress** |
| 4 | Triage & recurrence models | 06 Jul – 20 Jul 2026 | 🔜 Pending |
| 5 | LLM fine-tuning & agent integration | 21 Jul – 06 Aug 2026 | 🔜 Pending |
| 6 | API, UI & evaluation | 07 Aug – 13 Aug 2026 | 🔜 Pending |
| 7 | Dissertation review & submission | 14 Aug – 19 Aug 2026 | 🔜 Pending |

---

## Milestones Completed

### ✅ Phase 1 — Dissertation Outline & Literature Review (10 May 2026)

- Domain research: aviation MRO, EASA Level 1/2 ML governance, eTechlog/AHM standards
- Literature review across 20 papers covering RAG, multimodal learning, agentic AI,
  LoRA fine-tuning, LSTM sequence modelling, and NIST AI risk management
- Design decisions documented with research backing (see `docs/LITERATURE_REVIEW.md`)
- Outline viva slides prepared and presented

### ✅ Phase 2 — Data Acquisition & Preparation (15 Jun 2026)

Reproducible pipeline (`src/data/`, `seed=42`) delivering:

**Real public datasets:**
| Source | Content | Volume |
|---|---|---|
| NASA C-MAPSS (FD001–FD004) | Turbofan run-to-failure time series | 14 files (train/test/RUL) |
| FAA SDR 2023–2025 | Service Difficulty Reports | ~197,000 rows, 76 columns |
| NASA ASRS (3 report sets) | De-identified maintenance reports | 3 PDFs, 150 parsed reports |
| FAA Airworthiness Directives | AD rules via Federal Register API | 500 records, 49 full-text |

**Processed outputs:**
- 196,118 SDR records normalised onto 8-class defect taxonomy (166,037 mapped, 30,081 OTHER)
- 26,210 real defect→action pairs extracted from SDR free text (regex splitter)
- **1,213 retrievable knowledge documents** (563 synthetic + 500 FAA AD + 150 ASRS)

**Synthetic corpus:**
- 4,425 electronic techlog records across 70 tail numbers (Emirates-style A6-registry fleet)
- 3,915 C-MAPSS-style signal windows with defect-category degradation signatures
- 189-item QA benchmark: 163 MUST_CITE / 17 CAN_ANSWER / 9 MUST_ABSTAIN

**Train/val/test splits (chronological, no temporal leakage):**
- Triage: 3,540 / 442 / 443 — 8 classes, ~400–480 per class
- Recurrence: 3,470 / 372 / 373 — 37% positive rate (recurrence within 30 days)

### ✅ Mid-Semester Report & Viva (16 Jun 2026)

- Report submitted (signed by student 16/06/2026, supervisor Alla Venkatesh Rao)
- PDF: `docs/4e8e35284c7b855ed33336a5c05a5eb74c21229c (1).pdf`
- Viva slides: `docs/MidSem_Viva_Slides_2024AA05939.pptx`

---

## Current Phase — Phase 3: RAG Pipeline & Vector Store

**Target:** 16 Jun – 05 Jul 2026

**Work to complete:**
- [ ] Embed 1,213 knowledge corpus documents into Chroma vector store
  using `sentence-transformers` (all-MiniLM or similar)
- [ ] Implement retrieval agent (LangChain + Chroma) returning top-k cited docs
- [ ] Evaluate Recall@k and nDCG against the 189-item QA benchmark
- [ ] Measure hallucination rate and citation correctness on MUST_CITE items
- [ ] Verify MUST_ABSTAIN items trigger the safety escalation path

---

## System Architecture (Target)

```
Engineer Query
      |
      v
Agent Orchestrator (LangGraph)
      |
      +---> Triage Agent        ---> 8-class defect label + confidence
      |       (PyTorch MLP: text embedding + metadata + 42 signal features)
      |
      +---> Recurrence Agent    ---> repeat-risk within 30 days
      |       (PyTorch LSTM: per-tail defect history sequences)
      |
      +---> Retrieval Agent     ---> top-k cited docs from 1,213-doc corpus
              (LangChain + Chroma)
                    |
                    v
            Reasoning Agent (Mistral-7B + LoRA)
            Fine-tuned on 26,210 real defect→action pairs
                    |
                    v
            Safety Layer
            (confidence gate ≥85% strong / 70–85% verify / <70% abstain)
                    |
                    v
            Engineer UI (Streamlit + FastAPI)
```

---

## Dataset Summary (from `data/dataset_summary.json`)

| Dataset | Type | Volume |
|---|---|---|
| Synthetic techlogs | Synthetic | 4,425 records, 70 tail histories |
| Knowledge corpus | Mixed | 1,213 documents total |
| C-MAPSS signal windows | Synthetic | 3,915 windows, 117,450 cycle-rows |
| Triage splits | Processed | 3,540 / 442 / 443 |
| Recurrence splits | Processed | 3,470 / 372 / 373 |
| SDR normalised records | Processed | 196,118 records |
| Defect-action pairs | Processed | 26,210 pairs |
| QA benchmark | Processed | 189 items |

---

## Key Design Decisions (Literature-Backed)

| Decision | Rationale | Reference |
|---|---|---|
| RAG + LoRA fine-tuning | Grounded answers (citations) + domain adaptation | [Lewis'20] + [Hu'22] |
| Multimodal fusion (text + metadata + signals) | +13% accuracy over text-only | [He'22] |
| Agentic orchestration (LangGraph) | Specialised agents > monolithic LLM | [Schick'23] |
| LSTM for recurrence | Sequence model learns temporal dependencies | [Chen'21] |
| EASA Level 1/2 safety layer | Mandatory for aviation AI governance | EASA'23 |

---

## Evaluation Plan

| Component | Metrics |
|---|---|
| RAG retrieval | Recall@k, nDCG, hallucination rate, citation correctness, abstention P/R |
| Triage classifier | Accuracy, Precision/Recall/F1, AUROC, AUPRC per class |
| Recurrence model | Accuracy, F1, AUROC, AUPRC (positive: recurrence within 30 days) |
| End-to-end system | Latency p95, audit log completeness |

---

## Key Files

| File | Description |
|---|---|
| `docs/4e8e35284c7b...pdf` | Submitted mid-semester report |
| `docs/MidSem_Viva_Slides_2024AA05939.pptx` | Mid-sem viva slides |
| `docs/LITERATURE_REVIEW.md` | Literature review + design justifications |
| `data/DATA_CARD.md` | Full dataset provenance, schemas, licensing |
| `data/dataset_summary.json` | Generated pipeline run summary |
| `src/data/prepare_all.py` | One-shot data pipeline orchestrator |
| `src/data/taxonomy.py` | ATA chapters, 8 defect classes, fleet definitions |
