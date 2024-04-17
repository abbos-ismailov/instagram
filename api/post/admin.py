from django.contrib import admin
from .models import Post, Comment, PostLike, CommentLike
# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ["id", "author", "created_time"]
    search_fields = ["id", "author__username", "caption"]


class CommentAdmin(admin.ModelAdmin):
    list_display = ["id", "author", "created_time"]
    search_fields = ["id", "author__username", "text"]


class PostLikeAdmin(admin.ModelAdmin):
    list_display = ["id", "author", "created_time"]
    search_fields = ["id", "author__username", "post__caption"]


class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ["id", "author", "created_time"]
    search_fields = ["id", "author__username", "comment_text"]


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(PostLike, PostLikeAdmin)
admin.site.register(CommentLike, CommentLikeAdmin)
