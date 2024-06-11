# from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import JSONField


class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    imdb_id = models.CharField(max_length=50, null=True, blank=True)
    download_urls = JSONField(null=True, blank=True)
    streaming_urls = JSONField(null=True, blank=True)
    title = models.CharField(max_length=255)
    overview = models.TextField()
    languages = JSONField()
    casts = JSONField()
    imdb_rating = models.FloatField(null=True, blank=True)
    tmdb_rating = models.FloatField(null=True, blank=True)
    director = JSONField()
    genres = JSONField()
    release_date = models.DateField()
    poster_url = models.URLField()
    backdrop_url = models.URLField()
    production_countries = JSONField()
    standard_user = models.BooleanField(default=False)
    premium_user = models.BooleanField(default=False)

    def __str__(self):
        return self.title
