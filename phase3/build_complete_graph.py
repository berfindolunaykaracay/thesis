"""
Phase 3 — Step 5: Complete graph (every datum present).

The richest view, combining three layers:

  1. Categorical concept layer (245 nodes) — identical to global_graph
  2. Sample layer (942 nodes)              — one node per experiment, numerical attributes
  3. Property-bin layer (27 nodes)         — physically meaningful numerical regimes

Edges:
  - concept ↔ concept   : co-occurrence
  - sample  ↔ concept   : this experiment uses this categorical attribute
  - sample  ↔ property  : this experiment falls into this numerical regime

Physical bin thresholds (from polymer literature):
  Modulus (GPa)         : <1 | 1-3 | 3-10 | >10
  Strength (MPa)        : <10 | 10-30 | 30-60 | >60         (UBMK C1-C4 thresholds)
  Strain to failure     : <5 (brittle) | 5-50 | >50 (ductile)
  ΔE / Δσ improvement % : <0 (degraded) | 0-50 | 50-200 | >200
  Δε strain change %    : <-50 | -50..0 | 0..50 | >50
  MMT loading (wt%)     : <1 | 1-3 | 3-7 | >7

Visual style = Phase 1 / UBMK2026.
Sample nodes use C1-C4 cluster colors; property bins are dark red.

Outputs:
  output/complete_graph.html
  output/complete_graph.gexf
  output/complete_graph_stats.txt
  output/property_bin_breakdown.txt
"""
import os
from collections import defaultdict, Counter
from itertools import combinations

import numpy as np
import pandas as pd
import networkx as nx

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

PROPERTY_BINS = {
    "matrix_modulus": {
        "column": "Polymer matrix elastic modulus (GPa)",
        "thresholds": [1.0, 3.0, 10.0],
        "labels":     ["E<1 GPa (soft)",   "E 1-3 GPa",
                       "E 3-10 GPa",       "E>10 GPa (rigid)"],
    },
    "matrix_strength": {
        "column": "Polymer matrix Strength (MPa)",
        "thresholds": [10.0, 30.0, 60.0],
        "labels":     ["σ<10 MPa (C1)",  "σ 10-30 MPa (C2)",
                       "σ 30-60 MPa (C3)", "σ>60 MPa (C4)"],
    },
    "matrix_strain": {
        "column": "Polymer matrix strain to failure",
        "thresholds": [5.0, 50.0],
        "labels":     ["ε<5 (brittle)", "ε 5-50 (moderate)", "ε>50 (ductile)"],
    },
    "dE_modulus": {
        "column": "Elastic Modulus improvement (%)",
        "thresholds": [0.0, 50.0, 200.0],
        "labels":     ["ΔE<0 (degraded)", "ΔE 0-50%",
                       "ΔE 50-200%",      "ΔE>200%"],
    },
    "dsigma_strength": {
        "column": "Strength improvement (%)",
        "thresholds": [0.0, 50.0, 200.0],
        "labels":     ["Δσ<0 (degraded)", "Δσ 0-50%",
                       "Δσ 50-200%",      "Δσ>200%"],
    },
    "de_strain": {
        "column": "Strain to failure improvement%",
        "thresholds": [-50.0, 0.0, 50.0],
        "labels":     ["Δε<-50%",         "Δε -50 to 0",
                       "Δε 0-50%",        "Δε>50%"],
    },
    "MMT_loading": {
        "column": "MMT weight%",
        "thresholds": [1.0, 3.0, 7.0],
        "labels":     ["MMT<1 wt%",       "MMT 1-3 wt%",
                       "MMT 3-7 wt%",     "MMT>7 wt%"],
    },
}

# Same regime cluster scheme used in UBMK2026 / Phase 1
CLUSTER_DEFS = {
    "C1": {"color": "#FF6B6B", "name": "Low strength"},
    "C2": {"color": "#4ECDC4", "name": "Medium-low strength"},
    "C3": {"color": "#45B7D1", "name": "Medium strength"},
    "C4": {"color": "#96CEB4", "name": "High strength"},
}


def load_dataset():
    df = pd.read_excel(DATASET)
    df.columns = [c.strip() for c in df.columns]
    df["Article"] = df["Article"].ffill()
    return df


def assign_bin(value, thresholds, labels):
    if pd.isna(value):
        return None
    for i, t in enumerate(thresholds):
        if value < t:
            return labels[i]
    return labels[-1]


def assign_strength_cluster(s):
    if pd.isna(s):
        return None
    if s < 10:  return "C1"
    if s < 30:  return "C2"
    if s < 60:  return "C3"
    return "C4"


