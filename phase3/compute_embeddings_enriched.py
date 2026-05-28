"""
Phase 3 — Enriched node embeddings (Advisor Suggestion 1).

Re-encodes all concept nodes after augmenting each description with 1-2
sentences of domain-specific chemistry / physics context drawn from
polymer- and clay-nanocomposite literature. Polymer matrices, clay
modifications, dispersion morphologies, polymer categories, and test
methods all receive a short, factual descriptor before the dataset-derived
statistics are appended.

Output:
  output/embeddings_enriched.npz
  output/node_descriptions_enriched.txt

A separate comparison script (compare_embeddings_before_after.py) then
contrasts the enriched embeddings with the original embeddings.npz.
"""
import os
import numpy as np
import networkx as nx

GRAPH_GEXF = "output/complete_graph.gexf"
OUT = "output"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# ----- Domain knowledge dictionaries -----------------------------------------

POLYMER_CHEMISTRY = {
    # Polyamide family
    "PA6":  "semi-crystalline aliphatic polyamide (nylon-6) formed by ring-opening polymerization of ε-caprolactam, with strong inter-chain hydrogen bonding between amide groups",
    "PA12": "semi-crystalline polyamide (nylon-12) with longer hydrocarbon spacer between amide groups, giving lower water uptake and lower modulus than PA6",
    "PA66": "semi-crystalline aliphatic polyamide (nylon-6,6) with alternating diamine and diacid units, higher melting point than PA6",
    "PA":   "generic aliphatic polyamide family, semi-crystalline engineering thermoplastics with strong hydrogen-bonded backbones",
    "PA7":  "less common odd-numbered polyamide variant in the nylon family",
    "PA8":  "less common odd-numbered polyamide variant in the nylon family",
    "Nylon 6": "common name for PA6",
    "Nylon 66": "common name for PA66",
    "PA6/PP":   "binary blend of polyamide-6 and polypropylene, used to balance polarity and processability",

    # Polyolefins
    "PP":     "isotactic polypropylene, a low-surface-energy semi-crystalline polyolefin with limited intrinsic compatibility with polar fillers like clay",
    "HDPE":   "high-density polyethylene, a strongly crystalline, non-polar polyolefin",
    "LLDPE":  "linear low-density polyethylene with short-chain branching and improved toughness",
    "PE":     "generic polyethylene; non-polar polyolefin",
    "PP/EPDM":"polypropylene blended with ethylene-propylene-diene rubber for impact modification",
    "PP/PC":  "polypropylene/polycarbonate blend used for combined toughness and stiffness",
    "PP/PLA": "polypropylene/polylactic-acid blend balancing biodegradability with mechanical performance",

    # Acrylates / methacrylates
    "PMMA": "atactic poly(methyl methacrylate), an amorphous glassy acrylic polymer known for optical transparency and moderate stiffness",
    "PMA":  "poly(methyl acrylate), a rubbery acrylic polymer with low glass-transition temperature (around 10 °C), giving it elastomer-like behaviour at room temperature",
    "PVA":  "poly(vinyl alcohol), water-soluble polymer rich in hydroxyl groups, with strong polarity",
    "PVC":  "poly(vinyl chloride), amorphous polar polymer typically used with plasticizers; halogenated backbone",
    "PVP":  "poly(vinyl pyrrolidone), water-soluble amorphous polymer with strong dipole moment",

    # Thermosets
    "Epoxy":   "thermosetting polymer formed by curing diglycidyl-ether-based resins with amine or anhydride hardeners; high cross-link density and inherently brittle failure",
    "DGEBA":   "diglycidyl ether of bisphenol-A, the most widely used epoxy resin precursor",
    "EPON 828":"a commercial DGEBA-type epoxy resin",
    "UP":      "unsaturated polyester, low-cost thermoset cured by free-radical polymerization of vinyl monomers (typically styrene)",
    "Vinyl Ester":"thermoset combining unsaturated polyester chemistry with epoxy-like backbone for improved toughness",
    "Bis-GMA/TTEGDMA":"dimethacrylate dental-resin formulation based on bisphenol-A glycidyl methacrylate diluted with triethyleneglycol dimethacrylate",
    "DGEAC":   "diglycidyl ether of aliphatic compound; aliphatic epoxy variant",
    "Dimethacrylate Copolymer":"dental/biomedical dimethacrylate thermoset",

    # Biodegradable
    "PLA":      "polylactic acid, biodegradable aliphatic polyester from lactic-acid monomers; semi-crystalline, with relatively low toughness",
    "PLLA":     "poly-L-lactic acid, optically pure stereoisomer of PLA",
    "PLA/PBAT": "polylactic-acid blended with poly(butylene adipate terephthalate) for improved ductility while remaining biodegradable",
    "PLA/PP":   "biodegradable PLA blended with polypropylene",
    "PCL":      "polycaprolactone, biodegradable semi-crystalline polyester with very low melting point (~60 °C)",
    "PBT":      "poly(butylene terephthalate), engineering thermoplastic polyester",
    "PHBV":     "poly(3-hydroxybutyrate-co-3-hydroxyvalerate), bacterial biopolyester",
    "BIOPA11":  "bio-based polyamide-11 derived from castor oil, semi-crystalline",
    "Chitosan": "naturally derived polysaccharide with -NH2 functional groups",
    "rPET":     "recycled poly(ethylene terephthalate)",

    # Elastomers
    "NBR":   "acrylonitrile-butadiene rubber, a polar elastomer in which nitrile groups give chemical resistance and the cationic clay surface a natural ionic affinity",
    "CNBR":  "carboxylated nitrile rubber, an NBR variant with pendant -COOH groups that further enhance polar/ionic interactions",
    "NBR/PU":"NBR/polyurethane blend for combined chemical and abrasion resistance",
    "PU":    "polyurethane, segmented block copolymer with tunable hard- and soft-segment ratios",
    "NR":    "natural rubber, cis-polyisoprene with very high elongation and resilience",

    # Glassy / niche
    "PS":   "atactic polystyrene, amorphous glassy polymer with brittle failure",
    "PSF":  "polysulfone, amorphous high-performance thermoplastic with high glass-transition temperature",
    "PI":   "polyimide, high-temperature aromatic engineering polymer",
    "MGSL135i":"specific dental-/biomedical-grade resin commercial product",
    "PPH1":   "polypropylene homopolymer grade variant",
    "PPH2":   "polypropylene homopolymer grade variant",
    "PPH3":   "polypropylene homopolymer grade variant",
    "PPH4":   "polypropylene homopolymer grade variant",
    "PPH1/PP":"polypropylene homopolymer blend variant",
    "PPH2/PP":"polypropylene homopolymer blend variant",
    "PPH3/PP":"polypropylene homopolymer blend variant",
    "PPH4/PP":"polypropylene homopolymer blend variant",
    "Nylon 7": "less common odd-numbered nylon variant",
    "Nylon 8": "less common odd-numbered nylon variant",
    "Nylon66": "alternative spelling of PA66",
    "Nylon 6": "alternative spelling of PA6",
}

