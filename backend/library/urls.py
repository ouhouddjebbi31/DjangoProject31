from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ReadingListViewSet

router = DefaultRouter()
router.register('reading-list', ReadingListViewSet, basename='reading-list')
urlpatterns = [path('', include(router.urls))]
