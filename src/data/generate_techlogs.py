"""
Generate the synthetic aircraft techlog dataset.

Produces ~5,000 internally-consistent defect records spread across a fleet of
aircraft and a ~2.3-year window. Tail histories are coherent so that recurring
defects (same category on the same tail within the recurrence horizon) are
correctly labelled - this is what the LSTM recurrence model and the early
warning experiments (T2) consume.

Outputs:
  data/raw/techlogs/techlogs.jsonl   (one record per line, full schema)
  data/raw/techlogs/techlogs.csv     (flat tabular view for pandas/Excel)

Run standalone:  python -m src.data.generate_techlogs
"""
import csv
import json
import os
import random
from datetime import date, timedelta

from . import taxonomy as tax

FLEET_SIZE = 70
DATE_START = date(2024, 1, 1)
DATE_END = date(2026, 5, 31)
TARGET_RECORDS = 5000
FLIGHT_PHASES = ["Pre-flight", "Taxi", "Take-off", "Climb", "Cruise",
                 "Descent", "Approach", "Landing", "Post-flight", "Walkaround"]


def _build_fleet(rng):
    """Create a fleet of aircraft with stable tail / MSN / engine identities."""
    fleet = []
    type_keys = list(tax.AIRCRAFT_TYPES.keys())
    for i in range(FLEET_SIZE):
        ac_type = rng.choice(type_keys)
        spec = tax.AIRCRAFT_TYPES[ac_type]
        tail = f"{spec['tail_prefix']}{rng.randint(10, 99)}{chr(rng.randint(65, 90))}"
        fleet.append({
            "tail": tail,
            "aircraft_type": ac_type,
            "family": spec["family"],
            "engine": spec["engine"],
            "msn": rng.randint(1000, 9999),
        })
    return fleet


def _make_narrative(rng, profile, component, phase):
    """Build a noisy techlog free-text entry plus a clean expansion."""
    symptom = rng.choice(profile["symptoms"])
    templates = [
        "{comp} {symptom} during {phase}.",
        "{symptom} on {comp} reported {phase}.",
        "Crew report {symptom}. {comp} suspect.",
        "{comp}: {symptom} ({phase}). Please investigate.",
        "Noted {symptom} affecting {comp}.",
    ]
    clean = rng.choice(templates).format(
        comp=component.capitalize(), symptom=symptom, phase=phase.lower())
    # Inject abbreviation noise to mimic real handwritten/terse TLP entries.
    raw = clean
    for full, abbr in tax.ABBREVIATIONS.items():
        if full in raw.lower():
            raw = raw.replace(full, abbr).replace(full.capitalize(), abbr)
    if rng.random() < 0.5:
        raw = raw.upper()
    if rng.random() < 0.3:
        raw = raw.rstrip(".") + " PLS ADV."
    return raw, clean


def _weighted_choice(rng, items, weights):
    return rng.choices(items, weights=weights, k=1)[0]


