from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('post.urls')),
    path("user/", include("user.urls")),
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='api-schema'),
        name='api-docs',),
    path('api/user/', include('user.api_urls')),
    path('api/comment/', include('comment.api_urls')),
    path('api/', include('post.api_urls')),]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,)
    import debug_toolbar
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),]