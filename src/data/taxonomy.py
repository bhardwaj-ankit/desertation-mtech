"""
Shared aviation maintenance taxonomy.

This module is the single source of truth that keeps every generated dataset
internally consistent: a techlog narrative, its ATA chapter, severity, the
operational signal window, the recurrence behaviour and the knowledge corpus
that resolves it all derive from the same defect-category profile.

References for the schema / vocabulary (all public):
  * ATA iSpec 2200 chapter numbering
  * FAA Service Difficulty Reports (SDR) field structure
  * IATA eTechLog / AHM guidance (defect-narrative pain points)
  * NASA C-MAPSS sensor layout (21 sensors + 3 operational settings)
"""

# ---------------------------------------------------------------------------
# ATA chapters used in the project (subset relevant to line-maintenance defects)
# ---------------------------------------------------------------------------
ATA_CHAPTERS = {
    "21": "Air Conditioning & Pressurisation",
    "24": "Electrical Power",
    "27": "Flight Controls",
    "28": "Fuel",
    "29": "Hydraulic Power",
    "32": "Landing Gear",
    "34": "Navigation",
    "36": "Pneumatic / Bleed Air",
    "49": "Auxiliary Power Unit (APU)",
    "52": "Doors",
    "53": "Fuselage Structure",
    "57": "Wing Structure",
    "72": "Engine (Turbine)",
    "73": "Engine Fuel & Control",
    "78": "Engine Exhaust / Thrust Reverser",
}

