"""
Parse NASA ASRS curated report-set PDFs into structured JSONL records.

Each PDF contains ~50 de-identified aviation safety/maintenance reports.
The three sets in this project are:
  * mechanic.pdf     — maintenance technician reports
  * fuel.pdf         — fuel management issues
  * cabin_fumes.pdf  — cabin smoke / fumes / odour incidents

Output:
  data/processed/asrs_reports.jsonl          — one record per report (all 3 PDFs)
  data/processed/asrs_summary.json           — run statistics
  data/raw/knowledge_corpus/corpus.jsonl     — records appended as RAG documents
  data/raw/knowledge_corpus/docs/ASRS-*.md  — individual markdown doc files

Run standalone:  python -m src.data.parse_asrs
"""
import json
import os
import re

try:
    from pypdf import PdfReader
    _PDF_OK = True
except ImportError:
    _PDF_OK = False

from . import taxonomy as tax

# ---------------------------------------------------------------------------
# PDF sets: (filename_stem, report_topic, default_defect_hint)
# ---------------------------------------------------------------------------
_PDF_SETS = [
    ("mechanic",     "Aircraft Maintenance",          None),
    ("fuel",         "Fuel Management",               "FUEL_SYSTEM"),
    ("cabin_fumes",  "Cabin Smoke / Fumes / Odour",   "PNEUMATIC_BLEED"),
]

# ---------------------------------------------------------------------------
# Defect classification (same logic as ingest_real._classify but tuned for
# ASRS narrative language, which is verbose prose rather than SDR shorthand)
# ---------------------------------------------------------------------------
_KEYWORDS = [
    ("STRUCTURAL_DAMAGE",    ("crack", "corros", "fractur", "fatigue", "dent",
                              "skin", "spar", "stringer", "fuselage", "delamina",
                              "doubler", "fitting", "structural")),
    ("ELECTRICAL_FAULT",     ("electr", "wiring", "harness", "generator", "battery",
                              "circuit breaker", "relay", "connector", "voltage",
                              "alternator", "inverter", "bus ")),
    ("HYDRAULIC_LEAK",       ("hydraulic", "actuator", "reservoir", "hyd fluid",
                              "fluid leak", "hose", "servo")),
    ("FUEL_SYSTEM",          ("fuel", "tank", "boost pump", "fqu", "fueling",
                              "defuel", "fuel pump", "fuel leak", "fuel line",
                              "fuel spill", "fuel nozzle")),
    ("PNEUMATIC_BLEED",      ("bleed", "pneumatic", "duct", "pressur", "precooler",
                              "pack", "smoke", "fumes", "odour", "odor", "fume")),
    ("LANDING_GEAR_BRAKE",   ("landing gear", "brake", "tire", "tyre", "wheel",
                              "strut", "nose gear", "main gear", "anti-skid",
                              "shimmy", "gear door")),
    ("POWERPLANT",           ("engine", "turbine", "compressor", "nacelle",
                              "thrust reverser", "reverser", "nozzle", "egt",
                              "fan blade", "igniter", "combustor", "n1", "n2",
                              "oil consumption", "chip detect")),
    ("SENSOR_INDICATION",    ("sensor", "probe", "transducer", "indication",
                              "gauge", "warning light", "caution", "fault message",
                              "cmc", "ecam", "eicas", "bite", "adc")),
]

_ATA_TOKENS = {
    "21": "PNEUMATIC_BLEED",
    "24": "ELECTRICAL_FAULT",
    "27": "STRUCTURAL_DAMAGE",
    "28": "FUEL_SYSTEM",
    "29": "HYDRAULIC_LEAK",
    "32": "LANDING_GEAR_BRAKE",
    "34": "SENSOR_INDICATION",
    "36": "PNEUMATIC_BLEED",
    "49": "ELECTRICAL_FAULT",
    "52": "STRUCTURAL_DAMAGE",
    "53": "STRUCTURAL_DAMAGE",
    "57": "STRUCTURAL_DAMAGE",
    "72": "POWERPLANT",
    "73": "FUEL_SYSTEM",
    "78": "POWERPLANT",
}


def _classify(text, component="", anomaly="", hint=None):
    """Return (defect_category, confidence) from narrative + metadata fields."""
    combined = f"{text} {component} {anomaly}".lower()
    for cat, kws in _KEYWORDS:
        if any(k in combined for k in kws):
            return cat, "keyword"
    if hint and hint in tax.DEFECT_CATEGORIES:
        return hint, "topic_hint"
    return "OTHER", "unmapped"


