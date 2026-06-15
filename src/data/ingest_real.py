"""
Ingest the downloaded REAL public data into project-usable form.

Two integrations make the live downloads directly consumable by the prototype:

  1. FAA SDR  -> normalised defect records mapped onto the project's 8-class
     defect taxonomy (via JASC/ATA chapter + discrepancy-text keywords), so the
     real malfunction narratives can augment triage training / RAG context.
  2. FAA AD   -> real Airworthiness Directive documents converted into the
     knowledge-corpus schema and appended to ``corpus.jsonl`` (+ ``docs/``), so
     the RAG retriever cites genuine authoritative AD text, not only synthetic.

NASA C-MAPSS and ASRS are already usable as downloaded (C-MAPSS in canonical
schema; ASRS as de-identified PDF report sets) and are catalogued, not rewritten.

Run standalone:  python -m src.data.ingest_real
"""
import csv
import json
import os
import re
import sys

from . import taxonomy as tax

# Markers that separate the defect description from the corrective action inside
# the single free-text SDR "Discrepancy" field (case-insensitive, first wins).
_CA_SPLIT = re.compile(
    r"(?i)\b(?:corrective\s+action|corr\.?\s*action|c/a|action\s+taken|"
    r"rectification|rectified|disposition)\b\s*[:.\-]?\s*")
# Leading "DISC:" / "DISCREPANCY:" labels to strip off the defect part.
_DISC_LABEL = re.compile(r"(?i)^\s*(?:disc|discrepancy)\s*[:.\-]\s*")


def _split_defect_action(text):
    """Return (defect_text, corrective_action, has_action) from SDR free text."""
    m = _CA_SPLIT.search(text or "")
    if m:
        defect = text[:m.start()].strip(" -.:")
        action = text[m.end():].strip(" -.:")
    else:
        defect, action = (text or "").strip(), ""
    defect = _DISC_LABEL.sub("", defect).strip()
    return defect, action, bool(action)

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

# ATA chapter (2-digit) -> defect category, primary chapters winning.
def _build_ata_map():
    m = {}
    for key, prof in tax.DEFECT_CATEGORIES.items():
        if prof["ata"]:
            m.setdefault(prof["ata"][0], key)           # primary first
    for key, prof in tax.DEFECT_CATEGORIES.items():
        for ata in prof["ata"][1:]:
            m.setdefault(ata, key)                       # then secondaries
    return m

_ATA_MAP = _build_ata_map()

_KEYWORDS = [
    ("STRUCTURAL_DAMAGE", ("crack", "corro", "fatigue", "skin", "spar",
                            "stringer", "fuselage", "fitting", "doubler", "delamin")),
    ("ELECTRICAL_FAULT", ("wir", "electr", "generator", "battery", " bus ",
                          "circuit", "relay", "harness", "connector")),
    ("HYDRAULIC_LEAK", ("hydraulic", "actuator", "reservoir", "hyd ")),
    ("FUEL_SYSTEM", ("fuel", "tank", "boost pump")),
    ("PNEUMATIC_BLEED", ("bleed", "pneumatic", "duct", "pressuriz", "precooler")),
    ("LANDING_GEAR_BRAKE", ("landing gear", "brake", "tire", "tyre", "wheel",
                            "strut", "nose gear", "main gear", "anti-skid")),
    ("POWERPLANT", ("engine", "turbine", "compressor", "nacelle", "thrust rev",
                    "nozzle", "egt", "n1 ", "n2 ", "fan blade")),
    ("SENSOR_INDICATION", ("sensor", "probe", "transducer", "indication",
                           "indicator", "gauge", "warning")),
]


def _classify(jasc, text):
    ata = (jasc or "")[:2]
    if ata in _ATA_MAP:
        return _ATA_MAP[ata], "ata"
    low = (text or "").lower()
    for cat, kws in _KEYWORDS:
        if any(k in low for k in kws):
            return cat, "keyword"
    return "OTHER", "unmapped"


