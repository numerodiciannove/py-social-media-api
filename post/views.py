from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from post.models import Tag, Post, Comment
from post.permissions import IsPostAuthorOrReadOnly
from post.serializers import (
    TagSerializer,
    PostSerializer,
    PostRetrieveSerializer,
    CommentSerializer,
    CommentListSerializer,
)


class DefaultPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class TagViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)


class CommentViewSet(viewsets.ModelViewSet):
    """Shows only author's comments if author is authorized"""
    queryset = Comment.objects.all()
    serializer_class = CommentListSerializer
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        queryset = Comment.objects.filter(author=user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated, IsPostAuthorOrReadOnly)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PostRetrieveSerializer

        return PostSerializer

    def create(self, request, *args, **kwargs):
        """Create post with automatically added author if author is
        authorized"""
        author = request.user

        serializer = self.get_serializer(
            data=request.data, context={"author": author, "request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Delete author's own post if author is authorized"""
        instance = self.get_object()
        if instance.author != request.user:
            raise PermissionDenied(
                "You do not have permission to delete this post."
            )
        self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["GET"],
        detail=False,
        url_path="my_board",
    )
    def user_posts(self, request) -> Response:
        """The user receives all his/her posts"""
        queryset = Post.objects.filter(author=request.user)
        serializer = PostSerializer(
            queryset,
            many=True,
            context={"request": request})

        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def like_post(self, request, pk=None):
        post = self.get_object()
        author = request.user
        if author in post.likes.all():
            post.likes.remove(author)
            message = "Post unliked successfully"
        else:
            post.likes.add(author)
            message = "Post liked successfully"

        return Response({"message": message}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"], url_path="comment_post")
    def comment_post(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)

        serializer = CommentSerializer(
            data=request.data, context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, post=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True, methods=["DELETE"],
        url_path="comments/(?P<comment_pk>[^/.]+)"
    )
    def comment_delete(self, request, pk=None, comment_pk=None):
        comment = get_object_or_404(Comment, pk=comment_pk, post__id=pk)
        if request.user == comment.author:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {
                    "error": "You do not have permission to delete this comment."},
                status=status.HTTP_403_FORBIDDEN,
            )

    @action(
        methods=["GET"],
        detail=True,
        url_path="comments",
    )
    def comments(self, request, pk=None) -> Response:
        """Get a list of comments for specified post"""
        post = self.get_object()
        queryset = Comment.objects.filter(post=post)
        serializer = CommentListSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        url_path="followings",
    )
    def get_following_posts(self, request) -> Response:
        """User receives all posts of the users he/she follows"""
        following_users = request.user.follows.all()
        queryset = self.queryset.filter(author__in=following_users)
        serializer = PostSerializer(
            queryset, many=True, context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="title",
                description="Filter by title insensitive contains",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                "tags",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by tag ids (ex. ?tags=4,7)",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """List posts with filter by title or tags"""
        return super().list(request, *args, **kwargs)
