from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def query_netflix_engine(selected_genres, era, max_runtime, industry):
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    
    # Base query for structural rules matching runtime
    query = """
        SELECT type, title, genres, release_year, runtime_minutes, rating, plot_summary 
        FROM movies 
        WHERE runtime_minutes <= ?
    """
    params = [max_runtime]
    
    # 1. Industry (Hollywood / Bollywood) Forward Filtering Rule
    if industry == 'Bollywood':
        query += " AND genres LIKE ?"
        params.append("%International Movies%")
    elif industry == 'Hollywood':
        query += " AND genres NOT LIKE ?"
        params.append("%International Movies%")
        
    # 2. Multi-era segmentation routing rules
    if era == '90s':
        query += " AND release_year BETWEEN 1990 AND 1999"
    elif era == '2000s':
        query += " AND release_year BETWEEN 2000 AND 2009"
    elif era == 'Modern':
        query += " AND release_year >= 2010"
    elif era == 'Classic':
        query += " AND release_year < 1990"
        
    # 3. Append dynamic genre wildcard loops
    if selected_genres:
        genre_conditions = []
        for genre in selected_genres:
            genre_conditions.append("genres LIKE ?")
            params.append(f"%{genre}%")
        query += " AND (" + " OR ".join(genre_conditions) + ")"
        
    query += " ORDER BY rating DESC LIMIT 30" 
    
    cursor.execute(query, params)
    raw_rows = cursor.fetchall()
    conn.close()
    
    processed_recommendations = []
    for row in raw_rows:
        movie_genres = [g.strip().lower() for g in row[2].split(',')]
        match_count = 0
        
        if selected_genres:
            for ug in selected_genres:
                if any(ug.lower() in mg for mg in movie_genres):
                    match_count += 1
            match_percentage = int((match_count / len(selected_genres)) * 100)
        else:
            match_percentage = 100
            
        processed_recommendations.append({
            'type': row[0],
            'title': row[1],
            'genres': row[2],
            'year': row[3],
            'runtime': row[4],
            'rating': row[5],
            'plot': row[6],
            'match': min(match_percentage, 100)
        })
        
    return processed_recommendations

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        genres = request.form.getlist('genres')
        era = request.form.get('era')
        max_runtime = int(request.form.get('runtime', 180))
        industry = request.form.get('industry', 'All') # Capture industry field
        
        results = query_netflix_engine(genres, era, max_runtime, industry)
        
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)