# ---------------------------------------------------------------------------
# PDF text extraction & report segmentation
# ---------------------------------------------------------------------------
_ACN_RE = re.compile(
    r"ACN:\s*(\d+)\s*\((\d+)\s+of\s+(\d+)\)", re.I
)
_SECTION_RE = re.compile(
    r"^(Narrative|Synopsis|Callback|Time\s*/\s*Day|Place|Aircraft|Component|"
    r"Person|Events|Assessments)\s*:?\s*$", re.I | re.M
)
# Field extractors for the structured metadata block
_FIELD_RE = {
    "aircraft":  re.compile(r"Make Model Name\s*:\s*(.+)", re.I),
    "operator":  re.compile(r"Aircraft Operator\s*:\s*(.+)", re.I),
    "phase":     re.compile(r"Flight Phase\s*:\s*(.+)", re.I),
    "component": re.compile(r"Aircraft Component\s*:\s*(.+)", re.I),
    "anomaly":   re.compile(r"Anomaly\.[^:]+:\s*(.+)", re.I),
    "reporter":  re.compile(r"Function\.Maintenance\s*:\s*(.+)", re.I),
    "date":      re.compile(r"Date\s*:\s*(\d{6})", re.I),
}


def _extract_text(pdf_path):
    """Return concatenated text from all PDF pages."""
    reader = PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        t = page.extract_text() or ""
        pages.append(t)
    return "\n".join(pages)


def _split_reports(full_text):
    """Split full PDF text into per-report blocks keyed by ACN number."""
    positions = [(m.start(), m.group(1), m.group(2))
                 for m in _ACN_RE.finditer(full_text)]
    if not positions:
        return []
    reports = []
    for i, (start, acn, idx) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(full_text)
        reports.append((acn, idx, full_text[start:end]))
    # De-duplicate: synopses section and narratives section both start with ACN;
    # keep the longer block (narratives section contains the synopsis too).
    seen = {}
    for acn, idx, block in reports:
        if acn not in seen or len(block) > len(seen[acn][1]):
            seen[acn] = (idx, block)
    return [(acn, idx, block) for acn, (idx, block) in seen.items()]


def _parse_report(acn, idx, block, pdf_stem, topic, hint):
    """Parse one report block into a structured dict."""
    # --- metadata fields ---
    def _get(pattern):
        m = pattern.search(block)
        return m.group(1).strip() if m else ""

    aircraft  = _get(_FIELD_RE["aircraft"])
    operator  = _get(_FIELD_RE["operator"])
    phase     = _get(_FIELD_RE["phase"])
    component = _get(_FIELD_RE["component"])
    reporter  = _get(_FIELD_RE["reporter"])
    raw_date  = _get(_FIELD_RE["date"])          # YYYYMM
    date_str  = f"{raw_date[:4]}-{raw_date[4:6]}-01" if len(raw_date) == 6 else ""

    # Collect all anomaly lines (there can be several)
    anomalies = [m.group(1).strip()
                 for m in _FIELD_RE["anomaly"].finditer(block)]
    anomaly_str = "; ".join(anomalies[:4])

    # --- narrative text ---
    # The free text follows "Narrative: 1" (and sometimes "Narrative: 2")
    narr_blocks = re.split(r"Narrative\s*:\s*\d+", block, flags=re.I)
    # narr_blocks[0] is the metadata; rest are the actual narratives
    narratives = [nb.strip() for nb in narr_blocks[1:] if nb.strip()]
    # Trim trailing Synopsis / Callback lines that bleed in from the next report
    cleaned = []
    for nb in narratives:
        # Stop at what looks like the start of the next ACN or a heading
        cut = re.search(r"\n(ACN:|Synopsis\s*$|Callback\s*$)", nb, re.M | re.I)
        cleaned.append(nb[:cut.start()].strip() if cut else nb)
    narrative = "\n\n".join(cleaned)

    # --- defect classification ---
    cat, confidence = _classify(narrative, component, anomaly_str, hint)

    return {
        "doc_id":         f"ASRS-{acn}",
        "acn":            acn,
        "report_index":   int(idx),
        "pdf_set":        pdf_stem,
        "topic":          topic,
        "date":           date_str,
        "aircraft":       aircraft,
        "operator":       operator,
        "flight_phase":   phase,
        "component":      component,
        "anomalies":      anomalies,
        "reporter_role":  reporter,
        "narrative":      narrative,
        "defect_category":   cat,
        "classification":    confidence,
        "source":         "NASA ASRS (de-identified)",
    }


