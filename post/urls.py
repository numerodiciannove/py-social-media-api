from django.urls import path, include
from rest_framework import routers

from post.views import TagViewSet

router = routers.DefaultRouter()
router.register("tags", TagViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "post"
