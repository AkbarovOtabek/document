from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CertDocumentViewSet

router = DefaultRouter()
# URL будет: /api/cert-documents/
router.register(r'cert-documents', CertDocumentViewSet,
                basename='cert-document')

urlpatterns = [
    path('', include(router.urls)),
]
