"""
Phase 3 — Quantitative embedding evaluation (Advisor Suggestions 1 + 3).

Compares the four embedding models against three quantitative criteria:

  A. Polymer-family clustering quality (Suggestion 3)
       Silhouette score
       Adjusted Rand Index (ARI) vs. ground-truth polymer-family labels
       Normalized Mutual Information (NMI) vs. ground-truth labels

  B. Graph-distance vs. embedding-distance agreement (Suggestion 3)
       Spearman correlation between (1 - cosine) and shortest-path length

  C. Description-enrichment effect (Suggestion 1)
       Cosine similarity within the polyamide family BEFORE vs AFTER enrichment
       (original embeddings.npz vs embeddings_enriched.npz / minilm)

Outputs:
  output/quantitative_evaluation.txt
  output/multi_model_comparison.png
"""
import os
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

GRAPH_GEXF = "output/complete_graph.gexf"
OUT = "output"

MODELS = {
    "minilm-orig":   "output/embeddings.npz",            # before enrichment
    "minilm":        "output/embeddings_minilm.npz",     # after enrichment
    "scibert":       "output/embeddings_scibert.npz",
    "matscibert":    "output/embeddings_matscibert.npz",
    "materialsbert": "output/embeddings_materialsbert.npz",
    "matbert":       "output/embeddings_matbert.npz",
}

# Ground-truth polymer-family groupings for ARI / NMI
POLYMER_FAMILIES = {
    "polyamide":   ["PA", "PA6", "PA7", "PA8", "PA12", "PA66",
                    "Nylon 6", "Nylon 66", "Nylon 7", "Nylon 8", "BIOPA11"],
    "polyolefin":  ["PP", "HDPE", "LLDPE", "PE", "PP/EPDM", "PP/PC",
                    "PP/PLA", "PPH1", "PPH2", "PPH3", "PPH4",
                    "PPH1/PP", "PPH2/PP", "PPH3/PP", "PPH4/PP", "PA6/PP"],
    "thermoset":   ["Epoxy", "DGEBA", "UP", "Vinyl Ester", "DGEAC",
                    "EPON 828", "MGSL135i", "Bis-GMA/TTEGDMA",
                    "Dimethacrylate Copolymer"],
    "acrylic":     ["PMMA", "PMA", "PVA", "PVC", "PVP"],
    "biopolymer":  ["PLA", "PLLA", "PLA/PBAT", "PLA/PP", "PCL", "PHBV",
                    "Chitosan", "PBT", "rPET"],
    "elastomer":   ["NR", "NBR", "CNBR", "NBR/PU", "PU"],
    "glassy":      ["PS", "PSF", "PI"],
}


# ---- Loaders ----------------------------------------------------------------

def load_embeddings(path):
    d = np.load(path, allow_pickle=True)
    return d["embeddings"], list(d["node_ids"])


def polymer_label_map():
    """polymer node id → family name. Used as ground-truth for ARI/NMI."""
    out = {}
    for fam, members in POLYMER_FAMILIES.items():
        for m in members:
            out[f"polymer:{m}"] = fam
    return out


# ---- Metrics ----------------------------------------------------------------

def evaluate_polymer_family_clustering(emb, node_ids):
    """Silhouette, ARI, NMI for polymer nodes against ground-truth families."""
    from sklearn.metrics import (silhouette_score, adjusted_rand_score,
                                 normalized_mutual_info_score)
    from sklearn.cluster import KMeans

    label_map = polymer_label_map()
    polymer_idx = [i for i, n in enumerate(node_ids) if n in label_map]
    if len(polymer_idx) < 6:
        return {"silhouette": np.nan, "ARI": np.nan, "NMI": np.nan,
                "n_polymers": len(polymer_idx)}

    sub_emb = emb[polymer_idx]
    truth = [label_map[node_ids[i]] for i in polymer_idx]
    # Encode truth labels as integers
    fam_to_int = {f: k for k, f in enumerate(sorted(set(truth)))}
    truth_int = np.array([fam_to_int[t] for t in truth])

    # Silhouette using ground-truth labels in cosine space
    # (sklearn silhouette wants a distance metric, so use precomputed)
    cos = sub_emb @ sub_emb.T
    cos = np.clip(cos, -1, 1)
    dist = 1.0 - cos
    np.fill_diagonal(dist, 0)
    try:
        sil = silhouette_score(dist, truth_int, metric="precomputed")
    except Exception:
        sil = np.nan

    # Cluster with KMeans (k = number of families) and compare to truth
    k = len(fam_to_int)
    km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(sub_emb)
    pred = km.labels_
    ari = adjusted_rand_score(truth_int, pred)
    nmi = normalized_mutual_info_score(truth_int, pred)

    return {"silhouette": float(sil), "ARI": float(ari), "NMI": float(nmi),
            "n_polymers": len(polymer_idx), "n_families": k}


