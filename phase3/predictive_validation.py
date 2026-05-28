"""
Phase 3 — Predictive validation of embeddings (Advisor Suggestion 4).

Task: predict the modulus-improvement percentage (ΔE) of each experiment from
its categorical features, with and without concept embeddings as auxiliary
inputs. If embeddings genuinely encode useful information, predictive
accuracy should improve.

Two baselines vs four embedding-augmented models:
  baseline    : only one-hot categorical features
  +minilm     : baseline + averaged MiniLM (enriched) embeddings of categorical concepts
  +scibert    : baseline + averaged SciBERT embeddings
  +matscibert : baseline + averaged MatSciBERT embeddings
  +materialsbert: baseline + averaged MaterialsBERT embeddings

Evaluation: 5-fold cross-validation on samples that have non-null ΔE.
Reports R² and MAE on the arcsinh-transformed target so that negative
improvements are handled correctly.

Output:
  output/predictive_validation.txt
  output/predictive_validation.png
"""
import os
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

GRAPH_GEXF = "output/complete_graph.gexf"
DATASET    = "../Dataset_LatestVersion.xlsx"
OUT        = "output"

EMBEDDING_PATHS = {
    "minilm":        f"{OUT}/embeddings_minilm.npz",
    "scibert":       f"{OUT}/embeddings_scibert.npz",
    "matscibert":    f"{OUT}/embeddings_matscibert.npz",
    "materialsbert": f"{OUT}/embeddings_materialsbert.npz",
    "matbert":       f"{OUT}/embeddings_matbert.npz",
}

TARGETS = [
    ("modulus",  "Elastic Modulus improvement (%)",      "Elastic modulus improvement arcsinh"),
    ("strength", "Strength improvement (%)",             "Strength improvement arcsinh"),
    ("strain",   "Strain to failure improvement%",       "Strain to failure improvement arcsinh"),
]

CATEGORICAL_COLUMNS = {
    "polymer":      "Polymer matrix name",
    "modification": "Modification (modified/unmodified)",
    "dispersion":   "Dispersion(microcomposite/exfoliated/intercalated/agglomerated)",
    "category":     "Thermoset? Thermoplastic? Elastomer?",
    "test_method":  "Test Method",
    "data_source":  "Experimental/Simulated",
}


def load_dataset():
    df = pd.read_excel(DATASET)
    df.columns = [c.strip() for c in df.columns]
    df["Article"] = df["Article"].ffill()
    return df


def load_embedding_bank(path):
    d = np.load(path, allow_pickle=True)
    return {nid: vec for nid, vec in zip(list(d["node_ids"]),
                                          list(d["embeddings"]))}


def build_feature_matrix(df, bank=None):
    """One-hot categorical + (optionally) averaged embeddings per row."""
    # One-hot for the six categorical columns
    onehots = []
    for _, col in CATEGORICAL_COLUMNS.items():
        oh = pd.get_dummies(df[col].fillna("__missing__"), prefix=col)
        onehots.append(oh)
    X_cat = pd.concat(onehots, axis=1).values.astype(np.float32)

    if bank is None:
        return X_cat

    # Average embeddings for each row across its categorical neighbours
    dim = next(iter(bank.values())).shape[0]
    X_emb = np.zeros((len(df), dim), dtype=np.float32)
    for i, (_, row) in enumerate(df.iterrows()):
        vecs = []
        for ntype, col in CATEGORICAL_COLUMNS.items():
            v = row.get(col)
            if isinstance(v, str):
                key = f"{ntype}:{v}"
                if key in bank:
                    vecs.append(bank[key])
        if vecs:
            X_emb[i] = np.mean(vecs, axis=0)
    return np.hstack([X_cat, X_emb])


def run_for_target(df_full, target_short, target_raw, target_trans):
    """Returns dict of results for one mechanical-property target."""
    from sklearn.model_selection import KFold
    from sklearn.linear_model import Ridge
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.metrics import r2_score, mean_absolute_error

    target_col = target_trans if target_trans in df_full.columns else target_raw
    df = df_full.dropna(subset=[target_col]).reset_index(drop=True)
    y = pd.to_numeric(df[target_col], errors="coerce")
    df = df.loc[y.notna()].reset_index(drop=True)
    y = y[y.notna()].values
    print(f"\n  [{target_short}] usable rows: {len(df)}")

    results = {}
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    X_base = build_feature_matrix(df, bank=None)

    def cv_eval(X, regressor="ridge"):
        r2s, maes = [], []
        for tr, te in kf.split(X):
            if regressor == "ridge":
                m = Ridge(alpha=0.01).fit(X[tr], y[tr])
            else:  # gradient boosting
                m = GradientBoostingRegressor(
                    n_estimators=200, max_depth=4, learning_rate=0.05,
                    random_state=42).fit(X[tr], y[tr])
            p = m.predict(X[te])
            r2s.append(r2_score(y[te], p))
            maes.append(mean_absolute_error(y[te], p))
        return float(np.mean(r2s)), float(np.std(r2s)), float(np.mean(maes))

    for regressor in ["ridge", "gbm"]:
        r2, r2_std, mae = cv_eval(X_base, regressor=regressor)
        results[f"{regressor}_baseline"] = {"feat_dim": X_base.shape[1], "n": len(y),
                                            "R2": r2, "R2_std": r2_std, "MAE": mae}
        print(f"    {regressor:5s} baseline   R²={r2:.3f} ± {r2_std:.3f}, MAE={mae:.3f}")

        for key, path in EMBEDDING_PATHS.items():
            if not os.path.exists(path):
                continue
            bank = load_embedding_bank(path)
            X_aug = build_feature_matrix(df, bank=bank)
            r2, r2_std, mae = cv_eval(X_aug, regressor=regressor)
            results[f"{regressor}_+{key}"] = {"feat_dim": X_aug.shape[1], "n": len(y),
                                              "R2": r2, "R2_std": r2_std, "MAE": mae}
            print(f"    {regressor:5s} +{key:13s} R²={r2:.3f} ± {r2_std:.3f}, MAE={mae:.3f}")
    return results


