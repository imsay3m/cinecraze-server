import environ

env = environ.Env()
environ.Env.read_env()
from datetime import date, timedelta

import requests
from django_filters.rest_framework import (
    BaseInFilter,
    BooleanFilter,
    CharFilter,
    DjangoFilterBackend,
    FilterSet,
)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Movie
from .serializers import MovieSerializer

TMDB_API_KEY = env.str("TMDB_API_KEY")
TMDB_MOVIE_API_URL = "https://api.themoviedb.org/3/movie/{}"
TMDB_MOVIE_CREDITS_URL = "https://api.themoviedb.org/3/movie/{}/credits"
TMDB_MOVIE_VIDEOS_URL = "https://api.themoviedb.org/3/movie/{}/videos"


def fetch_movie_data_from_tmdb(tmdb_id):
    """
    Fetches the latest movie data from the TMDB API for the given tmdb_id.
    Returns a dictionary containing the movie data, or None if the fetch failed.
    """
    response = requests.get(
        TMDB_MOVIE_API_URL.format(tmdb_id), params={"api_key": TMDB_API_KEY}
    )
    credits_response = requests.get(
        TMDB_MOVIE_CREDITS_URL.format(tmdb_id), params={"api_key": TMDB_API_KEY}
    )
    videos_response = requests.get(
        TMDB_MOVIE_VIDEOS_URL.format(tmdb_id), params={"api_key": TMDB_API_KEY}
    )

    if (
        response.status_code == 200
        and credits_response.status_code == 200
        and videos_response.status_code == 200
    ):
        tmdb_data = response.json()
        credits_data = credits_response.json()
        videos_data = videos_response.json()

        title = tmdb_data.get("title")
        overview = tmdb_data.get("overview")
        release_date = tmdb_data.get("release_date")
        poster_path = tmdb_data.get("poster_path")
        poster_url = (
            f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
        )
        backdrop_path = tmdb_data.get("backdrop_path")
        backdrop_url = (
            f"https://image.tmdb.org/t/p/original{backdrop_path}"
            if backdrop_path
            else ""
        )
        imdb_id = tmdb_data.get("imdb_id")
        imdb_rating = tmdb_data.get("vote_average")
        tmdb_rating = tmdb_data.get("vote_average")
        genres = [genre["name"] for genre in tmdb_data.get("genres", [])]
        languages = [
            language["name"] for language in tmdb_data.get("spoken_languages", [])
        ]
        production_countries = [
            country["name"] for country in tmdb_data.get("production_countries", [])
        ]
        trailer_url = ""
        for video in videos_data.get("results", []):
            if video["site"] == "YouTube" and video["type"] == "Trailer":
                trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
                break

        # Get cast and director
        casts = [
            {
                "name": cast["name"],
                "character": cast["character"],
                "profile_path": (
                    f'https://image.tmdb.org/t/p/w200{cast["profile_path"]}'
                    if cast.get("profile_path")
                    else ""
                ),
            }
            for cast in credits_data.get("cast", [])[:5]
        ]
        directors = [
            {
                "name": crew["name"],
                "profile_path": (
                    f'https://image.tmdb.org/t/p/w200{crew["profile_path"]}'
                    if crew.get("profile_path")
                    else ""
                ),
            }
            for crew in credits_data.get("crew", [])
            if crew["job"] == "Director"
        ]
        director = directors[0] if directors else {}

        return {
            "title": title,
            "overview": overview,
            "release_date": release_date,
            "poster_url": poster_url,
            "backdrop_url": backdrop_url,
            "trailer_url": trailer_url,
            "imdb_id": imdb_id,
            "imdb_rating": imdb_rating,
            "tmdb_rating": tmdb_rating,
            "genres": genres,
            "languages": languages,
            "production_countries": production_countries,
            "casts": casts,
            "director": director,
        }
    return None


class CharArrayFilter(BaseInFilter, CharFilter):
    pass


