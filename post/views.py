from django.shortcuts import render
from rest_framework import viewsets

from post.models import Tag
from post.serializers import TagSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = []
