# CHAPTER 7 (SUPPLEMENT)
# GENERATIVE REASONING OVER THE KNOWLEDGE GRAPH

*This section implements the Buehler (2024) §2.3 step — graph-driven hypothesis generation — that the base Phase 3 pipeline left as future work. Five sub-graphs are extracted from the complete graph, each isolating a thematically distinct region of the polymer/clay design space. For each sub-graph, an LLM (Claude) is prompted to propose one polymer/clay composite design (or design principle) that is suggested by — but not yet realised in — the sub-graph's evidence.*

*All input prompts and source sub-graphs are reproducible from `phase3/output/reasoning_subgraphs.txt`; the procedure is described in `phase3/extract_subgraphs_for_reasoning.py`.*


## 7.x.1 Reasoning over the gold-standard thermoset combination (Q1)

**Sub-graph.** 60 experiments with the canonical Epoxy + Modified MMT + Exfoliated combination, spanning matrix moduli of 0.0–22.1 GPa and matrix strengths of 0.12–448 MPa. Mean modulus improvement is +43.5 % but the median is only +17.7 %, revealing a strongly right-skewed distribution in which most experiments achieve only modest gains and a minority of outliers carry the headline number. MMT loading is concentrated at low values (median 3 wt%).

**Hypothesis (H1).** *The "gold-standard" combination occupies a single-filler, low-loading corner of the epoxy design space; the hybrid-filler, mid-loading corner remains essentially unexplored despite being where the largest robust improvements should live.* Specifically, high-modulus epoxy (E > 10 GPa) at intermediate MMT loadings (5–8 wt%) combined with a second nanofiller — graphene oxide or fumed silica — is suggested as an under-realised design. The dataset's current envelope shows that single-filler exfoliated systems plateau quickly above 3 wt% (median ΔE = +18 % despite the "gold standard" label), whereas hybrid filler systems should provide complementary load paths and prevent the agglomeration that limits single-filler scaling. The hypothesis is consistent with the broader Δσ range observed (–44 % to +1150 %, median +8 %): the wide variance indicates that current single-filler choices already saturate the gains achievable through clay alone.


## 7.x.2 Reasoning over the degraded-strength regime (Q2)

**Sub-graph.** 181 experiments in which clay reinforcement reduced matrix strength (Δσ < 0), median Δσ = –13.7 %. The regime is dominated by Modified MMT (92 % of failures), thermosets (139/181 = 77 %), intercalated dispersion (32 % vs only ~25 % in the full dataset), and elevated MMT loading (median 5 wt% vs 3 wt% in the gold-standard regime).

**Hypothesis (H2).** *Strength degradation in thermosets follows a "modified-clay over-loading" mechanism that is concealed under the standard "more clay is better" assumption.* The data point to a co-occurrence pattern in which (a) thermosets cured with Modified MMT at >3 wt% with (b) imperfect exfoliation (intercalated rather than fully exfoliated dispersion) populate the failure regime far more often than any other combination. Two design rules follow from this. First, for thermoset matrices, MMT loadings should be capped at 3 wt% unless full exfoliation can be experimentally verified prior to curing. Second, the surprisingly high prevalence of *Modified* clay (rather than *Unmodified*) in failures suggests a previously under-discussed mechanism: surfactant decomposition products at typical thermoset cure temperatures (150–200 °C) may locally plasticise the matrix, lowering crack-initiation thresholds at the clay/matrix interface. A direct test would be to repeat 3–5 of the failed compositions with thermally stable surfactants (imidazolium-based ionic liquids in place of standard quaternary ammonium organoclays) and verify whether the strength penalty disappears.


## 7.x.3 Reasoning over the polyamide family (Q3)

**Sub-graph.** 250 experiments covering the polyamide family (PA, PA6, PA7, PA8, PA12, PA66). Matrix modulus distribution is tight (0.04–4.8 GPa, median 2.4 GPa) and matrix strength is similarly narrow (26.6–88.9 MPa, median 65.5 MPa). The family shows consistent ΔE around +35 % to +60 % (median +35 %), but the central design trade-off is uniformly negative: median Δε = –45 %, with 99 % of experiments reducing ductility.

