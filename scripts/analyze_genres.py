import pandas as pd
import ast
from collections import Counter

def analyze_genres():
    try:
        df = pd.read_csv('data/clean/books_clean.csv')
        print(f"Total books: {len(df)}")
        
        all_genres = []
        for genres_str in df['genres']:
            try:
                # Genres are likely stored as stringified lists or just strings
                if genres_str.startswith('['):
                    genres = ast.literal_eval(genres_str)
                    all_genres.extend(genres)
                else:
                    all_genres.append(genres_str)
            except:
                continue
                
        genre_counts = Counter(all_genres)
        print("\nTop 20 Genres:")
        for genre, count in genre_counts.most_common(20):
            print(f"{genre}: {count}")
            
        print(f"\nTotal unique genres: {len(genre_counts)}")
        
    except Exception as e:
        print(f"Error analyzing genres: {e}")

if __name__ == "__main__":
    analyze_genres()
