from rest_framework import serializers
from api.accounts.models import User
from .models import Post, PostLike, Comment, CommentLike
from rest_framework.exceptions import ValidationError



class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    
    class Meta:
        model = User
        fields = ["id", "username", "photo"]
    
    
class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    post_likes_count = serializers.SerializerMethodField("get_post_likes_count")
    post_comments_count = serializers.SerializerMethodField("get_post_comments_count")
    me_liked = serializers.SerializerMethodField("get_me_liked")
    
    class Meta:
        model = Post
        fields = ["id", "author", "file", "caption", "created_time", 'post_likes_count', 'post_comments_count', "me_liked"]

    def get_post_likes_count(self, obj):
        return obj.postLike_post.count()
    
    def get_post_comments_count(self, obj):
        return obj.comment_post.count()

    def get_me_liked(self, obj):
        request = self.context.get("request", None)
        if request and request.user.is_authenticated:
            try:
                like = PostLike.objects.get(post=obj, author=request.user)
                return True
            except PostLike.DoesNotExist:
                return False
        return False


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField("get_replies")
    likes_count = serializers.SerializerMethodField("get_likes_count")
    me_liked = serializers.SerializerMethodField("get_me_liked")

    class Meta:
        model = Comment
        fields = ["id", "author", "post", "text", "parent", "created_time", "replies", "me_liked", "likes_count"]


    def get_replies(self, obj):
        if obj.child_parent.exists():
            serializers = self.__class__(obj.child_parent.all(), many=True, context=self.context)
            return serializers.data
        else:
            return None
        
    def get_me_liked(self, obj):
        request = self.context.get("request", None)
        if request.user.is_authenticated:
            return obj.commentLike_post.filter(author=request.user).exists()
        else:
            return False
    
    def get_likes_count(self, obj):
        return obj.commentLike_post.count()


class CommentLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = CommentLike
        fields = ["id", "author", "comment"]



class PostLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = PostLike
        fields = ["id", "author", "post"]