MODIFICATION_DESCRIPTIONS = {
    "Modified":  "organomodified montmorillonite (OMMT) in which the native sodium counter-ions of the clay galleries have been exchanged with organic surfactant cations (typically quaternary alkylammonium) so as to increase the d-spacing and improve compatibility with low-polarity polymers",
    "Unmodified":"pristine sodium montmorillonite with native Na+ inter-layer cations; the hydrophilic surface limits compatibility with non-polar polymers but preserves the native ionic affinity for polar polymers and elastomers",
}

DISPERSION_PHYSICS = {
    "intercalated":              "polymer chains have penetrated the inter-layer galleries of the clay so the d-spacing increases, but the layered silicate stacks remain intact",
    "exfoliated":                "individual clay platelets are fully separated and dispersed homogeneously throughout the polymer matrix, providing maximum interfacial area",
    "intercalated/exfoliated":   "mixed morphology containing both intercalated stacks and exfoliated single platelets coexisting in the same composite",
    "Exfoliated/intercalated":   "mixed morphology containing both intercalated stacks and exfoliated single platelets coexisting in the same composite",
    "microcomposite":            "no nanoscale intercalation has been achieved; the clay remains in large micron-scale agglomerates and behaves as a conventional filler",
    "agglomerated":              "clay particles are clustered into agglomerates rather than dispersed, often acting as stress concentrators that nucleate failure",
    "disordered intercalated/exfoliated":"a disordered combination of partially intercalated and partially exfoliated clay structures without long-range order",
    "intercalated/microcomposite":"co-existence of intercalated regions and unintercalated micron-scale agglomerates",
    "intercalated/agglomerated":  "intercalated nanocomposite regions coexisting with poorly dispersed agglomerates",
    "intercalated/partially exfoliated":"intercalated clay stacks with partial exfoliation of single platelets at the edges",
    "Partially exfoliated":      "clay platelets partly separated from their parent stacks but not fully isolated",
    "Partially exfoliated/disordered intercalated":"partial exfoliation combined with disordered intercalation regions",
    "intercalated with agglomeration":"intercalated nanocomposite regions with localized agglomeration",
    "Mixed":                     "mixed dispersion state without a single dominant morphology",
    "Mixed (mostly intercalated)":"mixed dispersion state in which intercalated morphology dominates",
}