def build_graph(df):
    G = nx.Graph()
    pair_rows = defaultdict(list)
    node_rows = defaultdict(list)
    sample_bins = defaultdict(list)

    # --- categorical concept nodes ---
    for ntype, col in NODE_FIELDS.items():
        for val in df[col].dropna().unique():
            G.add_node(f"{ntype}:{val}", node_type=ntype, label=str(val))

    # --- property bin nodes ---
    for prop, defn in PROPERTY_BINS.items():
        for lbl in defn["labels"]:
            G.add_node(f"property:{lbl}",
                       node_type="property_bin",
                       property_family=prop,
                       label=lbl)

    # --- per-row processing: sample nodes + edges ---
    for idx, row in df.iterrows():
        sid = f"sample:{idx}"
        cluster = assign_strength_cluster(row.get(PROPERTY_BINS["matrix_strength"]["column"]))
        sample_attrs = {"node_type": "sample", "label": f"exp_{idx}",
                        "cluster": cluster if cluster else "uncluster"}
        for prop, defn in PROPERTY_BINS.items():
            v = row.get(defn["column"])
            sample_attrs[prop] = float(v) if pd.notna(v) else None
        G.add_node(sid, **sample_attrs)

        # sample → categorical concept edges
        present_concepts = []
        for ntype, col in NODE_FIELDS.items():
            v = row.get(col)
            if pd.notna(v):
                target = f"{ntype}:{v}"
                G.add_edge(sid, target, weight=1, edge_type="sample_concept")
                present_concepts.append(target)
                node_rows[target].append(idx)
        # concept-concept (within same row)
        for a, b in combinations(present_concepts, 2):
            key = (a, b) if a < b else (b, a)
            pair_rows[key].append(idx)

        # sample → property bin edges
        for prop, defn in PROPERTY_BINS.items():
            v = row.get(defn["column"])
            bin_lbl = assign_bin(v, defn["thresholds"], defn["labels"])
            if bin_lbl is not None:
                tgt = f"property:{bin_lbl}"
                G.add_edge(sid, tgt, weight=1, edge_type="sample_property")
                sample_bins[tgt].append(idx)

    # concept-concept edges with co-occurrence weights
    for (a, b), rows in pair_rows.items():
        G.add_edge(a, b, weight=len(rows), n_rows=len(rows),
                   edge_type="concept_concept")

    # Annotate node-level counts
    for n, rows in node_rows.items():
        G.nodes[n]["n_rows"] = len(rows)
    for bin_id, samples in sample_bins.items():
        G.nodes[bin_id]["n_samples"] = len(samples)

    return G


def graph_stats(G):
    type_counts = Counter(d["node_type"] for _, d in G.nodes(data=True))
    edge_types  = Counter(d.get("edge_type") for _, _, d in G.edges(data=True))
    degrees = [d for _, d in G.degree()]
    return {
        "Number of nodes":     G.number_of_nodes(),
        "Number of edges":     G.number_of_edges(),
        "Average node degree": round(np.mean(degrees), 3),
        "Max node degree":     max(degrees),
        "Median node degree":  int(np.median(degrees)),
        "Density":             round(nx.density(G), 6),
        "Components":          nx.number_connected_components(G),
        **{f"  {t} nodes": n for t, n in type_counts.items()},
        **{f"  {t} edges": n for t, n in edge_types.items()},
    }


def write_bin_breakdown(G):
    with open(f"{OUT}/property_bin_breakdown.txt", "w") as f:
        f.write("=== Property bin populations (her bin'e kaç sample düştü) ===\n\n")
        for prop, defn in PROPERTY_BINS.items():
            f.write(f"--- {prop} ---\n")
            for lbl in defn["labels"]:
                nid = f"property:{lbl}"
                n = G.nodes[nid].get("n_samples", 0)
                f.write(f"  {lbl:28s} : {n} samples\n")
            f.write("\n")


