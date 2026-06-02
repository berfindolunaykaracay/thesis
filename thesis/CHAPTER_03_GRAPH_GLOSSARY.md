# Chapter 3 (Methodology Annex) — Graph and Centrality Concepts

*Short explanatory notes for the polymer/clay-nanocomposite analysis used throughout this thesis. The content of this annex follows the supervisor-provided reference document "Graph and Centrality Concepts in Berfin's Thesis" (Karaçay / supervisor brief, June 2026) and is reproduced here as the canonical glossary for Phases 1–3 and Chapter 7.*

**Purpose.** This annex summarises the main graph/network concepts used in this thesis and translates them into their materials-science meaning. The focus is on how centrality metrics help identify which polymer families, modification states, and structure-property motifs carry the most information in polymer–MMT nanocomposite datasets.

**Central idea.** In this thesis, centrality is *not* used as a purely mathematical network metric. It is used as an **interpretability tool**: it helps identify which polymer family acts as a performance carrier, a knowledge hub, or a bridge between mechanical regimes.

---

## 3.A.1 Shortest centrality summary

| Concept | Plain meaning | Interpretation in this thesis |
|---|---|---|
| Degree | How many connections does the node have? | How many experiments, concepts, or material states is a polymer associated with? |
| Degree centrality | Normalized number of connections. | How central is the polymer within a given stiffness cluster? |
| Weighted degree | Sum of the weights of all connected edges. | Total contribution of a polymer to mechanical improvement. |
| Betweenness | Bridge role within the graph. | Does the polymer connect different material regimes or subdomains? |
| Eigenvector centrality | Connection to other important nodes. | Is the polymer connected to influential regions of the graph? |
| Edge variance | Spread of response magnitudes. | Is the reinforcement response stable or chaotic? |
| Community | A locally connected subgroup. | Do polymer, dispersion, and test-method concepts naturally cluster together? |
| Density | How tightly connected the network is. | Is the regime structurally organized or dispersed? |
| Cosine similarity | Semantic closeness between embedded concepts. | Are material concepts semantically close in the embedding space? |
| Motif | A recurring local pattern. | A repeated structure-property archetype, e.g. modification → stiffness gain → ductility penalty. |

---

## 3.A.2 Graph levels in the thesis

This thesis uses graph thinking at more than one level. The early stages use graph abstraction to represent mechanical performance relationships; the later stage moves toward Buehler-style knowledge graphs and graph-driven hypothesis generation.

| Level | What is represented? | Scientific function |
|---|---|---|
| **Phase 1** | Elastic-modulus-based C1–C4 clusters; graph construction within each stiffness regime. | Shows how matrix stiffness regime shapes graph topology and modulus improvement patterns. |
| **Phase 2** | Elastic modulus, strength, and strain-to-failure are treated as property layers. | Reveals performance trade-offs, especially stiffness/strength gain versus ductility penalty. |
| **Phase 3 / Chapter 7** | Concept nodes, property bins, article nodes, embeddings, cosine similarity, and graph traversal. | Turns the dataset into a knowledge map that can suggest testable material hypotheses. |

---

## 3.A.3 Core graph vocabulary

- **Node.** A knowledge unit in the graph. A node may represent a polymer, composite, modification state, dispersion state, property bin, article, or test method.
- **Edge.** A relationship between two nodes. In the performance graph, an edge often represents a measured property change such as modulus, strength, or strain-to-failure improvement.
- **Edge weight.** The magnitude assigned to an edge, such as $\Delta E\%$, $\Delta\sigma\%$, or $\Delta\varepsilon\%$. It tells how strong the mechanical response is.
- **Cluster.** A stiffness-regime group defined by neat polymer matrix modulus. The thesis uses C1–C4 to separate soft, semi-soft, intermediate, and rigid polymer regimes.
- **Property layer.** A graph layer based on a specific mechanical property. The main layers are elastic modulus, strength, and strain-to-failure.
- **Knowledge hub.** A node that carries high informational or functional importance in the graph. A hub can be highly connected, strongly weighted, or strategically positioned between subdomains.

---

## 3.A.4 Centrality metrics and materials interpretation

