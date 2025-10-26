from sentence_transformers import SentenceTransformer, util

# Load model sekali saja
_model = SentenceTransformer("all-MiniLM-L6-v2")

def find_best_match(query: str, candidates: list, top_k: int = 1):
    """
    Cari game paling mirip dengan query.
    """
    if not candidates:
        return []

    embeddings_q = _model.encode(query, convert_to_tensor=True)
    embeddings_c = _model.encode(candidates, convert_to_tensor=True)

    cosine_scores = util.cos_sim(embeddings_q, embeddings_c)[0]
    top_results = cosine_scores.topk(min(top_k, len(candidates)))
    results = []
    for score, idx in zip(top_results.values.tolist(), top_results.indices.tolist()):
        results.append((candidates[idx], float(score)))
    return results