def main():
    os.makedirs(OUT, exist_ok=True)
    print("Loading dataset...")
    df = load_dataset()

    all_results = {}
    for short, raw, trans in TARGETS:
        print(f"\n=== TARGET: {short} ({trans}) ===")
        all_results[short] = run_for_target(df, short, raw, trans)

    # ---- Write report ----
    with open(f"{OUT}/predictive_validation.txt", "w") as f:
        f.write("=" * 78 + "\n")
        f.write("PREDICTIVE VALIDATION OF EMBEDDINGS — Suggestion 4 (multi-target)\n")
        f.write("=" * 78 + "\n\n")
        f.write(f"Targets evaluated: modulus improvement (ΔE), strength improvement (Δσ),\n")
        f.write(f"                   strain-to-failure improvement (Δε), all in arcsinh space\n")
        f.write(f"Validation       : 5-fold cross-validation\n")
        f.write(f"Regressors       : Ridge (α=0.01) and Gradient Boosting (200 trees, depth 4)\n")
        f.write(f"Features         : one-hot encoding of {len(CATEGORICAL_COLUMNS)} categorical columns\n")
        f.write(f"                   ± row-averaged embeddings of the corresponding concept nodes\n\n")

        for short, _, _ in TARGETS:
            r_d = all_results[short]
            n = next(iter(r_d.values()))["n"]
            f.write(f"\n--- Target: {short.upper()} improvement (n = {n}) ---\n\n")
            f.write(f"{'model':24s} | {'feat_dim':>9s} | {'R²':>10s} | {'R² std':>8s} | {'MAE':>10s}\n")
            f.write("-" * 70 + "\n")
            for k, r in r_d.items():
                f.write(f"{k:24s} | {r['feat_dim']:>9d} | "
                        f"{r['R2']:>10.4f} | {r['R2_std']:>8.4f} | {r['MAE']:>10.4f}\n")

            f.write("\nEmbedding-attributable R² gain:\n")
            for regressor in ["ridge", "gbm"]:
                base_r2 = r_d[f"{regressor}_baseline"]["R2"]
                f.write(f"  {regressor.upper()} baseline R² = {base_r2:.4f}\n")
                for k, r in r_d.items():
                    if not k.startswith(f"{regressor}_+"):
                        continue
                    delta = r["R2"] - base_r2
                    sig = " improves" if delta > 0 else " degrades"
                    f.write(f"    {k:24s}: ΔR² = {delta:+.4f}{sig}\n")

    print(f"\nReport written to {OUT}/predictive_validation.txt")

    # ---- Plot: GBM panel for each target ----
    try:
        n_targets = len(TARGETS)
        fig, ax = plt.subplots(1, n_targets, figsize=(5 * n_targets, 5),
                               facecolor="#ffffff", sharey=True)
        if n_targets == 1:
            ax = [ax]
        for col, (short, _, _) in enumerate(TARGETS):
            r_d = all_results[short]
            ks = [k for k in r_d if k.startswith("gbm_")]
            r2s = [r_d[k]["R2"] for k in ks]
            r2_stds = [r_d[k]["R2_std"] for k in ks]
            labels = [k.replace("gbm_", "") for k in ks]
            x = np.arange(len(ks))
            colors = ["#888888"] + ["#3498db", "#27ae60", "#e74c3c", "#f39c12", "#9b59b6"][:len(ks) - 1]
            ax[col].bar(x, r2s, yerr=r2_stds, color=colors, capsize=4)
            base = r_d["gbm_baseline"]["R2"]
            ax[col].axhline(base, color="black", linestyle="--", alpha=0.5,
                            label=f"baseline = {base:.3f}")
            ax[col].set_xticks(x)
            ax[col].set_xticklabels(labels, rotation=25, ha="right", fontsize=8)
            ax[col].set_ylabel("R²" if col == 0 else "")
            ax[col].set_title(f"Δ{short}  (n = {next(iter(r_d.values()))['n']})")
            ax[col].grid(axis="y", alpha=0.3)
            ax[col].legend(fontsize=8)
        plt.suptitle("Predictive Validation Across All Three Mechanical Targets (GBM, 5-fold CV)")
        plt.tight_layout()
        plt.savefig(f"{OUT}/predictive_validation.png", dpi=150, facecolor="#ffffff")
        plt.close()
        print(f"Plot written to {OUT}/predictive_validation.png")
    except Exception as e:
        print(f"Plot failed: {e}")


if __name__ == "__main__":
    main()
