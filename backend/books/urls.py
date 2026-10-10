from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuthorViewSet, BookViewSet, GenreViewSet, ReviewViewSet

router = DefaultRouter()
router.register('books', BookViewSet)
router.register('authors', AuthorViewSet)
router.register('genres', GenreViewSet)
router.register('reviews', ReviewViewSet)

urlpatterns = [path('', include(router.urls))]
