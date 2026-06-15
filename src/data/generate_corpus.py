"""
Generate the RAG knowledge corpus.

This is the non-parametric memory the RAG / reasoning agents retrieve and cite.
It mirrors the authoritative artefact types the dissertation targets:

  * AMM  - Aircraft Maintenance Manual task snippets (per ATA chapter/component)
  * MEL  - Minimum Equipment List / CDL deferral policy entries
  * AD   - FAA Airworthiness Directives (corrective actions for unsafe conditions)
  * EO   - Engineering Orders / Service Bulletins
  * ADV  - Operational advisories / troubleshooting bulletins
  * CASE - Prior resolved techlog cases (derived from the techlog dataset)

Each document carries stable metadata (doc_id, type, ata_chapter, title,
source, applicability) so QA pairs can reference exact citations and the
retriever can be evaluated with Recall@k / nDCG.

Outputs:
  data/raw/knowledge_corpus/corpus.jsonl          (all documents, one per line)
  data/raw/knowledge_corpus/index.csv             (lightweight doc index)
  data/raw/knowledge_corpus/docs/<doc_id>.md      (human-readable per-doc files)

Run standalone:  python -m src.data.generate_corpus
"""
import csv
import json
import os
import random

from . import taxonomy as tax
from .generate_techlogs import generate as gen_techlogs


