import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import os

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

def train_ranker():
    artifacts_dir = "artifacts"
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    # Load embeddings
    print("Loading embeddings...")
    try:
        book_embeddings = np.load(os.path.join(artifacts_dir, "book_embeddings.npy"))
        book_ids = np.load(os.path.join(artifacts_dir, "book_ids.npy"))
    except FileNotFoundError:
        print("Artifacts not found. Run scripts/build_index.py first.")
        return

    # Simulate training data
    # In a real scenario, we'd use actual user logs. Here we simulate:
    # Positive: User likes a book -> User embedding is close to book embedding
    # Negative: Random book
    
    print("Simulating training data...")
    num_samples = 10000
    input_dim = book_embeddings.shape[1]
    
    user_embs = []
    item_embs = []
    labels = []
    
    for _ in range(num_samples):
        # Pick a "target" book the user likes
        target_idx = np.random.randint(0, len(book_embeddings))
        target_emb = book_embeddings[target_idx]
        
        # Create a user embedding somewhat close to the target (simulating history)
        noise = np.random.normal(0, 0.1, input_dim)
        user_emb = target_emb + noise
        
        # Positive sample
        user_embs.append(user_emb)
        item_embs.append(target_emb)
        labels.append(1.0)
        
        # Negative sample (random book)
        neg_idx = np.random.randint(0, len(book_embeddings))
        neg_emb = book_embeddings[neg_idx]
        
        user_embs.append(user_emb)
        item_embs.append(neg_emb)
        labels.append(0.0)
        
    X_user = torch.tensor(np.array(user_embs), dtype=torch.float32)
    X_item = torch.tensor(np.array(item_embs), dtype=torch.float32)
    y = torch.tensor(np.array(labels), dtype=torch.float32).unsqueeze(1)
    
    # Train/Val split
    X_user_train, X_user_val, X_item_train, X_item_val, y_train, y_val = train_test_split(
        X_user, X_item, y, test_size=0.2
    )
    
    # Model
    model = BookRanker(input_dim)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    print("Training ranker...")
    epochs = 5
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        outputs = model(X_user_train, X_item_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()
        
        model.eval()
        with torch.no_grad():
            val_outputs = model(X_user_val, X_item_val)
            val_loss = criterion(val_outputs, y_val)
            predicted = (val_outputs > 0.5).float()
            accuracy = (predicted == y_val).float().mean()
            
        print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}, Val Loss: {val_loss.item():.4f}, Val Acc: {accuracy.item():.4f}")
        
    torch.save(model.state_dict(), os.path.join(models_dir, "ranker.pt"))
    print("Model saved to models/ranker.pt")

if __name__ == "__main__":
    train_ranker()
