from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .forms import RegisterForm
from .models import Movie, WatchStatus
from .utils import (
    gemini_search, gemini_details,
    movie_exists, add_movie_to_db,
    get_unique_genres, get_unique_languages,
)
import requests, uuid
from django.conf import settings

# ---------------------- Register View ----------------------------

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "movies/register.html", {"form": form})


# ---------------------- Logout View ----------------------------

def custom_logout(request):
    logout(request)
    return redirect("login")


# ---------------------- Home View ----------------------------

@login_required
def home(request):
    movies = Movie.objects.all()

    # Filter selections
    sel_lang = request.GET.get("lang")
    sel_genre = request.GET.get("genre")
    y1 = request.GET.get("start_year")
    y2 = request.GET.get("end_year")
    my_movies = request.GET.get("my_movies") == "1"

    # Apply filters
    if sel_lang:
        movies = movies.filter(language__icontains=sel_lang)
    if sel_genre:
        movies = movies.filter(genre__icontains=sel_genre)
    if y1 and y2:
        try:
            movies = movies.filter(year__gte=y1, year__lte=y2)
        except ValueError:
            pass
    if my_movies:
        movies = movies.filter(added_by=request.user.username)

    # Build watched status
    user_watch_status = {
        ws.title: ws.watched
        for ws in WatchStatus.objects.filter(user=request.user)

    }

    records = []
    for movie in movies:
        rec = {
            "title": movie.title,
            "year": movie.year,
            "genre": movie.genre,
            "language": movie.language,
            "cast": movie.cast,
            "imdb": movie.imdb,
            "rt": movie.rt,
            "google": movie.google,
            "poster": movie.poster,
            "added_by": movie.added_by,
            "watched": user_watch_status.get(movie.title, False)
        }
        records.append(rec)

    # Dropdowns
    lang_choices = get_unique_languages()
    genre_choices = get_unique_genres()
    years = movies.values_list('year', flat=True)
    year_choices = sorted(set(int(y[:4]) for y in years if y and y[:4].isdigit()))

    context = {
        "movies": records,
        "lang_choices": lang_choices,
        "genre_choices": genre_choices,
        "year_choices": year_choices,
        "sel_lang": sel_lang,
        "sel_genre": sel_genre,
        "sel_start_year": y1,
        "sel_end_year": y2,
        "my_movies_checked": my_movies,
    }

    return render(request, "movies/home.html", context)


# ---------------------- Search View ----------------------------

@login_required
def search(request):
    if request.GET.get("q"):
        results = gemini_search(request.GET["q"])
        return render(request, "movies/search.html", {"results": results.to_dict("records")})
    return render(request, "movies/search.html")


# ---------------------- Add Movie View ----------------------------

@login_required
def add_movie(request):
    title = request.POST.get("title")
    if movie_exists(title):
        return render(request, "movies/search.html", {"error": "Movie already exists!"})

    data = gemini_details(title)
    poster_url = data.pop("poster_url")
    fname = f"{uuid.uuid4()}.jpg"
    path = settings.MEDIA_ROOT / "posters" / fname
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(requests.get(poster_url, timeout=10).content)

    data["poster"] = f"posters/{fname}"
    add_movie_to_db(data, added_by=request.user.username)
    return redirect("home")


# ---------------------- Toggle Watch View ----------------------------

@login_required
@require_POST
def toggle_watch(request):
    title = request.POST["title"]
    user = request.user.username
    
    watch, created = WatchStatus.objects.get_or_create(username=user, title=title)
    watch.watched = not watch.watched
    watch.save()
    
    return redirect(request.META.get("HTTP_REFERER", "home"))
