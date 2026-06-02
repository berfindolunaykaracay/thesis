"""
Phase 2 — C4 toughness-preserving subpopulation analysis (advisor request,
2026-06-02).

Within the rigid polymer cluster (C4, matrix E > 1 GPa) the supervisor's
review identified a subpopulation where both Δσ > 0 AND Δε > 0 — i.e.
strength AND strain-to-failure simultaneously improve, contrary to the
default "ductility penalty" reading of C4. This script reproduces the
analysis on the post-PMA-correction Dataset_LatestVersion.xlsx, reports
sample counts, polymer-family enrichment, modification effect, dispersion
breakdown, baseline matrix properties, and group-mean comparisons, and
generates the Δσ vs Δε scatter plot recommended in the supervisor's
"Recommended figure" section.

Outputs:
  output/c4_toughness_subpopulation.txt
  output/c4_toughness_scatter.png
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DATASET = "../Dataset_LatestVersion.xlsx"
OUT = "output"

COL_MATRIX_E = "Polymer matrix elastic modulus (GPa)"
COL_MATRIX_S = "Polymer matrix Strength (MPa)"
COL_MATRIX_EPS = "Polymer matrix strain to failure"
COL_DE = "Elastic Modulus improvement (%)"
COL_DSIG = "Strength improvement (%)"
COL_DEPS = "Strain to failure improvement%"
COL_POLY = "Polymer matrix name"
COL_MOD = "Modification (modified/unmodified)"
COL_DISP = "Dispersion(microcomposite/exfoliated/intercalated/agglomerated)"


def main():
    os.makedirs(OUT, exist_ok=True)
    df = pd.read_excel(DATASET)

    # C4 = rigid polymers, matrix modulus > 1 GPa
    c4 = df[df[COL_MATRIX_E] > 1.0].copy()
    # require numerical strength and strain improvement
    c4 = c4[c4[COL_DSIG].apply(lambda v: pd.notna(pd.to_numeric(v, errors="coerce")))
            & c4[COL_DEPS].apply(lambda v: pd.notna(pd.to_numeric(v, errors="coerce")))]
    c4[COL_DSIG] = pd.to_numeric(c4[COL_DSIG], errors="coerce")
    c4[COL_DEPS] = pd.to_numeric(c4[COL_DEPS], errors="coerce")
    c4[COL_DE] = pd.to_numeric(c4[COL_DE], errors="coerce")

    pos = c4[(c4[COL_DSIG] > 0) & (c4[COL_DEPS] > 0)].copy()
    rem = c4.drop(pos.index)

    lines = []
    def w(s=""):
        lines.append(s)
        print(s)

    w("=" * 95)
    w("C4 TOUGHNESS-PRESERVING SUBPOPULATION ANALYSIS (advisor request, 2026-06-02)")
    w("Dataset: Dataset_LatestVersion.xlsx (post PMA unit correction)")
    w("=" * 95)

    n_c4 = len(c4)
    n_pos_sig = (c4[COL_DSIG] > 0).sum()
    n_pos_eps = (c4[COL_DEPS] > 0).sum()
    n_pos_both = len(pos)
    # all three positive
    n_pos_all3 = ((c4[COL_DE] > 0) & (c4[COL_DSIG] > 0) & (c4[COL_DEPS] > 0)).sum()

    w("")
    w("1. C4 subpopulation counts")
    w(f"   C4 samples with numerical strength and strain data : {n_c4}")
    w(f"   Positive strength improvement (Δσ > 0)             : {n_pos_sig}  "
      f"({100*n_pos_sig/n_c4:.1f}%)")
    w(f"   Positive strain improvement (Δε > 0)               : {n_pos_eps}  "
      f"({100*n_pos_eps/n_c4:.1f}%)")
    w(f"   Positive Δσ AND positive Δε                        : {n_pos_both}  "
      f"({100*n_pos_both/n_c4:.1f}%)")
    w(f"   Positive ΔE AND Δσ AND Δε                          : {n_pos_all3}  "
      f"({100*n_pos_all3/n_c4:.1f}%)")

    w("")
    w("2. Group-mean comparison")
    w(f"   {'metric':<22}{'positive':>15}{'remaining':>15}")
    for label, col in [("ΔE  mean", COL_DE), ("Δσ  mean", COL_DSIG),
                       ("Δε  mean", COL_DEPS)]:
        p = pos[col].mean()
        r = rem[col].mean()
        w(f"   {label:<22}{p:>14.2f}%{r:>14.2f}%")
    for label, col in [("ΔE  median", COL_DE), ("Δσ  median", COL_DSIG),
                       ("Δε  median", COL_DEPS)]:
        p = pos[col].median()
        r = rem[col].median()
        w(f"   {label:<22}{p:>14.2f}%{r:>14.2f}%")
    # toughness proxy = (1 + Δσ)(1 + Δε) - 1, with values in fractional form
    p_tprx = ((1 + pos[COL_DSIG]/100.0) * (1 + pos[COL_DEPS]/100.0) - 1.0) * 100.0
    r_tprx = ((1 + rem[COL_DSIG]/100.0) * (1 + rem[COL_DEPS]/100.0) - 1.0) * 100.0
    w(f"   {'toughness-proxy mean':<22}{p_tprx.mean():>14.2f}%{r_tprx.mean():>14.2f}%")
    w(f"   {'toughness-proxy med':<22}{p_tprx.median():>14.2f}%{r_tprx.median():>14.2f}%")

    w("")
    w("3. Polymer-family enrichment (positive subgroup vs remaining)")
    fams = sorted(set(c4[COL_POLY].dropna().unique()))
    rows = []
    for f in fams:
        ntot = (c4[COL_POLY] == f).sum()
        npos = (pos[COL_POLY] == f).sum()
        nrem = (rem[COL_POLY] == f).sum()
        frac = 100 * npos / ntot if ntot else 0
        rows.append((f, ntot, npos, nrem, frac))
    rows.sort(key=lambda r: (-r[2], -r[1]))
    w(f"   {'family':<28}{'total':>8}{'positive':>10}{'remaining':>11}"
      f"{'pos%':>8}")
    for f, ntot, npos, nrem, frac in rows:
        if ntot < 1:
            continue
        w(f"   {str(f)[:28]:<28}{ntot:>8d}{npos:>10d}{nrem:>11d}{frac:>7.1f}%")

    w("")
    w("4. Modification effect")
    for grp_name, grp in [("Positive subgroup", pos), ("Remaining C4", rem)]:
        modn = grp[COL_MOD].astype(str).str.lower().str.strip().value_counts()
        w(f"   {grp_name}: " +
          ", ".join(f"{k}={v}" for k, v in modn.items()))

    w("")
    w("5. Dispersion-state distribution (positive subgroup)")
    disp = pos[COL_DISP].astype(str).str.strip().value_counts()
    for k, v in disp.items():
        w(f"   {k[:55]:<55} {v}")

    w("")
    w("6. Baseline matrix properties (median)")
    w(f"   {'property':<28}{'positive':>12}{'remaining':>13}")
    for label, col in [("matrix modulus (GPa)", COL_MATRIX_E),
                       ("matrix strength (MPa)", COL_MATRIX_S),
                       ("matrix strain", COL_MATRIX_EPS)]:
        p_v = pd.to_numeric(pos[col], errors="coerce").median()
        r_v = pd.to_numeric(rem[col], errors="coerce").median()
        w(f"   {label:<28}{p_v:>12.2f}{r_v:>13.2f}")

    out_txt = f"{OUT}/c4_toughness_subpopulation.txt"
    with open(out_txt, "w") as f:
        f.write("\n".join(lines))
    print(f"Wrote {out_txt}")

    # ------- recommended figure: Δσ vs Δε scatter (advisor §10) -------
    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    fam_top = [r[0] for r in rows[:6]]
    cmap = plt.get_cmap("tab10")
    fam_color = {f: cmap(i) for i, f in enumerate(fam_top)}
    # remaining samples — light grey background
    ax.scatter(rem[COL_DSIG], rem[COL_DEPS], s=14, c="lightgrey",
               alpha=0.45, edgecolors="none", label="remaining C4")
    # positive subgroup, coloured by top-6 families; others in dark grey
    for f in fam_top:
        sub = pos[pos[COL_POLY] == f]
        if len(sub) == 0:
            continue
        # marker shape = modification
        for mod_state, marker in [("modified", "o"), ("unmodified", "s")]:
            s2 = sub[sub[COL_MOD].astype(str).str.lower().str.strip() == mod_state]
            if len(s2) == 0:
                continue
            ax.scatter(s2[COL_DSIG], s2[COL_DEPS], s=55, c=[fam_color[f]],
                       marker=marker, edgecolors="black", linewidths=0.5,
                       label=f"{f} ({mod_state})")
    other_pos = pos[~pos[COL_POLY].isin(fam_top)]
    if len(other_pos):
        ax.scatter(other_pos[COL_DSIG], other_pos[COL_DEPS], s=40,
                   c="black", marker="x", label="other positive")
    ax.axhline(0, color="black", lw=0.7); ax.axvline(0, color="black", lw=0.7)
    ax.set_xlabel("Δσ — strength improvement (%)")
    ax.set_ylabel("Δε — strain-to-failure improvement (%)")
    ax.set_title("C4 (rigid polymer) toughness-preserving subpopulation\n"
                 "upper-right quadrant: simultaneous strength and strain gain")
    ax.text(0.02, 0.97,
            f"C4 n = {n_c4}\npositive (Δσ>0 & Δε>0) n = {n_pos_both}  "
            f"({100*n_pos_both/n_c4:.1f}%)",
            transform=ax.transAxes, va="top", fontsize=10,
            bbox=dict(facecolor="white", edgecolor="lightgrey", alpha=0.9))
    ax.legend(fontsize=8, loc="lower right", framealpha=0.92)
    ax.set_xlim(-110, max(200, pos[COL_DSIG].max() * 1.05))
    ax.set_ylim(-110, max(200, pos[COL_DEPS].max() * 1.05))
    plt.tight_layout()
    out_png = f"{OUT}/c4_toughness_scatter.png"
    plt.savefig(out_png, dpi=160)
    plt.close()
    print(f"Wrote {out_png}")


if __name__ == "__main__":
    main()
