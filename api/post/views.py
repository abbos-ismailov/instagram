from django.shortcuts import render, get_object_or_404
from rest_framework import generics, views, response, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from .models import Post, PostLike, Comment, CommentLike
from api.accounts.models import User
from .serializers import PostSerializer, PostLikeSerializer, CommentSerializer, CommentLikeSerializer
from api.base.custom_pagination import CustomPagination
# Create your views here.


class PostListApiView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny, ]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Post.objects.all()


class PostCreateApiView(views.APIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = PostSerializer

    def post(self, request):
            request.data["author"] = request.user.id
            data = request.data
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                data_response = {"status": True, "data": data}
                return response.Response(data_response, status=status.HTTP_201_CREATED)


class PostRetriveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]

    def put(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.serializer_class(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response({
            "status": True,
            "message": "Updated successfully"
        })

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        post.delete()
        return response.Response({
            "status": True,
            "message": "Delete successfully"
        })


class CommentAddListApiView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Comment.objects.filter(post__id=self.request.data.get("post"), parent=None)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentLikeListAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    serializer_class = CommentLikeSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = CommentLike.objects.filter(comment__id=self.request.data.get("comment")).order_by("created_time")
        return queryset    
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostLikeApiView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            post_like = PostLike.objects.create(
                author=self.request.user,
                post_id=pk
            )
            serializer = PostLikeSerializer(post_like)
            data = {
                "status": True,
                "message": "bu postga like bosildi",
                "data": serializer.data
            }
            return response.Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            data = {
                "status": False,
                "message": f"{e}",
                "data": None
            }
            return response.Response(data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            post_like = PostLike.objects.get(
                author=self.request.user,
                post_id=pk
            )
            post_like.delete()
            data = {
                "status": True,
                "message": "LIKE o'chirildi",
                "data": None
            }
            return response.Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            data = {
                "status": False,
                "message": f"{e}",
                "data": None
            }
            return response.Response(data, status=status.HTTP_400_BAD_REQUEST)


class CommentLikeApiView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            comment_like = CommentLike.objects.create(
                author=self.request.user,
                comment_id=pk
            )
            serializer = CommentLikeSerializer(comment_like)
            data = {
                "status": True,
                "message": "bu commentga like bosildi",
                "data": serializer.data
            }
            return response.Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            data = {
                "status": False,
                "message": f"{e}",
                "data": None
            }
            return response.Response(data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            comment_like = CommentLike.objects.get(
                author=self.request.user,
                comment_id=pk
            )
            comment_like.delete()
            data = {
                "status": True,
                "message": "LIKE o'chirildi",
                "data": None
            }
            return response.Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            data = {
                "status": False,
                "message": f"{e}",
                "data": None
            }
            return response.Response(data, status=status.HTTP_400_BAD_REQUEST)



