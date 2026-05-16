"""
Phase 3 — Step 2: Buehler-style global concept graph.

A single global graph — all 942 rows combined (no modified/unmodified split,
no per-cluster split). Tabular-data analog of Buehler 2024 Section 2.1.

Nodes (categorical concepts):
  - polymer, modification, dispersion, category, article, test_method, data_source

Numerical data are NOT nodes — Buehler's "concepts as nodes" principle.
Numerical values are attached to each node/edge as attributes.

All numerical averages are computed in TWO spaces:
  - 'mean_X'         : raw arithmetic mean (interpretable but outlier-sensitive)
  - 'mean_X_arcsinh' : mean in arcsinh space (outlier-robust, handles negatives)

This is Buehler-style numerical encoding: no information loss, transformation logged.

Visual style = Phase 1 / UBMK2026:
  - white background, black font
  - blue polymer, green Modified / red Unmodified
  - physics control panel
  - info-box header
  - edge length ∝ 1/√(co-occurrence)

Outputs:
  output/graph_stats.txt           — Buehler Table 1 analog
  output/degree_distribution.png   — log-log + power-law fit
  output/community_breakdown.txt
  output/top_hubs.txt
  output/global_graph.gexf
  output/global_graph.html
"""
import os
from collections import defaultdict, Counter
from itertools import combinations

import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

DATASET = "../Dataset_LatestVersion.xlsx"
OUT = "output"

NODE_FIELDS = {
    "polymer":      "Polymer matrix name",
    "modification": "Modification (modified/unmodified)",
    "dispersion":   "Dispersion(microcomposite/exfoliated/intercalated/agglomerated)",
    "category":     "Thermoset? Thermoplastic? Elastomer?",
    "article":      "Article",
    "test_method":  "Test Method",
    "data_source":  "Experimental/Simulated",
}

# Raw column → (alias, arcsinh column) for averaging stats
NUMERIC_FIELDS = {
    "matrix_modulus":   ("Polymer matrix elastic modulus (GPa)",
                         "Polymer matrix elastic modulus arcsinh"),
    "matrix_strength":  ("Polymer matrix Strength (MPa)",
                         "Polymer matrix strength arcsinh"),
    "matrix_strain":    ("Polymer matrix strain to failure",
                         "Polymer matrix strain to failure arcsinh"),
    "dE_modulus":       ("Elastic Modulus improvement (%)",
                         "Elastic modulus improvement arcsinh"),
    "dsigma_strength":  ("Strength improvement (%)",
                         "Strength improvement arcsinh"),
    "de_strain":        ("Strain to failure improvement%",
                         "Strain to failure improvement arcsinh"),
}
MMT_COL = "MMT weight%"  # always positive, no transform needed


def load_dataset():
    df = pd.read_excel(DATASET)
    df.columns = [c.strip() for c in df.columns]
    df["Article"] = df["Article"].ffill()
    return df


def _row_stats(sub_df):
    out = {}
    for k, (raw, arcs) in NUMERIC_FIELDS.items():
        raw_vals = pd.to_numeric(sub_df[raw], errors="coerce").dropna()
        arc_vals = pd.to_numeric(sub_df[arcs], errors="coerce").dropna()
        out[f"mean_{k}"]         = float(raw_vals.mean()) if len(raw_vals) else None
        out[f"mean_{k}_arcsinh"] = float(arc_vals.mean()) if len(arc_vals) else None
        out[f"n_{k}"]            = int(len(raw_vals))
    mmt = pd.to_numeric(sub_df[MMT_COL], errors="coerce").dropna()
    out["mean_MMT_pct"] = float(mmt.mean()) if len(mmt) else None
    return out


def build_graph(df):
    G = nx.Graph()
    pair_rows = defaultdict(list)
    node_rows = defaultdict(list)

    for ntype, col in NODE_FIELDS.items():
        for val in df[col].dropna().unique():
            G.add_node(f"{ntype}:{val}", node_type=ntype, label=str(val))

    for idx, row in df.iterrows():
        present = []
        for ntype, col in NODE_FIELDS.items():
            v = row.get(col)
            if pd.notna(v):
                nid = f"{ntype}:{v}"
                present.append(nid)
                node_rows[nid].append(idx)
        for a, b in combinations(present, 2):
            key = (a, b) if a < b else (b, a)
            pair_rows[key].append(idx)

    for nid, rows in node_rows.items():
        stats = _row_stats(df.loc[rows])
        stats["n_rows"] = len(rows)
        for k, v in stats.items():
            G.nodes[nid][k] = v

    for (a, b), rows in pair_rows.items():
        attrs = _row_stats(df.loc[rows])
        attrs["weight"] = len(rows)
        attrs["n_rows"] = len(rows)
        G.add_edge(a, b, **attrs)

    return G


