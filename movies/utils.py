import pandas as pd, requests, os, google.generativeai as genai
from django.conf import settings
from dotenv import dotenv_values

ENV = dotenv_values()
CSV_PATH = settings.BASE_DIR / "movies.csv"
HEADERS = [
    "title","year","genre","language","cast","imdb","rt","google","poster","added_by"
]
# ------------------------- CSV helpers -------------------------

def read_catalog():
    if not CSV_PATH.exists():
        return pd.DataFrame(columns=HEADERS)
    return pd.read_csv(CSV_PATH)

def write_row(row_dict):
    df = read_catalog()
    df = pd.concat([df, pd.DataFrame([row_dict])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)

def exists(title: str) -> bool:
    df = read_catalog()
    return title.strip().lower() in df["title"].str.lower().tolist()

def unique_languages(df: pd.DataFrame):
    return sorted({l.strip() for lang in df["language"].dropna() for l in str(lang).split(",")})

def unique_genres(df: pd.DataFrame):
    return sorted({g.strip() for genre in df["genre"].dropna() for g in str(genre).split(",")})


# ------------------------- Gemini ------------------------------
GEMINI_KEY = ENV["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")  # cheaper + fast

# ------------------------- Backup API keys ---------------------
OMDB_KEY = ENV.get("OMDB_API_KEY")


# ------------------------- SEARCH ------------------------------

def gemini_search(query: str) -> pd.DataFrame:
    """Return DF columns (title, year). Falls back to OMDb."""
    prompt = (
        f"Return JSON list (max 6) of movies related to '{query}' with keys: title, year"
    )
    try:
        txt = model.generate_content(prompt, request_options={"timeout": 10}).text
        return pd.read_json(txt)
    except Exception:
        return omdb_search(query)

# ------------------------- DETAILS -----------------------------

def gemini_details(title: str) -> dict:
    """Return comprehensive movie dict. Fallback OMDb."""
    prompt = (
        f"For the film '{title}' output JSON: title, year, genre, language, cast (top3), imdb, rt, google, poster_url"
    )
    try:
        txt = model.generate_content(prompt, request_options={"timeout": 10}).text
        return pd.read_json(txt).iloc[0].to_dict()
    except Exception:
        return omdb_details(title)

# ------------------------- OMDb helpers ------------------------

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