from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('organizations.urls', namespace='organizations')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    # (необязательно) если хочешь, чтобы и STATIC тоже раздавался:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
