"""
Build processed train / validation / test splits for the modelling tasks.

Splits are CHRONOLOGICAL (train = earliest, test = latest) to avoid temporal
leakage - essential for the recurrence / early-warning tasks where future
information must not leak into training.

Tasks produced:
  triage/      multimodal defect classification
               features: text (narrative) + metadata + C-MAPSS signal summary
               label: defect_category (8 classes)
  recurrence/  per-event sequence -> will-recur-within-horizon label
               features: ordered prior-defect sequence on the same tail
               label: is_recurrence

Each split is written as JSONL; a manifest records sizes, class balance and the
date boundaries used.

Run standalone:  python -m src.data.build_splits
"""
import csv
import json
import os
from datetime import date

from . import taxonomy as tax

TRAIN_FRAC, VAL_FRAC = 0.8, 0.1   # test gets the remaining 0.1 (latest in time)


def _load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f]


def _load_signal_summary(path):
    if not os.path.exists(path):
        return {}
    out = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            out[row["techlog_id"]] = row
    return out


def _chrono_split(records):
    records = sorted(records, key=lambda r: (r["date"], r["techlog_id"]))
    n = len(records)
    a = int(n * TRAIN_FRAC)
    b = int(n * (TRAIN_FRAC + VAL_FRAC))
    return records[:a], records[a:b], records[b:]


def _triage_example(t, signal):
    """Multimodal example: text + metadata + (optional) signal features."""
    ex = {
        "techlog_id": t["techlog_id"],
        "text": t["raw_narrative"],
        "clean_text": t["clean_narrative"],
        "metadata": {
            "aircraft_type": t["aircraft_type"],
            "family": t["family"],
            "ata_chapter": t["ata_chapter"],
            "flight_phase": t["flight_phase"],
            "station": t["station"],
            "severity": t["severity"],
            "deferred": t["deferred"],
        },
        "has_signal": t["has_signal"],
        "label": t["defect_category"],
    }
    if signal:
        ex["signal_features"] = {
            k: float(v) for k, v in signal.items()
            if k.startswith("sensor_")
        }
    else:
        ex["signal_features"] = {}
    return ex


def _recurrence_examples(records):
    """Per-event sequence of the tail's prior defects -> recurrence label."""
    records = sorted(records, key=lambda r: (r["tail"], r["date"], r["techlog_id"]))
    by_tail = {}
    for r in records:
        by_tail.setdefault(r["tail"], []).append(r)

    examples = []
    for tail, seq in by_tail.items():
        for i, r in enumerate(seq):
            prior = seq[max(0, i - 5):i]   # up to 5 preceding events
            if not prior:
                continue
            d0 = date.fromisoformat(r["date"])
            steps = []
            for p in prior:
                steps.append({
                    "defect_category": p["defect_category"],
                    "ata_chapter": p["ata_chapter"],
                    "severity": p["severity"],
                    "days_before": (d0 - date.fromisoformat(p["date"])).days,
                })
            examples.append({
                "techlog_id": r["techlog_id"],
                "tail": tail,
                "date": r["date"],
                "current_defect_category": r["defect_category"],
                "sequence": steps,
                "label": 1 if r["is_recurrence"] else 0,
            })
    return examples


def _write(split_dir, name, rows):
    os.makedirs(split_dir, exist_ok=True)
    with open(os.path.join(split_dir, f"{name}.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def _balance(rows, key):
    out = {}
    for r in rows:
        out[r[key]] = out.get(r[key], 0) + 1
    return out


def generate(raw_techlogs="data/raw/techlogs/techlogs.jsonl",
             signal_summary="data/raw/cmapss_signals/signal_summary.csv",
             out_dir="data/processed"):
    techlogs = _load_jsonl(raw_techlogs)
    signals = _load_signal_summary(signal_summary)

    # ---- Triage (multimodal classification) ----
    triage = [_triage_example(t, signals.get(t["techlog_id"])) for t in techlogs]
    # attach date for chronological split, then strip
    for ex, t in zip(triage, techlogs):
        ex["_date"] = t["date"]
    triage.sort(key=lambda e: (e["_date"], e["techlog_id"]))
    n = len(triage)
    a, b = int(n * TRAIN_FRAC), int(n * (TRAIN_FRAC + VAL_FRAC))
    tri_train, tri_val, tri_test = triage[:a], triage[a:b], triage[b:]
    for grp in (tri_train, tri_val, tri_test):
        for e in grp:
            e.pop("_date", None)
    for nm, grp in (("train", tri_train), ("val", tri_val), ("test", tri_test)):
        _write(os.path.join(out_dir, "triage"), nm, grp)

    # ---- Recurrence (sequence classification) ----
    tr_records, va_records, te_records = _chrono_split(techlogs)
    rec_train = _recurrence_examples(tr_records)
    rec_val = _recurrence_examples(va_records)
    rec_test = _recurrence_examples(te_records)
    for nm, grp in (("train", rec_train), ("val", rec_val), ("test", rec_test)):
        _write(os.path.join(out_dir, "recurrence"), nm, grp)

    manifest = {
        "label_space": {
            "triage_classes": tax.DEFECT_KEYS,
            "recurrence_classes": [0, 1],
        },
        "split_strategy": "chronological (no temporal leakage)",
        "fractions": {"train": TRAIN_FRAC, "val": VAL_FRAC,
                      "test": round(1 - TRAIN_FRAC - VAL_FRAC, 3)},
        "triage": {
            "train": len(tri_train), "val": len(tri_val), "test": len(tri_test),
            "train_class_balance": _balance(tri_train, "label"),
            "with_signal_modality": sum(1 for e in triage if e.get("has_signal")),
        },
        "recurrence": {
            "train": len(rec_train), "val": len(rec_val), "test": len(rec_test),
            "train_positive": sum(e["label"] for e in rec_train),
            "test_positive": sum(e["label"] for e in rec_test),
        },
    }
    with open(os.path.join(out_dir, "splits_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"  splits: triage train/val/test = "
          f"{len(tri_train)}/{len(tri_val)}/{len(tri_test)}; "
          f"recurrence = {len(rec_train)}/{len(rec_val)}/{len(rec_test)}")
    return manifest


if __name__ == "__main__":
    generate()
