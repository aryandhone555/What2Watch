from django.shortcuts import render
from django.views.decorators.http import require_POST
from .utils_watch import read_status, toggle_status 

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from .utils import gemini_search, gemini_details, read_catalog, write_row, exists
from .utils import (
    read_catalog, write_row, exists,
    gemini_search, gemini_details,
    unique_languages, unique_genres,  # ← ✅ add these
    # optionally: decade_ranges (if still used elsewhere)
)

import requests, uuid
from django.conf import settings

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "movies/register.html", {"form": form})
#--------------------------------------------------------------------------------------------
# views.py
from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    logout(request)
    return redirect('login')  # or redirect('register') if you have separate register page
#--------------------------------------------------------------------------------------------

@login_required

def home(request):
    df = read_catalog()

    # dropdown data
    lang_choices  = unique_languages(df)
    genre_choices = unique_genres(df)
    all_years = sorted(df["year"].dropna().astype(str).str[:4].astype(int).unique())
    year_choices = list(range(min(all_years), max(all_years)+1)) if all_years else []

    # selected filters
    sel_lang    = request.GET.get("lang")
    sel_genre   = request.GET.get("genre")
    y1          = request.GET.get("start_year")
    y2          = request.GET.get("end_year")
    my_movies   = request.GET.get("my_movies") == "1"

    # filtering
    if sel_lang:
        df = df[df["language"].str.contains(sel_lang, case=False, na=False)]
    if sel_genre:
        df = df[df["genre"].str.contains(sel_genre, case=False, na=False)]
    if y1 and y2:
        try:
            y1, y2 = int(y1), int(y2)
            df = df[df["year"].astype(str).str[:4].astype(int).between(y1, y2)]
        except ValueError:
            pass
    if my_movies:
        df = df[df["added_by"] == request.user.username]
    
    # add watched flag ------------------------------------------------
    user_status = read_status(request.user.username)
    records = []
    for _, row in df.iterrows():
        rec = row.to_dict()
        rec["watched"] = user_status.get(row["title"], False)
        records.append(rec)

    # context = {
    #     "movies": df.to_dict("records"),
    #     "lang_choices": lang_choices,
    #     "genre_choices": genre_choices,
    #     "year_choices": year_choices,
    #     "sel_lang": sel_lang,
    #     "sel_genre": sel_genre,
    #     "sel_start_year": y1,
    #     "sel_end_year": y2,
    #     "my_movies_checked": my_movies,
    # }

    context = {
    "movies": records,     # pass the updated list with watched info!
    "lang_choices": lang_choices,
    "genre_choices": genre_choices,
    "year_choices": year_choices,
    "sel_lang": sel_lang,
    "sel_genre": sel_genre,
    "sel_start_year": y1,
    "sel_end_year": y2,
    "my_movies_checked": my_movies,}


    return render(request, "movies/home.html", context)

# def home(request):
#     df = read_catalog()

#     # dropdown data
#     lang_choices  = unique_languages(df)
#     genre_choices = unique_genres(df)
#     all_years = sorted(df["year"].dropna().astype(str).str[:4].astype(int).unique())
#     year_choices = list(range(min(all_years), max(all_years)+1)) if all_years else []

#     # selected filters
#     sel_lang  = request.GET.get("lang")
#     sel_genre = request.GET.get("genre")
#     y1 = request.GET.get("start_year")
#     y2 = request.GET.get("end_year")

#     # filtering
#     if sel_lang:
#         df = df[df["language"].str.contains(sel_lang, case=False, na=False)]
#     if sel_genre:
#         df = df[df["genre"].str.contains(sel_genre, case=False, na=False)]
#     if y1 and y2:
#         try:
#             y1, y2 = int(y1), int(y2)
#             df = df[df["year"].astype(str).str[:4].astype(int).between(y1, y2)]
#         except ValueError:
#             pass

#     context = {
#         "movies": df.to_dict("records"),
#         "lang_choices": lang_choices,
#         "genre_choices": genre_choices,
#         "year_choices": year_choices,
#         "sel_lang": sel_lang,
#         "sel_genre": sel_genre,
#         "sel_start_year": y1,
#         "sel_end_year": y2,
#     }
#     return render(request, "movies/home.html", context)

# def home(request):
#     df = read_catalog()
#     genre = request.GET.get('genre')
#     year = request.GET.get('year')
#     lang = request.GET.get('lang')

#     if genre: df = df[df.genre == genre]
#     if year: df = df[df.year == int(year)]
#     if lang: df = df[df.language == lang]

#     movies = df.to_dict("records")
#     return render(request, "movies/home.html", {"movies": movies})

@login_required
def search(request):
    if request.GET.get("q"):
        results = gemini_search(request.GET["q"])
        return render(request, "movies/search.html", {"results": results.to_dict("records")})
    return render(request, "movies/search.html")

@login_required
def add_movie(request):
    title = request.POST.get("title")
    if exists(title):
        return render(request, "movies/search.html", {"error": "Movie already exists!"})

    data = gemini_details(title)
    poster_url = data.pop("poster_url")
    fname = f"{uuid.uuid4()}.jpg"
    path = settings.MEDIA_ROOT / "posters" / fname
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(requests.get(poster_url, timeout=10).content)

    row = {**data, "poster": f"posters/{fname}", "added_by": request.user.username}
    write_row(row)
    return redirect("home")

# Toggle view
@login_required
@require_POST
def toggle_watch(request):
    title = request.POST["title"]
    toggle_status(request.user.username, title)
    # return to the same page
    return redirect(request.META.get("HTTP_REFERER", "home"))
