"""
Phase 3 — Generative Reasoning Pilot (addresses Buehler §2.3).

Extracts interesting sub-graphs from complete_graph.gexf and formats each as
a Buehler-style natural-language prompt, ready to feed to an LLM for
hypothesis generation.

Five reasoning queries selected to span:
  Q1. A productive, well-studied combination (Epoxy + Modified + Exfoliated)
  Q2. A degraded-strength regime (Δσ<0) — what concepts dominate?
  Q3. The polyamide family — semantic neighbours in property space
  Q4. The extreme improvement regime (ΔE>200%) — outlier or signal?
  Q5. A sparsely studied combination — opportunity for new design
"""
import os
import re
from collections import Counter, defaultdict

import numpy as np
import networkx as nx

GRAPH = "output/complete_graph.gexf"
OUT   = "output/reasoning_subgraphs.txt"


def load():
    G = nx.read_gexf(GRAPH)
    return G


def fmt(v, unit="", dec=2):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    return f"{v:.{dec}f}{unit}"


def describe_sample(G, n):
    d = G.nodes[n]
    return (
        f"  {d.get('label','?')}  (cluster={d.get('cluster','?')})  "
        f"E={fmt(d.get('matrix_modulus'),' GPa')}, "
        f"σ={fmt(d.get('matrix_strength'),' MPa')}, "
        f"ε={fmt(d.get('matrix_strain'))}, "
        f"ΔE={fmt(d.get('dE_modulus'),'%',1)}, "
        f"Δσ={fmt(d.get('dsigma_strength'),'%',1)}, "
        f"Δε={fmt(d.get('de_strain'),'%',1)}, "
        f"MMT={fmt(d.get('MMT_loading'),' wt%')}"
    )


def get_samples_with(G, concept_labels):
    """Return sample nodes connected to ALL given concept node labels."""
    target_ids = []
    for lbl in concept_labels:
        for n, d in G.nodes(data=True):
            if d.get("node_type") != "sample" and d.get("label") == lbl:
                target_ids.append(n)
                break
    if len(target_ids) != len(concept_labels):
        return []
    samples = []
    for n, d in G.nodes(data=True):
        if d.get("node_type") != "sample":
            continue
        neighbors = set(G.neighbors(n))
        if all(t in neighbors for t in target_ids):
            samples.append(n)
    return samples


def get_samples_in_bin(G, bin_label):
    bin_id = None
    for n, d in G.nodes(data=True):
        if d.get("node_type") == "property_bin" and d.get("label") == bin_label:
            bin_id = n
            break
    if bin_id is None:
        return []
    return [n for n in G.neighbors(bin_id)
            if G.nodes[n].get("node_type") == "sample"]


def concept_distribution(G, samples):
    """For a list of sample nodes, count which concept neighbours appear."""
    counts = defaultdict(lambda: Counter())
    for s in samples:
        for nbr in G.neighbors(s):
            d = G.nodes[nbr]
            if d.get("node_type") in (None, "sample", "property_bin"):
                continue
            counts[d["node_type"]][d["label"]] += 1
    return counts


def summary_block(G, samples, top_k=5):
    out = []
    out.append(f"  Number of samples in this sub-graph: {len(samples)}")
    # Concept distribution
    cd = concept_distribution(G, samples)
    for ntype in ["polymer", "modification", "dispersion", "category", "test_method"]:
        if ntype not in cd: continue
        top = cd[ntype].most_common(top_k)
        out.append(f"  Top {ntype}: " + ", ".join(f"{n}×{c}" for n, c in top))
    # Property statistics
    props = {}
    for k in ["matrix_modulus", "matrix_strength", "matrix_strain",
              "dE_modulus", "dsigma_strength", "de_strain", "MMT_loading"]:
        vals = [G.nodes[s].get(k) for s in samples]
        vals = [v for v in vals if v is not None and not (isinstance(v, float) and np.isnan(v))]
        if not vals: continue
        props[k] = (np.mean(vals), np.median(vals), np.min(vals), np.max(vals), len(vals))
    if props:
        out.append("  Property statistics (mean | median | min | max | n):")
        for k, (mu, md, lo, hi, n) in props.items():
            out.append(f"    {k:18s}: {mu:8.2f} | {md:8.2f} | {lo:8.2f} | {hi:8.2f} | n={n}")
    return "\n".join(out)


def show_sample_examples(G, samples, k=5):
    if len(samples) <= k:
        sel = samples
    else:
        rng = np.random.RandomState(42)
        idx = rng.choice(len(samples), k, replace=False)
        sel = [samples[i] for i in sorted(idx)]
    return "\n".join(describe_sample(G, s) for s in sel)


