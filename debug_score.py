import numpy as np
import torch
from models.infer_ranker import RankerInference

def debug_scores():
    print("Initializing Ranker...")
    ranker = RankerInference()
    
    print(f"Model available: {ranker.available}")
    
    # Create dummy embeddings
    # User embedding (1, 384)
    user_emb = np.random.rand(384).astype(np.float32)
    user_emb = user_emb / np.linalg.norm(user_emb)
    
    # Candidate embeddings (10, 384)
    # Make some very similar and some very different
    cand_embs = []
    
    # 1. Perfect match
    cand_embs.append(user_emb)
    
    # 2. Opposite match
    cand_embs.append(-user_emb)
    
    # 3. Random matches
    for _ in range(8):
        vec = np.random.rand(384).astype(np.float32)
        vec = vec / np.linalg.norm(vec)
        cand_embs.append(vec)
        
    cand_embs = np.array(cand_embs)
    
    print("\n--- Predicting Scores ---")
    scores = ranker.predict_score(user_emb, cand_embs)
    
    print("Scores output:", scores)
    print("Standard Deviation:", np.std(scores))
    
    # Check fallback logic manually
    print("\n--- Manual Fallback Check ---")
    dot_products = np.dot(cand_embs, user_emb)
    # norms are 1
    cosine_sims = dot_products
    fallback_scores = 0.6 + (cosine_sims + 1) / 2 * 0.39
    print("Calculated Fallback Scores:", fallback_scores)
    
    if ranker.available:
        with torch.no_grad():
            n = len(cand_embs)
            user_emb_tensor = torch.tensor(user_emb, dtype=torch.float32).unsqueeze(0).repeat(n, 1)
            cand_emb_tensor = torch.tensor(cand_embs, dtype=torch.float32)
            model_scores = ranker.model(user_emb_tensor, cand_emb_tensor).squeeze().numpy()
            print("Raw Model Scores:", model_scores)
            print("Model Std Dev:", np.std(model_scores))

if __name__ == "__main__":
    debug_scores()