def graph_stats(G):
    degrees = [d for _, d in G.degree()]
    components = list(nx.connected_components(G))
    giant = max(components, key=len)
    Gg = G.subgraph(giant).copy()
    g_degrees = [d for _, d in Gg.degree()]

    try:
        from networkx.algorithms.community import greedy_modularity_communities
        comms = list(greedy_modularity_communities(G))
    except Exception:
        comms = []

    type_counts = Counter(d["node_type"] for _, d in G.nodes(data=True))
    stats = {
        "Number of nodes":      G.number_of_nodes(),
        "Number of edges":      G.number_of_edges(),
        "Average node degree":  round(np.mean(degrees), 3),
        "Maximum node degree":  max(degrees),
        "Minimum node degree":  min(degrees),
        "Median node degree":   int(np.median(degrees)),
        "Density":              round(nx.density(G), 6),
        "Number of communities": len(comms),
        "Components":           len(components),
        "Giant component nodes": Gg.number_of_nodes(),
        "Giant component edges": Gg.number_of_edges(),
        "Giant component avg degree": round(np.mean(g_degrees), 3),
    }
    stats.update({f"  {t} nodes": n for t, n in type_counts.items()})
    return stats, comms, Gg


def power_law_fit(degrees, fname):
    degs = [d for d in degrees if d > 0]
    counts = Counter(degs)
    xs = np.array(sorted(counts.keys()))
    ys = np.array([counts[x] for x in xs])

    xmin = max(2, int(np.quantile(degs, 0.50)))
    tail_mask = xs >= xmin
    if tail_mask.sum() >= 3:
        log_x = np.log10(xs[tail_mask])
        log_y = np.log10(ys[tail_mask])
        slope, intercept = np.polyfit(log_x, log_y, 1)
        alpha = -slope
    else:
        alpha = float("nan")

    plt.figure(figsize=(7, 5))
    plt.loglog(xs, ys, "bo", markersize=4, label="Data")
    if not np.isnan(alpha):
        x_fit = np.linspace(xmin, max(xs), 50)
        y_fit = (10**intercept) * x_fit**slope
        plt.loglog(x_fit, y_fit, "r--",
                   label=f"power-law α={alpha:.3f} (xmin={xmin})")
    plt.xlabel("degree k")
    plt.ylabel("count P(k)")
    plt.title("Phase 3 — Degree Distribution (Buehler-style)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(fname, dpi=150)
    plt.close()
    return alpha


def top_hubs(G, k=10):
    out = {}
    deg = dict(G.degree(weight="weight"))
    btw = nx.betweenness_centrality(G, weight=None)
    eig = nx.eigenvector_centrality_numpy(G, weight="weight")
    for ntype in NODE_FIELDS:
        nodes = [n for n in G.nodes if G.nodes[n]["node_type"] == ntype]
        out[ntype] = {
            "weighted_degree": sorted(((deg[n], n) for n in nodes), reverse=True)[:k],
            "betweenness":     sorted(((btw[n], n) for n in nodes), reverse=True)[:k],
            "eigenvector":     sorted(((eig[n], n) for n in nodes), reverse=True)[:k],
        }
    return out


def write_reports(G, stats, comms, hubs, alpha):
    with open(f"{OUT}/graph_stats.txt", "w") as f:
        f.write("=== Phase 3 — Global Buehler-style Graph ===\n\n")
        for k, v in stats.items():
            f.write(f"  {k:32s}: {v}\n")
        f.write(f"  {'Power-law exponent α':32s}: {alpha:.3f}\n")

    # ---- Communities on FULL graph ----
    with open(f"{OUT}/community_breakdown.txt", "w") as f:
        f.write(f"=== Communities — FULL graph ({len(comms)} communities) ===\n\n")
        for i, c in enumerate(sorted(comms, key=len, reverse=True)[:20]):
            type_dist = Counter(G.nodes[n]["node_type"] for n in c)
            f.write(f"Community {i+1}: {len(c)} nodes — {dict(type_dist)}\n")
            non_art = [G.nodes[n]["label"] for n in c
                       if G.nodes[n]["node_type"] != "article"][:8]
            f.write(f"  non-article members (first 8): {non_art}\n\n")

        # ---- Communities on CONCEPT-ONLY subgraph (articles excluded) ----
        try:
            from networkx.algorithms.community import greedy_modularity_communities
            concept_nodes_only = [n for n, d in G.nodes(data=True)
                                  if d["node_type"] != "article"]
            Gc = G.subgraph(concept_nodes_only).copy()
            comms_c = list(greedy_modularity_communities(Gc))
        except Exception:
            Gc, comms_c = None, []

        if Gc is not None:
            f.write(f"\n\n=== Communities — CONCEPT-ONLY ({Gc.number_of_nodes()} "
                    f"nodes, articles removed; {len(comms_c)} communities) ===\n\n")
            for i, c in enumerate(sorted(comms_c, key=len, reverse=True)[:20]):
                type_dist = Counter(Gc.nodes[n]["node_type"] for n in c)
                f.write(f"Community {i+1}: {len(c)} nodes — {dict(type_dist)}\n")
                members = [Gc.nodes[n]["label"][:30] for n in c][:12]
                f.write(f"  members (first 12): {members}\n\n")

    with open(f"{OUT}/top_hubs.txt", "w") as f:
        f.write("=== Top 10 hubs by centrality, per node type ===\n\n")
        for ntype, metrics in hubs.items():
            f.write(f"--- {ntype} ---\n")
            for metric, items in metrics.items():
                f.write(f"  by {metric}:\n")
                for v, n in items:
                    label = G.nodes[n]["label"]
                    f.write(f"    {v:.4f}  {label[:80]}\n")
            f.write("\n")


def export_html(G, stats, alpha):
    try:
        from pyvis.network import Network
    except ImportError:
        return False

    net = Network(height="900px", width="100%", bgcolor="#ffffff",
                  font_color="black", notebook=False)
    net.set_options("""
    var options = {
      "configure": {"enabled": true, "filter": ["physics"]},
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -30000,
          "centralGravity": 0.05,
          "springLength": 250,
          "springConstant": 0.002,
          "damping": 0.4,
          "avoidOverlap": 1
        },
        "stabilization": {"iterations": 2000}
      }
    }
    """)

    # Color palette aligned with Phase 1 / UBMK2026
    type_colors = {
        "polymer":      "#3498db",
        "modification": {"Modified": "#27ae60", "Unmodified": "#e74c3c"},
        "dispersion":   "#f39c12",
        "category":     "#9b59b6",
        "article":      "#95a5a6",
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
        deg_w = G.degree(n, weight="weight")
        color = (type_colors["modification"].get(label, "#7f8c8d")
                 if ntype == "modification" else type_colors[ntype])
        size = max(20, min(55, 18 + np.log10(max(1, deg_w)) * 9))
        if ntype == "article":
            label_short = label[:40].split(",")[0]
        else:
            label_short = label

        title = (
            f"{ntype.upper()}: {label}\n"
            f"  experiments: {d.get('n_rows', 0)}\n"
            f"  raw degree: {G.degree(n)}  |  weighted degree: {deg_w}\n"
            f"  --- avg matrix property (raw) ---\n"
            f"  E   = {_fmt(d.get('mean_matrix_modulus'),  ' GPa')}\n"
            f"  σ   = {_fmt(d.get('mean_matrix_strength'), ' MPa')}\n"
            f"  ε   = {_fmt(d.get('mean_matrix_strain'))}\n"
            f"  --- avg improvement (raw %) ---\n"
            f"  ΔE  = {_fmt(d.get('mean_dE_modulus'),      '%', 1)}\n"
            f"  Δσ  = {_fmt(d.get('mean_dsigma_strength'), '%', 1)}\n"
            f"  Δε  = {_fmt(d.get('mean_de_strain'),       '%', 1)}\n"
            f"  --- arcsinh-space mean (outlier-robust) ---\n"
            f"  ΔE_a = {_fmt(d.get('mean_dE_modulus_arcsinh'),      '', 3)}\n"
            f"  Δσ_a = {_fmt(d.get('mean_dsigma_strength_arcsinh'), '', 3)}\n"
            f"  Δε_a = {_fmt(d.get('mean_de_strain_arcsinh'),       '', 3)}\n"
            f"  MMT  = {_fmt(d.get('mean_MMT_pct'), ' wt%')}"
        )
        net.add_node(n, label=label_short, color=color, size=size, title=title)

    for u, v, d in G.edges(data=True):
        w = d["weight"]
        width  = max(1, min(w / 3, 12))
        length = max(40, 500 / np.sqrt(w))
        edge_title = (
            f"{G.nodes[u]['label'][:30]}  ⟷  {G.nodes[v]['label'][:30]}\n"
            f"  co-occurrences: {w}\n"
            f"  --- avg in shared experiments (raw %) ---\n"
            f"  ΔE  = {_fmt(d.get('mean_dE_modulus'),      '%', 1)}\n"
            f"  Δσ  = {_fmt(d.get('mean_dsigma_strength'), '%', 1)}\n"
            f"  Δε  = {_fmt(d.get('mean_de_strain'),       '%', 1)}\n"
            f"  --- arcsinh-space (robust) ---\n"
            f"  ΔE_a = {_fmt(d.get('mean_dE_modulus_arcsinh'),      '', 3)}\n"
            f"  Δσ_a = {_fmt(d.get('mean_dsigma_strength_arcsinh'), '', 3)}\n"
            f"  Δε_a = {_fmt(d.get('mean_de_strain_arcsinh'),       '', 3)}\n"
            f"  MMT  = {_fmt(d.get('mean_MMT_pct'), ' wt%')}"
        )
        net.add_edge(u, v, color="#cccccc", width=width, length=length,
                     title=edge_title)

    filename = f"{OUT}/global_graph.html"
    net.save_graph(filename)

    header = f"""
    <div style="padding: 20px; background-color: #f8f9fa; margin: 10px;
                border-radius: 5px; border: 2px solid #2c3e50;">
        <h2 style="color: #2c3e50;">Phase 3 — Buehler-style Global Concept Graph</h2>
        <p>All 942 experiments combined. Numerical means computed in arcsinh space (negative-compatible, outlier-robust).</p>
        <p><strong>Nodes:</strong> {stats['Number of nodes']}
           | <strong>Edges:</strong> {stats['Number of edges']}
           | <strong>Avg degree:</strong> {stats['Average node degree']}
           | <strong>Density:</strong> {stats['Density']}
           | <strong>Communities:</strong> {stats['Number of communities']}
           | <strong>Power-law α:</strong> {alpha:.3f}</p>
        <p><strong>Legend:</strong>
           &#x1F535; Blue: Polymer matrix |
           &#x1F7E2; Modified |
           &#x1F534; Unmodified |
           &#x1F7E0; Dispersion |
           &#x1F7E3; Category |
           <span style="color:#16a085;">&#9679;</span> Test Method |
           <span style="color:#d35400;">&#9679;</span> Exp/Sim |
           &#26AB; Article</p>
        <p><strong>Edge length</strong> ∝ 1/√(co-occurrence count): frequently co-occurring concepts drawn closer.
           <strong>Node size</strong> = log-scaled weighted degree.</p>
    </div>
    """
    with open(filename, "r") as f:
        html = f.read()
    html = html.replace("<center>\n<h1></h1>\n</center>",
                        f"<center>\n{header}\n</center>")
    with open(filename, "w") as f:
        f.write(html)
    return True


def main():
    os.makedirs(OUT, exist_ok=True)
    df = load_dataset()
    print(f"Loaded {len(df)} rows")

    G = build_graph(df)
    print(f"Built graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    stats, comms, Gg = graph_stats(G)
    print("\n=== Buehler Table 1 analog ===")
    for k, v in stats.items():
        print(f"  {k:32s}: {v}")

    alpha = power_law_fit([d for _, d in G.degree()],
                          f"{OUT}/degree_distribution.png")
    print(f"  {'Power-law exponent α':32s}: {alpha:.3f}")

    hubs = top_hubs(G)
    write_reports(G, stats, comms, hubs, alpha)

    # GEXF sanitize None
    G_export = G.copy()
    for _, d in G_export.nodes(data=True):
        for k, v in list(d.items()):
            if v is None:
                d[k] = float("nan")
    for _, _, d in G_export.edges(data=True):
        for k, v in list(d.items()):
            if v is None:
                d[k] = float("nan")
    nx.write_gexf(G_export, f"{OUT}/global_graph.gexf")

    if export_html(G, stats, alpha):
        print(f"\nInteractive viz: {OUT}/global_graph.html")
    print(f"\nReports in {OUT}/")


if __name__ == "__main__":
    main()