class MovieFilter(FilterSet):
    languages = CharFilter(field_name="languages", method="filter_languages")
    genres = CharFilter(field_name="genres", method="filter_genres")
    new_release = BooleanFilter(field_name="new_release", method="filter_new_release")
    upcoming = BooleanFilter(field_name="upcoming", method="filter_upcoming")

    class Meta:
        model = Movie
        fields = ["languages", "genres", "new_release", "upcoming"]

    def filter_languages(self, queryset, name, value):
        return queryset.filter(languages__icontains=value)

    def filter_genres(self, queryset, name, value):
        return queryset.filter(genres__icontains=value)

    def filter_new_release(self, queryset, name, value):
        if value:
            today = date.today()
            sixty_days_ago = today - timedelta(days=60)
            return queryset.filter(release_date__range=(sixty_days_ago, today))
        return queryset

    def filter_upcoming(self, queryset, name, value):
        if value:
            return queryset.filter(release_date__gt=date.today())
        return queryset


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = MovieFilter
    search_fields = ["title", "overview"]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


@api_view(["POST"])
def add_movie(request):
    if request.method == "POST":
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            tmdb_id = serializer.validated_data["tmdb_id"]
            download_urls = serializer.validated_data["download_urls"]
            streaming_urls = serializer.validated_data["streaming_urls"]
            standard_user = serializer.validated_data["standard_user"]
            premium_user = serializer.validated_data["premium_user"]

            # Fetch movie data from TMDB API
            movie_data = fetch_movie_data_from_tmdb(tmdb_id)
            if not movie_data:
                return Response(
                    {
                        "error": "Failed to fetch data from TMDB. Please Check the tmdb id."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create and save the movie instance
            movie = Movie(
                tmdb_id=tmdb_id,
                imdb_id=movie_data["imdb_id"],
                download_urls=download_urls,
                streaming_urls=streaming_urls,
                title=movie_data["title"],
                overview=movie_data["overview"],
                languages=movie_data["languages"],
                casts=movie_data["casts"],
                imdb_rating=movie_data["imdb_rating"],
                tmdb_rating=movie_data["tmdb_rating"],
                director=movie_data["director"],
                genres=movie_data["genres"],
                release_date=movie_data["release_date"],
                poster_url=movie_data["poster_url"],
                backdrop_url=movie_data["backdrop_url"],
                trailer_url=movie_data["trailer_url"],
                production_countries=movie_data["production_countries"],
                standard_user=standard_user,
                premium_user=premium_user,
            )
            movie.save()

            return Response(MovieSerializer(movie).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
def update_movie(request, tmdb_id):
    # Check if 'fetch_latest' is in request data
    if "fetch_latest" not in request.data:
        return Response(
            {"error": "'fetch_latest' field is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    movie = get_object_or_404(Movie, tmdb_id=tmdb_id)

    # Fetch the latest movie data from TMDB API if requested
    if request.data["fetch_latest"]:
        movie_data = fetch_movie_data_from_tmdb(tmdb_id)
        if movie_data:
            movie.title = movie_data["title"]
            movie.overview = movie_data["overview"]
            movie.release_date = movie_data["release_date"]
            movie.poster_url = movie_data["poster_url"]
            movie.backdrop_url = movie_data["backdrop_url"]
            movie.trailer_url = movie_data["trailer_url"]
            movie.imdb_id = movie_data["imdb_id"]
            movie.imdb_rating = movie_data["imdb_rating"]
            movie.tmdb_rating = movie_data["tmdb_rating"]
            movie.genres = movie_data["genres"]
            movie.languages = movie_data["languages"]
            movie.production_countries = movie_data["production_countries"]
            movie.casts = movie_data["casts"]
            movie.director = movie_data["director"]

    # Apply partial updates from request data
    serializer = MovieSerializer(movie, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def delete_movie(request, tmdb_id):
    movie = get_object_or_404(Movie, tmdb_id=tmdb_id)

    if request.method == "DELETE":
        movie_title = movie.title
        movie.delete()
        return Response(
            {"message": f"Movie '{movie_title}' has been deleted."},
            status=status.HTTP_200_OK,
        )
    return Response(
        {"error": "Invalid request method."},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )
