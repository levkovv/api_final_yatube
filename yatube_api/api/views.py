from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from posts.models import Group, Post
from .permissions import IsAuthorOrReadOnly
from .serializers import (CommentSerializer, FollowSerializer, GroupSerializer,
                          PostSerializer)

User = get_user_model()


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        comments = post.comments.all()
        return comments

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        post_id=self.kwargs.get('post_id'))


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        user = self.request.user
        new_queryset = user.follower.all()
        return new_queryset

    def perform_create(self, serializer):
        user_to_following = get_object_or_404(
            User, username=serializer.initial_data.get('following'))
        serializer.save(
            user=self.request.user,
            following=user_to_following
        )
