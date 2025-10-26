import json, os
from sentence_transformers import SentenceTransformer, util

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "games.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    games_data = json.load(f)

# Gunakan kombinasi teks biar konteks makin kuat
game_names = [g["name"] for g in games_data]
texts = [
    f"{g['name']} | Genres: {', '.join(g.get('genres', []))} | {g.get('description_raw', '')}"
    for g in games_data
]

print("🧠 Memuat model AI (SentenceTransformer)...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("📊 Membuat embedding (ini agak lama)...")
embeddings = model.encode(texts, convert_to_tensor=True)

def find_closest_name(user_input):
    query_emb = model.encode(user_input, convert_to_tensor=True)
    scores = util.pytorch_cos_sim(query_emb, embeddings)[0]
    best_idx = scores.argmax().item()
    return game_names[best_idx], best_idx

def recommend_game(user_input):
    best_name, best_idx = find_closest_name(user_input)
    query_emb = embeddings[best_idx]

    cosine_scores = util.pytorch_cos_sim(query_emb, embeddings)[0]
    results = sorted(zip(game_names, cosine_scores.tolist()), key=lambda x: x[1], reverse=True)
    top10 = [r for r in results if r[0] != best_name][:10]

    result_text = f"🎮 *Rekomendasi game mirip dengan {best_name}:*\n\n"
    for i, (name, score) in enumerate(top10, start=1):
        result_text += f"{i}. {name} — {score * 100:.2f}% kemiripan\n"
    return result_text
