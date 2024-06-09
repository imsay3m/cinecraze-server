from rest_framework import serializers

from .models import Movie


class MovieSerializer(serializers.ModelSerializer):
    fetch_latest = serializers.BooleanField(required=False)

    class Meta:
        model = Movie
        fields = [
            "tmdb_id",
            "imdb_id",
            "download_urls",
            "streaming_urls",
            "standard_user",
            "premium_user",
            "fetch_latest",
            "title",
            "overview",
            "languages",
            "casts",
            "imdb_rating",
            "tmdb_rating",
            "director",
            "genres",
            "release_date",
            "poster_url",
            "production_countries",
        ]
        extra_kwargs = {
            "standard_user": {"required": False, "default": False},
            "premium_user": {"required": False, "default": False},
            "imdb_id": {"required": False},
            "title": {"required": False},
            "overview": {"required": False},
            "languages": {"required": False},
            "casts": {"required": False},
            "imdb_rating": {"required": False},
            "tmdb_rating": {"required": False},
            "director": {"required": False},
            "genres": {"required": False},
            "release_date": {"required": False},
            "poster_url": {"required": False},
            "production_countries": {"required": False},
        }
