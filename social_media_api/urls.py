from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from social_media_api import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/doc/", SpectacularAPIView.as_view(), name="schema"),
    path("api/post/", include("post.urls", namespace="post")),
    path("api/user/", include("user.urls", namespace="user")),
    path("api/doc/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/doc/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
