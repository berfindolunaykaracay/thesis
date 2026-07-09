"""
Phase 2 — Outlier-robustness analysis (advisor request).

For each (cluster, property), reports mean / median / IQR /
arcsinh-mean / winsorized mean / outlier-retained vs outlier-removed
comparison. This addresses the supervisor's note that the raw "mean
improvement" in C2 was dominated by a single PMA outlier (now reassigned
to C1 after unit correction).

Output:
  output/outlier_robustness.txt
"""
import os
import numpy as np
import pandas as pd

DATASET = "../Dataset_LatestVersion.xlsx"
OUT = "output"

PROPS = [
    ("ΔE modulus",  "Elastic Modulus improvement (%)"),
    ("Δσ strength", "Strength improvement (%)"),
    ("Δε strain",   "Strain to failure improvement%"),
]

# Phase 2 modulus-based cluster thresholds
def cluster(m):
    if pd.isna(m): return None
    if m < 0.1: return "C1"
    if m < 0.5: return "C2"
    if m < 1.0: return "C3"
    return "C4"


def winsorize(arr, limits=(0.05, 0.05)):
    arr = np.sort(arr)
    n = len(arr)
    lo = int(np.ceil(limits[0] * n))
    hi = int(np.floor((1 - limits[1]) * n))
    return arr[lo:hi]


def robust_stats(vals):
    vals = np.array(vals, dtype=float)
    vals = vals[~np.isnan(vals)]
    if len(vals) == 0:
        return None
    q25, q50, q75 = np.percentile(vals, [25, 50, 75])
    iqr = q75 - q25
    arc_mean = float(np.mean(np.arcsinh(vals)))
    if len(vals) >= 5:
        wins = winsorize(vals)
        wins_mean = float(np.mean(wins)) if len(wins) > 0 else float("nan")
    else:
        wins_mean = float("nan")
    # outliers via 1.5×IQR rule
    lo_fence, hi_fence = q25 - 1.5 * iqr, q75 + 1.5 * iqr
    keep = vals[(vals >= lo_fence) & (vals <= hi_fence)]
    return {
        "n": int(len(vals)),
        "mean": float(np.mean(vals)),
        "median": float(q50),
        "IQR": float(iqr),
        "min": float(np.min(vals)),
        "max": float(np.max(vals)),
        "arcsinh_mean": arc_mean,
        "winsorized_mean": wins_mean,
        "n_outliers": int(len(vals) - len(keep)),
        "mean_no_outliers": float(np.mean(keep)) if len(keep) > 0 else float("nan"),
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    df = pd.read_excel(DATASET)
    df["cluster"] = df["Polymer matrix elastic modulus (GPa)"].apply(cluster)

    lines = []
    lines.append("=" * 95)
    lines.append("OUTLIER-ROBUSTNESS ANALYSIS — Phase 2 mechanical improvements")
    lines.append("=" * 95)
    lines.append("Phase-2 cluster thresholds (elastic modulus): "
                 "C1 < 0.1 GPa | 0.1-0.5 GPa | 0.5-1.0 GPa | > 1.0 GPa\n")

    for cid in ["C1", "C2", "C3", "C4"]:
        sub = df[df["cluster"] == cid]
        lines.append(f"\n--- Cluster {cid} (n_total = {len(sub)}) ---")
        for label, col in PROPS:
            vals = pd.to_numeric(sub[col], errors="coerce").dropna().values
            stats = robust_stats(vals)
            if not stats:
                lines.append(f"  {label}: no data")
                continue
            lines.append(
                f"  {label} (n={stats['n']:>3}): "
                f"mean={stats['mean']:>9.2f}  median={stats['median']:>8.2f}  "
                f"IQR={stats['IQR']:>8.2f}  "
                f"arcsinh-mean={stats['arcsinh_mean']:>5.2f}  "
                f"wins-mean={stats['winsorized_mean']:>9.2f}  "
                f"outliers={stats['n_outliers']}  "
                f"mean(no out)={stats['mean_no_outliers']:>9.2f}"
            )

    # Modified vs unmodified within each cluster, robust comparison
    lines.append("\n\n" + "=" * 95)
    lines.append("Modified vs. Unmodified — robust statistics per cluster")
    lines.append("=" * 95 + "\n")
    df["mod"] = df["Modification (modified/unmodified)"].astype(str).str.strip().str.lower()
    for cid in ["C1", "C2", "C3", "C4"]:
        lines.append(f"\n--- {cid} ---")
        for label, col in PROPS:
            for mod_state, mod_label in [("modified", "Modified  "),
                                          ("unmodified", "Unmodified")]:
                sub = df[(df["cluster"] == cid) & (df["mod"] == mod_state)]
                vals = pd.to_numeric(sub[col], errors="coerce").dropna().values
                stats = robust_stats(vals)
                if not stats:
                    continue
                lines.append(
                    f"  {label}  {mod_label} (n={stats['n']:>3}): "
                    f"mean={stats['mean']:>9.2f}  median={stats['median']:>8.2f}  "
                    f"arcsinh={stats['arcsinh_mean']:>5.2f}  "
                    f"mean(no out)={stats['mean_no_outliers']:>9.2f}"
                )

    out_path = f"{OUT}/outlier_robustness.txt"
    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
