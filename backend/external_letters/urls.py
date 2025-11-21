from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ExternalLetterViewSet,
    ExternalLettersCategoryViewSet,
    ExternalLetterReplyViewSet,
)

app_name = "external_letters"

router = DefaultRouter()
router.register(r"categories", ExternalLettersCategoryViewSet,
                basename="ext-cat")
router.register(r"letters", ExternalLetterViewSet, basename="ext-letter")
router.register(r"replies", ExternalLetterReplyViewSet,
                basename="ext-letter-reply")

urlpatterns = [
    path("", include(router.urls)),
]
