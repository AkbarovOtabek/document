from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
     path('admin/', admin.site.urls),
     path('api/', include('organizations.urls', namespace='organizations')),
     path("api/staff/", include("staffUsers.urls", namespace="staffUsers")),
     path("api/auth/token/", TokenObtainPairView.as_view(),
         name="token_obtain_pair"),
     path("api/auth/token/refresh/",
         TokenRefreshView.as_view(), name="token_refresh"),
     path("api/org-structure/", include("organizationsStaff.urls", namespace="organizationsStaff")),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    # (необязательно) если хочешь, чтобы и STATIC тоже раздавался:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
