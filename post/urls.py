from django.urls import path, include
from rest_framework import routers

from post.views import TagViewSet, PostViewSet, CommentViewSet

router = routers.DefaultRouter()
router.register("tags", TagViewSet)
router.register("posts", PostViewSet)
router.register("comments", CommentViewSet)

urlpatterns = router.urls

app_name = "post"
