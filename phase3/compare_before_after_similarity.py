"""
Phase 3 — Side-by-side before/after similarity comparison
(Advisor Suggestion 1b: "açıklama ekleyince sonuçlar daha mantıklı hale
geldi mi diye göster" — direct top-K neighbour comparison BEFORE and AFTER
description enrichment).

For a curated set of focal concept nodes, prints the top-5 cosine
neighbours using each of the five embedding sets (the base-template
MiniLM, the enriched MiniLM, and the three domain-specific models),
so that the qualitative effect of enrichment AND model choice can be
read directly.
"""
import os
import numpy as np

OUT = "output"

EMBEDDINGS = {
    "MiniLM (no enrichment)":   "embeddings.npz",
    "MiniLM (enriched)":        "embeddings_minilm.npz",
    "SciBERT":                  "embeddings_scibert.npz",
    "MatSciBERT":               "embeddings_matscibert.npz",
    "MaterialsBERT":            "embeddings_materialsbert.npz",
    "MatBERT (LBNL)":           "embeddings_matbert.npz",
}

# Focal concepts for which to compare top-5 neighbours
FOCAL_NODES = [
    "polymer:PA6",
    "polymer:Epoxy",
    "polymer:PMA",
    "modification:Modified",
    "modification:Unmodified",
    "dispersion:exfoliated",
    "dispersion:agglomerated",
    "category:Thermoset",
    "category:Elastomer",
    "test_method:Tensile Test",
]


def load_emb(fname):
    path = os.path.join(OUT, fname)
    if not os.path.exists(path):
        return None
    d = np.load(path, allow_pickle=True)
    return d["embeddings"], list(d["node_ids"])


def top_k(emb, node_ids, query_id, k=5, exclude_types=None):
    """Top-k cosine neighbours of query_id excluding articles."""
    if query_id not in node_ids:
        return None
    i = node_ids.index(query_id)
    cos = emb @ emb[i]
    cos[i] = -np.inf  # exclude self
    # Exclude articles (noisy)
    for j, nid in enumerate(node_ids):
        if nid.startswith("article:"):
            cos[j] = -np.inf
    order = np.argsort(-cos)
    return [(node_ids[j].replace("polymer:", "").replace("dispersion:", "")
             .replace("modification:", "").replace("category:", "")
             .replace("test_method:", ""), float(cos[j]))
            for j in order[:k]]


def main():
    loaded = {label: load_emb(fname) for label, fname in EMBEDDINGS.items()}
    available = {l: r for l, r in loaded.items() if r is not None}

    print(f"Loaded {len(available)}/{len(EMBEDDINGS)} embedding sets:\n")
    for label in available:
        print(f"  {label}: shape {available[label][0].shape}")

    out_lines = []
    out_lines.append("=" * 90)
    out_lines.append("BEFORE / AFTER (and across models) TOP-5 NEIGHBOUR COMPARISON")
    out_lines.append("Direct answer to advisor Suggestion 1b:")
    out_lines.append('  "açıklama eklemeden önceki ve sonraki benzerlik sonuçlarını')
    out_lines.append('   yan yana koyup açıklama ekleyince sonuçlar daha mantıklı')
    out_lines.append('   hale geldi mi diye gösterebilirsin"')
    out_lines.append("=" * 90 + "\n")

    for node in FOCAL_NODES:
        label_clean = node.split(":", 1)[1]
        out_lines.append(f"\n{'═' * 90}")
        out_lines.append(f"  FOCAL CONCEPT: {label_clean}  ({node.split(':')[0]})")
        out_lines.append(f"{'═' * 90}")
        # Column header
        header = f"  {'rank':4s} | " + " | ".join(f"{model:30s}" for model in available)
        out_lines.append(header)
        out_lines.append("  " + "-" * (len(header) - 2))
        # For each model, get top-5
        results = {}
        for model, (emb, nids) in available.items():
            results[model] = top_k(emb, nids, node, k=5) or [("—", 0.0)] * 5
        for rank in range(5):
            row = f"  #{rank+1:<3d} | "
            cells = []
            for model in available:
                lbl, score = results[model][rank]
                lbl_short = lbl[:22]
                cells.append(f"{lbl_short:>22s} {score:5.3f}")
            out_lines.append(row + " | ".join(cells))

    out_path = os.path.join(OUT, "before_after_neighbours.txt")
    with open(out_path, "w") as f:
        f.write("\n".join(out_lines))
    print(f"\nReport written: {out_path}")


if __name__ == "__main__":
    main()