# ---------------------------------------------------------------------------
# Corpus / RAG document writer
# ---------------------------------------------------------------------------
def _to_corpus_doc(rec):
    """Convert a parsed ASRS report into the project's knowledge-corpus schema."""
    title = (f"ASRS {rec['acn']}: {rec['topic']} - "
             f"{rec['component'] or rec['aircraft'] or 'Aviation Safety Report'}")
    text = rec["narrative"] if rec["narrative"] else f"Synopsis: {rec['topic']}"
    return {
        "doc_id":          rec["doc_id"],
        "doc_type":        "CASE",
        "title":           title,
        "ata_chapter":     "",
        "defect_category": rec["defect_category"] if rec["defect_category"] != "OTHER" else "",
        "applicability":   rec["aircraft"] or "Air Carrier",
        "source":          rec["source"],
        "effective_date":  rec["date"],
        "text": (
            f"**Report:** {rec['doc_id']}  "
            f"**Aircraft:** {rec['aircraft']}  "
            f"**Component:** {rec['component']}  "
            f"**Flight Phase:** {rec['flight_phase']}\n\n"
            f"**Anomalies:** {'; '.join(rec['anomalies'])}\n\n"
            + text
        )[:6000],
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def parse(
    asrs_dir="data/raw/nasa_asrs/report_sets",
    out_dir="data/processed",
    corpus_path="data/raw/knowledge_corpus/corpus.jsonl",
    docs_dir="data/raw/knowledge_corpus/docs",
):
    if not _PDF_OK:
        print("  parse_asrs: pypdf not installed — skipped")
        return {"records": 0, "corpus_docs": 0}

    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(docs_dir, exist_ok=True)

    all_records = []
    by_set = {}
    by_cat = {}

    for stem, topic, hint in _PDF_SETS:
        pdf_path = os.path.join(asrs_dir, f"{stem}.pdf")
        if not os.path.exists(pdf_path):
            print(f"  parse_asrs: {stem}.pdf not found — skipped")
            continue

        full_text = _extract_text(pdf_path)
        raw_reports = _split_reports(full_text)
        set_records = []
        for acn, idx, block in raw_reports:
            rec = _parse_report(acn, idx, block, stem, topic, hint)
            if not rec["narrative"]:
                continue
            set_records.append(rec)
            by_cat[rec["defect_category"]] = by_cat.get(rec["defect_category"], 0) + 1

        all_records.extend(set_records)
        by_set[stem] = len(set_records)
        print(f"  parse_asrs: {stem}.pdf -> {len(set_records)} reports parsed")

    # Write processed JSONL
    out_path = os.path.join(out_dir, "asrs_reports.jsonl")
    with open(out_path, "w", encoding="utf-8") as f:
        for rec in all_records:
            f.write(json.dumps(rec) + "\n")

    # Append to RAG corpus
    corpus_docs = [_to_corpus_doc(r) for r in all_records]
    with open(corpus_path, "a", encoding="utf-8") as f:
        for doc in corpus_docs:
            f.write(json.dumps(doc) + "\n")

    # Write individual markdown files (UTF-8 so em-dashes / special chars survive)
    for doc in corpus_docs:
        md_path = os.path.join(docs_dir, f"{doc['doc_id']}.md")
        with open(md_path, "w", encoding="utf-8", errors="replace") as f:
            f.write(f"# {doc['title']}\n\n"
                    f"- **Doc ID:** {doc['doc_id']}\n"
                    f"- **Type:** CASE (NASA ASRS de-identified)\n"
                    f"- **Source:** {doc['source']}\n"
                    f"- **Defect Category:** {doc['defect_category']}\n\n"
                    f"{doc['text']}\n")

    summary = {
        "total_records": len(all_records),
        "corpus_docs_added": len(corpus_docs),
        "by_pdf_set": by_set,
        "by_defect_category": dict(sorted(by_cat.items(), key=lambda x: -x[1])),
    }
    with open(os.path.join(out_dir, "asrs_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(f"  parse_asrs: {len(all_records)} total ASRS records -> "
          f"{out_path}")
    print(f"             {len(corpus_docs)} docs appended to RAG corpus")
    return summary


def generate():
    return parse()


if __name__ == "__main__":
    generate()
