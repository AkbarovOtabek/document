# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExternalLetterViewSet, ExternalLettersCategoryViewSet

app_name = 'external_letters'

router = DefaultRouter()
router.register(r'categories', ExternalLettersCategoryViewSet,
                basename='ext-cat')
router.register(r'letters', ExternalLetterViewSet, basename='ext-letter')

urlpatterns = [
    path('', include(router.urls)),
]
