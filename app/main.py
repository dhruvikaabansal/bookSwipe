from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import numpy as np
import faiss
import torch
import os
from fastapi.middleware.cors import CORSMiddleware
from models.infer_ranker import RankerInference
import logging

logging.basicConfig(filename='debug.log', level=logging.INFO, format='%(asctime)s %(message)s')

app = FastAPI(title="BookSwipe API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Setup
DB_PATH = "db/app.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Artifacts Loading
ARTIFACTS_DIR = "artifacts"
try:
    book_embeddings = np.load(os.path.join(ARTIFACTS_DIR, "book_embeddings.npy"))
    book_ids = np.load(os.path.join(ARTIFACTS_DIR, "book_ids.npy"))
    index = faiss.read_index(os.path.join(ARTIFACTS_DIR, "faiss.index"))
    ranker = RankerInference()
    
    # Create a mapping from book_id to index in embeddings
    book_id_to_idx = {bid: i for i, bid in enumerate(book_ids)}
    
    # Load metadata for quick access (in memory for prototype)
    import pandas as pd
    books_df = pd.read_csv("data/clean/books_clean.csv")
    books_meta = books_df.set_index("book_id").to_dict(orient="index")
    
except Exception as e:
    print(f"Error loading artifacts: {e}")
    book_embeddings = None
    index = None
    ranker = None
    books_meta = {}

# Models
class UserAction(BaseModel):
    user_id: str
    book_id: int

class BookResponse(BaseModel):
    book_id: int
    title: str
    author: str
    description: str
    genres: str
    avg_rating: float
    score: Optional[float] = None

# Endpoints

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth/demo-login")
def demo_login():
    return {"user_id": "demo_user", "token": "demo_token"}

@app.post("/user/{user_id}/like")
def like_book(user_id: str, action: UserAction, db: sqlite3.Connection = Depends(get_db)):
    db.execute(
        "INSERT OR REPLACE INTO user_actions (user_id, book_id, action) VALUES (?, ?, 'like')",
        (user_id, action.book_id)
    )
    db.commit()
    return {"status": "liked"}

@app.post("/user/{user_id}/pass")
def pass_book(user_id: str, action: UserAction, db: sqlite3.Connection = Depends(get_db)):
    db.execute(
        "INSERT OR REPLACE INTO user_actions (user_id, book_id, action) VALUES (?, ?, 'pass')",
        (user_id, action.book_id)
    )
    db.commit()
    return {"status": "passed"}

@app.get("/user/{user_id}/history")
def get_history(user_id: str, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("SELECT book_id, action FROM user_actions WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    return [{"book_id": r["book_id"], "action": r["action"]} for r in rows]

@app.get("/recommend", response_model=List[BookResponse])
def recommend(user_id: str, n: int = 10, genres: Optional[str] = None, db: sqlite3.Connection = Depends(get_db)):
    logging.info(f"Recommend called for user {user_id} with genres: {genres}")
    if index is None:
        logging.error("Index is None")
        raise HTTPException(status_code=503, detail="Search index not ready")

    # Parse requested genres
    requested_genres = []
    if genres:
        requested_genres = [g.strip().lower() for g in genres.split(',')]

    # 1. Get user history
    cursor = db.execute("SELECT book_id FROM user_actions WHERE user_id = ? AND action = 'like'", (user_id,))
    liked_ids = [r["book_id"] for r in cursor.fetchall()]
    
    # 2. Compute user profile
    user_emb = None
    if liked_ids:
        # Get embeddings for liked books
        liked_indices = [book_id_to_idx[bid] for bid in liked_ids if bid in book_id_to_idx]
        if liked_indices:
            user_emb = np.mean(book_embeddings[liked_indices], axis=0).reshape(1, -1)
            faiss.normalize_L2(user_emb)
    
    # If no user embedding (cold start), use a generic query or random
    if user_emb is None:
        # Create a random vector or use average of all books as a starting point
        # For now, let's pick a random book's embedding to simulate "exploration"
        import random
        rand_idx = random.randint(0, len(book_embeddings) - 1)
        user_emb = book_embeddings[rand_idx].reshape(1, -1)
    
    # 3. Retrieval
    # We retrieve more candidates to allow for filtering
    k = 2000 
    D, I = index.search(user_emb, k)
    candidate_indices = I[0]
    
    # Filter out already seen AND filter by genre
    cursor = db.execute("SELECT book_id FROM user_actions WHERE user_id = ?", (user_id,))
    seen_ids = set(r["book_id"] for r in cursor.fetchall())
    
    filtered_indices = []
    for idx in candidate_indices:
        if idx == -1: continue
        bid = book_ids[idx]
        
        if bid in seen_ids:
            continue
            
        # Genre Filtering
        if requested_genres:
            book_meta = books_meta.get(bid)
            if not book_meta: continue
            
            book_genres = str(book_meta.get('genres', '')).lower()
            match = False
            for rg in requested_genres:
                if rg in book_genres:
                    match = True
                    break
            if not match:
                continue
                
        filtered_indices.append(idx)
            
    if not filtered_indices and requested_genres:
        # Fallback: If vector search found nothing in this genre (e.g. user likes Romance but asked for Sci-Fi),
        # we manually search the database for books of this genre.
        logging.info("Vector search yielded 0 results for genre. Using fallback.")
        all_items = list(books_meta.items())
        import random
        random.shuffle(all_items)
        
        for bid, meta in all_items:
            if len(filtered_indices) >= n: break
            if bid in seen_ids: continue
            
            book_genres = str(meta.get('genres', '')).lower()
            match = False
            for rg in requested_genres:
                if rg in book_genres:
                    match = True
                    break
            
            if match:
                # Find the index for this book_id to get its embedding later
                if bid in book_id_to_idx:
                    filtered_indices.append(book_id_to_idx[bid])

    if not filtered_indices:
        # Final Fallback: just show something random if everything else failed
        pass
        
    # 4. Ranking
    if not filtered_indices:
         return []

    candidate_embs = book_embeddings[filtered_indices]
    scores = ranker.predict_score(user_emb[0], candidate_embs)
    
    # Sort by score
    ranked_results = sorted(zip(filtered_indices, scores), key=lambda x: x[1], reverse=True)[:n]
    
    results = []
    for idx, score in ranked_results:
        bid = book_ids[idx]
        meta = books_meta.get(bid)
        if meta:
            # Ensure book_id is in response and cast types
            meta_with_id = meta.copy()
            meta_with_id['book_id'] = int(bid)
            meta_with_id['score'] = float(score)
            results.append(BookResponse(**meta_with_id))
            
    return results

# Fix for book_id in meta
# When loading:
# books_df = pd.read_csv("data/clean/books_clean.csv")
# books_meta = books_df.set_index("book_id").to_dict(orient="index")
# The values in books_meta won't have 'book_id'.
# I handle this in the recommend function by adding it back.
