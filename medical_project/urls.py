from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from .media_proxy import github_media_proxy

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('accounts/', include('accounts.urls')),
]

# Serve static files in both development and production
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Media file serving
if settings.DEBUG:
    # Development: serve local files directly
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Production: proxy GitHub storage through Render domain
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', github_media_proxy, name='media'),
    ]

