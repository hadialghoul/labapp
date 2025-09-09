from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path
from .views import debug_media_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('accounts/', include('accounts.urls')),
]

# Debug media serving with logging
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', debug_media_view, name='media'),
]

# Serve static files in both development and production
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

