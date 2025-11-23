# BookSwipe 📚

A Tinder-style book recommendation app that learns from your likes and dislikes.

## Features
- **Swipe UI**: Like (Right) or Pass (Left) on books.
- **Smart Recommendations**: Uses sentence-transformers + Faiss + Neural Ranker to suggest books based on your history.
- **Demo Mode**: Try it out without logging in.

## Quickstart (Docker)

Prerequisites: Docker & Docker Compose.

```bash
docker-compose up --build
```

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Local Development (Manual)

### Backend
1. Install Python 3.11+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Generate Data & Build Artifacts:
   ```bash
   python scripts/generate_data.py
   python data/preprocess.py
   python scripts/build_index.py
   python models/train_ranker.py
   ```
4. Run API:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend
1. Install Node.js 18+
2. Setup & Run:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Architecture
- **Embeddings**: `all-MiniLM-L6-v2` (Sentence Transformers)
- **Vector DB**: Faiss (FlatIP)
- **Ranker**: PyTorch MLP (User History Mean + Candidate -> Score)
- **Backend**: FastAPI
- **Frontend**: React + Vite

## Privacy
This is a demo application. No personal data is stored persistently outside the local SQLite database.