def query(G, name, description, samples):
    block = f"\n{'='*70}\nQUERY: {name}\n{'='*70}\n\n{description}\n\n"
    block += "SUB-GRAPH SUMMARY:\n"
    block += summary_block(G, samples) + "\n\n"
    block += "REPRESENTATIVE SAMPLES (5 of these):\n"
    block += show_sample_examples(G, samples) + "\n\n"
    block += "REASONING TASK:\n"
    block += ("Based on the co-occurrence patterns and property statistics above, "
              "propose ONE polymer/clay composite design (or design principle) that "
              "is suggested by — but not yet realised in — this sub-graph. "
              "Justify your hypothesis from the co-occurrence and property "
              "distribution evidence shown.\n")
    return block


def main():
    G = load()
    samples = [n for n, d in G.nodes(data=True) if d.get("node_type") == "sample"]
    print(f"Loaded complete_graph: {G.number_of_nodes()} nodes, "
          f"{G.number_of_edges()} edges, {len(samples)} samples")

    queries = []

    # Q1 — Productive thermoset cluster
    q1_samples = get_samples_with(G, ["Epoxy", "Modified", "exfoliated"])
    queries.append(query(G, "Q1 — Epoxy + Modified MMT + Exfoliated dispersion",
                         "A well-studied 'gold standard' combination in the thermoset literature. "
                         "What is the actual property envelope it occupies, and what is the "
                         "next logical step to push beyond it?",
                         q1_samples))

    # Q2 — Degraded strength regime
    q2_samples = get_samples_in_bin(G, "Δσ<0 (degraded)")
    queries.append(query(G, "Q2 — Degraded-strength regime (Δσ < 0)",
                         "Experiments where clay reinforcement REDUCED the strength of the "
                         "matrix. Which concept combinations dominate this failure regime, "
                         "and what does that suggest about design rules to AVOID?",
                         q2_samples))

    # Q3 — Polyamide family
    q3_samples = []
    for poly in ["PA6", "PA12", "PA66", "PA7", "PA8", "PA"]:
        for n, d in G.nodes(data=True):
            if d.get("label") == poly and d.get("node_type") == "polymer":
                q3_samples.extend([s for s in G.neighbors(n)
                                   if G.nodes[s].get("node_type") == "sample"])
                break
    q3_samples = list(set(q3_samples))
    queries.append(query(G, "Q3 — Polyamide family (PA, PA6, PA7, PA8, PA12, PA66)",
                         "The polyamide family clusters tightly in transformer embedding space "
                         "(cosine 0.83–0.97). What property envelope does the family span, and "
                         "what would the IDEAL polyamide-MMT design look like based on the "
                         "best-performing combinations?",
                         q3_samples))

    # Q4 — Extreme improvement regime
    q4_samples = get_samples_in_bin(G, "ΔE>200%")
    queries.append(query(G, "Q4 — Extreme modulus-improvement regime (ΔE > 200%)",
                         "Experiments where clay produced more than 3x stiffness. Are these "
                         "real opportunities or artefacts of very soft matrices? What design "
                         "lesson can be extracted that is robust to the baseline effect?",
                         q4_samples))

    # Q5 — Sparse: Elastomer + Unmodified (search for opportunity)
    q5_samples = get_samples_with(G, ["Elastomer", "Unmodified"])
    queries.append(query(G, "Q5 — Elastomer + Unmodified MMT (sparse combination)",
                         "An under-explored corner of the design space. Given how few "
                         "experiments occupy this combination, what design hypothesis would "
                         "you propose to fill the gap?",
                         q5_samples))

    with open(OUT, "w") as f:
        f.write("REASONING SUB-GRAPHS — for LLM-driven hypothesis generation\n")
        f.write("(addresses Buehler 2024 §2.3, missing from base Phase 3 pipeline)\n")
        f.write("="*70 + "\n")
        for q in queries:
            f.write(q)

    print(f"\nWrote {len(queries)} reasoning sub-graphs to {OUT}")
    print(f"Sample counts per query: " +
          ", ".join(str(len(s)) for s in
                    [get_samples_with(G, ['Epoxy','Modified','exfoliated']),
                     get_samples_in_bin(G, 'Δσ<0 (degraded)'),
                     q3_samples,
                     get_samples_in_bin(G, 'ΔE>200%'),
                     get_samples_with(G, ['Elastomer','Unmodified'])]))


if __name__ == "__main__":
    main()
