from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def query_inference_engine(selected_genres, era, max_runtime):
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Base Forward Filtering Query
    query = "SELECT * FROM movies WHERE runtime_minutes <= ?"
    params = [max_runtime]
    
    # Apply Era Rules
    if era == '90s':
        query += " AND release_year BETWEEN 1990 AND 1999"
    elif era == '2000s':
        query += " AND release_year BETWEEN 2000 AND 2009"
    elif era == 'Modern':
        query += " AND release_year >= 2010"
    elif era == 'Classic':
        query += " AND release_year < 1990"
        
    cursor.execute(query, params)
    raw_results = cursor.fetchall()
    conn.close()
    
    # Apply Genre Rules via programming intersection logic & compile Match Scores
    final_recommendations = []
    for movie in raw_results:
        movie_genres = [g.strip() for g in movie['genres'].split(',')]
        # Find overlapping genres
        match_count = len(set(selected_genres).intersection(set(movie_genres)))
        
        if match_count > 0 or not selected_genres:
            # Simple rule logic to calculate match confidence badge
            match_percentage = 100 if not selected_genres else int((match_count / len(selected_genres)) * 100)
            
            final_recommendations.append({
                'title': movie['title'],
                'genres': movie['genres'],
                'year': movie['release_year'],
                'runtime': movie['runtime_minutes'],
                'rating': movie['rating'],
                'plot': movie['plot_summary'],
                'match': min(match_percentage, 100)
            })
            
    # Sort recommendations by viewer rating DESC (Rule 4)
    return sorted(final_recommendations, key=lambda x: x['rating'], reverse=True)

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    recommendations = None
    if request.method == 'POST':
        genres = request.form.getlist('genres')
        era = request.form.get('era')
        max_runtime = int(request.form.get('runtime', 180))
        
        recommendations = query_inference_engine(genres, era, max_runtime)
        
    return render_template('index.html', results=recommendations)

if __name__ == '__main__':
    app.run(debug=True)