def evaluate_graph_distance_correlation(emb, node_ids, G, sample_size=200):
    """Spearman correlation between (1 - cosine) and graph shortest-path length."""
    from scipy.stats import spearmanr

    # Restrict to non-article concept nodes (smaller, cleaner sub-graph)
    keep = [n for n in node_ids
            if n in G and G.nodes[n].get("node_type") not in ("article",)]
    idx = [node_ids.index(n) for n in keep]
    if len(keep) < 20:
        return {"spearman": np.nan, "n_pairs": 0}
    sub_emb = emb[idx]
    cos = sub_emb @ sub_emb.T
    cos = np.clip(cos, -1, 1)

    # Sample random pairs and compute graph SP length
    rng = np.random.RandomState(42)
    cos_vals, sp_vals = [], []
    pairs_done = set()
    attempts = 0
    while len(cos_vals) < sample_size and attempts < sample_size * 10:
        i, j = rng.choice(len(keep), 2, replace=False)
        if (i, j) in pairs_done or (j, i) in pairs_done:
            attempts += 1
            continue
        pairs_done.add((i, j))
        try:
            sp = nx.shortest_path_length(G, keep[i], keep[j])
        except nx.NetworkXNoPath:
            attempts += 1
            continue
        cos_vals.append(1 - cos[i, j])
        sp_vals.append(sp)
        attempts += 1

    if len(cos_vals) < 10:
        return {"spearman": np.nan, "n_pairs": len(cos_vals)}
    rho, p = spearmanr(cos_vals, sp_vals)
    return {"spearman": float(rho), "p_value": float(p),
            "n_pairs": len(cos_vals)}


def evaluate_intra_family_cohesion(emb, node_ids):
    """Mean intra-family cosine vs mean inter-family cosine."""
    label_map = polymer_label_map()
    polymer_idx = [i for i, n in enumerate(node_ids) if n in label_map]
    if not polymer_idx:
        return {"intra": np.nan, "inter": np.nan, "gap": np.nan}
    sub_emb = emb[polymer_idx]
    sub_ids = [node_ids[i] for i in polymer_idx]
    fams = [label_map[n] for n in sub_ids]
    cos = sub_emb @ sub_emb.T
    intra, inter = [], []
    for i in range(len(sub_ids)):
        for j in range(i + 1, len(sub_ids)):
            (intra if fams[i] == fams[j] else inter).append(cos[i, j])
    return {
        "intra": float(np.mean(intra)) if intra else np.nan,
        "inter": float(np.mean(inter)) if inter else np.nan,
        "gap":   float(np.mean(intra) - np.mean(inter)) if intra and inter else np.nan,
        "n_intra_pairs": len(intra),
        "n_inter_pairs": len(inter),
    }


# ---- Main -------------------------------------------------------------------

