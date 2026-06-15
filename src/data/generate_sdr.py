"""
Generate FAA Service Difficulty Report (SDR) style structured defect records.

The real FAA SDR database (public, downloadable by year) anchors failure
taxonomies for benchmarking. Here we emit records using the canonical SDR field
structure so downstream code can treat synthetic and real SDR data identically.
A portion of the records are "filed" from the synthetic techlogs (the more
severe / structural ones, as happens operationally); the rest are independent
fleet-wide reports to broaden the failure taxonomy.

Output:
  data/raw/faa_sdr/sdr_records.csv
  data/raw/faa_sdr/sdr_records.jsonl

Run standalone:  python -m src.data.generate_sdr
"""
import csv
import json
import os
import random

from . import taxonomy as tax
from .generate_techlogs import generate as gen_techlogs

# Canonical-ish SDR column names (subset that public SDR exports expose).
SDR_FIELDS = [
    "sdr_control_number", "difficulty_date", "submitter_type",
    "operator_designator", "aircraft_make", "aircraft_model",
    "engine_make_model", "ata_code", "part_name", "part_condition",
    "nature_of_condition", "stage_of_operation", "part_location",
    "discrepancy_narrative", "corrective_action", "how_discovered",
]

PART_CONDITIONS = ["Cracked", "Failed", "Leaking", "Worn", "Corroded",
                   "Malfunctioned", "Loose", "Burned", "Intermittent"]
NATURE_OF_CONDITION = ["Warning Indication", "Loss of System", "Fluid Loss",
                       "Structural", "Smoke/Fumes", "Degraded Performance",
                       "False Indication", "Component Separation"]
STAGE = ["Ground", "Taxi", "Takeoff", "Climb", "Cruise", "Descent",
         "Approach", "Landing"]
HOW_DISCOVERED = ["Crew Report", "Scheduled Inspection", "Walkaround",
                  "Maintenance Check", "BITE/CMC", "Pilot Squawk"]
MAKE_FROM_FAMILY = {"A320": "AIRBUS", "A330": "AIRBUS", "A350": "AIRBUS",
                    "B737": "BOEING", "B777": "BOEING", "B787": "BOEING"}


def _condition_for(defect_key, rng):
    mapping = {
        "ELECTRICAL_FAULT": ["Failed", "Intermittent", "Burned"],
        "HYDRAULIC_LEAK": ["Leaking", "Failed"],
        "FUEL_SYSTEM": ["Malfunctioned", "Leaking", "Failed"],
        "STRUCTURAL_DAMAGE": ["Cracked", "Corroded", "Loose"],
        "SENSOR_INDICATION": ["Malfunctioned", "Intermittent"],
        "PNEUMATIC_BLEED": ["Leaking", "Failed", "Malfunctioned"],
        "LANDING_GEAR_BRAKE": ["Worn", "Failed", "Leaking"],
        "POWERPLANT": ["Failed", "Worn", "Cracked"],
    }
    return rng.choice(mapping.get(defect_key, PART_CONDITIONS))


def _nature_for(defect_key, rng):
    mapping = {
        "ELECTRICAL_FAULT": ["Warning Indication", "Loss of System"],
        "HYDRAULIC_LEAK": ["Fluid Loss", "Loss of System"],
        "FUEL_SYSTEM": ["Warning Indication", "Fluid Loss", "Degraded Performance"],
        "STRUCTURAL_DAMAGE": ["Structural", "Component Separation"],
        "SENSOR_INDICATION": ["False Indication", "Warning Indication"],
        "PNEUMATIC_BLEED": ["Loss of System", "Smoke/Fumes", "Degraded Performance"],
        "LANDING_GEAR_BRAKE": ["Degraded Performance", "Component Separation"],
        "POWERPLANT": ["Degraded Performance", "Warning Indication"],
    }
    return rng.choice(mapping.get(defect_key, NATURE_OF_CONDITION))


