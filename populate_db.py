import sqlite3

def init_db():
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    
    # Create movies table matching Task 1 design
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genres TEXT NOT NULL,
            release_year INTEGER NOT NULL,
            runtime_minutes INTEGER NOT NULL,
            rating REAL DEFAULT 0.0,
            plot_summary TEXT
        )
    ''')
    
    # Seed sample datasets
    sample_movies = [
        ("The Matrix", "Sci-Fi, Thriller", 1999, 136, 8.7, "A computer hacker learns from mysterious rebels about the true nature of his reality."),
        ("Inception", "Sci-Fi, Thriller", 2010, 148, 8.8, "A thief who steals corporate secrets through the use of dream-sharing technology."),
        ("Minority Report", "Sci-Fi, Thriller", 2002, 145, 7.6, "In a future where a special police unit can arrest killers before they commit their crimes, an officer is himself accused."),
        ("Pulp Fiction", "Thriller", 1994, 154, 8.9, "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine."),
        ("Interstellar", "Sci-Fi", 2014, 169, 8.7, "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.")
    ]
    
    cursor.executemany('''
        INSERT INTO movies (title, genres, release_year, runtime_minutes, rating, plot_summary)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_movies)
    
    conn.commit()
    conn.close()
    print("Knowledge base synchronized successfully.")

if __name__ == '__main__':
    init_db()