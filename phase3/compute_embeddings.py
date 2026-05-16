"""
Phase 3 — Adım 3: Buehler-style node embeddings.

Her kavram düğümü için Buehler-tarzı kendinden açıklamalı bir metin
oluşturup, sentence-transformers (all-MiniLM-L6-v2) ile 384 boyutlu
bir vektöre dönüştürür. Sonra:

  - Cosine similarity matrisi (245 × 245)
  - Her düğüm için top-5 anlamsal komşu (article'lar hariç)
  - 2D UMAP projeksiyon (Phase 1/UBMK renk paletinde)
  - 'Disparate concept' yol örnekleri — Buehler signature analiz

Çıktılar:
  output/node_descriptions.txt
  output/embeddings.npz
  output/top_similar.txt
  output/embedding_2d.png
  output/path_examples.txt
"""
import os
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

GRAPH_GEXF = "output/global_graph.gexf"
OUT = "output"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def _fmt(v, unit="", dec=2):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    return f"{v:.{dec}f}{unit}"


def describe_node(G, n, d):
    """Buehler-style text description for a concept node."""
    ntype = d["node_type"]
    label = d["label"]
    n_rows = int(d.get("n_rows", 0)) if not (isinstance(d.get("n_rows"), float)
                                             and np.isnan(d.get("n_rows"))) else 0
    parts = []
    if ntype == "polymer":
        parts.append(f"{label} is a polymer matrix used in {n_rows} "
                     "montmorillonite clay nanocomposite experiments.")
    elif ntype == "modification":
        parts.append(f"{label} montmorillonite clay state, used in {n_rows} experiments.")
    elif ntype == "dispersion":
        parts.append(f"{label} dispersion morphology of clay in polymer, "
                     f"observed in {n_rows} experiments.")
    elif ntype == "category":
        parts.append(f"{label} polymer family, used in {n_rows} experiments.")
    elif ntype == "test_method":
        parts.append(f"{label} mechanical test method, applied in {n_rows} experiments.")
    elif ntype == "data_source":
        parts.append(f"{label} data source ({n_rows} entries).")
    elif ntype == "article":
        snippet = label[:120].replace("\n", " ")
        parts.append(f"Research article: {snippet}. Contains {n_rows} experiments.")
    else:
        parts.append(f"{label} ({ntype}, {n_rows} experiments).")

    e  = _fmt(d.get("mean_matrix_modulus"),  " GPa")
    s  = _fmt(d.get("mean_matrix_strength"), " MPa")
    st = _fmt(d.get("mean_matrix_strain"))
    bits = []
    if e:  bits.append(f"average elastic modulus {e}")
    if s:  bits.append(f"strength {s}")
    if st: bits.append(f"strain to failure {st}")
    if bits:
        parts.append("Associated polymer matrices have " + ", ".join(bits) + ".")

    # Raw mean (interpretable but outlier-sensitive)
    de  = _fmt(d.get("mean_dE_modulus"),      "%", 1)
    ds  = _fmt(d.get("mean_dsigma_strength"), "%", 1)
    dst = _fmt(d.get("mean_de_strain"),       "%", 1)
    imp = []
    if de:  imp.append(f"modulus improvement {de}")
    if ds:  imp.append(f"strength improvement {ds}")
    if dst: imp.append(f"strain-to-failure change {dst}")
    if imp:
        parts.append("With clay reinforcement, average " + ", ".join(imp) + ".")

    # Arcsinh-space mean (outlier-robust) — appended so embedding sees both signals
    de_a  = _fmt(d.get("mean_dE_modulus_arcsinh"),      "", 2)
    ds_a  = _fmt(d.get("mean_dsigma_strength_arcsinh"), "", 2)
    dst_a = _fmt(d.get("mean_de_strain_arcsinh"),       "", 2)
    imp_a = []
    if de_a:  imp_a.append(f"arcsinh modulus improvement {de_a}")
    if ds_a:  imp_a.append(f"arcsinh strength improvement {ds_a}")
    if dst_a: imp_a.append(f"arcsinh strain change {dst_a}")
    if imp_a:
        parts.append("In outlier-robust arcsinh space: " + ", ".join(imp_a) + ".")

    mmt = _fmt(d.get("mean_MMT_pct"), " wt%", 1)
    if mmt:
        parts.append(f"Typical MMT loading {mmt}.")
    return " ".join(parts)


