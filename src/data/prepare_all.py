"""
One-shot data-preparation orchestrator.

Runs the full groundwork pipeline in dependency order, threading the SAME
in-memory techlog records through every downstream generator so all datasets
stay perfectly consistent (a techlog, its SDR filing, its signal window, the
prior-case document that resolves it, and its train/val/test placement all
refer to the same event).

Usage:
    python -m src.data.prepare_all
"""
import json
import os
import time

from . import taxonomy as tax
from . import download_public, generate_corpus, generate_qa, ingest_real
from . import generate_sdr, generate_signals, generate_techlogs, build_splits


def main():
    t0 = time.time()
    print("=" * 64)
    print("Aircraft Techlog Intelligence - dataset groundwork")
    print(f"seed={tax.RANDOM_SEED}  recurrence_horizon={tax.RECURRENCE_HORIZON_DAYS}d")
    print("=" * 64)

    print("[1/8] download REAL public datasets (C-MAPSS, FAA SDR, ASRS, FAA AD)")
    sources = download_public.generate()

    print("[2/8] synthetic techlogs")
    techlogs = generate_techlogs.generate()

    print("[3/8] FAA SDR-style records (synthetic, schema-matched)")
    generate_sdr.generate(techlogs=techlogs)

    print("[4/8] RAG knowledge corpus (synthetic)")
    docs = generate_corpus.generate(techlogs=techlogs)

    print("[5/8] ingest REAL downloads (FAA SDR -> normalised, FAA AD -> corpus, ASRS -> corpus)")
    real = ingest_real.generate()

    print("[6/8] C-MAPSS-style operational signals (synthetic, real C-MAPSS in data/raw)")
    generate_signals.generate(techlogs=techlogs)

    print("[7/8] QA benchmark (can-answer / must-cite / must-abstain)")
    qa = generate_qa.generate(docs=docs)

    print("[8/8] processed train/val/test splits")
    manifest = build_splits.generate()

    summary = {
        "seed": tax.RANDOM_SEED,
        "recurrence_horizon_days": tax.RECURRENCE_HORIZON_DAYS,
        "counts": {
            "techlogs": len(techlogs),
            "knowledge_documents_synthetic": len(docs),
            "knowledge_documents_real_ad": real["real_ad_docs"],
            "real_sdr_normalised": real["real_sdr"].get("records", 0),
            "real_sdr_defect_action_pairs": real["real_sdr"].get("defect_action_pairs", 0),
            "asrs_reports_parsed": real.get("asrs", {}).get("total_records", 0),
            "qa_items": len(qa),
        },
        "splits": manifest,
        "public_sources": {k: v["fetch"] for k, v in sources.items()},
        "generated_unix": int(time.time()),
    }
    os.makedirs("data", exist_ok=True)
    with open("data/dataset_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("-" * 64)
    print(f"DONE in {time.time()-t0:.1f}s. Summary -> data/dataset_summary.json")
    print("-" * 64)
    return summary


if __name__ == "__main__":
    main()
