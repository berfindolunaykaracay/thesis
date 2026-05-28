"""
Phase 3 — Multi-model embedding comparison (Advisor Suggestion 2).

Encodes the SAME enriched node descriptions with four different transformer
models and saves each set of embeddings for downstream comparison.

Models compared:
  1. sentence-transformers/all-MiniLM-L6-v2  (general English, 384-d) — baseline
  2. allenai/scibert_scivocab_uncased        (scientific papers, 768-d)
  3. m3rg-iitd/matscibert                    (materials-science papers, 768-d)
  4. pranav-s/MaterialsBERT                  (materials-domain BERT, 768-d)

For BERT-style models (2-4), we use mean-pooling over the last hidden state
to obtain a single 768-d sentence vector. Vectors are L2-normalized to make
cosine comparable across models.

Output (one .npz per model):
  output/embeddings_minilm_enriched.npz
  output/embeddings_scibert.npz
  output/embeddings_matscibert.npz
  output/embeddings_materialsbert.npz
"""
import os
import numpy as np
import networkx as nx

GRAPH_GEXF = "output/complete_graph.gexf"
OUT = "output"

MODELS = {
    "minilm":       "sentence-transformers/all-MiniLM-L6-v2",
    "scibert":      "allenai/scibert_scivocab_uncased",
    "matscibert":   "m3rg-iitd/matscibert",
    "materialsbert":"pranav-s/MaterialsBERT",
}


def load_descriptions():
    """Re-build the same enriched descriptions used in compute_embeddings_enriched.py.
    We load directly from the saved npz so all four models see the same text."""
    data = np.load(f"{OUT}/embeddings_enriched.npz", allow_pickle=True)
    return list(data["descriptions"]), list(data["node_ids"])


def encode_sentence_transformer(model_name, texts):
    from sentence_transformers import SentenceTransformer
    print(f"  Loading sentence-transformers model: {model_name}")
    m = SentenceTransformer(model_name)
    return m.encode(texts, show_progress_bar=False, normalize_embeddings=True)


def mean_pool(token_embeddings, attention_mask):
    """Standard sentence-BERT mean pooling."""
    import torch
    mask = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    summed = torch.sum(token_embeddings * mask, 1)
    counts = torch.clamp(mask.sum(1), min=1e-9)
    return summed / counts


def encode_bert(model_name, texts, batch_size=8):
    """Mean-pool + L2 normalize a BERT-style model."""
    import torch
    from transformers import AutoTokenizer, AutoModel
    print(f"  Loading HF model: {model_name}")
    tok = AutoTokenizer.from_pretrained(model_name)
    mdl = AutoModel.from_pretrained(model_name)
    mdl.eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            enc = tok(batch, padding=True, truncation=True, max_length=256,
                      return_tensors="pt")
            o = mdl(**enc)
            pooled = mean_pool(o.last_hidden_state, enc["attention_mask"])
            # L2 normalize
            pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
            out.append(pooled.cpu().numpy())
    return np.vstack(out)


def main():
    os.makedirs(OUT, exist_ok=True)
    print("Loading enriched descriptions and node ids...")
    descriptions, node_ids = load_descriptions()
    print(f"  {len(descriptions)} descriptions, {len(node_ids)} node ids")

    for key, mname in MODELS.items():
        out_path = f"{OUT}/embeddings_{key}.npz"
        if os.path.exists(out_path) and key != "minilm":
            print(f"\n[{key}] already exists at {out_path}, skipping")
            continue
        print(f"\n[{key}] {mname}")
        try:
            if key == "minilm":
                emb = encode_sentence_transformer(mname, descriptions)
            else:
                emb = encode_bert(mname, descriptions)
            np.savez(out_path,
                     embeddings=emb,
                     node_ids=np.array(node_ids),
                     descriptions=np.array(descriptions),
                     model=mname)
            print(f"  Saved: shape={emb.shape} → {out_path}")
        except Exception as e:
            print(f"  FAILED: {e}")
            print(f"  (skipping {key}; will be missing from comparison)")


if __name__ == "__main__":
    main()