def _amm_documents(rng):
    docs = []
    n = 1
    for key, prof in tax.DEFECT_CATEGORIES.items():
        for ata in prof["ata"]:
            for comp in tax.components_for(prof, ata)[:3]:
                doc_id = f"AMM-{ata}-{n:03d}"
                title = f"AMM {ata}-{rng.randint(10,90)}-{rng.randint(0,9)}{rng.randint(0,9)} " \
                        f"Removal/Installation - {comp.title()}"
                steps = [
                    f"Ensure the {tax.ata_title(ata)} system is de-energised and safety tags fitted.",
                    f"Gain access to the {comp} per the applicable access panel task.",
                    f"Inspect the {comp} for signs of {rng.choice(prof['symptoms'])}.",
                    f"If defect confirmed, {rng.choice(prof['actions'])}.",
                    "Carry out an operational test and verify no fault messages remain.",
                    "Close access, remove safety tags and make the techlog entry.",
                ]
                text = (f"Applicable to ATA {ata} ({tax.ata_title(ata)}). "
                        f"Component: {comp}.\n\nProcedure:\n" +
                        "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps)))
                docs.append({
                    "doc_id": doc_id, "doc_type": "AMM", "title": title,
                    "ata_chapter": ata, "defect_category": key,
                    "applicability": "All fitted types",
                    "source": "Aircraft Maintenance Manual (synthetic)",
                    "text": text,
                })
                n += 1
    return docs


def _mel_documents(rng):
    docs = []
    n = 1
    for key, prof in tax.DEFECT_CATEGORIES.items():
        for ata in prof["ata"][:2]:
            cat = rng.choice(["A", "B", "C", "D"])
            interval = {"A": "per remarks", "B": "3 days", "C": "10 days",
                        "D": "120 days"}[cat]
            doc_id = f"MEL-{ata}-{n:03d}"
            ata_comps = tax.components_for(prof, ata)
            comp = rng.choice(ata_comps)
            title = f"MEL {ata}-{rng.randint(10,60):02d}-{rng.randint(1,9)} {comp.title()}"
            text = (f"Item: {comp} ({tax.ata_title(ata)}).\n"
                    f"Repair Category: {cat} (rectification interval {interval}).\n"
                    f"Number installed / required for dispatch may be reduced subject to "
                    f"the following provisos:\n"
                    f"(O) Operational and (M) Maintenance procedures must be established.\n"
                    f"May be inoperative provided associated {rng.choice(ata_comps)} "
                    f"is verified serviceable and crew is advised. "
                    f"Defects classified Critical may NOT be deferred under this item.")
            docs.append({
                "doc_id": doc_id, "doc_type": "MEL", "title": title,
                "ata_chapter": ata, "defect_category": key,
                "applicability": f"Repair Category {cat}",
                "source": "Minimum Equipment List / CDL (synthetic)",
                "text": text,
            })
            n += 1
    return docs


def _ad_documents(rng):
    docs = []
    keys = [k for k, p in tax.DEFECT_CATEGORIES.items()
            if k in ("STRUCTURAL_DAMAGE", "POWERPLANT", "FUEL_SYSTEM",
                     "ELECTRICAL_FAULT")]
    for i in range(40):
        key = rng.choice(keys)
        prof = tax.DEFECT_CATEGORIES[key]
        ata, comp = tax.pick_ata_component(rng, prof)
        year = rng.choice([2022, 2023, 2024, 2025])
        ad_no = f"{year}-{rng.randint(1,26):02d}-{rng.randint(1,20):02d}"
        doc_id = f"AD-{ad_no}"
        title = f"Airworthiness Directive {ad_no} - {comp.title()} ({tax.ata_title(ata)})"
        text = (f"Unsafe condition: reports of {rng.choice(prof['symptoms'])} on the "
                f"{comp} which, if not corrected, could result in "
                f"{'structural failure' if key=='STRUCTURAL_DAMAGE' else 'loss of function'}.\n"
                f"Applicability: {rng.choice(list(tax.AIRCRAFT_TYPES.keys()))} aircraft.\n"
                f"Required action: within {rng.choice([100,250,500,750])} flight hours, "
                f"{rng.choice(prof['actions'])} and perform a repetitive inspection at "
                f"intervals not to exceed {rng.choice([500,1000,1500])} flight hours.\n"
                f"Compliance is mandatory.")
        docs.append({
            "doc_id": doc_id, "doc_type": "AD", "title": title,
            "ata_chapter": ata, "defect_category": key,
            "applicability": "Mandatory",
            "source": "FAA Airworthiness Directive (synthetic, real format)",
            "text": text,
        })
    return docs


def _eo_documents(rng):
    docs = []
    for i in range(35):
        key = rng.choice(tax.DEFECT_KEYS)
        prof = tax.DEFECT_CATEGORIES[key]
        ata, comp = tax.pick_ata_component(rng, prof)
        doc_id = f"EO-{2024}-{i+1:03d}"
        title = f"Engineering Order {doc_id} - Modification of {comp.title()}"
        text = (f"Reason: recurring {rng.choice(prof['symptoms'])} on {comp}.\n"
                f"Instruction: {rng.choice(prof['actions'])}; update build standard "
                f"and record on the aircraft technical records.\n"
                f"Effectivity: ATA {ata} ({tax.ata_title(ata)}). "
                f"Embodiment at next available {rng.choice(['A-check','C-check','line opportunity'])}.")
        docs.append({
            "doc_id": doc_id, "doc_type": "EO", "title": title,
            "ata_chapter": ata, "defect_category": key,
            "applicability": "Fleet campaign",
            "source": "Engineering Order / Service Bulletin (synthetic)",
            "text": text,
        })
    return docs


def _advisory_documents(rng):
    docs = []
    for i in range(30):
        key = rng.choice(tax.DEFECT_KEYS)
        prof = tax.DEFECT_CATEGORIES[key]
        ata = rng.choice(prof["ata"])
        ata_comps = tax.components_for(prof, ata)
        doc_id = f"ADV-{i+1:03d}"
        title = f"Troubleshooting Advisory {doc_id} - {prof['label']}"
        symptom = rng.choice(prof["symptoms"])
        text = (f"Symptom: {symptom} (ATA {ata}).\n"
                f"Likely causes: {', '.join(rng.sample(ata_comps, k=min(3,len(ata_comps))))}.\n"
                f"Recommended sequence:\n"
                f"1. Confirm the indication with a BITE / CMC interrogation.\n"
                f"2. {rng.choice(prof['actions']).capitalize()}.\n"
                f"3. If symptom persists, escalate to base maintenance / engineering.\n"
                f"Note: do not clear the defect without an operational test.")
        docs.append({
            "doc_id": doc_id, "doc_type": "ADV", "title": title,
            "ata_chapter": ata, "defect_category": key,
            "applicability": "Guidance only",
            "source": "Operational Advisory (synthetic)",
            "text": text,
        })
    return docs


def _case_documents(rng, techlogs):
    """Turn a sample of resolved techlogs into citable 'prior case' documents."""
    docs = []
    resolved = [t for t in techlogs if t["resolution_status"] == "Closed"]
    sample = rng.sample(resolved, k=min(400, len(resolved)))
    for t in sample:
        doc_id = f"CASE-{t['techlog_id']}"
        title = f"Resolved Case {t['techlog_id']} - {t['defect_label']} on {t['aircraft_type']}"
        text = (f"Aircraft: {t['aircraft_type']} (tail {t['tail']}), station {t['station']}.\n"
                f"Reported {t['date']} during {t['flight_phase']}.\n"
                f"Defect: {t['clean_narrative']}\n"
                f"ATA {t['ata_chapter']} ({t['ata_title']}), severity {t['severity']}.\n"
                f"Resolution: {t['action_taken']}\n"
                f"Outcome: closed serviceable.")
        docs.append({
            "doc_id": doc_id, "doc_type": "CASE", "title": title,
            "ata_chapter": t["ata_chapter"], "defect_category": t["defect_category"],
            "applicability": t["aircraft_type"],
            "source": "Prior resolved techlog case (synthetic)",
            "text": text,
        })
    return docs


def generate(out_dir="data/raw/knowledge_corpus", techlogs=None, seed=tax.RANDOM_SEED):
    rng = random.Random(seed + 13)
    if techlogs is None:
        techlogs = gen_techlogs()

    docs = []
    docs += _amm_documents(rng)
    docs += _mel_documents(rng)
    docs += _ad_documents(rng)
    docs += _eo_documents(rng)
    docs += _advisory_documents(rng)
    docs += _case_documents(rng, techlogs)

    os.makedirs(out_dir, exist_ok=True)
    docs_dir = os.path.join(out_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    with open(os.path.join(out_dir, "corpus.jsonl"), "w") as f:
        for d in docs:
            f.write(json.dumps(d) + "\n")

    with open(os.path.join(out_dir, "index.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "doc_id", "doc_type", "ata_chapter", "defect_category",
            "applicability", "source", "title"])
        writer.writeheader()
        for d in docs:
            writer.writerow({k: d[k] for k in writer.fieldnames})

    # Human-readable per-document markdown (handy for manual inspection / demos).
    for d in docs:
        with open(os.path.join(docs_dir, f"{d['doc_id']}.md"), "w") as f:
            f.write(f"# {d['title']}\n\n")
            f.write(f"- **Doc ID:** {d['doc_id']}\n- **Type:** {d['doc_type']}\n")
            f.write(f"- **ATA:** {d['ata_chapter']} ({tax.ata_title(d['ata_chapter'])})\n")
            f.write(f"- **Source:** {d['source']}\n- **Applicability:** {d['applicability']}\n\n")
            f.write(d["text"] + "\n")

    by_type = {}
    for d in docs:
        by_type[d["doc_type"]] = by_type.get(d["doc_type"], 0) + 1
    print(f"  knowledge_corpus: {len(docs)} documents "
          f"({', '.join(f'{k}:{v}' for k, v in sorted(by_type.items()))})")
    return docs


if __name__ == "__main__":
    generate()
