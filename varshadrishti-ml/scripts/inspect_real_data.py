"""
VarshaDrishti — Real INSAT-3DR Data Inspection Script
======================================================
Inspects the actual numerical contents of:
  - L1B: 3RIMG_17AUG2026_2345_L1B_STD_V01R00.h5
  - L2B: 3RIMG_17AUG2026_2345_L2B_IMC_V01R00.h5

Does NOT resample, normalize, train, or modify any file.
Saves report to: reports/real_data_inspection.txt
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

try:
    import h5py
    import numpy as np
except ImportError:
    print("ERROR: Required packages missing.")
    print("Install with:  pip install h5py numpy")
    sys.exit(1)

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).parent.parent
L1B_PATH  = BASE_DIR / "data" / "raw" / "insat3dr_l1b" / "3RIMG_17AUG2026_2345_L1B_STD_V01R00.h5"
L2B_PATH  = BASE_DIR / "data" / "raw" / "insat3dr_l2b" / "3RIMG_17AUG2026_2345_L2B_IMC_V01R00.h5"
REPORT    = BASE_DIR / "reports" / "real_data_inspection.txt"

L1B_CHANNELS = ["IMG_VIS", "IMG_SWIR", "IMG_MIR", "IMG_TIR1", "IMG_TIR2", "IMG_WV"]
IMC_FILL_VALUE = -999.0
EPOCH = datetime(2000, 1, 1, 0, 0, 0)


# ── Helpers ────────────────────────────────────────────────────────────────────

def sep(width=72):
    return "=" * width

def subsep(width=72):
    return "-" * width

def minutes_to_utc(minutes_val):
    return EPOCH + timedelta(minutes=float(minutes_val))

def channel_stats(dataset, name):
    """Return stats dict for a single L1B channel dataset (uint16 or similar)."""
    raw = dataset[()]          # full load; squeeze leading dim if shape is [1, H, W]
    if raw.ndim == 3 and raw.shape[0] == 1:
        raw = raw[0]

    # Detect fill value from attributes
    fill_val = None
    for attr_key in ("_FillValue", "FillValue", "fill_value", "missing_value"):
        if attr_key in dataset.attrs:
            fill_val = dataset.attrs[attr_key]
            break

    arr = raw.astype(np.float64)
    total_px = arr.size

    if fill_val is not None:
        invalid_mask = (raw == fill_val) | ~np.isfinite(arr)
    else:
        invalid_mask = ~np.isfinite(arr)

    invalid_px = int(np.sum(invalid_mask))
    valid_px   = total_px - invalid_px
    valid_arr  = arr[~invalid_mask]

    stats = {
        "shape":       raw.shape,
        "dtype":       str(dataset.dtype),
        "fill_value":  fill_val,
        "total_px":    total_px,
        "invalid_px":  invalid_px,
        "pct_invalid": 100.0 * invalid_px / total_px if total_px > 0 else 0.0,
        "valid_px":    valid_px,
    }
    if valid_arr.size > 0:
        stats["raw_min"]  = float(np.nanmin(valid_arr))
        stats["raw_max"]  = float(np.nanmax(valid_arr))
        stats["mean"]     = float(np.nanmean(valid_arr))
        stats["std"]      = float(np.nanstd(valid_arr))
    else:
        stats["raw_min"] = stats["raw_max"] = stats["mean"] = stats["std"] = float("nan")

    return stats

def geo_stats(dataset, name):
    raw  = dataset[()]
    arr  = raw.astype(np.float64)
    fin  = np.isfinite(arr)
    valid_arr = arr[fin]
    return {
        "shape":     raw.shape,
        "dtype":     str(dataset.dtype),
        "finite_px": int(np.sum(fin)),
        "invalid_px": int(np.sum(~fin)),
        "min":  float(np.nanmin(valid_arr)) if valid_arr.size else float("nan"),
        "max":  float(np.nanmax(valid_arr)) if valid_arr.size else float("nan"),
    }

def imc_stats(dataset):
    """Compute rainfall statistics, excluding fill value -999."""
    raw = dataset[()]
    if raw.ndim == 3 and raw.shape[0] == 1:
        raw = raw[0]

    arr = raw.astype(np.float64)
    fill_mask  = np.isclose(arr, IMC_FILL_VALUE) | (arr < -990) | ~np.isfinite(arr)
    valid_arr  = arr[~fill_mask]

    total_px   = arr.size
    invalid_px = int(np.sum(fill_mask))
    valid_px   = total_px - invalid_px

    stats = {
        "shape":       raw.shape,
        "dtype":       str(dataset.dtype),
        "total_px":    total_px,
        "invalid_px":  invalid_px,
        "valid_px":    valid_px,
        "pct_valid":   100.0 * valid_px / total_px if total_px > 0 else 0.0,
    }
    if valid_arr.size > 0:
        stats["min"]  = float(np.nanmin(valid_arr))
        stats["max"]  = float(np.nanmax(valid_arr))
        stats["mean"] = float(np.nanmean(valid_arr))
        stats["std"]  = float(np.nanstd(valid_arr))
        pct_keys = [50, 75, 90, 95, 99, 99.9]
        stats["percentiles"] = {str(p): float(np.percentile(valid_arr, p)) for p in pct_keys}

        bins = [
            ("== 0 (no rain)",   (valid_arr == 0)),
            (">0 and <=1",       (valid_arr > 0) & (valid_arr <= 1)),
            (">1 and <=5",       (valid_arr > 1) & (valid_arr <= 5)),
            (">5 and <=10",      (valid_arr > 5) & (valid_arr <= 10)),
            (">10 and <=20",     (valid_arr > 10) & (valid_arr <= 20)),
            (">20 and <=50",     (valid_arr > 20) & (valid_arr <= 50)),
            (">50",              (valid_arr > 50)),
        ]
        stats["rainfall_bins"] = {label: int(np.sum(mask)) for label, mask in bins}
    else:
        stats["min"] = stats["max"] = stats["mean"] = stats["std"] = float("nan")
        stats["percentiles"] = {}
        stats["rainfall_bins"] = {}

    return stats

def read_time(hf):
    """Find a time/scan_time dataset and convert to UTC."""
    for key in ("time", "scan_time", "Time", "IMAGE_DATE_AND_TIME"):
        if key in hf:
            val = hf[key][()]
            try:
                minutes = float(np.ravel(val)[0])
                return minutes_to_utc(minutes), float(minutes)
            except Exception:
                pass
    # Also check root attributes
    for attr in hf.attrs:
        if "time" in attr.lower() or "date" in attr.lower():
            pass  # logged separately
    return None, None


# ── Main report ────────────────────────────────────────────────────────────────

def build_report():
    lines = []

    def P(s=""):
        lines.append(s)
        print(s)

    P(sep())
    P("VarshaDrishti — Real INSAT-3DR Data Inspection Report")
    P(f"Generated: {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')} UTC")
    P(sep())

    # ── Verify file existence ──────────────────────────────────────────────────
    for label, path in [("L1B", L1B_PATH), ("L2B", L2B_PATH)]:
        if not path.exists():
            P(f"ERROR: {label} file not found at {path}")
            return lines
    P("Both HDF5 files found. Proceeding with inspection.")
    P()

    # ══════════════════════════════════════════════════════════════════════════
    # L1B
    # ══════════════════════════════════════════════════════════════════════════
    P(sep())
    P("SECTION 1 — L1B INSAT-3DR IMAGER CHANNELS")
    P(f"File: {L1B_PATH.name}")
    P(sep())

    l1b_geo = {}
    l1b_time_utc = None

    with h5py.File(L1B_PATH, "r") as hf:

        # Root attributes
        P("Root-level attributes:")
        for k, v in hf.attrs.items():
            P(f"  {k}: {v}")
        P()

        # Time
        l1b_time_utc, l1b_minutes = read_time(hf)
        if l1b_time_utc:
            P(f"L1B Time: {l1b_minutes:.2f} minutes since 2000-01-01 -> {l1b_time_utc.strftime('%Y-%m-%d %H:%M UTC')}")
        else:
            P("L1B Time: Not found in expected datasets.")
        P()

        # Channels
        for ch in L1B_CHANNELS:
            P(subsep())
            P(f"Channel: {ch}")
            if ch not in hf:
                P(f"  WARNING: {ch} not found in file.")
                P()
                continue

            ds = hf[ch]
            # Print attributes for this dataset
            P(f"  Attributes:")
            for k, v in ds.attrs.items():
                P(f"    {k}: {v}")

            s = channel_stats(ds, ch)
            P(f"  Shape        : {s['shape']}")
            P(f"  Dtype        : {s['dtype']}")
            P(f"  Fill Value   : {s['fill_value']}")
            P(f"  Total pixels : {s['total_px']:,}")
            P(f"  Invalid px   : {s['invalid_px']:,}  ({s['pct_invalid']:.3f}%)")
            P(f"  Valid px     : {s['valid_px']:,}")
            P(f"  Raw min      : {s['raw_min']}")
            P(f"  Raw max      : {s['raw_max']}")
            P(f"  Mean         : {s['mean']:.4f}")
            P(f"  Std dev      : {s['std']:.4f}")
            P()

        # Geolocation
        P(subsep())
        P("L1B Geolocation Grids:")
        for geo_name in hf.keys():
            if "lat" in geo_name.lower() or "lon" in geo_name.lower():
                gs = geo_stats(hf[geo_name], geo_name)
                l1b_geo[geo_name] = gs
                P(f"  {geo_name}:")
                P(f"    Shape       : {gs['shape']}")
                P(f"    Dtype       : {gs['dtype']}")
                P(f"    Min         : {gs['min']:.4f}")
                P(f"    Max         : {gs['max']:.4f}")
                P(f"    Finite px   : {gs['finite_px']:,}")
                P(f"    Invalid px  : {gs['invalid_px']:,}")
                P()

    # ══════════════════════════════════════════════════════════════════════════
    # L2B
    # ══════════════════════════════════════════════════════════════════════════
    P(sep())
    P("SECTION 2 — L2B IMC RAINFALL TARGET")
    P(f"File: {L2B_PATH.name}")
    P(sep())

    l2b_geo = {}
    l2b_time_utc = None

    with h5py.File(L2B_PATH, "r") as hf:

        # Root attributes
        P("Root-level attributes:")
        for k, v in hf.attrs.items():
            P(f"  {k}: {v}")
        P()

        # Time
        l2b_time_utc, l2b_minutes = read_time(hf)
        if l2b_time_utc:
            P(f"L2B Time: {l2b_minutes:.2f} minutes since 2000-01-01 -> {l2b_time_utc.strftime('%Y-%m-%d %H:%M UTC')}")
        else:
            P("L2B Time: Not found in expected datasets.")
        P()

        # List all datasets for reference
        P("All datasets/groups in L2B file:")
        def _visitor(name, obj):
            if isinstance(obj, h5py.Dataset):
                P(f"  [Dataset] {name}  shape={obj.shape}  dtype={obj.dtype}")
        hf.visititems(_visitor)
        P()

        # IMC rainfall
        P(subsep())
        P("Rainfall Dataset: IMC")
        if "IMC" not in hf:
            P("  WARNING: IMC dataset not found.")
        else:
            ds_imc = hf["IMC"]
            P("  IMC Attributes:")
            for k, v in ds_imc.attrs.items():
                P(f"    {k}: {v}")
            s = imc_stats(ds_imc)
            P(f"  Shape            : {s['shape']}")
            P(f"  Dtype            : {s['dtype']}")
            P(f"  Total pixels     : {s['total_px']:,}")
            P(f"  Invalid (fill)   : {s['invalid_px']:,}")
            P(f"  Valid pixels     : {s['valid_px']:,}  ({s['pct_valid']:.2f}%)")
            P(f"  Min (excl. fill) : {s['min']:.4f} mm/hr")
            P(f"  Max (excl. fill) : {s['max']:.4f} mm/hr")
            P(f"  Mean (valid)     : {s['mean']:.4f} mm/hr")
            P(f"  Std  (valid)     : {s['std']:.4f} mm/hr")
            P()
            P("  Percentiles (valid pixels, mm/hr):")
            for pct, val in s.get("percentiles", {}).items():
                P(f"    {pct:>5}th : {val:.4f}")
            P()
            P("  Rainfall intensity distribution (valid pixels):")
            for label, count in s.get("rainfall_bins", {}).items():
                pct = 100.0 * count / s["valid_px"] if s["valid_px"] > 0 else 0
                P(f"    {label:<22} : {count:>10,}  ({pct:.2f}%)")
            P()

        # L2B Geolocation
        P(subsep())
        P("L2B Geolocation Grids:")
        for geo_name in hf.keys():
            if "lat" in geo_name.lower() or "lon" in geo_name.lower():
                gs = geo_stats(hf[geo_name], geo_name)
                l2b_geo[geo_name] = gs
                P(f"  {geo_name}:")
                P(f"    Shape       : {gs['shape']}")
                P(f"    Dtype       : {gs['dtype']}")
                P(f"    Min         : {gs['min']:.4f}")
                P(f"    Max         : {gs['max']:.4f}")
                P(f"    Finite px   : {gs['finite_px']:,}")
                P(f"    Invalid px  : {gs['invalid_px']:,}")
                P()

    # ══════════════════════════════════════════════════════════════════════════
    # Spatial Compatibility Check
    # ══════════════════════════════════════════════════════════════════════════
    P(sep())
    P("SECTION 3 — SPATIAL COMPATIBILITY CHECK (L1B 4-km vs L2B)")
    P(sep())

    # Find the 4-km-resolution geo grids from L1B (for MIR/TIR channels)
    l1b_4km_lat = next((k for k in l1b_geo if "lat" in k.lower() and "4" in k.lower()), None)
    l1b_4km_lon = next((k for k in l1b_geo if "lon" in k.lower() and "4" in k.lower()), None)

    # Fallback: pick first lat/lon regardless of name
    if l1b_4km_lat is None:
        l1b_4km_lat = next((k for k in l1b_geo if "lat" in k.lower()), None)
    if l1b_4km_lon is None:
        l1b_4km_lon = next((k for k in l1b_geo if "lon" in k.lower()), None)

    l2b_lat = next((k for k in l2b_geo if "lat" in k.lower()), None)
    l2b_lon = next((k for k in l2b_geo if "lon" in k.lower()), None)

    if l1b_4km_lat and l2b_lat:
        g1 = l1b_geo[l1b_4km_lat]
        g2 = l2b_geo[l2b_lat]
        P(f"L1B lat grid ({l1b_4km_lat}):")
        P(f"  Shape: {g1['shape']}  Min: {g1['min']:.4f}  Max: {g1['max']:.4f}")
        P(f"L2B lat grid ({l2b_lat}):")
        P(f"  Shape: {g2['shape']}  Min: {g2['min']:.4f}  Max: {g2['max']:.4f}")
        shapes_match = (g1['shape'] == g2['shape'])
        lat_range_ok = abs(g1['min'] - g2['min']) < 0.5 and abs(g1['max'] - g2['max']) < 0.5
        P(f"Shapes identical   : {shapes_match}")
        P(f"Lat range similar  : {lat_range_ok}")
        P()
    else:
        P("Could not locate comparable lat/lon grids for compatibility check.")
        P()

    # Temporal proximity
    P(sep())
    P("SECTION 4 — TEMPORAL PROXIMITY CHECK")
    P(sep())
    if l1b_time_utc and l2b_time_utc:
        delta_min = abs((l1b_time_utc - l2b_time_utc).total_seconds()) / 60.0
        P(f"L1B observation : {l1b_time_utc.strftime('%Y-%m-%d %H:%M UTC')}")
        P(f"L2B observation : {l2b_time_utc.strftime('%Y-%m-%d %H:%M UTC')}")
        P(f"Time difference : {delta_min:.1f} minutes")
        if delta_min <= 30:
            P("RESULT: Temporally compatible (within 30-minute tolerance).")
        else:
            P(f"WARNING: Time difference of {delta_min:.1f} min exceeds 30-minute tolerance.")
    else:
        P("Could not determine timestamps from file. Manual verification required.")

    P()
    P(sep())
    P("INSPECTION COMPLETE")
    P(sep())

    return lines


if __name__ == "__main__":
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    report_lines = build_report()

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print()
    print(f"Report saved to: {REPORT}")
