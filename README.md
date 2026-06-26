# Agentic Multimodal AI Framework for Aircraft Techlog Intelligence

**AIMLCZG628T: Dissertation / Project Work — BITS Pilani**
**Student:** Ankit Bhardwaj · **BITS ID:** 2024AA05939
**Supervisor:** Alla Venkatesh Rao · **Carried out at:** The Emirates Group, Dubai, UAE

> An evidence-grounded **"Techlog Copilot"** that helps aircraft maintenance engineers
> triage defects, retrieve cited maintenance evidence, predict recurring faults, and
> receive explainable, safety-constrained recommendations — aligned to EASA AI
> governance (Level 1/2) and IATA eTechLog/AHM guidance.

---

## Project status

| # | Phase | Dates | Status |
|---|---|---|---|
| 1 | Dissertation outline & literature review | 05 May – 10 May 2026 | ✅ Complete |
| 2 | Data acquisition & preparation | 10 May – 15 Jun 2026 | ✅ Complete |
| 3 | **RAG pipeline & vector store** | 16 Jun – 05 Jul 2026 | 🚧 **In progress** |
| 4 | Triage & recurrence models | 06 Jul – 20 Jul 2026 | 🔜 Pending |
| 5 | LLM fine-tuning & agent integration | 21 Jul – 06 Aug 2026 | 🔜 Pending |
| 6 | API, UI & evaluation | 07 Aug – 13 Aug 2026 | 🔜 Pending |
| 7 | Dissertation review & submission | 14 Aug – 19 Aug 2026 | 🔜 Pending |

The mid-semester report and viva are complete (submitted 16 Jun 2026, supervised by
Alla Venkatesh Rao). The project is now in Phase 3: embedding the 1,213-document
knowledge corpus into Chroma and implementing the retrieval agent.
See **[data/DATA_CARD.md](data/DATA_CARD.md)** for full dataset provenance and
**[docs/](docs/)** for submitted reports, slides, and literature review.

---

## Data

The pipeline produces **two layers** (run with one command, deterministic, `seed=42`):

### Real public data — downloaded live
| Source | Content | Path |
|---|---|---|
| **NASA C-MAPSS** | Turbofan run-to-failure time series (FD001–FD004) | `data/raw/nasa_cmapss/` |
| **FAA SDR** | Service Difficulty Reports 2023–2025 (~197k rows, 76-col schema) | `data/raw/faa_sdr/real/` |
| **NASA ASRS** | 3 report sets — 150 de-identified maintenance reports (PDF) | `data/raw/nasa_asrs/` |
| **FAA Airworthiness Directives** | 500 AD rules (Federal Register) + 49 full text (govinfo) | `data/raw/faa_ad/real/` |

**Derived from the real data**
- `data/processed/real_sdr_normalized.jsonl` — 196,118 SDR records mapped onto the
  8-class defect taxonomy (166,037 mapped; 30,081 flagged OTHER).
- `data/processed/real_sdr_defect_action_pairs.jsonl` — **26,210 real defect→action
  pairs** (corrective action parsed out of SDR free text via regex splitter).
- 500 real FAA ADs + 150 ASRS reports folded into the RAG corpus.

### Synthetic data — schema-matched, internally consistent
- 4,425 synthetic techlogs across 70 tail numbers (Emirates-style A6-registry fleet)
- 563-doc synthetic knowledge corpus (42 AMM / 16 MEL / 40 AD / 35 EO / 30 advisory / 400 prior-case)
- 3,915 C-MAPSS-*style* signal windows (3 op settings + 21 sensors, defect-category degradation signatures)
- 189-item QA benchmark: 163 MUST_CITE / 17 CAN_ANSWER / 9 MUST_ABSTAIN
- Chronological (leakage-safe) splits: triage 3,540/442/443 · recurrence 3,470/372/373

**Total knowledge corpus: 1,213 retrievable documents** (563 synthetic + 500 FAA AD + 150 ASRS)

> Real data lives under `data/raw/**` (git-ignored, ~310 MB, fully reproducible).
> Synthetic component↔ATA-chapter pairings are validated 0-mismatch.

