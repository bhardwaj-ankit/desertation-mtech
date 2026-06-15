# Data Card — Aircraft Techlog Intelligence Datasets

**Project:** An Agentic Multimodal AI Framework for Aircraft Techlog Intelligence
**Phase:** Requirement Analysis & Dataset Preparation
**Generator:** `src/data/` (Python standard library only — no pandas/numpy required)
**Reproduce:** `python -m src.data.prepare_all` (deterministic, `seed=42`)

---

## 1. Why this data exists

The deep-research report and abstract specify a **"minimum viable (public)"**
data plan: FAA SDR + FAA AD + NASA ASRS + NASA C-MAPSS + curated manuals, with
synthetic QA pairs, and an **"airline uplift"** path for real internal techlogs
later.

This package delivers **two layers**:

1. **Real public data — downloaded live** (`python -m src.data.download_public`):
   NASA C-MAPSS, FAA SDR (3 years), NASA ASRS report sets, and FAA Airworthiness
   Directives (Federal Register API + govinfo full text). The real SDR is
   normalised onto the project taxonomy and the real ADs are folded into the RAG
   corpus (see §5–6).
2. **A complete, internally-consistent synthetic corpus that mirrors the real
   sources' schemas**, so RAG / multimodal triage / recurrence / safety
   experiments have richly-labelled, leakage-controlled splits today. The same
   event (a techlog) is threaded through its synthetic SDR filing, C-MAPSS signal
   window, prior-case document and train/val/test placement.

> **Integrity note:** the files under `data/raw/{nasa_cmapss,faa_sdr/real,
> nasa_asrs,faa_ad/real}/` are **real public-source data** fetched live (status
> in `data/raw/public_sources_status.json`, provenance in each `SOURCE.md`).
> The techlogs, the synthetic SDR/corpus, and the C-MAPSS-*style* signal windows
> are **synthetic** (clearly labelled, for prototyping only). No proprietary
> airline data is used.

---

## 2a. Real public data — downloaded live

| Source | Path | Volume |
|---|---|---|
| NASA C-MAPSS (FD001–FD004) | `data/raw/nasa_cmapss/CMAPSSData/` | 4 sub-datasets, ~43 MB (train/test/RUL `.txt` + PDF) |
| FAA SDR (2023–2025) | `data/raw/faa_sdr/real/SDR-*.csv` | 3 files, ~197k report rows, ~99 MB (76-col official schema) |
| NASA ASRS report sets | `data/raw/nasa_asrs/report_sets/*.pdf` | Mechanic / Fuel / Cabin-Fumes (de-identified narratives) |
| FAA Airworthiness Directives | `data/raw/faa_ad/real/` | 500 AD rules (metadata JSONL) + 49 full-text (govinfo) |

Derived from the real data:
- `data/processed/real_sdr_normalized.jsonl` + `real_sdr_summary.json` — 196,118
  real SDR records normalised onto the 8-class taxonomy (166,037 mapped via
  JASC/ATA chapter + discrepancy keywords; 30,081 OTHER). Each record's free-text
  `Discrepancy` is split into `defect_text` + `corrective_action`.
- `data/processed/real_sdr_defect_action_pairs.jsonl` — **26,210 real
  defect→action pairs** (the corrective action parsed out of the SDR narrative,
  often citing the resolving AMM/SRM task). Direct supervised signal for the
  "next best action" / recommendation copilot and RAG grounding.
- 500 real AD documents appended to the RAG corpus (`AD-FR-*`), 49 with real
  full text — so retrieval cites genuine authoritative ADs.

Re-fetch any time with `python -m src.data.download_public` (cached if present).
`data/raw/*` is git-ignored (reproducible), so these large files don't bloat the repo.

## 2b. Synthetic data produced (`seed=42`)

| Dataset | Path | Volume |
|---|---|---|
| Synthetic techlogs | `data/raw/techlogs/techlogs.{csv,jsonl}` | 4,425 records, 70 tails |
| FAA SDR-style records | `data/raw/faa_sdr/sdr_records.{csv,jsonl}` | 2,422 records |
| RAG knowledge corpus | `data/raw/knowledge_corpus/corpus.jsonl` + `docs/*.md` | 563 documents |
| C-MAPSS-style signals | `data/raw/cmapss_signals/signal_{windows,summary}.csv` | 3,915 windows / 117,450 cycle-rows |
| QA benchmark | `data/processed/qa_pairs.jsonl` | 189 items |
| Triage splits | `data/processed/triage/{train,val,test}.jsonl` | 3,540 / 442 / 443 |
| Recurrence splits | `data/processed/recurrence/{train,val,test}.jsonl` | 3,470 / 372 / 373 |
| Run summary | `data/dataset_summary.json` | — |

Synthetic knowledge corpus: AMM 42, MEL 16, AD 40, EO 35, ADV 30, CASE 400.
**Plus 500 REAL FAA AD documents** appended → `corpus.jsonl` holds **1,063 docs**.
All synthetic component↔ATA-chapter pairings are validated consistent (0 mismatches).

---

## 3. Schemas

### 3.1 Techlogs (`techlogs.jsonl`)
Mirrors an electronic Technical Log Page (TLP) entry.
`techlog_id, tail, aircraft_type, family, engine, msn, date, station,
flight_phase, ata_chapter, ata_title, defect_category, defect_label, component,
severity, raw_narrative, clean_narrative, reported_by, action_taken,
resolution_status, deferred, mel_ref, is_recurrence, prior_techlog_id,
recurrence_horizon_days, has_signal`