# ---------------------------------------------------------------------------
# Eight defect categories (matches the 8-class triage classifier in README).
# Each profile drives narrative generation, severity, signals and recurrence.
# ---------------------------------------------------------------------------
# Field meanings:
#   ata          : ATA chapters this defect maps to, PRIMARY FIRST (weighted)
#   components   : dict {ata_chapter -> [component nouns]} so that the chosen
#                  component is always consistent with the chosen ATA chapter
#   symptoms     : observable symptom phrases (free text, techlog style)
#   actions      : typical maintenance actions / resolutions
#   severity_w   : weights for (Minor, Major, Critical)
#   deferrable_p : probability the defect is MEL/CDL deferrable
#   recurrence_p : base probability of a repeat within the recurrence horizon
#   signal_mode  : which C-MAPSS-style degradation signature to inject
DEFECT_CATEGORIES = {
    "ELECTRICAL_FAULT": {
        "label": "Electrical Fault",
        "ata": ["24", "49"],
        "components": {
            "24": ["generator", "bus tie relay", "TR unit", "battery",
                   "wiring harness", "circuit breaker", "GCU"],
            "49": ["APU generator", "APU GCU"],
        },
        "symptoms": ["intermittent power loss", "BUS warning illuminated",
                     "CB tripped repeatedly", "voltage fluctuation",
                     "GEN OFF caption", "battery discharge"],
        "actions": ["replaced generator control unit", "reset and secured CB",
                    "renewed wiring connector", "swapped TR unit",
                    "performed insulation resistance check"],
        "severity_w": (0.45, 0.40, 0.15),
        "deferrable_p": 0.55,
        "recurrence_p": 0.30,
        "signal_mode": "electrical",
    },
    "HYDRAULIC_LEAK": {
        "label": "Hydraulic Leak",
        "ata": ["29", "27", "32"],
        "components": {
            "29": ["hydraulic pump", "reservoir", "EDP", "hose assembly",
                   "filter module", "PTU"],
            "27": ["flight control actuator"],
            "32": ["landing gear actuator"],
        },
        "symptoms": ["fluid stain observed", "system pressure low",
                     "reservoir quantity dropping", "weeping at union",
                     "LO PRESS caption", "Qty LO advisory"],
        "actions": ["replaced hydraulic hose", "torqued B-nut to spec",
                    "renewed actuator seals", "serviced reservoir",
                    "replaced EDP"],
        "severity_w": (0.40, 0.45, 0.15),
        "deferrable_p": 0.35,
        "recurrence_p": 0.28,
        "signal_mode": "pressure_drift",
    },
    "FUEL_SYSTEM": {
        "label": "Fuel System Anomaly",
        "ata": ["28", "73", "49"],
        "components": {
            "28": ["boost pump", "fuel valve", "fuel quantity probe",
                   "crossfeed valve", "fuel filter"],
            "73": ["FCU", "engine fuel metering unit"],
            "49": ["APU fuel control unit"],
        },
        "symptoms": ["FUEL PUMP caption", "pressure low during climb",
                     "imbalance advisory", "FQI erratic indication",
                     "low fuel flow", "smell of fuel in bay"],
        "actions": ["replaced boost pump", "renewed fuel filter",
                    "recalibrated fuel quantity probe", "replaced FCU",
                    "leak-checked and resealed coupling"],
        "severity_w": (0.40, 0.42, 0.18),
        "deferrable_p": 0.45,
        "recurrence_p": 0.32,
        "signal_mode": "flow_anomaly",
    },
    "STRUCTURAL_DAMAGE": {
        "label": "Structural Crack / Dent / Corrosion",
        "ata": ["53", "57", "52"],
        "components": {
            "53": ["fuselage skin", "stringer", "lap joint", "access panel"],
            "57": ["wing leading edge", "fairing"],
            "52": ["door frame"],
        },
        "symptoms": ["crack found during walkaround", "dent beyond limits",
                     "corrosion under panel", "loose fastener row",
                     "paint cracking along seam", "delamination noted"],
        "actions": ["raised structural assessment to engineering",
                    "applied temporary repair per SRM",
                    "blended out corrosion within limits",
                    "installed doubler per repair scheme",
                    "monitored crack with reference marks"],
        "severity_w": (0.30, 0.45, 0.25),
        "deferrable_p": 0.20,
        "recurrence_p": 0.22,
        "signal_mode": "none",
    },
    "SENSOR_INDICATION": {
        "label": "Sensor / Indication Fault",
        "ata": ["34", "21", "24"],
        "components": {
            "34": ["air data probe", "AOA vane", "pressure transducer", "RVDT"],
            "21": ["cabin temperature sensor"],
            "24": ["ECAM display unit"],
        },
        "symptoms": ["disagree caption", "erratic gauge reading",
                     "spurious warning", "indication frozen",
                     "fault message on CMC", "intermittent NCD"],
        "actions": ["replaced air data probe", "cleaned electrical connector",
                    "swapped temperature sensor", "performed BITE test, fault cleared",
                    "renewed transducer"],
        "severity_w": (0.55, 0.35, 0.10),
        "deferrable_p": 0.65,
        "recurrence_p": 0.35,
        "signal_mode": "sensor_bias",
    },
    "PNEUMATIC_BLEED": {
        "label": "Pneumatic / Bleed Leak",
        "ata": ["36", "21", "49"],
        "components": {
            "36": ["bleed valve", "duct", "PRV", "HP valve",
                   "flow control valve"],
            "21": ["precooler", "pack flow control valve"],
            "49": ["APU bleed valve"],
        },
        "symptoms": ["BLEED FAULT caption", "duct overheat warning",
                     "leak detection loop active", "pressure regulation poor",
                     "pack flow low", "wing anti-ice low pressure"],
        "actions": ["replaced bleed valve", "renewed duct coupling",
                    "replaced precooler control valve", "reset overheat detection",
                    "torqued V-band clamp"],
        "severity_w": (0.45, 0.42, 0.13),
        "deferrable_p": 0.50,
        "recurrence_p": 0.27,
        "signal_mode": "temp_rise",
    },
    "LANDING_GEAR_BRAKE": {
        "label": "Landing Gear / Brake Issue",
        "ata": ["32", "29"],
        "components": {
            "32": ["brake unit", "tyre", "shock strut", "WOW sensor",
                   "uplock", "steering actuator"],
            "29": ["anti-skid valve"],
        },
        "symptoms": ["brake temperature high", "tyre worn to limit",
                     "strut low on servicing", "gear disagree indication",
                     "anti-skid fault", "nose wheel shimmy reported"],
        "actions": ["replaced brake unit", "changed tyre and wheel assembly",
                    "serviced shock strut to chart", "replaced WOW sensor",
                    "renewed anti-skid control valve"],
        "severity_w": (0.42, 0.43, 0.15),
        "deferrable_p": 0.40,
        "recurrence_p": 0.26,
        "signal_mode": "pressure_drift",
    },
    "POWERPLANT": {
        "label": "Powerplant / Engine Anomaly",
        "ata": ["72", "78", "49"],
        "components": {
            "72": ["HP compressor", "fuel nozzle", "N1 sensor",
                   "oil chip detector", "bearing", "EGT harness"],
            "78": ["thrust reverser"],
            "49": ["APU power section"],
        },
        "symptoms": ["EGT exceedance on start", "vibration high cruise",
                     "oil consumption increased", "stall during acceleration",
                     "N2 hung start", "reverser unlock advisory"],
        "actions": ["performed compressor wash", "replaced fuel nozzle set",
                    "renewed EGT thermocouple harness", "borescoped HPT, within limits",
                    "replaced N1 speed sensor"],
        "severity_w": (0.30, 0.45, 0.25),
        "deferrable_p": 0.30,
        "recurrence_p": 0.30,
        "signal_mode": "degradation",
    },
}

