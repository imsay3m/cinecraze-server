from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MovieViewSet, add_movie, delete_movie, update_movie

router = DefaultRouter()
router.register(r"movies", MovieViewSet)
# router.register(r"shows", ShowsViewSet)


urlpatterns = [
    path("movies/add/", add_movie, name="add_movie"),
    path("movies/<int:tmdb_id>/update/", update_movie, name="update_movie"),
    path("movies/<int:tmdb_id>/delete/", delete_movie, name="delete_movie"),
    path("", include(router.urls)),
]