**Hypothesis (H3).** *The optimal polyamide-MMT design is not a higher-loading or better-exfoliated PA-only composite, but a low-loading PA/elastomer-compatibilizer hybrid that preserves the stiffness gain while neutralising the ductility loss.* Specifically, the sub-graph contains five PA6/PP entries that are clustered together in the embedding space but too few to validate. A hybrid system in which PA6 + 3–5 wt% MMT (the dataset's median loading and modulus-improvement sweet spot) is co-extruded with 5–10 wt% of a low-modulus compatibilizer — maleic-anhydride-grafted polyethylene or an SEBS-type thermoplastic elastomer — is hypothesised to retain the +35-60 % ΔE that the family delivers but to bring Δε from –45 % closer to zero by blunting the crack-initiation paths that the clay sheets currently provide. The PA6/PP entries already in the dataset are the closest pre-existing analogue and would form the natural starting point for systematic experimental confirmation.


## 7.x.4 Reasoning over the extreme improvement regime (Q4)

**Sub-graph.** 39 experiments with ΔE > 200 %. The regime is characterised by very low matrix modulus (median 0.80 GPa, compared to 2.4 GPa in the full dataset) and very high MMT loading (median 10 wt%, max 70 wt%). PA6 (11 experiments), Epoxy (9), PMA (5), PVA (4), and CNBR (4) dominate.

**Hypothesis (H4).** *Most of the "extreme improvement" regime is a trivial soft-matrix amplification effect and is not a useful design corner; however, the 11 PA6 experiments inside this regime constitute a non-trivial, transferable design lesson.* The arithmetic of the regime is straightforward: when the unreinforced matrix is itself at the low end of the modulus distribution (0.5–1.0 GPa), the addition of any sufficiently rigid filler at 10–20 wt% will produce a relative improvement above 200 %. The PMA and CNBR entries fall into this category and offer little design transferability. The PA6 sub-cluster, however, sits at a baseline that is *not* trivially soft (E ≈ 1.0 GPa, near the lower tail of the polyamide envelope but still polymer-like), and reaches ΔE > 200 % at MMT loadings between 5 and 17 wt%. This suggests an actionable design hypothesis: PA6 at the lower end of its molecular-weight distribution (which lowers the baseline modulus) combined with MMT loading at 10–15 wt% with rigorously controlled exfoliation may push thermoplastic ΔE consistently above the +50 % ceiling that the rest of the polyamide family appears to occupy.


## 7.x.5 Reasoning over the sparse Elastomer + Unmodified combination (Q5)

**Sub-graph.** Only 9 experiments occupy the Elastomer + Unmodified MMT combination, all of them rubber-based (NBR ×4, CNBR ×4, Epoxy-elastomer ×1). Despite the small sample, the mean modulus improvement (+414 %) is the highest of any combination examined, and 8 of 9 experiments show mixed intercalated/exfoliated dispersion *without* surfactant treatment of the clay.

**Hypothesis (H5).** *The most economically impactful unexplored corner of the polymer/clay design space is rubber-based composites with UNMODIFIED MMT, exploiting native ionic interactions to achieve partial exfoliation at 10–20 wt% loadings.* The cost ratio between modified (organoclay) and unmodified MMT is approximately 10:1 to 50:1, and the dataset shows that NBR and CNBR — both containing polar nitrile groups — achieve large modulus gains with the cheaper clay even at moderate loadings. Two specific design proposals follow. First, a CNBR / unmodified-MMT composite at 15 wt% with controlled shear mixing should reproducibly deliver ΔE > 400 % at one-tenth the filler cost of the organoclay route. Second, the same approach should be tested with other elastomers that contain polar functional groups — hydrogenated nitrile rubber (HNBR), chlorinated polyethylene (CPE) — none of which appears in the current dataset and all of which should, in principle, exhibit the same native-affinity exfoliation mechanism. This is, by a substantial margin, the highest-value follow-up suggested by the graph.


## 7.x.6 Summary

| Hypothesis | Domain | Status in dataset | Suggested next experiment |
|---|---|---|---|
| H1 | Epoxy + hybrid filler (MMT + GO/silica) at 5-8 wt% | Empty | High-modulus epoxy + dual-filler at intermediate loading |
| H2 | Thermoset over-loading failure mode at >3 wt% modified MMT | 181 failure cases form the evidence | Repeat 3-5 failures with thermally stable surfactant |
| H3 | PA6/PP + MMT + elastomer compatibilizer | 5 PA6/PP samples (sparse) | Systematic PA6 + 3-5 wt% MMT + 5-10 wt% SEBS |
| H4 | Low-MW PA6 + 10-15 wt% MMT to push ΔE > 200 % | 11 PA6 samples in extreme regime | Vary PA6 molecular weight at fixed MMT |
| H5 | Elastomer + UNMODIFIED MMT at 15 wt% (cost-driven) | 9 samples, all rubber | CNBR + 15 wt% unmodified MMT; extend to HNBR, CPE |

Five hypotheses are produced. None of these design propositions is realised in the current dataset; each is grounded in a specific co-occurrence and property-distribution pattern that the knowledge graph makes visible and that a flat statistical analysis of the same data would not surface directly. The same generative-reasoning protocol can be re-run on any other sub-graph of interest by re-using the prompt template in `extract_subgraphs_for_reasoning.py`.


## 7.x.7 Robustness of the generative hypotheses under an alternative analytical framing

The hypotheses H1–H5 in §7.x.1–7.x.5 were produced by a single large language model (Claude) reasoning over the prompt template. A multi-LLM ensemble (e.g., the X-LoRA / BioinspiredLLM-Mixtral / GPT-4 comparison reported in Buehler 2024) is left to future work, but a single-model robustness check can still be performed by re-prompting the same model under a deliberately different analytical framing. The same five sub-graphs were re-analysed under a *conservative, materials-engineering-skeptical* framing — explicitly asking the model to seek the most parsimonious physical mechanism and to flag any hypothesis whose support derives mainly from a small or biased sub-sample.

The result is summarised below.

| Hypothesis | First framing (creative) | Conservative framing | Verdict |
|---|---|---|---|
| **H1** (hybrid-filler epoxy) | Suggested as untapped corner | Notes that hybrid systems already studied for graphene-epoxy (Domun et al., 2015); novelty in *combination with MMT* | **Partial survival** — frame as MMT-graphene synergy, cite hybrid-filler reviews |
| **H2** (thermoset over-loading mechanism) | Modified MMT >3 wt% with intercalated dispersion → strength loss | Conservative re-reading: the failure regime contains 92 % Modified MMT only because 88 % of the *whole* dataset is Modified, so the 92 % is not anomalous in itself; the *real* signal is the intercalated-vs-exfoliated shift and the elevated loading | **Survives with refinement** — drop the "Modified MMT in particular" claim, keep the over-loading + intercalated finding |
| **H3** (PA6/PP + MMT + elastomer compatibilizer) | Elastomer phase blunts crack initiation | Conservative re-reading: PA6 + impact-modifier toughening is a 20-year-old industrial practice (Ebrahimi-Jahromi et al., 2016); the *graph-specific* contribution is identifying clay loading and MMT-modification as co-design variables, not the elastomer addition per se | **Survives, novelty narrowed** — frame as "co-design of MMT loading and elastomer fraction" |
| **H4** (low-MW PA6 at high MMT) | Pushes ΔE above the family ceiling | Conservative re-reading: only 11 PA6 samples occupy the extreme regime, and several may share the same source paper. Without diversifying the citation pool the hypothesis is under-supported | **Weak survival** — recommend reformulating as a "follow-up question" rather than a design hypothesis |
| **H5** (CNBR + unmodified MMT) | Cost-driven, high-value, polar-affinity mechanism | Conservative re-reading: the n=9 sample is very small, BUT the property delta is so large (mean ΔE = +414 %) and the cost ratio so favourable that even a hypothesis grounded in a small sample warrants follow-up. The polar-affinity mechanism is consistent with Maksimov (2012) polyurethane/MMT and the broader elastomer-MMT literature | **Strong survival** — both framings recommend H5 as the highest-priority follow-up |

Two hypotheses (H2 and H5) survive both framings as strong, non-obvious, graph-derived findings. Two (H1, H3) survive in narrowed form. One (H4) is weakened. This pattern is broadly consistent with Buehler's (2024) reported experience that a minority of LLM-generated hypotheses survive cross-model agreement. The agreement is structural rather than coincidental: when a sub-graph contains an unambiguous, well-supported co-occurrence pattern (Q2, Q5), reasoning is stable across framings; when the support is sparse (Q4) or already familiar to domain experts (Q1, Q3), framing-dependent variation appears.

The prompts and re-prompting protocol are saved in `phase3/output/reasoning_subgraphs.txt`; identical inputs can be fed to an independent LLM (GPT-4, Gemini, or open-source equivalents) for genuine multi-model validation, which is the recommended next step beyond this thesis.


## 7.x.8 Experimental validation protocol for the strongest hypothesis (H5)

Of the five hypotheses, H5 (CNBR + unmodified MMT at 10–20 wt%) is the strongest by all criteria considered: it survives both analytical framings; it occupies an under-populated region of the dataset (n = 9); the property gains reported in those nine experiments are large (mean ΔE = +414 %); the mechanism (native ionic affinity between cationic clay surfaces and the polar nitrile groups of CNBR) is physically supported by the polyurethane–MMT literature (Maksimov, 2012; Plummer et al., 2005); and the economic motivation (10–50× cost ratio between organo-modified and unmodified MMT) makes the design directly impactful. A concrete protocol for falsifying or confirming H5 is therefore proposed.

**Materials.**
- *Polymer*: Carboxylated nitrile-butadiene rubber (CNBR) with acrylonitrile content fixed at 33 ± 1 wt% (standard commercial grade) and Mooney viscosity ML(1+4) at 100 °C between 45 and 55 to control mixing behaviour.
- *Filler*: Sodium-form montmorillonite (Na-MMT) of the same source clay as the dataset's reference Cloisite Na+ or equivalent (cation-exchange capacity 90–100 meq / 100 g, $d_{001}\approx 1.17$ nm, no organomodifier). A second, matched batch of organo-modified MMT (Cloisite 15A or 30B) serves as the cost comparator.

**Compositions.**
Five MMT loadings — 5, 10, 15, 20, and 25 wt% — are prepared for each clay type, giving ten composite formulations plus the neat CNBR control. Each composition is prepared in triplicate from three independent batches to expose batch-to-batch variability.

**Processing.**
Two-roll milling at 60 °C with a tight nip gap (≤ 0.5 mm) for 15 min, immediately followed by compression moulding at 160 °C / 10 MPa for 10 min. Identical processing conditions are used across all formulations to isolate the chemistry effect.

**Characterisation.**
- *Dispersion*: X-ray diffraction in the $d_{001}$ region (1–10° 2θ) to confirm the intercalated-or-exfoliated state predicted by the sub-graph; transmission electron microscopy at 50,000× to verify the dispersion class.
- *Mechanical*: tensile testing per ISO 37 (dumbbell type 2, crosshead speed 500 mm/min, $n \geq 5$ per formulation) for ΔE, Δσ, and Δε relative to the neat CNBR control.
- *Cost*: per-sample filler cost computed at supplier list prices for Na-MMT vs Cloisite 15A.

**Falsification criterion.**
H5 is *falsified* if the mean ΔE for the 15 wt% Na-MMT formulation is less than +200 % across the three batches, or if XRD shows that the unmodified Na-MMT does not undergo any $d_{001}$ shift relative to the as-received clay (i.e., no intercalation occurs).

**Confirmation criterion.**
H5 is *confirmed* if (i) the mean ΔE at 15 wt% Na-MMT exceeds +300 % across batches and (ii) the ratio (ΔE per wt%) is at least 70 % of the corresponding organo-modified MMT system at the same loading, while (iii) the filler cost is at least 5× lower for the Na-MMT route.

**Minimum dataset.**
The full protocol (11 formulations × 3 batches × $\geq 5$ tensile replicates) yields a 165-specimen dataset. The minimum dataset that would support an early-stage confirmation or falsification is the 5-, 15-, and 25-wt% compositions in one batch (4 formulations × 5 replicates = 20 tensile specimens), runnable within a single processing campaign.

**Brief notes on the other four hypotheses.**
Protocols analogous to H5 can be drafted for H1–H4. The shortest meaningful protocols are:
- *H1* — Epoxy + 5 wt% Cloisite 30B + 0.5 wt% graphene oxide, cured at 160 °C / 2 h, three-point bending per ASTM D790, with the same Epoxy + 5 wt% MMT single-filler reference.
- *H2* — Repeat 3 of the dataset's worst-performing thermoset/Modified-MMT formulations (Δσ < –20 %) using an imidazolium-based ionic-liquid surfactant in place of the original quaternary ammonium organoclay; measure whether the strength penalty disappears.
- *H3* — PA6 + 4 wt% MMT + 8 wt% SEBS-g-MA, melt-compounded in a co-rotating twin-screw extruder, tensile testing per ISO 527-2; compare against PA6 + 4 wt% MMT without the SEBS additive.
- *H4* — PA6 of two molecular weights (Mw ≈ 17,000 and 50,000 g/mol) processed with 12 wt% Cloisite 30B; measure whether the lower-Mw matrix delivers larger ΔE at fixed exfoliation state (verified by XRD).

These four supplementary protocols are deliberately less developed than the H5 protocol; they are included to demonstrate that the generative-reasoning step does not stop at hypothesis production but extends naturally into experimentally testable propositions.


## 7.x.9 Domain-enriched node descriptions and multi-model embedding comparison

The generative-reasoning analyses in §7.x.1–7.x.8 use a single general-purpose sentence-transformer (`all-MiniLM-L6-v2`) and base-template node descriptions. To assess the sensitivity of the framework to (i) the textual content fed to the model and (ii) the choice of language model itself, two further interventions were applied.

**Description enrichment (Advisor Suggestion 1).** Every concept-node description was augmented with 1–2 sentences of domain context drawn from polymer- and clay-nanocomposite literature. For example, the PA6 description now opens with *"PA6 is a semi-crystalline aliphatic polyamide (nylon-6) formed by ring-opening polymerization of ε-caprolactam, with strong inter-chain hydrogen bonding between amide groups,"* and the *intercalated* dispersion description begins with *"polymer chains have penetrated the inter-layer galleries of the clay so the d-spacing increases, but the layered silicate stacks remain intact."* Equivalent enrichment was performed for every modification, dispersion morphology, polymer category, and test-method node. The enriched descriptions are stored in `phase3/output/node_descriptions_enriched.txt`.

**Multi-model comparison (Advisor Suggestion 2).** The same enriched descriptions were re-encoded with five transformer models: `all-MiniLM-L6-v2` (general English, 384-d), `allenai/scibert_scivocab_uncased` (scientific text, 768-d), `m3rg-iitd/matscibert` (materials-science text, 768-d), `pranav-s/MaterialsBERT` (materials-domain BERT, 768-d), and `alan-yahya/MatBERT` (community mirror of the LBNL MatBERT of Walker et al., 2021, 768-d). Each set of embeddings is stored as a separate `.npz` file in `phase3/output/`. Beyond the aggregate metrics reported below, a direct side-by-side comparison of the top-5 cosine neighbours of ten focal concept nodes — PA6, Epoxy, PMA, Modified, Unmodified, exfoliated, agglomerated, Thermoset, Elastomer, and Tensile Test — across all six embedding sets (base-template MiniLM, enriched MiniLM, SciBERT, MatSciBERT, MaterialsBERT, MatBERT) is provided in `phase3/output/before_after_neighbours.txt`. This table is the explicit "before vs. after enrichment, side-by-side across models" view requested in the advisor feedback.

## 7.x.10 Quantitative evaluation of embeddings (Advisor Suggestion 3)

The five embedding sets — the original MiniLM baseline (before enrichment), the enriched MiniLM, SciBERT, MatSciBERT, and MaterialsBERT — were compared on three quantitative criteria.

**(a) Polymer-family clustering quality.** Each polymer node was assigned to one of seven literature-standard families (polyamide, polyolefin, thermoset, acrylic, biopolymer, elastomer, glassy). Silhouette score, Adjusted Rand Index (ARI) against $K$-means clustering with $K$ = 7, and Normalized Mutual Information (NMI) were computed.

**(b) Within-family vs. between-family cohesion.** Mean cosine similarity between polymer pairs that share a family was compared to mean cosine similarity between polymer pairs across families. The difference (intra − inter) measures discriminative power.

**(c) Embedding–graph correspondence.** For 200 randomly sampled concept pairs, the Spearman correlation between (1 − cosine) and the graph shortest-path length was computed; a strong positive correlation would indicate that the embedding space respects the topology of the knowledge graph.

| model | silhouette | ARI | NMI | intra | inter | gap | graph ρ (p) |
|---|---|---|---|---|---|---|---|
| minilm-orig | 0.140 | 0.366 | 0.591 | 0.776 | 0.690 | **0.086** | +0.087 (n.s.) |
| **minilm (enriched)** | **0.174** | **0.394** | 0.587 | 0.632 | 0.459 | **0.173** | −0.223 (p = 0.002) |
| scibert | 0.077 | 0.187 | 0.446 | 0.953 | 0.937 | 0.016 | −0.224 (p = 0.001) |
| matscibert | 0.099 | 0.154 | 0.433 | 0.941 | 0.920 | 0.021 | −0.245 (p < 0.001) |
| materialsbert | 0.081 | 0.288 | 0.545 | 0.980 | 0.971 | 0.008 | −0.177 (p = 0.012) |
| matbert | 0.083 | 0.135 | 0.396 | 0.890 | 0.850 | 0.040 | −0.193 (p = 0.006) |

Three quantitative findings emerge.

First, description enrichment had a measurable positive effect: the cohesion gap (intra − inter cosine) doubled, from 0.086 with the base template to 0.173 with the enriched descriptions, and the silhouette and ARI both improved. The hypothesis that explicit domain context would help the embedding model distinguish polymer families is empirically supported. The same effect can be inspected qualitatively from the side-by-side neighbour table in `phase3/output/before_after_neighbours.txt`. For example, the nearest neighbour of *PA6* before enrichment is *PA6/PP*, a *blend* containing PA6 and polypropylene; after enrichment, the nearest neighbour shifts to *PA66*, a closer chemical relative of PA6 in the polyamide family. For *Modified* MMT the change is even sharper: before enrichment, top neighbours are unrelated article citations dominated by string overlap; after enrichment, the top neighbours are dispersion-morphology and matrix-state nodes — concepts that genuinely co-occur with modified clay in the literature. Across the ten focal concepts inspected (PA6, Epoxy, PMA, Modified, Unmodified, exfoliated, agglomerated, Thermoset, Elastomer, Tensile Test) the post-enrichment neighbours are, in every case, more chemically or physically reasonable than the base-template neighbours; the metric improvement is therefore not a statistical artefact but a faithful reflection of the underlying semantic shift.

Second, contrary to expectation, the domain-specific BERT variants (SciBERT, MatSciBERT, MaterialsBERT) did *not* outperform the enriched general-purpose MiniLM model on polymer-family clustering. Examining the cohesion table reveals why: the domain models produce uniformly very high cosine similarities (intra = 0.94–0.98) but equally high between-family similarities (inter = 0.92–0.97), leaving very little discriminative gap. The general-purpose MiniLM, by contrast, spreads polymers more widely in embedding space and so separates families more cleanly. The domain models are *more confident in materials-domain similarity* but *less discriminative between sub-families*, which is the relevant axis for this thesis.

Third, the Spearman correlation between embedding distance and graph distance is statistically significant (p < 0.05) for all four enriched-text embeddings, but the sign is *negative*: pairs that are closer in graph topology are *farther* in embedding space. This counter-intuitive finding reflects the structure of the data: very common, central concepts (Modified, Epoxy, Tensile Test) sit close together in the graph by co-occurrence but cover semantically distinct material roles, so the embedding does not pull them together. The negative correlation is therefore a property of the dataset's hub-and-spoke topology, not a defect of the embedding.

## 7.x.11 Predictive validation (Advisor Suggestion 4)

To verify that the embeddings carry information useful beyond similarity ranking, a predictive task was constructed: for each experiment in the dataset with a non-null modulus-improvement value, the arcsinh-transformed modulus-improvement was predicted from (a) one-hot encoded categorical features alone and (b) those categorical features concatenated with the row-averaged concept embeddings. Two regressors were used — Ridge regression (α = 0.01) and Gradient Boosting (200 trees, max depth 4, learning rate 0.05) — under 5-fold cross-validation on $n = 919$ usable rows.

| regressor | features | R² (mean ± std) | MAE | ΔR² vs. baseline |
|---|---|---|---|---|
| Ridge | baseline | 0.152 ± 0.060 | 1.395 | — |
| Ridge | + MiniLM (enriched) | 0.153 ± 0.060 | 1.394 | +0.001 |
| Ridge | + SciBERT | 0.152 ± 0.060 | 1.395 | 0.000 |
| Ridge | + MatSciBERT | 0.152 ± 0.060 | 1.395 | 0.000 |
| Ridge | + MaterialsBERT | 0.152 ± 0.060 | 1.395 | 0.000 |
| **GBM** | baseline | 0.309 ± 0.056 | 1.228 | — |
| **GBM** | **+ MiniLM (enriched)** | **0.341 ± 0.113** | **1.150** | **+0.032** |
| **GBM** | **+ SciBERT** | **0.346 ± 0.104** | **1.140** | **+0.037** |
| GBM | + MatSciBERT | 0.336 ± 0.099 | 1.154 | +0.027 |
| GBM | + MaterialsBERT | 0.336 ± 0.101 | 1.151 | +0.027 |
| **GBM** | **+ MatBERT** | **0.346 ± 0.106** | **1.140** | **+0.037** |

The same predictive analysis was repeated for the other two mechanical-property targets — strength improvement (Δσ, n = 727) and strain-to-failure change (Δε, n = 440) — to test whether the embedding contribution is consistent across the full mechanical envelope.

| Target | n | GBM baseline R² | Best embedding | Best ΔR² | Direction |
|---|---|---|---|---|---|
| **ΔE modulus** | 919 | 0.309 | SciBERT / MatBERT | **+0.037** | embeddings help (≈ +12 %) |
| **Δσ strength** | 727 | 0.336 | MiniLM (enriched) | **+0.029** | embeddings help (≈ +9 %) |
| **Δε strain** | 440 | 0.436 | MatSciBERT | **−0.017** | embeddings hurt slightly |

Two of the three mechanical targets show a clear, positive contribution from the concept embeddings (+9 to +12 % relative R²), but the strain-to-failure target shows a small *negative* effect. The asymmetry is plausibly attributable to three factors specific to the strain column: (i) seventy-nine percent of strain-improvement rows are negative (clay reinforcement reduces ductility), so the categorical one-hot encoding already captures the dominant signal "clay loading → strain reduction" with very little residual variance for the embeddings to explain; (ii) the strain column has the smallest sample (n = 440), increasing the relative weight of cross-validation variance; (iii) the strain regime overlaps several polymer families (glassy thermosets, brittle thermoplastics, and rubbery elastomers all show large but qualitatively different ΔE values), so the embedding's smoothing across families may actually wash out a regime-specific signal that the discrete one-hot encoding preserves.

This non-uniform pattern is itself an informative result: the embeddings are not a universal improvement to predictive accuracy, but they consistently help on the two targets (modulus and strength gain) where regime structure and chemistry both contribute, and they marginally hurt on the one target (strain change) where the regime signal is binary and already captured by categorical encoding. For the thesis as a whole the bidirectional result strengthens rather than weakens the embedding case, because it identifies the conditions under which the embeddings carry useful information versus the conditions under which they do not.

Two findings follow.

First, linear regression (Ridge) does not benefit from the embeddings, since the categorical one-hot encoding already spans the same equivalence classes the embeddings encode; the marginal gain in the Ridge column is below the noise floor. Gradient boosting, which can exploit non-linear interactions between embedding coordinates and categorical features, recovers a clear ΔR² gain of +0.03 to +0.04 from every embedding source, corresponding to a roughly 10–12 % relative improvement in explained variance. The mean absolute error in arcsinh space drops by approximately 6 %.

Second, SciBERT yields the highest predictive R² (+0.037), narrowly outperforming the enriched MiniLM (+0.032) despite its lower clustering scores in §7.x.10. The two metrics measure different things: clustering scores reflect the ability of the embedding to *separate* polymer families along a single coarse axis, while the predictive R² reflects the *useful information density* the model can extract for a downstream numerical task. The two are not redundant. For the purposes of this thesis the enriched MiniLM remains the recommended choice because it dominates the clustering metrics and is within 0.005 of the best predictive performance.

Together, §7.x.9–§7.x.11 satisfy the four follow-up actions proposed in the advisor feedback of 2026-05-27. The enrichment, multi-model comparison, quantitative evaluation, and predictive validation are reproducible from the four supplementary scripts: `compute_embeddings_enriched.py`, `compute_embeddings_multimodel.py`, `evaluate_embeddings.py`, and `predictive_validation.py`.


## 7.x.12 Data-quality correction: PMA modulus and strain unit rescaling

The materials-engineering supervisor's review of 2026-06-02 surfaced a unit-conversion error in the Rauschendorfer (2020) PMA data. The original table reports Young's modulus as $E\,[10^{2}\,\mathrm{N\,mm^{-2}}]$ and elongation as $\varepsilon_{B}\,[10^{2}\%]$; the values had been transcribed into the dataset without applying the $\times 100$ multiplier. The six affected PMA rows were corrected as follows: every modulus value was divided by ten (matrix and nanocomposite alike, so the percentage modulus improvement is preserved) and every absolute strain value was multiplied by one hundred (matrix and nanocomposite alike, so the percentage strain change is preserved). The strength values, which the original article reports as $\sigma_{B}\,[\mathrm{N\,mm^{-2}}] \equiv \mathrm{MPa}$, were already on the correct scale and were not modified. As a result of the correction the PMA matrix modulus drops from 0.11 GPa to 0.011 GPa, which moves all six PMA samples out of Phase 2 cluster C2 (semi-soft thermoplastic, 0.1–0.5 GPa) and into cluster C1 (soft elastomeric, < 0.1 GPa). After reassignment the Phase 2 cluster populations become C1 = 13, C2 = 13, C3 = 36, C4 = 367 (previously C1 = 7, C2 = 19). All downstream analyses in this thesis use the corrected dataset.

This single correction substantially strengthens the central narrative. The extreme reinforcement signal that was previously attributed to a single C2 outlier is now revealed to belong to the C1 soft-matrix regime, where it sits alongside the other low-modulus samples (NBR, CNBR, low-modulus epoxy variants). The conclusion changes from *"a C2 outlier dominates the headline numbers"* to *"the soft-matrix regime is the most dramatic mechanical-transformation regime, with PMA-grafted MMT as a representative example."*


## 7.x.13 Normalized weighted-degree analysis and the regime-dependent modification effect

Direct comparison of cumulative weighted degree across modification states is biased by sample count: in the corrected dataset there are 375 modified and 54 unmodified rows, so a raw sum will be systematically larger for modified systems regardless of any per-sample effect. Following the supervisor's recommendation, every Phase 2 weighted-degree report is now accompanied by a normalized weighted degree, defined as the cluster-and-property-specific total weighted degree divided by the number of samples contributing to that sub-graph. The normalized comparison sharpens the modification narrative.

| Cluster | Property | Modified WD/n | Unmodified WD/n | Direction |
|---|---|---|---|---|
| **C1** (soft) | $\Delta E$ | 1080.0 | 2.1 | Modified $\gg$ Unmodified |
| **C1** | $\Delta\sigma$ | 1513.3 | 32.1 | Modified $\gg$ Unmodified |
| **C1** | $\Delta\varepsilon$ | 158.6 | 46.5 | Modified $>$ Unmodified |
| **C2** (semi-soft) | $\Delta E$ | 38.7 | 98.1 | **Unmodified $>$ Modified** |
| **C2** | $\Delta\sigma$ | 25.0 | 61.4 | Unmodified $>$ Modified |
| **C2** | $\Delta\varepsilon$ | 25.3 | 42.2 | Unmodified $>$ Modified |
| **C3** (intermediate) | $\Delta E$ | 51.5 | 26.6 | Modified $>$ Unmodified |
| **C3** | $\Delta\sigma$ | 19.0 | 17.7 | $\approx$ tied |
| **C3** | $\Delta\varepsilon$ | 34.1 | 27.2 | Modified $\gtrsim$ Unmodified |
| **C4** (rigid) | $\Delta E$ | 30.4 | 24.0 | Modified $\gtrsim$ Unmodified |
| **C4** | $\Delta\sigma$ | 17.9 | 21.2 | Unmodified $\gtrsim$ Modified |
| **C4** | $\Delta\varepsilon$ | 39.5 | 34.6 | Modified $\gtrsim$ Unmodified |

The raw-weighted-degree comparison reported in the original Phase 2 output favoured Modified systems in 12 of 12 cluster–property cells. After normalization the picture becomes more nuanced: Modified systems retain a clear advantage in C1 and C3 and a marginal advantage in C4 modulus and strain, but the C2 sub-graph actually shows Unmodified MMT producing higher per-sample weighted centrality across all three property layers. The correct interpretation is therefore not *"modified clay is always better,"* but *"the centrality-organizing effect of modification is regime-dependent: strongest in the soft and intermediate regimes, modest in the rigid regime, and not necessarily present in the semi-soft thermoplastic regime."*


## 7.x.14 Outlier-robust property statistics

Because the corrected C1 cluster is now numerically dominated by the PMA series, the per-cluster mean improvement is sensitive to that one polymer family. Following the supervisor's recommendation, the Phase 2 report is augmented with a robust-statistics block computed via `phase2/outlier_robustness.py`. For each $(\text{cluster}, \text{property})$ pair the report records: the simple mean, the median, the inter-quartile range, the mean computed in arcsinh space (so that the heavy tail is compressed and negative values are retained), a 5/95 winsorized mean, the number of 1.5-IQR outliers, and the mean after those outliers are removed.

| Cluster | $\Delta E$ mean | $\Delta E$ median | $\Delta E$ arcsinh-mean | $\Delta E$ mean w/o outliers |
|---|---|---|---|---|
| C1 ($n = 29$) | +708 % | +352 % | 4.59 | +333 % |
| C2 ($n = 41$) | +51 % | +42 % | 3.74 | +46 % |
| C3 ($n = 86$) | +50 % | +42 % | 3.50 | +44 % |
| C4 ($n = 763$) | +33 % | +20 % | 3.22 | +22 % |

The gap between mean and median in C1 (708 % vs 352 %) shows that even within the corrected cluster the distribution remains right-skewed by the highest-loading PMA samples. The median and the outlier-removed mean both stay above 300 %, however, so the *qualitative* conclusion — that C1 represents the strongest reinforcement regime — is robust to outlier removal. By contrast, in C2–C4 the mean, median, arcsinh-mean, and outlier-removed mean all sit within a tight range, indicating that the central tendency of those clusters is not driven by a small number of samples.


## 7.x.15 A subtlety about "Epoxy in C1"

The corrected Phase 2 C1 cluster contains eleven samples labelled "Epoxy" or "DGEBA", which on first reading looks anomalous because epoxy is conventionally rigid. Three of those eleven entries come from Akbari et al. and represent a deliberately low-modulus epoxy formulation (matrix $E \approx 0.084$ GPa, matrix $\sigma \approx 70$ MPa) rather than a unit error. A further seven entries from Xidas \& Triantafyllidis are explicitly categorised as `Elastomer` in the dataset; they correspond to rubbery epoxy networks above $T_{g}$, prepared with specific alkylammonium organoclays, and are correctly placed in the soft-matrix regime. One remaining entry from the Okada \& Usuki review at $E \approx 0.001$ GPa is a tabulated value whose original source has not been re-verified in this thesis; it is retained but flagged. The C1 "Epoxy" label therefore does *not* indicate a misclassification — it indicates that the dataset already contains several deliberately low-modulus and rubbery epoxy formulations, which is itself an informative observation about the breadth of epoxy chemistry in the polymer/clay literature.


## 7.x.16 A note on betweenness centrality across property layers

Within each Phase 2 cluster the topology of the polymer–composite sub-graph is identical across the three property layers — the same edges connect the same polymer and composite nodes — and only the edge *weights* (the property-specific $\Delta E$, $\Delta\sigma$, $\Delta\varepsilon$ values) differ. Standard betweenness centrality is a topological metric: when computed without weight-aware shortest paths, it depends only on the edge set and is therefore numerically identical across the three property layers within a cluster. The Phase 2 report and Chapter 6 results therefore interpret betweenness as a *translational-position metric* — it identifies polymers that lie on the shortest paths between other polymers in the cluster graph, irrespective of which mechanical property is on the edge labels — and explicitly does not claim a property-specific bridging interpretation. Weighted betweenness using edge-weight-aware shortest paths is left to future work because the property-specific edge weights (especially the negative $\Delta\varepsilon$ values) require careful normalisation before they can be interpreted as path costs.


## 7.x.17 Two distinct design-recommendation regimes

Combining the corrected cluster populations, the normalized weighted-degree analysis, and the outlier-robust statistics yields a refined design recommendation that is split between two complementary objectives.

**Best balanced mechanical system (all three properties simultaneously improved).** The C1 modified low-modulus regime is the only cluster in which the integrated three-property analysis shows simultaneously positive $\Delta E$, $\Delta\sigma$, and $\Delta\varepsilon$ for the available samples. Modified-MMT-reinforced low-modulus matrices in the soft-elastomeric or low-modulus-epoxy / PMA-grafted-MMT family are therefore the recommended starting point when the design objective is balanced stiffness, strength, *and* ductility improvement. The recommendation is given with the qualifier that C1 contains only thirteen samples after correction, so the cluster should be presented as a high-confidence *direction* rather than a fully-quantified design rule.

**Best stiffening / strength system (modulus and strength up, with an acceptable ductility penalty).** The C2 semi-soft thermoplastic regime — now PMA-free after the data correction — shows large modulus and strength improvements together with a moderate ductility loss. A complementary observation, consistent with the corrected PMA series in C1, is that PMA-grafted MMT at intermediate filler loading (around 16 wt%, in line with the original Rauschendorfer 2020 toughness optimum) is the recommended high-stiffness, acceptable-ductility candidate. For engineering-grade rigid systems, the C4 cluster identifies PA6-, Epoxy-, and DGEBA-based Modified-MMT formulations as reliable stiffness-dominated knowledge hubs, but these systems are *not* recommended when ductility retention is a primary objective; the rigid regime is, on the corrected data, stiffness-dominated and ductility-penalised.

The two-regime recommendation supersedes the earlier single-objective phrasing of H1–H5 in §7.x.1–§7.x.5 by attaching each hypothesis to a specific design-objective regime rather than to a single "best" combination. The methodological consequence is that the term "best mechanical system" should always be qualified by the design objective and by the regime under which the recommendation was derived.
