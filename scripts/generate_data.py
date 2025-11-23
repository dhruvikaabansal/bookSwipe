import pandas as pd
import random
import os

def generate_synthetic_books(num_books=5000):
    titles_start = ["The", "A", "My", "Our", "Lost", "Found", "Hidden", "Secret", "Dark", "Bright"]
    titles_mid = ["Journey", "Adventure", "Mystery", "Love", "Life", "Death", "World", "Star", "Moon", "Sun"]
    titles_end = ["Begins", "Ends", "Returns", "Falls", "Rises", "Forever", "Today", "Tomorrow", "Yesterday"]
    
    authors_first = ["John", "Jane", "Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Henry"]
    authors_last = ["Smith", "Doe", "Johnson", "Brown", "Williams", "Jones", "Miller", "Davis", "Garcia", "Rodriguez"]
    
    genres_list = ["Fiction", "Non-Fiction", "Sci-Fi", "Fantasy", "Mystery", "Thriller", "Romance", "History", "Biography", "Self-Help"]
    
    books = []
    for i in range(num_books):
        title = f"{random.choice(titles_start)} {random.choice(titles_mid)} {random.choice(titles_end)}"
        author = f"{random.choice(authors_first)} {random.choice(authors_last)}"
        description = f"A {random.choice(['gripping', 'heartwarming', 'thrilling', 'insightful'])} story about {random.choice(['love', 'loss', 'hope', 'courage'])} in a {random.choice(['dystopian', 'magical', 'modern', 'historical'])} world."
        genres = "|".join(random.sample(genres_list, k=random.randint(1, 3)))
        avg_rating = round(random.uniform(3.0, 5.0), 2)
        num_ratings = random.randint(10, 10000)
        tags = f"{random.choice(['bestseller', 'classic', 'new-release', 'award-winning'])},{random.choice(['must-read', 'book-club', 'summer-read'])}"
        
        books.append({
            "book_id": i + 1,
            "title": title,
            "author": author,
            "description": description,
            "genres": genres,
            "avg_rating": avg_rating,
            "num_ratings": num_ratings,
            "tags": tags
        })
        
    df = pd.DataFrame(books)
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv("data/raw/books.csv", index=False)
    print(f"Generated {num_books} synthetic books in data/raw/books.csv")

if __name__ == "__main__":
    generate_synthetic_books()
