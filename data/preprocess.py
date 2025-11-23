import pandas as pd
import os
from sklearn.model_selection import train_test_split

def preprocess_data():
    # Check for real data first
    real_data_dir = "data/goodbooks-10k"
    real_data_path = os.path.join(real_data_dir, "books.csv")
    
    if os.path.exists(real_data_path):
        print(f"Using real data from {real_data_path}")
        df = pd.read_csv(real_data_path)
        
        # Load tags to get real genres
        try:
            tags_df = pd.read_csv(os.path.join(real_data_dir, "tags.csv"))
            book_tags_df = pd.read_csv(os.path.join(real_data_dir, "book_tags.csv"))
            
            print("Mapping tags to genres...")
            # Define standard genres we want to track
            target_genres = {
                'fantasy', 'science-fiction', 'sci-fi', 'mystery', 'thriller', 'romance', 
                'historical-fiction', 'young-adult', 'children', 'non-fiction', 'biography', 
                'history', 'self-help', 'business', 'poetry', 'comics', 'graphic-novels', 
                'horror', 'crime', 'classics', 'philosophy', 'psychology', 'travel', 'cooking'
            }
            
            # Normalize tag names
            tags_df['tag_name'] = tags_df['tag_name'].astype(str).str.lower().str.strip()
            
            # Filter for tags that match our target genres
            # We map variations to standard names
            genre_map = {
                'science-fiction': 'Science Fiction', 'sci-fi': 'Science Fiction',
                'historical-fiction': 'Historical',
                'young-adult': 'Young Adult',
                'graphic-novels': 'Graphic Novels',
                'self-help': 'Self Help'
            }
            
            def map_genre(tag):
                if tag in target_genres:
                    return genre_map.get(tag, tag.title())
                return None

            tags_df['genre'] = tags_df['tag_name'].apply(map_genre)
            valid_tags = tags_df.dropna(subset=['genre'])
            
            # Merge book_tags with valid genre tags
            # book_tags: goodreads_book_id, tag_id, count
            # books.csv has 'book_id' which matches 'goodreads_book_id' in book_tags usually, 
            # BUT in this dataset:
            # books.csv 'book_id' is 1-10000. 'goodreads_book_id' is the actual ID.
            # book_tags.csv 'goodreads_book_id' refers to the actual GoodReads ID.
            
            # Let's check the merge key. 
            # books.csv: book_id, goodreads_book_id, ...
            # book_tags.csv: goodreads_book_id, tag_id, count
            
            merged = book_tags_df.merge(valid_tags, on='tag_id')
            
            # Now we have books with their genre tags. 
            # We want the most popular genre tag for each book.
            # Group by goodreads_book_id and pick the genre with max count
            top_genres = merged.loc[merged.groupby('goodreads_book_id')['count'].idxmax()]
            
            # Create a map: goodreads_book_id -> genre
            book_genre_map = dict(zip(top_genres['goodreads_book_id'], top_genres['genre']))
            
            # Apply to main df
            df['genres'] = df['goodreads_book_id'].map(book_genre_map).fillna('Fiction') # Default to Fiction if missing
            
            # Create tags string for all valid tags per book
            # Group by goodreads_book_id and join all genres
            all_book_genres = merged.groupby('goodreads_book_id')['genre'].apply(lambda x: ' '.join(set(x)))
            book_tags_map = all_book_genres.to_dict()
            df['tags'] = df['goodreads_book_id'].map(book_tags_map).fillna('')
            
        except Exception as e:
            print(f"Error processing tags: {e}. Using default genres.")
            df['genres'] = "Fiction"
            df['tags'] = ""

        # Rename/Select
        df = df.rename(columns={
            # 'book_id': 'goodreads_book_id', # Keep original ID just in case
            # 'id': 'book_id', # Use row ID as our book_id
            'authors': 'author',
            'average_rating': 'avg_rating',
            'ratings_count': 'num_ratings',
            'original_title': 'original_title'
        })
        
        # Fill missing title
        df['title'] = df['title'].fillna(df['original_title'])
        df['description'] = "<no description>" 
        
        # Keep only needed columns
        cols = ['book_id', 'title', 'author', 'description', 'genres', 'avg_rating', 'num_ratings', 'tags']
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        
        df = df[cols]
        
    else:
        print("Error: No data found. Please run scripts/generate_data.py or clone goodbooks-10k.")
        return

    output_dir = "data/clean"
    os.makedirs(output_dir, exist_ok=True)

    print("Loading data...")
    
    # 1. Clean text
    print("Cleaning text...")
    df['title'] = df['title'].fillna("").astype(str).str.strip()
    df['author'] = df['author'].fillna("Unknown").astype(str).str.strip()
    df['description'] = df['description'].fillna("<no description>").astype(str).str.strip()
    
    # 2. Normalize genres and tags
    print("Processing features...")
    df['genres'] = df['genres'].fillna("Fiction").astype(str)
    df['tags'] = df['tags'].fillna("").astype(str)
    
    # Create a combined text field for embeddings
    df['combined_text'] = (
        df['title'] + " " + 
        df['author'] + " " + 
        df['genres'] + " " + 
        df['tags'] + " " + 
        df['description']
    ).str.lower()
    
    # Save clean full dataset
    clean_path = os.path.join(output_dir, "books_clean.csv")
    df.to_csv(clean_path, index=False)
    print(f"Saved clean data to {clean_path}")
    
    # 3. Split train/val
    print("Splitting train/val...")
    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)
    
    train_df.to_csv("data/train.csv", index=False)
    val_df.to_csv("data/val.csv", index=False)
    print(f"Saved train ({len(train_df)}) and val ({len(val_df)}) sets.")

if __name__ == "__main__":
    preprocess_data()
