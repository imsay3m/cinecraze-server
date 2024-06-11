from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cine_request.views import CineRequestViewSet, MarkAsSolvedView

from .views import MovieViewSet, add_movie, delete_movie, update_movie

router = DefaultRouter()
router.register(r"movies", MovieViewSet)
# router.register(r"shows", ShowsViewSet)
router.register(r"cine-request", CineRequestViewSet)


urlpatterns = [
    path(
        "cine-request/solved/<int:pk>/",
        MarkAsSolvedView.as_view(),
        name="mark_as_solved",
    ),
    path("movies/add/", add_movie, name="add_movie"),
    path("movies/update/<int:tmdb_id>/", update_movie, name="update_movie"),
    path("movies/delete/<int:tmdb_id>/", delete_movie, name="delete_movie"),
    path("", include(router.urls)),
]
