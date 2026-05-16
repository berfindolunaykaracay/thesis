"""
Phase 3 — Step 4: Semantic similarity graph (Buehler signature output).

Uses the embeddings produced in Step 3 to build a second HTML graph whose
edges represent semantic similarity between concepts.

Difference:
  - Step 2 (global_graph.html)  : edge = "co-occurred in same experiment"
  - Step 4 (semantic_graph.html): edge = "textual descriptions are semantically similar"

Semantic edge rule:
  - Article nodes are excluded (too noisy)
  - For each node, top-K nearest concepts kept (top_k = 5)
  - Edge between two nodes is symmetrized (union)

Edge visualization:
  - width  ∝ cosine similarity (higher = thicker)
  - length ∝ 1 − cosine        (closer in meaning = shorter)

Style = Phase 1 / UBMK2026.

Outputs:
  output/semantic_graph.html
  output/semantic_graph.gexf
"""
import os
import numpy as np
import networkx as nx

OUT = "output"
TOP_K = 5
EXCLUDE_TYPES = {"article"}   # filter out citation noise


def main():
    print("Loading embeddings + concept graph...")
    G_full = nx.read_gexf(f"{OUT}/global_graph.gexf")
    data = np.load(f"{OUT}/embeddings.npz", allow_pickle=True)
    emb = data["embeddings"]
    node_ids = list(data["node_ids"])

    # Filter to non-article nodes for the semantic view
    keep_mask = np.array([G_full.nodes[n]["node_type"] not in EXCLUDE_TYPES
                          for n in node_ids])
    kept_emb = emb[keep_mask]
    kept_ids = [n for i, n in enumerate(node_ids) if keep_mask[i]]
    print(f"Filtered: {len(kept_ids)} nodes (articles excluded)")

    sim = kept_emb @ kept_emb.T
    np.fill_diagonal(sim, -np.inf)

    # Build semantic edges: top-K per node, take union (undirected)
    edges = {}
    for i, ni in enumerate(kept_ids):
        top_k_idx = np.argsort(-sim[i])[:TOP_K]
        for j in top_k_idx:
            if i == j:
                continue
            a, b = (ni, kept_ids[j]) if ni < kept_ids[j] else (kept_ids[j], ni)
            cos = float(sim[i, j])
            # take max if both directions agree (already symmetric for normalized)
            if (a, b) not in edges or cos > edges[(a, b)]:
                edges[(a, b)] = cos

    # Build NetworkX graph
    G = nx.Graph()
    for n in kept_ids:
        d = dict(G_full.nodes[n])
        G.add_node(n, **d)
    for (a, b), cos in edges.items():
        G.add_edge(a, b, cosine=cos)

    print(f"Semantic graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    # GEXF
    nx.write_gexf(G, f"{OUT}/semantic_graph.gexf")

    # ---- HTML viz ----
    from pyvis.network import Network
    net = Network(height="900px", width="100%", bgcolor="#ffffff",
                  font_color="black", notebook=False)
    net.set_options("""
    var options = {
      "configure": {"enabled": true, "filter": ["physics"]},
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -28000,
          "centralGravity": 0.04,
          "springLength": 200,
          "springConstant": 0.0018,
          "damping": 0.5,
          "avoidOverlap": 0.9
        },
        "stabilization": {"iterations": 2000}
      }
    }
    """)

    type_colors = {
        "polymer":      "#3498db",
        "modification": {"Modified": "#27ae60", "Unmodified": "#e74c3c"},
        "dispersion":   "#f39c12",
        "category":     "#9b59b6",
        "test_method":  "#16a085",
        "data_source":  "#d35400",
    }

    def _fmt(v, unit="", dec=2):
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return "—"
        return f"{v:.{dec}f}{unit}"

    for n, d in G.nodes(data=True):
        ntype = d["node_type"]
        label = d["label"]
        deg = G.degree(n)
        if ntype == "modification":
            color = type_colors["modification"].get(label, "#7f8c8d")
        else:
            color = type_colors.get(ntype, "#7f8c8d")
        size = max(22, min(55, 22 + np.log10(max(1, deg)) * 6))
        title = (
            f"{ntype.upper()}: {label}\n"
            f"  experiments: {d.get('n_rows', 0)}\n"
            f"  semantic neighbors: {deg}\n"
            f"  --- avg property (raw) ---\n"
            f"  E   = {_fmt(d.get('mean_matrix_modulus'),  ' GPa')}\n"
            f"  σ   = {_fmt(d.get('mean_matrix_strength'), ' MPa')}\n"
            f"  ΔE  = {_fmt(d.get('mean_dE_modulus'),      '%', 1)}\n"
            f"  Δσ  = {_fmt(d.get('mean_dsigma_strength'), '%', 1)}\n"
            f"  Δε  = {_fmt(d.get('mean_de_strain'),       '%', 1)}\n"
        )
        net.add_node(n, label=label, color=color, size=size, title=title)

    # Edges: width by cosine, length by (1 - cosine) → similar pairs draw closer
    for u, v, d in G.edges(data=True):
        cos = d["cosine"]
        width  = max(0.5, (cos - 0.4) * 8)     # only show contrast in 0.4..1.0
        length = max(30, 400 * (1 - cos))
        title = (f"{G.nodes[u]['label'][:25]}  ⟷  {G.nodes[v]['label'][:25]}\n"
                 f"  cosine similarity: {cos:.3f}")
        net.add_edge(u, v, color="#9ec5e8", width=width, length=length, title=title)

    filename = f"{OUT}/semantic_graph.html"
    net.save_graph(filename)

    header = f"""
    <div style="padding: 20px; background-color: #f8f9fa; margin: 10px;
                border-radius: 5px; border: 2px solid #2c3e50;">
        <h2 style="color: #2c3e50;">Phase 3 — Semantic Similarity Graph</h2>
        <p>Built from transformer-based node embeddings. Edges represent semantic
        similarity (not "same experiment"). Article nodes excluded for clarity.</p>
        <p><strong>Nodes:</strong> {G.number_of_nodes()}
           | <strong>Edges:</strong> {G.number_of_edges()}
           (top-{TOP_K} neighbors per node, unioned)</p>
        <p><strong>Legend:</strong>
           &#x1F535; Polymer |
           &#x1F7E2; Modified |
           &#x1F534; Unmodified |
           &#x1F7E0; Dispersion |
           &#x1F7E3; Category |
           <span style="color:#16a085;">&#9679;</span> Test Method |
           <span style="color:#d35400;">&#9679;</span> Exp/Sim</p>
        <p><strong>Edge width</strong> ∝ cosine similarity (thicker = more similar).
           <strong>Edge length</strong> ∝ (1 − cosine) (closer = semantically closer).
           <strong>Node size</strong> = log-scaled semantic neighbor count.</p>
    </div>
    """
    with open(filename, "r") as f:
        html = f.read()
    html = html.replace("<center>\n<h1></h1>\n</center>",
                        f"<center>\n{header}\n</center>")
    with open(filename, "w") as f:
        f.write(html)

    print(f"\nWrote: {filename}")
    print(f"Wrote: {OUT}/semantic_graph.gexf")


if __name__ == "__main__":
    main()
