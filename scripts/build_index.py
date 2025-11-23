import pandas as pd
import numpy as np
import faiss
import os
from sentence_transformers import SentenceTransformer

def build_index():
    data_path = "data/clean/books_clean.csv"
    artifacts_dir = "artifacts"
    os.makedirs(artifacts_dir, exist_ok=True)
    
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return

    print("Loading data...")
    df = pd.read_csv(data_path)
    
    # Use a small, fast model for CPU
    model_name = 'all-MiniLM-L6-v2'
    print(f"Loading model {model_name}...")
    model = SentenceTransformer(model_name)
    
    print("Computing embeddings...")
    # Embed the combined text field
    sentences = df['combined_text'].tolist()
    embeddings = model.encode(sentences, show_progress_bar=True)
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Save embeddings and IDs
    print("Saving artifacts...")
    np.save(os.path.join(artifacts_dir, "book_embeddings.npy"), embeddings)
    np.save(os.path.join(artifacts_dir, "book_ids.npy"), df['book_id'].values)
    
    # Build Faiss Index
    print("Building Faiss index...")
    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d) # Inner Product (Cosine Similarity since normalized)
    index.add(embeddings)
    
    faiss.write_index(index, os.path.join(artifacts_dir, "faiss.index"))
    print(f"Index built with {index.ntotal} vectors.")

if __name__ == "__main__":
    build_index()
