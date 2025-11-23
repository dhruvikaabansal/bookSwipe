import torch
import numpy as np
import os
# Define the model class again or import it if we structured it as a package
# For simplicity in this prototype, we redefine it here or expect it in a shared module.
# To keep it simple and standalone, I'll redefine the class structure.

import torch.nn as nn

class BookRanker(nn.Module):
    def __init__(self, input_dim):
        super(BookRanker, self).__init__()
        self.fc1 = nn.Linear(input_dim * 2, 64)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, user_emb, book_emb):
        x = torch.cat([user_emb, book_emb], dim=1)
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.sigmoid(self.fc3(x))
        return x

class RankerInference:
    def __init__(self, model_path="models/ranker.pt", input_dim=384):
        self.model = BookRanker(input_dim)
        if os.path.exists(model_path):
            try:
                self.model.load_state_dict(torch.load(model_path))
                self.model.eval()
                self.available = True
            except Exception as e:
                print(f"Error loading model: {e}. Using fallback.")
                self.available = False
        else:
            print(f"Warning: Ranker model not found at {model_path}. Using fallback.")
            self.available = False

    def predict_score(self, user_embedding, candidate_embeddings):
        """
        user_embedding: np.array (D,)
        candidate_embeddings: np.array (N, D)
        Returns: np.array (N,) scores
        """
        # Calculate Cosine Similarity first as a baseline/fallback
        # Assume embeddings are already normalized or close to it
        # Cosine sim is between -1 and 1
        
        # Normalize just in case
        user_norm = np.linalg.norm(user_embedding)
        cand_norm = np.linalg.norm(candidate_embeddings, axis=1)
        
        # Avoid division by zero
        if user_norm == 0: user_norm = 1e-9
        cand_norm[cand_norm == 0] = 1e-9
        
        dot_products = np.dot(candidate_embeddings, user_embedding)
        cosine_sims = dot_products / (user_norm * cand_norm)
        
        # Map cosine similarity (-1 to 1) to a "Match Score" (0% to 100%)
        # Previous formula was too conservative (60-99%).
        # New formula: (cosine_sim + 1) / 2
        # -1 -> 0.0
        #  0 -> 0.5
        #  1 -> 1.0
        fallback_scores = (cosine_sims + 1) / 2
        
        if not self.available:
            return fallback_scores
            
        # FORCE FALLBACK for prototype
        # The neural network is currently untrained and produces poor results.
        # We rely 100% on the Cosine Similarity (Content-Based) metric for now.
        return fallback_scores

        # try:
        #     with torch.no_grad():
        #         # Prepare batch
        #         n = len(candidate_embeddings)
        #         user_emb_tensor = torch.tensor(user_embedding, dtype=torch.float32).unsqueeze(0).repeat(n, 1)
        #         cand_emb_tensor = torch.tensor(candidate_embeddings, dtype=torch.float32)
        #         
        #         # Model output is sigmoid (0 to 1)
        #         model_scores = self.model(user_emb_tensor, cand_emb_tensor).squeeze().numpy()
        #         
        #         # If model outputs are too flat (e.g. untrained), mix with fallback
        #         if np.std(model_scores) < 0.01:
        #              return fallback_scores
        #         
        #         return model_scores
        # except Exception as e:
        #     print(f"Inference error: {e}. Using fallback.")
        #     return fallback_scores