def ingest_sdr(raw_dir="data/raw/faa_sdr/real", out_dir="data/processed"):
    files = sorted(f for f in os.listdir(raw_dir) if f.endswith(".csv")) \
        if os.path.isdir(raw_dir) else []
    if not files:
        print("  ingest_sdr: no real SDR CSVs found - skipped")
        return {"records": 0}

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "real_sdr_normalized.jsonl")
    pairs_path = os.path.join(out_dir, "real_sdr_defect_action_pairs.jsonl")
    by_cat, by_ata, by_year = {}, {}, {}
    n = 0
    n_action = 0
    with open(out_path, "w") as out, open(pairs_path, "w") as pout:
        for fn in files:
            with open(os.path.join(raw_dir, fn), newline="",
                      encoding="utf-8", errors="replace") as f:
                for row in csv.DictReader(f):
                    disc = (row.get("Discrepancy") or "").strip()
                    if not disc:
                        continue
                    jasc = (row.get("JASCCode") or "").strip()
                    cat, how = _classify(jasc, disc)
                    defect_text, action_text, has_action = _split_defect_action(disc)
                    date = (row.get("DifficultyDate") or "").strip()
                    year = date[-4:] if "/" in date else date[:4]
                    rec = {
                        "source": "FAA_SDR",
                        "sdr_date": date,
                        "jasc_code": jasc,
                        "ata_chapter": jasc[:2] if jasc else "",
                        "aircraft_make": (row.get("AircraftMake") or "").strip(),
                        "aircraft_model": (row.get("AircraftModel") or "").strip(),
                        "part_name": (row.get("PartName") or "").strip(),
                        "part_condition": (row.get("PartCondition") or "").strip(),
                        "stage_of_operation": (row.get("StageOfOperationCode") or "").strip(),
                        "discrepancy": disc,
                        "defect_text": defect_text,
                        "corrective_action": action_text,
                        "has_corrective_action": has_action,
                        "mapped_defect_category": cat,
                        "mapping_method": how,
                    }
                    out.write(json.dumps(rec) + "\n")
                    n += 1
                    if has_action:
                        n_action += 1
                        # Clean defect -> action supervised pair for the copilot.
                        pout.write(json.dumps({
                            "defect": defect_text,
                            "action": action_text,
                            "defect_category": cat,
                            "ata_chapter": rec["ata_chapter"],
                            "part_name": rec["part_name"],
                            "part_condition": rec["part_condition"],
                            "source": "FAA_SDR",
                            "sdr_date": date,
                        }) + "\n")
                    by_cat[cat] = by_cat.get(cat, 0) + 1
                    by_ata[rec["ata_chapter"]] = by_ata.get(rec["ata_chapter"], 0) + 1
                    if year:
                        by_year[year] = by_year.get(year, 0) + 1

    summary = {"records": n, "files": files,
               "with_corrective_action": n_action,
               "defect_action_pairs": n_action,
               "by_mapped_category": dict(sorted(by_cat.items(), key=lambda x: -x[1])),
               "by_year": dict(sorted(by_year.items())),
               "top_ata_chapters": dict(sorted(by_ata.items(), key=lambda x: -x[1])[:15])}
    with open(os.path.join(out_dir, "real_sdr_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    mapped = n - by_cat.get("OTHER", 0)
    print(f"  ingest_sdr: {n} real records normalised "
          f"({mapped} mapped to the 8-class taxonomy, {by_cat.get('OTHER',0)} OTHER); "
          f"{n_action} defect->action pairs extracted")
    return summary


def ingest_ad(raw_dir="data/raw/faa_ad/real",
              corpus_path="data/raw/knowledge_corpus/corpus.jsonl",
              docs_dir="data/raw/knowledge_corpus/docs"):
    jl = os.path.join(raw_dir, "faa_ads_federal_register.jsonl")
    if not os.path.exists(jl):
        print("  ingest_ad: no real AD file found - skipped")
        return []

    recs = [json.loads(l) for l in open(jl)]
    ft_dir = os.path.join(raw_dir, "full_text")
    os.makedirs(docs_dir, exist_ok=True)

    docs = []
    for d in recs:
        docnum = d.get("document_number", "")
        title = d.get("title", "Airworthiness Directive")
        abstract = (d.get("abstract") or "").strip()
        cat, _ = _classify("", f"{title} {abstract}")
        body = abstract
        ftp = os.path.join(ft_dir, f"{docnum}.txt")
        if os.path.exists(ftp):
            full = open(ftp, encoding="utf-8", errors="replace").read().strip()
            # Use full text only if it is genuine text (not a blocked HTML page).
            if full and "<!doctype html" not in full[:200].lower() \
                    and "request access" not in full[:400].lower():
                body = full[:6000]      # cap very long rules for the corpus
        doc = {
            "doc_id": f"AD-FR-{docnum}",
            "doc_type": "AD",
            "title": title,
            "ata_chapter": "",
            "defect_category": cat if cat != "OTHER" else "",
            "applicability": "Mandatory (FAA final rule)",
            "source": "FAA Airworthiness Directive (Federal Register, REAL)",
            "effective_date": d.get("effective_on") or d.get("publication_date", ""),
            "citation": d.get("citation", ""),
            "url": d.get("html_url", ""),
            "text": body,
        }
        docs.append(doc)
        with open(os.path.join(docs_dir, f"{doc['doc_id']}.md"), "w") as f:
            f.write(f"# {title}\n\n- **Doc ID:** {doc['doc_id']}\n"
                    f"- **Type:** AD (real)\n- **Source:** {doc['source']}\n"
                    f"- **Citation:** {doc['citation']}\n- **URL:** {doc['url']}\n\n{body}\n")

    # Append real AD docs to the retrievable corpus.
    with open(corpus_path, "a") as f:
        for doc in docs:
            f.write(json.dumps(doc) + "\n")
    print(f"  ingest_ad: appended {len(docs)} REAL FAA AD documents to the RAG corpus")
    return docs


def generate():
    sdr = ingest_sdr()
    ads = ingest_ad()
    return {"real_sdr": sdr, "real_ad_docs": len(ads)}


if __name__ == "__main__":
    generate()
