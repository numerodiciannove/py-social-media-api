from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from post.models import Tag, Post
from post.permissions import IsPostAuthorOrReadOnly
from post.serializers import (
    TagSerializer,
    PostSerializer,
    PostRetrieveSerializer,
)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticated, IsPostAuthorOrReadOnly)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = (IsAuthenticated, IsPostAuthorOrReadOnly)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PostRetrieveSerializer
        return PostSerializer

    """Create post with automatically added author if author is authorized"""

    def create(self, request, *args, **kwargs):
        author = request.user

        serializer = self.get_serializer(
            data=request.data,
            context={"author": author, "request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    """Delete author's own post if author is authorized"""

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            raise PermissionDenied(
                "You do not have permission to delete this post."
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post"],
    )
    def like_post(self, request, pk=None):
        post = self.get_object()
        author = request.user
        if author in post.likes.all():
            post.likes.remove(author)
            message = "Post unliked successfully"
        else:
            post.likes.add(author)
            message = "Post liked successfully"
        return Response({'message': message}, status=status.HTTP_200_OK)