def export_html(G, stats):
    from pyvis.network import Network
    net = Network(height="900px", width="100%", bgcolor="#ffffff",
                  font_color="black", notebook=False)
    net.set_options("""
    var options = {
      "configure": {"enabled": true, "filter": ["physics"]},
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -40000,
          "centralGravity": 0.04,
          "springLength": 180,
          "springConstant": 0.0012,
          "damping": 0.5,
          "avoidOverlap": 0.6
        },
        "stabilization": {"iterations": 1500}
      }
    }
    """)

    type_colors = {
        "polymer":      "#3498db",
        "modification": {"Modified": "#27ae60", "Unmodified": "#e74c3c"},
        "dispersion":   "#f39c12",
        "category":     "#9b59b6",
        "article":      "#95a5a6",
        "test_method":  "#16a085",
        "data_source":  "#d35400",
        "property_bin": "#8B0000",
    }

    def _fmt(v, unit="", dec=2):
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return "—"
        return f"{v:.{dec}f}{unit}"

    for n, d in G.nodes(data=True):
        ntype = d["node_type"]
        label = d["label"]
        deg_w = G.degree(n, weight="weight")

        if ntype == "sample":
            color = CLUSTER_DEFS.get(d.get("cluster"), {}).get("color", "#cccccc")
            size  = 6
            label_short = ""
            title = (
                f"SAMPLE: {label}  (strength cluster: {d.get('cluster')})\n"
                f"  --- matrix ---\n"
                f"  E   = {_fmt(d.get('matrix_modulus'),  ' GPa')}\n"
                f"  σ   = {_fmt(d.get('matrix_strength'), ' MPa')}\n"
                f"  ε   = {_fmt(d.get('matrix_strain'))}\n"
                f"  --- improvement ---\n"
                f"  ΔE  = {_fmt(d.get('dE_modulus'),      '%', 1)}\n"
                f"  Δσ  = {_fmt(d.get('dsigma_strength'), '%', 1)}\n"
                f"  Δε  = {_fmt(d.get('de_strain'),       '%', 1)}\n"
                f"  MMT = {_fmt(d.get('MMT_loading'),     ' wt%')}"
            )
        elif ntype == "property_bin":
            color = type_colors["property_bin"]
            n_s   = d.get("n_samples", 0)
            size  = max(25, min(60, 22 + np.log10(max(1, n_s)) * 9))
            label_short = label
            title = (f"PROPERTY BIN: {label}\n"
                     f"  family: {d.get('property_family')}\n"
                     f"  samples in this regime: {n_s}")
        else:
            if ntype == "modification":
                color = type_colors["modification"].get(label, "#7f8c8d")
            else:
                color = type_colors[ntype]
            size = max(20, min(55, 18 + np.log10(max(1, deg_w)) * 9))
            label_short = label[:40].split(",")[0] if ntype == "article" else label
            title = (f"{ntype.upper()}: {label}\n"
                     f"  experiments: {d.get('n_rows', 0)}\n"
                     f"  weighted degree: {deg_w}")

        net.add_node(n, label=label_short, color=color, size=size, title=title)

    for u, v, d in G.edges(data=True):
        et = d.get("edge_type")
        if et == "concept_concept":
            w      = d["weight"]
            width  = max(1, min(w / 3, 10))
            length = max(40, 500 / np.sqrt(w))
            color  = "#cccccc"
            tt = f"co-occurrences: {w}"
        elif et == "sample_property":
            width, length, color = 0.5, 100, "#d8b8b8"
            tt = "sample falls in this property regime"
        else:  # sample_concept
            width, length, color = 0.3, 130, "#e8e8e8"
            tt = "sample → concept"
        net.add_edge(u, v, color=color, width=width, length=length, title=tt)

    filename = f"{OUT}/complete_graph.html"
    net.save_graph(filename)

    sample_n = stats.get("  sample nodes", 0)
    prop_n   = stats.get("  property_bin nodes", 0)
    concept_n = stats["Number of nodes"] - sample_n - prop_n

    header = f"""
    <div style="padding: 20px; background-color: #f8f9fa; margin: 10px;
                border-radius: 5px; border: 2px solid #2c3e50;">
        <h2 style="color: #2c3e50;">Phase 3 — Complete Graph (All Data Combined)</h2>
        <p>Richest view: categorical concepts, individual experiment samples, and physical numerical regimes in a single graph.</p>
        <p><strong>Nodes:</strong> {stats['Number of nodes']}
           ({concept_n} categorical concepts + {prop_n} property bins + {sample_n} samples)
           | <strong>Edges:</strong> {stats['Number of edges']}</p>
        <p><strong>Concept Legend:</strong>
           &#x1F535; Polymer |
           &#x1F7E2; Modified |
           &#x1F534; Unmodified |
           &#x1F7E0; Dispersion |
           &#x1F7E3; Category |
           <span style="color:#16a085;">&#9679;</span> Test Method |
           <span style="color:#d35400;">&#9679;</span> Exp/Sim |
           &#26AB; Article</p>
        <p><strong>Property Bin:</strong>
           <span style="color:#8B0000;">&#9679;</span> Dark red (27 physical regimes:
           absolute E / σ / ε + Δ improvements + MMT loading)</p>
        <p><strong>Sample colors</strong> (by strength cluster):
           <span style="color:#FF6B6B;">&#9679;</span> C1 (0–10 MPa) |
           <span style="color:#4ECDC4;">&#9679;</span> C2 (10–30) |
           <span style="color:#45B7D1;">&#9679;</span> C3 (30–60) |
           <span style="color:#96CEB4;">&#9679;</span> C4 (60+)</p>
        <p><strong>Edges:</strong> concept-concept length ∝ 1/√co-occurrence;
           sample-concept fixed 130; sample-property fixed 100.</p>
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
    print(f"Built complete graph: {G.number_of_nodes()} nodes, "
          f"{G.number_of_edges()} edges")

    stats = graph_stats(G)
    with open(f"{OUT}/complete_graph_stats.txt", "w") as f:
        f.write("=== Phase 3 / Complete Graph stats ===\n\n")
        for k, v in stats.items():
            f.write(f"  {k:32s}: {v}\n")
            print(f"  {k:32s}: {v}")

    write_bin_breakdown(G)

    # GEXF sanitize None
    G_export = G.copy()
    for _, d in G_export.nodes(data=True):
        for k, v in list(d.items()):
            if v is None:
                d[k] = float("nan")
    nx.write_gexf(G_export, f"{OUT}/complete_graph.gexf")

    if export_html(G, stats):
        print(f"\nInteractive viz: {OUT}/complete_graph.html")
    print(f"\nReports in {OUT}/")


if __name__ == "__main__":
    main()
