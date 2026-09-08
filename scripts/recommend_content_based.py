import os
import pandas as pd
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

movies = pd.read_sql("SELECT movie_id, title, genres FROM movies", engine)

# genres are pipe-separated like "Action|Adventure|Sci-Fi" -- replace | with space
# so TF-IDF treats each genre as a separate "word"
movies["genres_cleaned"] = movies["genres"].str.replace("|", " ", regex=False)

# TF-IDF turns each movie's genre string into a numeric vector based on genre importance
tfidf = TfidfVectorizer()
genre_matrix = tfidf.fit_transform(movies["genres_cleaned"])

# cosine similarity compares every movie's vector to every other movie's vector
# result is a 9742 x 9742 matrix where each cell = similarity score (0 to 1)
similarity_matrix = cosine_similarity(genre_matrix)

def get_similar_movies(movie_title, top_n=10):
    # find the row index of the movie matching this title
    matches = movies[movies["title"].str.contains(movie_title, case=False, na=False)]
    if matches.empty:
        print(f"No movie found matching '{movie_title}'")
        return None

    idx = matches.index[0]
    matched_title = movies.loc[idx, "title"]

    # get similarity scores for this movie against all others
    scores = list(enumerate(similarity_matrix[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    # skip index 0 since that's the movie itself (similarity = 1.0)
    top_matches = scores[1:top_n+1]

    result = pd.DataFrame([
        {"title": movies.loc[i, "title"], "genres": movies.loc[i, "genres"], "similarity_score": round(score, 3)}
        for i, score in top_matches
    ])

    print(f"\nMovies similar to '{matched_title}':")
    print(result)
    return result

# test it
get_similar_movies("Toy Story")
get_similar_movies("Matrix")