def _record_from_techlog(t, rng, ctrl):
    return {
        "sdr_control_number": ctrl,
        "difficulty_date": t["date"],
        "submitter_type": "Air Carrier",
        "operator_designator": "EK_SYN",
        "aircraft_make": MAKE_FROM_FAMILY.get(t["family"], "UNKNOWN"),
        "aircraft_model": t["aircraft_type"],
        "engine_make_model": t["engine"],
        "ata_code": t["ata_chapter"],
        "part_name": t["component"],
        "part_condition": _condition_for(t["defect_category"], rng),
        "nature_of_condition": _nature_for(t["defect_category"], rng),
        "stage_of_operation": t["flight_phase"] if t["flight_phase"] in STAGE
        else rng.choice(STAGE),
        "part_location": f"ATA {t['ata_chapter']} - {t['ata_title']}",
        "discrepancy_narrative": t["clean_narrative"],
        "corrective_action": t["action_taken"],
        "how_discovered": rng.choice(HOW_DISCOVERED),
    }


def _standalone_record(rng, ctrl, year):
    defect_key = rng.choice(tax.DEFECT_KEYS)
    profile = tax.DEFECT_CATEGORIES[defect_key]
    ac_type = rng.choice(list(tax.AIRCRAFT_TYPES.keys()))
    spec = tax.AIRCRAFT_TYPES[ac_type]
    family = spec["family"]
    ata, component = tax.pick_ata_component(rng, profile)
    symptom = rng.choice(profile["symptoms"])
    month = rng.randint(1, 12)
    day = rng.randint(1, 28)
    return {
        "sdr_control_number": ctrl,
        "difficulty_date": f"{year}-{month:02d}-{day:02d}",
        "submitter_type": rng.choice(["Air Carrier", "Repair Station"]),
        "operator_designator": rng.choice(["EK_SYN", "OPR_A", "OPR_B", "MRO_1"]),
        "aircraft_make": MAKE_FROM_FAMILY.get(family, "UNKNOWN"),
        "aircraft_model": ac_type,
        "engine_make_model": spec["engine"],
        "ata_code": ata,
        "part_name": component,
        "part_condition": _condition_for(defect_key, rng),
        "nature_of_condition": _nature_for(defect_key, rng),
        "stage_of_operation": rng.choice(STAGE),
        "part_location": f"ATA {ata} - {tax.ata_title(ata)}",
        "discrepancy_narrative": f"{component.capitalize()} {symptom}.",
        "corrective_action": rng.choice(profile["actions"]),
        "how_discovered": rng.choice(HOW_DISCOVERED),
    }


def generate(out_dir="data/raw/faa_sdr", techlogs=None, seed=tax.RANDOM_SEED):
    rng = random.Random(seed + 7)
    if techlogs is None:
        techlogs = gen_techlogs()

    records = []
    ctrl = 1
    # ~25% of (Major/Critical or structural) techlogs get filed as SDRs.
    for t in techlogs:
        reportable = t["severity"] in ("Major", "Critical") or \
            t["defect_category"] == "STRUCTURAL_DAMAGE"
        if reportable and rng.random() < 0.45:
            records.append(_record_from_techlog(
                t, rng, f"SDR{2024000000 + ctrl}"))
            ctrl += 1

    # Add standalone fleet-wide reports to broaden the taxonomy (~1200).
    for _ in range(1200):
        year = rng.choice([2023, 2024, 2025, 2026])
        records.append(_standalone_record(rng, f"SDR{2024000000 + ctrl}", year))
        ctrl += 1

    records.sort(key=lambda r: r["difficulty_date"])

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "sdr_records.jsonl"), "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(out_dir, "sdr_records.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SDR_FIELDS)
        writer.writeheader()
        writer.writerows(records)

    print(f"  faa_sdr: {len(records)} SDR-style records")
    return records


if __name__ == "__main__":
    generate()