def main():
    os.makedirs(OUT, exist_ok=True)
    print("Loading complete graph...")
    G = nx.read_gexf(GRAPH_GEXF)

    print("\nEvaluating each model...")
    results = {}
    for key, path in MODELS.items():
        if not os.path.exists(path):
            print(f"  [{key}] missing — skipping")
            continue
        emb, node_ids = load_embeddings(path)
        print(f"  [{key}] {emb.shape}")
        clust = evaluate_polymer_family_clustering(emb, node_ids)
        cohes = evaluate_intra_family_cohesion(emb, node_ids)
        gcorr = evaluate_graph_distance_correlation(emb, node_ids, G)
        results[key] = {**clust, **{f"cohes_{k}": v for k, v in cohes.items()},
                        **{f"graph_{k}": v for k, v in gcorr.items()}}

    # ---- Write report ----
    with open(f"{OUT}/quantitative_evaluation.txt", "w") as f:
        f.write("=" * 78 + "\n")
        f.write("QUANTITATIVE EMBEDDING EVALUATION — Suggestions 1 & 3\n")
        f.write("=" * 78 + "\n\n")

        f.write("Models compared (cells: model row × metric column):\n\n")
        cols = ["silhouette", "ARI", "NMI",
                "cohes_intra", "cohes_inter", "cohes_gap",
                "graph_spearman", "graph_p_value", "graph_n_pairs"]
        header = "model            | " + " | ".join(f"{c:>13s}" for c in cols)
        f.write(header + "\n")
        f.write("-" * len(header) + "\n")
        for key, r in results.items():
            row = f"{key:16s} | " + " | ".join(
                f"{(r.get(c) if r.get(c) is not None else float('nan')):>13.3f}"
                for c in cols
            )
            f.write(row + "\n")

        f.write("\n\nMetric definitions\n")
        f.write("------------------\n")
        f.write("silhouette    : silhouette coefficient on polymer nodes vs. ground-truth families (higher = better separation; range -1..+1)\n")
        f.write("ARI           : Adjusted Rand Index between K-means clustering and true family labels (1 = perfect, 0 = random)\n")
        f.write("NMI           : Normalized Mutual Information between K-means clustering and true labels (1 = identical)\n")
        f.write("cohes_intra   : mean cosine similarity for polymer pairs WITHIN the same family\n")
        f.write("cohes_inter   : mean cosine similarity for polymer pairs ACROSS families\n")
        f.write("cohes_gap     : cohes_intra - cohes_inter (positive = embeddings discriminate families)\n")
        f.write("graph_spearman: Spearman correlation between (1 - cosine) and graph shortest-path length\n")
        f.write("graph_p_value : p-value of the Spearman correlation\n")
        f.write("graph_n_pairs : number of sampled concept pairs used in the correlation\n")

        f.write("\n\nGround-truth polymer-family groupings used\n")
        f.write("------------------------------------------\n")
        for fam, members in POLYMER_FAMILIES.items():
            f.write(f"  {fam:12s}: {', '.join(members)}\n")

    print(f"\nReport written to {OUT}/quantitative_evaluation.txt")

    # ---- Plot ----
    try:
        keys = list(results.keys())
        ari = [results[k]["ARI"] for k in keys]
        nmi = [results[k]["NMI"] for k in keys]
        sil = [results[k]["silhouette"] for k in keys]
        gap = [results[k]["cohes_gap"] for k in keys]

        fig, ax = plt.subplots(2, 2, figsize=(12, 8), facecolor="#ffffff")
        x = np.arange(len(keys))
        colors = ["#888888", "#3498db", "#27ae60", "#e74c3c", "#f39c12"][:len(keys)]

        ax[0, 0].bar(x, ari, color=colors); ax[0, 0].set_title("ARI vs. polymer family")
        ax[0, 1].bar(x, nmi, color=colors); ax[0, 1].set_title("NMI vs. polymer family")
        ax[1, 0].bar(x, sil, color=colors); ax[1, 0].set_title("Silhouette score")
        ax[1, 1].bar(x, gap, color=colors); ax[1, 1].set_title("Intra-family cohesion gap")
        for a in ax.flat:
            a.set_xticks(x); a.set_xticklabels(keys, rotation=20, ha="right")
            a.axhline(0, color="black", linewidth=0.5)
            a.grid(axis="y", alpha=0.3)
        plt.suptitle("Multi-Model Embedding Evaluation (Suggestions 1 & 3)")
        plt.tight_layout()
        plt.savefig(f"{OUT}/multi_model_comparison.png", dpi=150,
                    facecolor="#ffffff")
        plt.close()
        print(f"Plot written to {OUT}/multi_model_comparison.png")
    except Exception as e:
        print(f"Plot failed: {e}")


if __name__ == "__main__":
    main()