DEFECT_KEYS = list(DEFECT_CATEGORIES.keys())

SEVERITY_LEVELS = ["Minor", "Major", "Critical"]

# ---------------------------------------------------------------------------
# Fleet: aircraft types with realistic MSN ranges and engine fits
# ---------------------------------------------------------------------------
AIRCRAFT_TYPES = {
    "A320-214":  {"family": "A320", "engine": "CFM56-5B", "tail_prefix": "A6-A"},
    "A321-271":  {"family": "A320", "engine": "PW1100G",  "tail_prefix": "A6-A"},
    "A330-343":  {"family": "A330", "engine": "Trent772", "tail_prefix": "A6-E"},
    "A350-941":  {"family": "A350", "engine": "TrentXWB", "tail_prefix": "A6-X"},
    "B737-800":  {"family": "B737", "engine": "CFM56-7B", "tail_prefix": "A6-B"},
    "B777-31H":  {"family": "B777", "engine": "GE90-115", "tail_prefix": "A6-E"},
    "B787-9":    {"family": "B787", "engine": "Trent1000","tail_prefix": "A6-B"},
}

# Hub + outstation network (IATA codes) where defects are reported
STATIONS = ["DXB", "DWC", "AUH", "LHR", "JFK", "SIN", "BOM", "DEL", "CDG",
            "FRA", "SYD", "JNB", "IST", "HKG", "GRU", "LOS", "MEL", "MAN"]

# Reporter roles for the techlog "reported_by" / "actioned_by" fields
REPORTERS = ["Flight Crew", "Cabin Crew", "Line Engineer", "Walkaround Tech",
             "MCC Controller"]

# ---------------------------------------------------------------------------
# Techlog shorthand / abbreviation dictionary (drives the "noisy free text"
# pain point IATA documents, and the abbreviation-expansion task in T2).
# ---------------------------------------------------------------------------
ABBREVIATIONS = {
    "illuminated": "illum",
    "warning": "warn",
    "caption": "capt",
    "pressure": "press",
    "intermittent": "intmt",
    "investigate": "invest",
    "replaced": "repl",
    "checked": "ckd",
    "serviceable": "svc",
    "unserviceable": "u/s",
    "during": "dur",
    "climb": "clb",
    "cruise": "crz",
    "left hand": "LH",
    "right hand": "RH",
    "number": "no.",
    "found": "fnd",
    "nil defect": "NIL",
    "operations normal": "ops nml",
    "carried forward": "C/F",
}

# C-MAPSS sensor layout: 3 operational settings + 21 sensor measurements.
# We keep the canonical NASA C-MAPSS column naming so real and synthetic
# signal data share an identical schema.
CMAPSS_SETTINGS = [f"op_setting_{i}" for i in range(1, 4)]
CMAPSS_SENSORS = [f"sensor_{i}" for i in range(1, 22)]
CMAPSS_COLUMNS = ["unit", "cycle"] + CMAPSS_SETTINGS + CMAPSS_SENSORS

# Recurrence horizon (days): a repeat of the same defect category on the same
# tail within this window is labelled a recurrence (matches LITERATURE_REVIEW).
RECURRENCE_HORIZON_DAYS = 30

# Random seed for full reproducibility of the synthetic groundwork.
RANDOM_SEED = 42


def ata_title(chapter: str) -> str:
    """Return the human-readable ATA chapter title, or 'Unknown'."""
    return ATA_CHAPTERS.get(str(chapter), "Unknown")


def defect_label(key: str) -> str:
    """Return the display label for a defect-category key."""
    return DEFECT_CATEGORIES[key]["label"]


def all_components(profile) -> list:
    """Flatten the ata-keyed component map into a single list."""
    out = []
    for comps in profile["components"].values():
        out.extend(comps)
    return out


def components_for(profile, ata: str) -> list:
    """Components valid for a given ATA chapter (falls back to all)."""
    return profile["components"].get(str(ata)) or all_components(profile)


def pick_ata_component(rng, profile):
    """Pick an (ata, component) pair, biased to the primary ATA, always consistent.

    The ATA list is ordered primary-first; weights decay so the primary chapter
    dominates while secondary chapters still appear for realistic variety.
    """
    atas = profile["ata"]
    weights = [len(atas) - i for i in range(len(atas))]
    ata = rng.choices(atas, weights=weights, k=1)[0]
    component = rng.choice(components_for(profile, ata))
    return ata, component
