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