| Metric | Network definition | Materials-science interpretation |
|---|---|---|
| **Degree** | Counts the number of edges connected to a node. | A high-degree polymer is frequently represented across experiments or conceptual relations. This indicates representation and connectivity, *not necessarily best performance*. |
| **Degree centrality** | Normalizes degree by the maximum possible number of connections. | Useful for comparing centrality across clusters with different sizes. |
| **Weighted degree** | Sums edge weights connected to a node. | Indicates the total magnitude of mechanical response associated with that polymer or concept. High values may reflect strong improvement, but can also be outlier-driven. |
| **Betweenness centrality** | Measures how often a node lies on shortest paths between other nodes. | Identifies bridge polymers or concepts that connect different mechanical regimes, modification states, or dispersion mechanisms. |
| **Eigenvector centrality** | Rewards nodes connected to other highly important nodes. | Highlights concepts embedded in influential parts of the network, not merely concepts with many isolated links. |
| **Clustering coefficient** | Measures whether a node's neighbors are also connected to each other. | High local clustering suggests a coherent local motif, such as a polymer–dispersion–test-method subnetwork. |

---

## 3.A.5 How to interpret the metrics without overclaiming

- **A high weighted degree does not automatically mean the best material.** It means that the node is associated with large mechanical response magnitudes. These responses must be checked against data count, outliers, and ductility loss.
- **A high betweenness node is often more scientifically interesting than a merely high-degree node.** It may connect otherwise separate material regimes, making it useful for translating mechanisms from one domain to another.
- **Modified systems showing higher centrality suggests organization, not just improvement.** Surface modification may make the structure-property landscape more systematic by improving dispersion, interfacial compatibility, or response reproducibility.
- **Soft matrices can show very large percentage improvements.** This is expected because the modulus contrast between MMT and a soft polymer is enormous. The interpretation must therefore consider baseline modulus.
- **Rigid matrices may show lower percentage gains but more constrained topology.** In these systems, the limiting mechanism may be interface quality, platelet orientation, or ductility penalty rather than simple stiffness gain.

---

## 3.A.6 Property layers and ductility penalty

The key mechanical-property layers are $\Delta E\%$ for elastic modulus, $\Delta\sigma\%$ for strength, and $\Delta\varepsilon\%$ for strain-to-failure. These should *not* be interpreted independently. A system with very high stiffness improvement may still be undesirable if it produces a large ductility penalty.

| Observation | Meaning | Interpretive note |
|---|---|---|
| $\Delta E\%$ increases | The material becomes stiffer. | Usually expected with MMT addition. |
| $\Delta\sigma\%$ increases | The material becomes stronger. | Often depends on dispersion and interface quality. |
| $\Delta\varepsilon\%$ decreases | The material becomes less ductile or more brittle. | This is the **ductility penalty** and is central to the thesis interpretation. |

---

## 3.A.7 Semantic embeddings and cosine similarity

The semantic graph asks a different question from the co-occurrence or performance graph. Instead of asking which concepts appear together in an experiment, it asks which concepts are close in meaning. Node descriptions are converted into embedding vectors, and cosine similarity is used to rank semantic neighbors.

| Concept | Definition | Careful interpretation |
|---|---|---|
| **Embedding** | A vector representation of a concept or description. | Allows polymer names, test methods, and dispersion states to be compared semantically. |
| **Cosine similarity** | Similarity between two embedding vectors. | High similarity means the concepts are close in semantic space, *not necessarily experimentally equivalent*. |
| **UMAP** | A two-dimensional projection of high-dimensional embeddings. | Useful for visualization, but it should *not* be treated as proof of a physical mechanism. |

---

## 3.A.8 Graph-driven hypothesis generation

Graph traversal or shortest-path analysis can be used to connect material concepts and identify candidate hypotheses. **However, the graph does not prove the hypothesis.** It proposes a testable candidate that must be experimentally validated.

> **Careful wording (used throughout Chapter 7):** *The graph suggests that this material combination is a data-consistent and testable candidate, but it has not yet been experimentally verified.*

---

## 3.A.9 Suggested core thesis statement

The supervisor's reference document closes with the recommended core statement, reproduced verbatim and adopted in Chapter 1:

> **Polymer–MMT nanocomposite performance is not governed only by filler loading or modification status, but by a regime-dependent network topology in which matrix stiffness, dispersion state, modification, and mechanical-property trade-offs form recurring structure-property motifs.**
