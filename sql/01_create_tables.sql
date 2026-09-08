CREATE TABLE IF NOT EXISTS movies (
    movie_id INT PRIMARY KEY,
    title VARCHAR(255),
    genres VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS ratings (
    user_id INT,
    movie_id INT,
    rating NUMERIC(2,1),
    timestamp BIGINT,
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);

CREATE TABLE IF NOT EXISTS tags (
    user_id INT,
    movie_id INT,
    tag VARCHAR(255),
    timestamp BIGINT,
    PRIMARY KEY (user_id, movie_id, tag),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);

CREATE TABLE IF NOT EXISTS links (
    movie_id INT PRIMARY KEY,
    imdb_id VARCHAR(255),
    tmdb_id VARCHAR(255),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);

CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY,
    signup_date DATE,
    region VARCHAR(255),
    device VARCHAR(255),
    subscription_tier VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS watch_events (
    watch_id SERIAL PRIMARY KEY,
    user_id INT,
    movie_id INT,
    watch_date DATE,
    watch_duration_pct NUMERIC(5,2),
    device VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);

CREATE TABLE IF NOT EXISTS search_logs (
    search_id SERIAL PRIMARY KEY,
    user_id INT,
    search_query VARCHAR(255),
    searched_movie_id INT,
    clicked_movie_id INT,
    search_timestamp TIMESTAMP,
    result_rank INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (searched_movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (clicked_movie_id) REFERENCES movies(movie_id)
);