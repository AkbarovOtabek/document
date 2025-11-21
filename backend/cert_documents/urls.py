# cert_documents/urls.py
from rest_framework.routers import DefaultRouter
from .views import CertLetterViewSet, CertLetterReplyViewSet

router = DefaultRouter()
router.register("letters", CertLetterViewSet, basename="cert-letter")
router.register(
    "letter-replies",
    CertLetterReplyViewSet,
    basename="cert-letter-reply",
)

urlpatterns = router.urls
