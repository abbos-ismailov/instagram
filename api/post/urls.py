from django.urls import path
from .views import (
    PostListApiView,
    PostCreateApiView,
    PostRetriveUpdateDestroyApiView,
    CommentAddListApiView,
    CommentLikeListAddView,
    PostLikeApiView,
    CommentLikeApiView
)


urlpatterns = [
    path("lists/", PostListApiView.as_view()),
    path("create/", PostCreateApiView.as_view()),
    path("update-del/<uuid:pk>", PostRetriveUpdateDestroyApiView.as_view()),
    path("post-like/<uuid:pk>", PostLikeApiView.as_view()),
    path("comment/", CommentAddListApiView.as_view()),
    path("comment-like/", CommentLikeListAddView.as_view()),
    path("comment-like/<uuid:pk>", CommentLikeApiView.as_view()),
]