CATEGORY_DESCRIPTIONS = {
    "Thermoset":     "cross-linked polymer with a permanent three-dimensional covalent network; the cured polymer cannot be remelted or reprocessed",
    "Thermoplastic": "linear or branched polymer whose physical entanglements melt reversibly upon heating, allowing repeated reprocessing",
    "Elastomer":     "lightly cross-linked rubbery polymer capable of large reversible elastic deformation at and above room temperature",
}

TEST_METHOD_DESCRIPTIONS = {
    "Tensile Test":                          "uniaxial extension to failure following ISO 527 / ASTM D638; reports elastic modulus, tensile strength, and strain to failure",
    "Flexural Test":                         "three- or four-point bending test that reports flexural modulus and flexural strength",
    "Flexural Test (Three Point Bending)":   "three-point bending per ASTM D790 or ISO 178; reports flexural modulus and flexural strength",
    "Dynamic Mechanical Analysis":           "DMA: small-amplitude oscillatory deformation as a function of temperature and frequency; reports storage modulus E', loss modulus E'', and tan δ",
    "Compression Test":                      "uniaxial compression to measure compressive modulus and yield strength",
    "Nanoindentation":                       "instrumented indentation at the micro- or nano-scale; reports local modulus and hardness with depth resolution",
    "Three-Point Bend":                      "three-point bending; equivalent to flexural test",
    "Split Hopkinson Pressure Bar":          "high-strain-rate dynamic compression test for impact-rate stress-strain behaviour",
    "Impact Test":                           "instrumented Charpy or Izod test reporting impact toughness",
    "Short Beam Shear Test":                 "interlaminar shear test for fibre-reinforced composites",
    "Instrumented-indentation":              "depth-sensing indentation producing load-displacement curves for modulus and hardness",
    "Tensile/SENB":                          "single-edge-notch-bend fracture-toughness test combined with tensile characterisation",
    "FEM (COMSOL)":                          "finite-element simulation using the COMSOL Multiphysics package",
    "Finite Element Method":                 "finite-element numerical simulation of the mechanical response",
    "Compact Tension":                       "compact-tension geometry for plane-strain fracture-toughness measurement",
    "SENB/DMA":                              "single-edge-notch-bend fracture testing combined with dynamic mechanical analysis",
    "TEM/SEM/CT":                            "transmission electron microscopy, scanning electron microscopy, and X-ray computed tomography characterisation",
    "Tensile/DMA":                           "tensile testing combined with dynamic mechanical analysis",
    "DMA/SEN":                               "dynamic mechanical analysis combined with single-edge-notch fracture testing",
}

DATA_SOURCE_DESCRIPTIONS = {
    "Experimental": "data obtained from physical laboratory measurements on prepared specimens",
    "Simulated":    "data obtained from computational simulations (typically finite-element or molecular models) rather than physical experiments",
}


# ----- Description builder ---------------------------------------------------

def _fmt(v, unit="", dec=2):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    return f"{v:.{dec}f}{unit}"


