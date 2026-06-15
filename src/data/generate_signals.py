"""
Generate C-MAPSS-style multivariate operational signal windows.

NASA C-MAPSS provides simulated turbofan run-to-failure multivariate time
series (3 operational settings + 21 sensors) used when real ACARS / health
data is unavailable. We emit windows in the *identical* C-MAPSS schema, one
window per signal-bearing techlog, with a degradation signature injected
according to the defect category's ``signal_mode``. This is the telemetry
modality fused with text + metadata in the multimodal experiments (T2), and
the RUL column supports remaining-useful-life / early-warning baselines.

Outputs:
  data/raw/cmapss_signals/signal_windows.csv   (long format: one row per cycle)
  data/raw/cmapss_signals/signal_summary.csv   (per-techlog aggregated features)

Run standalone:  python -m src.data.generate_signals
"""
import csv
import math
import os
import random

from . import taxonomy as tax
from .generate_techlogs import generate as gen_techlogs

WINDOW = 30  # cycles per window leading up to the report

# Plausible per-sensor baselines (mean, noise) loosely following C-MAPSS ranges.
_BASELINES = {
    1: (518.7, 0.0), 2: (642.0, 0.5), 3: (1585.0, 6.0), 4: (1400.0, 9.0),
    5: (14.6, 0.0), 6: (21.6, 0.1), 7: (553.0, 0.5), 8: (2388.0, 0.1),
    9: (9050.0, 22.0), 10: (1.3, 0.0), 11: (47.5, 0.3), 12: (521.0, 0.7),
    13: (2388.0, 0.1), 14: (8130.0, 19.0), 15: (8.4, 0.03), 16: (0.03, 0.0),
    17: (392.0, 1.0), 18: (2388.0, 0.0), 19: (100.0, 0.0), 20: (38.8, 0.2),
    21: (23.3, 0.1),
}

# Which sensors each degradation mode drives, and the direction of drift.
_MODE_SENSORS = {
    "electrical":     {2: +1, 3: +1, 11: +1, 17: +1},
    "pressure_drift": {7: -1, 12: -1, 15: -1, 21: -1},
    "flow_anomaly":   {4: +1, 9: -1, 14: -1, 20: -1},
    "sensor_bias":    {6: +1, 16: +1, 10: +1},      # bias/offset, not true degradation
    "temp_rise":      {3: +1, 4: +1, 8: +1, 13: +1},
    "degradation":    {2: +1, 3: +1, 4: +1, 11: +1, 15: -1, 17: +1},
}


def _make_window(rng, mode, severity):
    """Return list of per-cycle dicts (op settings + 21 sensors + RUL)."""
    sev_gain = {"Minor": 0.6, "Major": 1.0, "Critical": 1.6}[severity]
    drift_map = _MODE_SENSORS.get(mode, {})
    rows = []
    for c in range(WINDOW):
        frac = c / (WINDOW - 1)                  # 0 -> 1 across the window
        rul = WINDOW - 1 - c                      # remaining cycles to the event
        op = [round(rng.uniform(0, 1), 4),       # op_setting_1 (flight regime)
              round(rng.uniform(0, 1), 4),       # op_setting_2
              round(rng.choice([0.0, 20.0, 40.0, 60.0, 80.0, 100.0]), 1)]
        sensors = []
        for s in range(1, 22):
            mean, noise = _BASELINES[s]
            val = mean + rng.gauss(0, noise)
            if s in drift_map:
                # Degradation grows non-linearly toward the event.
                span = max(abs(mean) * 0.04, noise * 8, 1.0)
                val += drift_map[s] * span * sev_gain * (frac ** 1.7)
            sensors.append(round(val, 4))
        rows.append({"cycle": c + 1, "op": op, "sensors": sensors, "rul": rul})
    return rows


def _summarise(window):
    """Aggregate a window into fusion-ready features: last value + slope per sensor."""
    feats = {}
    n = len(window)
    for i in range(21):
        series = [w["sensors"][i] for w in window]
        last = series[-1]
        # simple least-squares slope over cycle index
        xs = list(range(n))
        mx = sum(xs) / n
        my = sum(series) / n
        denom = sum((x - mx) ** 2 for x in xs) or 1.0
        slope = sum((xs[j] - mx) * (series[j] - my) for j in range(n)) / denom
        feats[f"sensor_{i+1}_last"] = round(last, 4)
        feats[f"sensor_{i+1}_slope"] = round(slope, 6)
    return feats


def generate(out_dir="data/raw/cmapss_signals", techlogs=None, seed=tax.RANDOM_SEED):
    rng = random.Random(seed + 21)
    if techlogs is None:
        techlogs = gen_techlogs()

    signal_logs = [t for t in techlogs if t["has_signal"]]

    os.makedirs(out_dir, exist_ok=True)
    long_path = os.path.join(out_dir, "signal_windows.csv")
    summ_path = os.path.join(out_dir, "signal_summary.csv")

    long_fields = ["unit", "techlog_id", "defect_category", "cycle", "RUL"] + \
        tax.CMAPSS_SETTINGS + tax.CMAPSS_SENSORS
    summ_fields = ["techlog_id", "defect_category", "severity"] + \
        [f"sensor_{i+1}_last" for i in range(21)] + \
        [f"sensor_{i+1}_slope" for i in range(21)]

    n_rows = 0
    with open(long_path, "w", newline="") as lf, open(summ_path, "w", newline="") as sf:
        lw = csv.DictWriter(lf, fieldnames=long_fields)
        sw = csv.DictWriter(sf, fieldnames=summ_fields)
        lw.writeheader()
        sw.writeheader()
        for unit, t in enumerate(signal_logs, start=1):
            mode = tax.DEFECT_CATEGORIES[t["defect_category"]]["signal_mode"]
            window = _make_window(rng, mode, t["severity"])
            for w in window:
                row = {"unit": unit, "techlog_id": t["techlog_id"],
                       "defect_category": t["defect_category"],
                       "cycle": w["cycle"], "RUL": w["rul"]}
                for j, name in enumerate(tax.CMAPSS_SETTINGS):
                    row[name] = w["op"][j]
                for j, name in enumerate(tax.CMAPSS_SENSORS):
                    row[name] = w["sensors"][j]
                lw.writerow(row)
                n_rows += 1
            summ = {"techlog_id": t["techlog_id"],
                    "defect_category": t["defect_category"],
                    "severity": t["severity"]}
            summ.update(_summarise(window))
            sw.writerow(summ)

    print(f"  cmapss_signals: {len(signal_logs)} windows, {n_rows} cycle-rows "
          f"(schema = 3 op settings + 21 sensors)")
    return signal_logs


if __name__ == "__main__":
    generate()