def main():
    os.makedirs(OUT, exist_ok=True)

    print("Loading graph...")
    G = nx.read_gexf(GRAPH_GEXF)
    nodes = list(G.nodes)
    print(f"Total concept nodes: {len(nodes)}")

    descriptions = []
    with open(f"{OUT}/node_descriptions.txt", "w") as f:
        for n in nodes:
            txt = describe_node(G, n, G.nodes[n])
            descriptions.append(txt)
            f.write(f"[{n}]\n{txt}\n\n")

    print(f"Loading model: {MODEL_NAME}")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL_NAME)

    print(f"Encoding {len(descriptions)} node descriptions...")
    emb = model.encode(descriptions, show_progress_bar=False,
                       normalize_embeddings=True)
    print(f"Embeddings shape: {emb.shape}")

    np.savez(f"{OUT}/embeddings.npz",
             embeddings=emb,
             node_ids=np.array(nodes),
             descriptions=np.array(descriptions))

    # ---- Cosine similarity ----
    sim = emb @ emb.T
    np.fill_diagonal(sim, -np.inf)
    types = {n: G.nodes[n]["node_type"] for n in nodes}

    # Concept-only candidate mask (exclude articles from neighbor candidates)
    is_article_arr = np.array([types[n] == "article" for n in nodes])

    with open(f"{OUT}/top_similar.txt", "w") as f:
        f.write("=== Top-5 cosine-similar CONCEPTS per node "
                "(articles excluded from candidates) ===\n\n")
        by_type = {}
        for i, n in enumerate(nodes):
            by_type.setdefault(types[n], []).append((i, n))
        for ntype, items in by_type.items():
            if ntype == "article":
                continue
            f.write(f"\n--- {ntype.upper()} ---\n")
            for i, n in items:
                # Mask out articles from neighbor candidates
                row = sim[i].copy()
                row[is_article_arr] = -np.inf
                top5 = np.argsort(-row)[:5]
                f.write(f"\n{G.nodes[n]['label']}  ({ntype})\n")
                for j in top5:
                    f.write(f"   {row[j]:.3f}  "
                            f"{G.nodes[nodes[j]]['label'][:40]:40s} "
                            f"({types[nodes[j]]})\n")

    # ---- 2D UMAP — concept-only (articles excluded) for clarity ----
    print("UMAP projecting to 2-D (concept-only, articles excluded)...")
    import umap
    concept_idx = np.array([i for i, n in enumerate(nodes)
                            if types[n] != "article"])
    concept_emb = emb[concept_idx]
    concept_nodes = [nodes[i] for i in concept_idx]
    concept_types = {n: types[n] for n in concept_nodes}

    reducer = umap.UMAP(n_neighbors=15, min_dist=0.6, spread=1.5,
                        metric="cosine", random_state=42)
    xy = reducer.fit_transform(concept_emb)

    # Phase1/UBMK palette (articles dropped)
    type_colors = {
        "polymer":      "#3498db",
        "modification": "#27ae60",
        "dispersion":   "#f39c12",
        "category":     "#9b59b6",
        "test_method":  "#16a085",
        "data_source":  "#d35400",
    }

    plt.figure(figsize=(12, 9), facecolor="#ffffff")
    ax = plt.gca()
    ax.set_facecolor("#ffffff")
    for ntype, color in type_colors.items():
        mask = np.array([concept_types[n] == ntype for n in concept_nodes])
        if not mask.any():
            continue
        ax.scatter(xy[mask, 0], xy[mask, 1], c=color, label=ntype,
                   s=80, alpha=0.85,
                   edgecolors="black", linewidths=0.7)

    for i, n in enumerate(concept_nodes):
        ax.annotate(G.nodes[n]["label"][:14],
                    (xy[i, 0], xy[i, 1]),
                    fontsize=8, alpha=0.95)

    ax.legend(loc="best", fontsize=10)
    ax.set_title("Phase 3 — UMAP 2-D Embedding Space (concept-only)\n"
                 "Articles excluded; n_neighbors=15, min_dist=0.6, spread=1.5")
    ax.set_xlabel("UMAP-1")
    ax.set_ylabel("UMAP-2")
    plt.tight_layout()
    plt.savefig(f"{OUT}/embedding_2d.png", dpi=150, facecolor="#ffffff")
    plt.close()

    # ---- Path examples ----
    path_pairs = [
        ("polymer:PA6",          "polymer:Epoxy"),
        ("modification:Modified", "modification:Unmodified"),
        ("dispersion:exfoliated", "dispersion:agglomerated"),
        ("category:Elastomer",    "category:Thermoset"),
        ("polymer:PA6",          "category:Elastomer"),
    ]
    nid_to_idx = {n: i for i, n in enumerate(nodes)}
    with open(f"{OUT}/path_examples.txt", "w") as f:
        f.write("=== Buehler-style path examples ===\n")
        f.write("Graph shortest path AND cosine similarity score per pair.\n\n")
        for src, dst in path_pairs:
            if src not in G or dst not in G:
                f.write(f"Skipped: {src} or {dst} not in graph.\n\n")
                continue
            f.write(f"\n--- {G.nodes[src]['label']}  →  {G.nodes[dst]['label']} ---\n")
            try:
                path = nx.shortest_path(G, src, dst)
                f.write(f"Graph shortest path ({len(path)-1} hops):\n")
                for p in path:
                    f.write(f"   {G.nodes[p]['node_type']:13s} : "
                            f"{G.nodes[p]['label'][:60]}\n")
            except nx.NetworkXNoPath:
                f.write("  (no graph path)\n")
            if src in nid_to_idx and dst in nid_to_idx:
                cos = float(emb[nid_to_idx[src]] @ emb[nid_to_idx[dst]])
                f.write(f"Embedding cosine similarity: {cos:.3f}\n")

    print(f"\nOutputs in {OUT}/")
    for fn in sorted(os.listdir(OUT)):
        print(f"  {fn}")


if __name__ == "__main__":
    main()