def describe_node_enriched(G, n, d):
    """Enriched description: 1-2 sentences of domain context + dataset stats."""
    ntype = d["node_type"]
    label = d["label"]
    n_rows = int(d.get("n_rows", 0)) if not (isinstance(d.get("n_rows"), float)
                                             and np.isnan(d.get("n_rows"))) else 0
    parts = []

    # Lead with domain context (NEW — Suggestion 1)
    if ntype == "polymer":
        chem = POLYMER_CHEMISTRY.get(label, "polymer matrix")
        parts.append(f"{label} is a {chem}.")
        parts.append(f"It is used as the matrix in {n_rows} montmorillonite clay nanocomposite experiments.")
    elif ntype == "modification":
        ctx = MODIFICATION_DESCRIPTIONS.get(label, "")
        parts.append(f"{label} clay: {ctx}.")
        parts.append(f"Used in {n_rows} experiments.")
    elif ntype == "dispersion":
        ctx = DISPERSION_PHYSICS.get(label, "")
        parts.append(f"{label}: {ctx}.")
        parts.append(f"Observed in {n_rows} experiments.")
    elif ntype == "category":
        ctx = CATEGORY_DESCRIPTIONS.get(label, "")
        parts.append(f"{label} polymer family: {ctx}.")
        parts.append(f"Used in {n_rows} experiments.")
    elif ntype == "test_method":
        ctx = TEST_METHOD_DESCRIPTIONS.get(label, "mechanical characterisation method")
        parts.append(f"{label}: {ctx}.")
        parts.append(f"Applied in {n_rows} experiments.")
    elif ntype == "data_source":
        ctx = DATA_SOURCE_DESCRIPTIONS.get(label, "")
        parts.append(f"{label} data: {ctx}.")
        parts.append(f"Covers {n_rows} entries.")
    elif ntype == "article":
        snippet = label[:120].replace("\n", " ")
        parts.append(f"Research article on polymer/clay nanocomposites: {snippet}.")
        parts.append(f"Contains {n_rows} experiments contributed to the dataset.")
    else:
        parts.append(f"{label} ({ntype}, {n_rows} experiments).")

    # Append dataset-derived statistics (same as before)
    e  = _fmt(d.get("mean_matrix_modulus"),  " GPa")
    s  = _fmt(d.get("mean_matrix_strength"), " MPa")
    st = _fmt(d.get("mean_matrix_strain"))
    bits = []
    if e:  bits.append(f"average matrix elastic modulus {e}")
    if s:  bits.append(f"average matrix strength {s}")
    if st: bits.append(f"average matrix strain to failure {st}")
    if bits:
        parts.append("Associated polymer matrices have " + ", ".join(bits) + ".")

    de  = _fmt(d.get("mean_dE_modulus"),      "%", 1)
    ds  = _fmt(d.get("mean_dsigma_strength"), "%", 1)
    dst = _fmt(d.get("mean_de_strain"),       "%", 1)
    imp = []
    if de:  imp.append(f"modulus improvement {de}")
    if ds:  imp.append(f"strength improvement {ds}")
    if dst: imp.append(f"strain-to-failure change {dst}")
    if imp:
        parts.append("With clay reinforcement, average " + ", ".join(imp) + ".")

    mmt = _fmt(d.get("mean_MMT_pct"), " wt%", 1)
    if mmt:
        parts.append(f"Typical MMT loading {mmt}.")

    return " ".join(parts)


# ----- Main ------------------------------------------------------------------

def main():
    os.makedirs(OUT, exist_ok=True)
    print("Loading graph...")
    G = nx.read_gexf(GRAPH_GEXF)

    # Only concept nodes (skip 942 sample nodes and 28 property bins)
    nodes = [n for n, d in G.nodes(data=True)
             if d.get("node_type") not in ("sample", "property_bin")]
    print(f"Concept nodes to enrich: {len(nodes)}")

    descriptions = []
    with open(f"{OUT}/node_descriptions_enriched.txt", "w") as f:
        for n in nodes:
            txt = describe_node_enriched(G, n, G.nodes[n])
            descriptions.append(txt)
            f.write(f"[{n}]\n{txt}\n\n")

    print(f"Loading model: {MODEL_NAME}")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL_NAME)

    print(f"Encoding {len(descriptions)} enriched descriptions...")
    emb = model.encode(descriptions, show_progress_bar=False,
                       normalize_embeddings=True)
    print(f"Embeddings shape: {emb.shape}")

    np.savez(f"{OUT}/embeddings_enriched.npz",
             embeddings=emb,
             node_ids=np.array(nodes),
             descriptions=np.array(descriptions))
    print(f"\nSaved to {OUT}/embeddings_enriched.npz")


if __name__ == "__main__":
    main()