### Reproduce the data
```bash
python3 -m src.data.prepare_all        # full pipeline (~8s when downloads are cached)
# or individual stages:
python3 -m src.data.download_public    # fetch the real public datasets
python3 -m src.data.ingest_real        # normalise real SDR + fold real ADs into corpus
```
The data pipeline is **standard-library only** (no pandas/numpy needed to generate it),
emitting CSV/JSONL that pandas/torch read in the modelling phase.

---

## Repository structure

```
dissertaion-abstract/
├── README.md                  # this file
├── TOOLS.md                   # technology stack & setup guide
├── GETTING_STARTED.md         # quick-start guide
├── requirements.txt
├── .env.example               # configuration template
├── docs/                      # submitted reports, slides, literature review
│   ├── 4e8e35284c7b...pdf     # mid-semester report (submitted 16 Jun 2026)
│   ├── MidSem_Viva_Slides_2024AA05939.pptx
│   ├── LITERATURE_REVIEW.md
│   ├── PROGRESS_SUMMARY.md
│   └── research/              # abstract, deep-research report, references
├── src/
│   ├── config.py              # configuration management
│   ├── agents/                # (phase 5) LangGraph agent stubs
│   ├── models/                # (phase 4) triage MLP + recurrence LSTM stubs
│   ├── utils/
│   └── data/                  # ✅ dataset acquisition & preparation pipeline
│       ├── taxonomy.py        # single source of truth (ATA, 8 defect classes, fleet…)
│       ├── download_public.py # live download of real public datasets
│       ├── ingest_real.py     # normalise real SDR + fold real ADs into the corpus
│       ├── generate_techlogs.py / generate_sdr.py / generate_corpus.py
│       ├── generate_signals.py / generate_qa.py
│       ├── build_splits.py    # chronological train/val/test splits
│       └── prepare_all.py     # one-shot orchestrator
├── data/
│   ├── DATA_CARD.md           # provenance, schemas, licensing, limitations
│   ├── dataset_summary.json   # generated run summary
│   ├── raw/                   # (git-ignored) real + synthetic raw data
│   └── processed/             # (git-ignored) splits, QA, normalised real data
├── models/                    # (phase 4) trained checkpoints
├── notebooks/                 # exploration
└── tests/                     # unit / integration tests
```

---

## Architecture

```
Engineer Query
      |
      v
Agent Orchestrator (LangGraph)
      |
      +---> Triage Agent        ---> 8-class defect label + confidence
      |       (PyTorch MLP)
      |
      +---> Recurrence Agent    ---> repeat-risk within 30 days
      |       (PyTorch LSTM)
      |
      +---> Retrieval Agent     ---> top-k cited documents from corpus
              (LangChain + Chroma)
                    |
                    v
            Reasoning Agent (Mistral-7B + LoRA)
                    |
                    v
            Safety Layer (confidence gate, abstention, audit log)
                    |
                    v
            Engineer UI (Streamlit + FastAPI)
```

**Stack:** LangGraph · LangChain + Chroma · sentence-transformers ·
PyTorch (MLP triage, LSTM recurrence) · Mistral-7B + LoRA · FastAPI · Streamlit ·
ragas / scikit-learn for evaluation. See **[TOOLS.md](TOOLS.md)**.

---

## Getting started

```bash
# 1. Environment (modelling phase needs the full stack)
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt           # (added in the modelling phase)

# 2. Prepare data
python3 -m src.data.prepare_all

# 3. Configure
cp .env.example .env                       # edit paths/models as needed
```

---

## Evaluation plan

- **RAG:** Recall@k, nDCG (vs gold doc ids), hallucination rate, citation correctness,
  abstention precision/recall
- **Triage / recurrence:** Accuracy, Precision/Recall/F1, AUROC, AUPRC
- **System:** latency (p95), audit completeness

---

## License & contact

Academic research project (BITS Pilani) — see institutional guidelines.
**Ankit Bhardwaj** · BITS ID 2024AA5039.

*All datasets here are public-source or synthetic; no proprietary airline data is used.
Prototype for academic research, not for operational deployment.*
