# CineMatch - AI Movie Recommendation System
### Project Documentation & Technical Architecture

CineMatch is a premium, high-performance web application designed for interactive movie discovery. It combines hybrid recommendation systems (Collaborative Filtering + Content-Based Filters) with generative AI (Google Gemini API using RAG) to deliver conversational recommendations, dynamic dashboard shelves, watchlist curations, sentiment-analyzed movie reviews, and responsive aesthetics.

---

## 1. Technology Stack

### Backend Architecture
- **Framework**: Flask (Python 3.12)
- **Database**: SQLite3 (File-based database optimized with custom indexes)
- **AI Integration**: Google Generative AI (`gemini-1.5-flash` model) for Retrieval-Augmented Generation (RAG) and conversational search
- **Natural Language Processing (NLP)**: 
  - `TextBlob` (with custom local lexicon fallback) for real-time sentiment analysis of user movie reviews
  - Custom Rule-Based NLP query parser for fallback conversational classification

### Frontend Architecture
- **Structure**: HTML5 Semantic Markup
- **Styling**: Tailwind CSS (Utility framework loaded via CDN with class-based Dark Mode configuration) + Vanilla CSS custom variables for visual animations
- **Interactions**: Vanilla JavaScript (ES6+) with Lenis Smooth Scrolling
  - **Dynamic Card Spotlights**: Cursor-tracking radial gradients using CSS properties
  - **Asynchronous AJAX Fetch**: Fully non-blocking UI updates for search queries, watchlist modifications, and poster loading

---

## 2. Core Features & System Implementations

### I. AI Chatbot Assistant
- **Retrieval-Augmented Generation (RAG)**: Connects to the Gemini API, feeding the model real-time SQLite search results ("Context") based on the user's message. The AI is instructed to only suggest movies that exist in the database, avoiding hallucinations.
- **Conversational Cleaning**: Employs an expanded dictionary of stop-words (pronouns, request verbs, media terms) to filter conversational noise (e.g. *"can you recommend some action movies to watch tonight"* gets cleaned down to the database filter `"Action"` rather than running a title search for the word *"you"*).
- **Greeting Warmth**: Detects user greetings (like *"hi"*, *"hello"*) and prepends a warm, friendly prefix response before listing movie results.
- **Dynamic Visual Genres**: The backend maps the matching user genre to a `display_genre` key (e.g. mapping `"sci-fi"` to *"Sci-Fi & Fantasy"*). The frontend renders this specific matched genre on the cards rather than default database listings.

### II. Hybrid Recommendation System
- **Content-Based Filtering**: Matches movies on genres, release eras, runtime constraints, mood categories, and language parameters.
- **User-Based Collaborative Filtering**: Measures user similarities dynamically. When a user likes a movie:
  1. The system identifies other users who liked the same movie.
  2. Computes **Jaccard Similarity Coefficients** between user interaction matrices.
  3. Recommends movies liked by similar users, weighted by their Jaccard similarity score.
- **Hybrid Scoring Formula**:
  $$\text{Score} = 0.5 \times \text{Content Score} + 0.5 \times \text{Collaborative Score}$$ (or 90% Content Score fallback if no user likes exist yet).

### III. Dynamic Interactive Dashboard
- **Trending Shelf**: Highlights highly rated modern releases.
- **Top Rated Shelf**: Isolates overall top-performing movies sorted by rating.
- **New Releases Shelf**: Spotlights recent cinematic additions.
- **Most Watched Shelf**: Aggregates interaction counts (likes, reviews, watchlist actions) dynamically from the database to rank popularity.

### IV. Real-time Movie Reviews & Sentiment Analysis
- **User Reviews**: Allows users to write reviews and rate movies.
- **Sentiment Classification**: Processes the review text through an NLP analyzer and labels the sentiment dynamically as **Positive**, **Neutral**, or **Negative**.
- **Helpfulness Voting**: Allows users to upvote helpful reviews.

### V. Asynchronous Movie Poster Fetcher & Cache
- **API Wrapper**: Fetches poster links asynchronously from an external IMDb search API wrapper.
- **Persistent Caching**: Saves resolved poster links in a dedicated `poster_cache` table. This reduces subsequent image load times from ~3 seconds (API lookup) to **<1ms** (local database read).
- **Background Prefetch Daemon**: Spins up a background worker thread on startup to pre-crawl and warm the SQLite database cache for the top 100+ popular movies.

---

## 3. Database Schema (DDL)

The SQLite database (`movies.db`) contains the following core tables:

### 1. `movies` Table (Catalog)
```sql
CREATE TABLE movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,                 -- 'Movie' or 'TV Show'
    title TEXT UNIQUE,         -- Movie Title
    genres TEXT,               -- Comma-separated genres
    release_year INTEGER,      -- Release Year
    runtime_minutes INTEGER,   -- Runtime in Minutes
    rating REAL,               -- Rating out of 10
    plot_summary TEXT,         -- Synopsis
    language TEXT DEFAULT 'English'
);
```

### 2. `poster_cache` Table (Image Cache)
```sql
CREATE TABLE poster_cache (
    title TEXT PRIMARY KEY,
    poster TEXT                -- Poster URL
);
```

### 3. `user_likes` Table (User Preferences)
```sql
CREATE TABLE user_likes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    movie_title TEXT,
    liked INTEGER,             -- 1 = Like, -1 = Dislike, 0 = Neutral
    UNIQUE(user_id, movie_title)
);
```

### 4. `watchlist` Tables
```sql
CREATE TABLE watchlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    watchlist_name TEXT
);

CREATE TABLE watchlist_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    watchlist_id INTEGER,
    movie_title TEXT,
    FOREIGN KEY(watchlist_id) REFERENCES watchlists(id)
);
```

### 5. `reviews` Table (Sentiment Feedback)
```sql
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_title TEXT,
    user_id INTEGER,
    username TEXT,
    rating INTEGER,
    review_text TEXT,
    helpful_votes INTEGER DEFAULT 0,
    sentiment TEXT,            -- 'Positive', 'Neutral', or 'Negative'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6. `interactions` Table (Usage Logs)
```sql
CREATE TABLE interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    movie_title TEXT,
    interaction_type TEXT,     -- 'like', 'dislike', 'review', 'watchlist'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Key Libraries & Dependencies

- **`Flask`**: Web micro-framework.
- **`google-generativeai`**: Google Gemini SDK for AI chatbot integration.
- **`TextBlob`**: Simple NLP library used for sentiment classification (fallback lexicon-based rule set included for offline robust operations).
- **`sqlite3`**: Database interface.
- **`python-dotenv`**: Secure management of local configuration parameters (like `GEMINI_API_KEY`).