- `raw_narrative` carries realistic techlog shorthand/abbreviations
  (e.g. *"Generator CB tripped repeatedly dur approach PLS ADV"*);
  `clean_narrative` is the normalised form (NLP target pair).
- **8 defect categories** (the triage label space) are correlated with ATA
  chapter, component, severity distribution and signal behaviour.

### 3.2 FAA SDR-style (`sdr_records.csv`)
Follows the public Service Difficulty Report structure:
`control_number, difficulty_date, operator, aircraft_make, aircraft_model,
engine_make, ata_code, part_name, part_condition, stage_of_operation,
nature_of_condition, remarks, corrective_action, precautionary_procedure`.

### 3.3 Knowledge corpus (`corpus.jsonl`)
One JSON object per document; full text also written to `docs/<doc_id>.md`.
`doc_id, doc_type, title, ata_chapter, defect_category, text, source, effective_date`.
Document types map to the abstract's authoritative artefacts:
- **AMM** — Aircraft Maintenance Manual procedure snippets
- **MEL** — Minimum Equipment List / CDL deferral entries (with category + rectification interval)
- **AD** — Airworthiness Directives (unsafe condition + required action + compliance time)
- **EO** — Engineering Orders / Service Bulletins
- **ADV** — operational advisories / troubleshooting notes
- **CASE** — prior resolved techlog cases (links back to a `techlog_id`)

### 3.4 C-MAPSS-style signals (`signal_windows.csv`)
**Identical schema to NASA C-MAPSS**: `unit, techlog_id, defect_category,
cycle, RUL, op_setting_1..3, sensor_1..21`. A degradation signature is injected
per the defect category's signal mode (pressure drift, flow anomaly, temp rise,
electrical, sensor bias) scaled by severity. `signal_summary.csv` provides
fusion-ready per-sensor `last` value + `slope` features.

### 3.5 QA benchmark (`qa_pairs.jsonl`)
`qa_id, question, answer_type, gold_doc_ids, reference_answer, ata_chapter,
defect_category, should_abstain`. **Safety taxonomy** labels:
`MUST_CITE` (163) · `CAN_ANSWER` (17) · `MUST_ABSTAIN` (9 — safety-critical
authority or out-of-scope). Drives Recall@k / nDCG (vs `gold_doc_ids`),
citation correctness, hallucination rate, and abstention precision/recall.

---

## 4. Modelling tasks the splits support

- **Multimodal triage** (`triage/`) — text + metadata + signal features →
  defect category (8 classes). Enables the abstract's headline ablation
  (text-only vs +metadata vs +signals). 3,888 of the examples carry the signal
  modality; class balance is roughly uniform (~400–480 per class in train).
- **Recurrence / early warning** (`recurrence/`) — ordered prior-defect
  sequence per tail → will-recur-within-30-days label. Suited to the LSTM /
  sequence baseline. Positive rate ≈ 37%.
- **Grounded RAG** — corpus + QA benchmark for retrieval, citation and
  abstention metrics.

**Splits are chronological** (train = earliest dates, test = latest) to prevent
temporal leakage — critical for the recurrence task.

---

## 5. Public source provenance (real data plan)

| Source | Endpoint used | Status |
|---|---|---|
| FAA Service Difficulty Reports | `external.apic4e.faa.gov/sdrs/retrieve/SDR-{year}.csv` (via faa.gov/av-info/download_SDR) | **downloaded (2023–2025)** |
| FAA Airworthiness Directives | Federal Register API + govinfo.gov full text | **downloaded (500 rules)** |
| NASA ASRS | `asrs.arc.nasa.gov/docs/rpsts/*.pdf` report sets | **downloaded (3 sets)** |
| NASA C-MAPSS | PHM S3 mirror (NASA PCoE turbofan ZIP) | **downloaded (FD001–FD004)** |

Each is documented in `data/raw/<source>/SOURCE.md`; machine-readable status in
`data/raw/public_sources_status.json`. The downloader skips anything already
present, and falls back to synthetic stand-ins if a source is unreachable.

**Access notes:** FAA `federalregister.gov` raw-text URLs are Cloudflare-gated
(serve a "Request Access" page) — full AD text is therefore pulled from
`govinfo.gov` instead. ASRS bulk CSV export requires the interactive form, so the
official curated **report-set PDFs** are used (parsing needs a PDF lib in the
project venv; the PDFs are stored as-is).

---

## 6. Limitations

Synthetic layer:
- Synthetic narratives approximate, but do not replace, real techlog language;
  SME review is still required before any operational claim.
- Synthetic AD/MEL/AMM document numbers and text are **illustrative**, not
  authoritative — for research/prototyping only (real ADs are clearly tagged
  `AD-FR-*` / source "…REAL").
- C-MAPSS-*style* signal windows are stylised degradation injections, not
  validated physics (the real NASA C-MAPSS files are provided separately).

Real layer:
- Real SDR→taxonomy mapping is heuristic (JASC/ATA + keywords); the `OTHER`
  bucket and `mapping_method` field flag low-confidence cases. SDR free text is
  noisy, upper-cased and abbreviation-heavy (genuine, not cleaned).
- ASRS report sets are PDFs; text extraction needs a PDF library in the venv.
- FAA AD full text covers the most-recent ~49 rules (govinfo); the rest carry
  the real Federal-Register abstract.
- Real SDR is US-registry GA+air-carrier data, not Emirates-fleet specific.
- Not for operational deployment (consistent with the abstract's scope).