def generate(out_dir="data/raw/techlogs", seed=tax.RANDOM_SEED):
    rng = random.Random(seed)
    fleet = _build_fleet(rng)
    total_days = (DATE_END - DATE_START).days

    # Roughly even per-tail event budget to hit the target record count.
    per_tail = max(1, TARGET_RECORDS // FLEET_SIZE)

    records = []
    seq = 1
    for ac in fleet:
        history = []  # (date, defect_key) for this tail, for recurrence labelling
        cur = DATE_START + timedelta(days=rng.randint(0, 20))
        for _ in range(per_tail + rng.randint(-3, 5)):
            if cur > DATE_END:
                break

            # Choose defect category: sometimes deliberately repeat a recent one
            # so the dataset contains genuine recurrence signal.
            recent = [(d, k) for (d, k) in history
                      if (cur - d).days <= tax.RECURRENCE_HORIZON_DAYS]
            defect_key = None
            if recent and rng.random() < 0.30:
                # bias toward repeating a recent category (weighted by its recurrence_p)
                cand = rng.choice(recent)[1]
                if rng.random() < tax.DEFECT_CATEGORIES[cand]["recurrence_p"] + 0.4:
                    defect_key = cand
            if defect_key is None:
                defect_key = rng.choice(tax.DEFECT_KEYS)

            profile = tax.DEFECT_CATEGORIES[defect_key]
            ata, component = tax.pick_ata_component(rng, profile)
            phase = rng.choice(FLIGHT_PHASES)
            severity = _weighted_choice(rng, tax.SEVERITY_LEVELS, list(profile["severity_w"]))
            raw, clean = _make_narrative(rng, profile, component, phase)

            deferred = (severity != "Critical") and (rng.random() < profile["deferrable_p"])
            mel_ref = ""
            status = "Closed"
            action = rng.choice(profile["actions"])
            if deferred:
                status = "Deferred"
                mel_ref = f"MEL {ata}-{rng.randint(10, 60):02d}-{rng.randint(1, 9)}"
                action = "Deferred under MEL; rectification scheduled."
            elif rng.random() < 0.04:
                status = "Open"
                action = "Under investigation."

            # Recurrence label: same category on this tail within the horizon prior.
            prior = [(d, k, idx) for idx, (d, k) in enumerate(history)
                     if k == defect_key and 0 < (cur - d).days <= tax.RECURRENCE_HORIZON_DAYS]
            is_recurrence = len(prior) > 0
            prior_id = records[prior[-1][2]]["techlog_id"] if prior else ""
            # NOTE: prior index maps into history order == record order for this tail,
            # so resolve against the matching global record below instead.

            tlp_id = f"TLP-{cur.year}-{seq:06d}"
            rec = {
                "techlog_id": tlp_id,
                "tail": ac["tail"],
                "aircraft_type": ac["aircraft_type"],
                "family": ac["family"],
                "engine": ac["engine"],
                "msn": ac["msn"],
                "date": cur.isoformat(),
                "station": rng.choice(tax.STATIONS),
                "flight_phase": phase,
                "ata_chapter": ata,
                "ata_title": tax.ata_title(ata),
                "defect_category": defect_key,
                "defect_label": profile["label"],
                "component": component,
                "severity": severity,
                "raw_narrative": raw,
                "clean_narrative": clean,
                "reported_by": rng.choice(tax.REPORTERS),
                "action_taken": action,
                "resolution_status": status,
                "deferred": deferred,
                "mel_ref": mel_ref,
                "is_recurrence": is_recurrence,
                "prior_techlog_id": "",  # filled below
                "recurrence_horizon_days": tax.RECURRENCE_HORIZON_DAYS,
                "has_signal": profile["signal_mode"] != "none",
            }
            # Resolve prior_techlog_id against the actual earlier record for this tail.
            if is_recurrence:
                for prev in reversed(records):
                    if (prev["tail"] == ac["tail"]
                            and prev["defect_category"] == defect_key
                            and 0 < (cur - date.fromisoformat(prev["date"])).days
                            <= tax.RECURRENCE_HORIZON_DAYS):
                        rec["prior_techlog_id"] = prev["techlog_id"]
                        break

            records.append(rec)
            history.append((cur, defect_key))
            seq += 1
            cur = cur + timedelta(days=rng.randint(3, 25))

    # Sort chronologically across the whole fleet for realism.
    records.sort(key=lambda r: (r["date"], r["techlog_id"]))

    os.makedirs(out_dir, exist_ok=True)
    jsonl_path = os.path.join(out_dir, "techlogs.jsonl")
    csv_path = os.path.join(out_dir, "techlogs.csv")
    with open(jsonl_path, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

    # Quick provenance stats for the console / logs.
    n_rec = sum(1 for r in records if r["is_recurrence"])
    n_def = sum(1 for r in records if r["deferred"])
    print(f"  techlogs: {len(records)} records, {len(fleet)} tails")
    print(f"    recurrences: {n_rec} ({100*n_rec/len(records):.1f}%), "
          f"deferred: {n_def} ({100*n_def/len(records):.1f}%)")
    return records


if __name__ == "__main__":
    generate()
