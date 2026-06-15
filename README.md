# Agentic Multimodal AI Framework for Aircraft Techlog Intelligence

**M.Tech (AI & ML) Dissertation — BITS Pilani**
**Student:** Ankit Bhardwaj · **BITS ID:** 2024AA5039
**Research area:** Artificial Intelligence · **Carried out at:** The Emirates Group, Dubai, UAE

> An evidence-grounded **"Techlog Copilot"** that helps aircraft maintenance engineers
> triage defects, retrieve cited maintenance evidence, predict recurring faults, and
> receive explainable, safety-constrained recommendations — aligned to EASA AI
> governance (Level 1/2) and IATA eTechLog/AHM guidance.

---

## Project status

| Layer | Status |
|---|---|
| **Data acquisition & preparation** | ✅ **Implemented** (`src/data/`, this milestone) |
| RAG pipeline / vector store | 🔜 Planned |
| Multimodal triage classifier | 🔜 Planned |
| Recurrence / early-warning model | 🔜 Planned |
| Agent orchestration + safety layer | 🔜 Planned |
| FastAPI + Streamlit app | 🔜 Planned |

This repository currently delivers the **Requirement Analysis & Dataset Preparation**
phase: a reproducible pipeline that downloads the real public aviation datasets named
in the proposal and generates an internally-consistent synthetic corpus for the
modelling tasks. See **[data/DATA_CARD.md](data/DATA_CARD.md)** for full provenance.

---

## Data

The pipeline produces **two layers** (run with one command, deterministic, `seed=42`):

### Real public data — downloaded live
| Source | Content | Path |
|---|---|---|
| **NASA C-MAPSS** | Turbofan run-to-failure time series (FD001–FD004) | `data/raw/nasa_cmapss/` |
| **FAA SDR** | Service Difficulty Reports 2023–2025 (~197k rows, 76-col schema) | `data/raw/faa_sdr/real/` |
| **NASA ASRS** | De-identified maintenance report sets (PDF) | `data/raw/nasa_asrs/` |
| **FAA Airworthiness Directives** | 500 AD rules (Federal Register) + 49 full text (govinfo) | `data/raw/faa_ad/real/` |

**Derived from the real data**
- `data/processed/real_sdr_normalized.jsonl` — 196,118 SDR records mapped onto the
  8-class defect taxonomy.
- `data/processed/real_sdr_defect_action_pairs.jsonl` — **26,210 real defect→action
  pairs** (corrective action parsed out of SDR free text, often citing the resolving AMM/SRM task).
- 500 real FAA AD documents folded into the RAG corpus.

### Synthetic data — schema-matched, internally consistent
- ~4,425 synthetic techlogs (coherent per-tail histories → recurrence labels)
- 563-doc synthetic knowledge corpus (AMM / MEL / AD / EO / advisory / prior cases)
- C-MAPSS-*style* operational signal windows (3 op settings + 21 sensors)
- 189-item QA benchmark with the **can-answer / must-cite / must-abstain** safety taxonomy
- Chronological (leakage-safe) train/val/test splits for triage and recurrence

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
├── LITERATURE_REVIEW.md       # literature review + design justifications
├── .env.example               # configuration template
├── research/                  # abstract, deep-research report, references, slides
├── src/
│   ├── config.py              # configuration management
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
├── models/                    # (planned) trained checkpoints
├── notebooks/                 # exploration
└── tests/                     # unit / integration tests
```

---

## Architecture (target)

```
Engineer query ─▶ Agent Orchestrator (LangGraph)
                    ├─ Triage Agent     → defect class (8) + confidence
                    ├─ Recurrence Agent → repeat-risk over horizon
                    └─ Retrieval Agent  → RAG over manuals/MEL/AD/cases
                            ▼
                    Reasoning Agent (fine-tuned LLM) → ranked, cited recommendation
                            ▼
                    Safety layer (confidence gate, abstention, audit log)
                            ▼
                    Engineer UI (Streamlit + FastAPI)
```

**Planned stack:** LangGraph · LangChain + Chroma · sentence-transformers ·
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
