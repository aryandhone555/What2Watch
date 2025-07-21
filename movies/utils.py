import pandas as pd
import requests
import os
import google.generativeai as genai
from django.contrib.auth.models import User
from movies.models import Movie, WatchStatus
from dotenv import dotenv_values

ENV = dotenv_values()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OMDB_KEY = os.getenv("OMDB_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

# ------------------- Database Helpers -------------------

def movie_exists(title: str) -> bool:
    return Movie.objects.filter(title__iexact=title.strip()).exists()

def add_movie_to_db(movie_dict: dict, added_by: str = "") -> Movie:
    movie, created = Movie.objects.get_or_create(
        title=movie_dict["title"],
        defaults={
            "year": movie_dict.get("year"),
            "genre": movie_dict.get("genre"),
            "language": movie_dict.get("language"),
            "cast": movie_dict.get("cast"),
            "imdb": movie_dict.get("imdb"),
            "rt": movie_dict.get("rt"),
            "google": movie_dict.get("google"),
            "poster": movie_dict.get("poster_url"),
            "added_by": added_by,
        }
    )
    return movie

def get_unique_languages():
    langs = Movie.objects.exclude(language__isnull=True).values_list("language", flat=True)
    return sorted({l.strip() for entry in langs for l in entry.split(",")})

def get_unique_genres():
    genres = Movie.objects.exclude(genre__isnull=True).values_list("genre", flat=True)
    return sorted({g.strip() for entry in genres for g in entry.split(",")})

# ------------------------- Gemini Search ------------------------------

def gemini_search(query: str) -> pd.DataFrame:
    prompt = (
        f"Return JSON list (max 6) of movies related to '{query}' with keys: title, year"
    )
    try:
        txt = model.generate_content(prompt, request_options={"timeout": 10}).text
        return pd.read_json(txt)
    except Exception:
        return omdb_search(query)

# ------------------------- Gemini Details -----------------------------

def gemini_details(title: str) -> dict:
    prompt = (
        f"For the film '{title}' output JSON: title, year, genre, language, cast (top3), imdb, rt, google, poster_url"
    )
    try:
        txt = model.generate_content(prompt, request_options={"timeout": 10}).text
        return pd.read_json(txt).iloc[0].to_dict()
    except Exception:
        return omdb_details(title)

# ------------------------- OMDb Helpers -------------------------------

def omdb_search(query: str) -> pd.DataFrame:
    url = f"https://www.omdbapi.com/?apikey={OMDB_KEY}&s={query}"
    try:
        res = requests.get(url, timeout=10).json()
    except requests.exceptions.RequestException:
        return pd.DataFrame([])

    if "Search" not in res:
        return pd.DataFrame([])
    
    return pd.DataFrame({
        "title": [m["Title"] for m in res["Search"]],
        "year":  [m["Year"] for m in res["Search"]]
    })

def omdb_details(title: str) -> dict:
    url = f"https://www.omdbapi.com/?apikey={OMDB_KEY}&t={title}&plot=short"
    try:
        res = requests.get(url, timeout=10).json()
    except requests.exceptions.RequestException:
        return {}

    if res.get("Response") == "False":
        return {}
    
    return {
        "title": res.get("Title"),
        "year": res.get("Year"),
        "genre": res.get("Genre"),
        "language": res.get("Language"),
        "cast": ", ".join(res.get("Actors", "").split(",")[:3]),
        "imdb": res.get("imdbRating"),
        "rt": "N/A",
        "google": "N/A",
        "poster_url": res.get("Poster")
    }
