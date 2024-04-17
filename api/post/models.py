from django.db import models
from django.contrib.auth import get_user_model
from api.base.models import BaseModel
from django.db.models import UniqueConstraint
# Create your models here.

User = get_user_model()
class Post(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts_user")
    file = models.FileField(upload_to="post-users/")
    caption = models.TextField(max_length=2000, null=True, blank=True)

    class Meta:
        db_table = "posts"
        verbose_name = "post"
        verbose_name_plural = "posts"
    
    def __str__(self) -> str:
        return f"{self.author} post about --> {self.caption}"


class Comment(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_user")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comment_post")
    text = models.CharField(max_length=500)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="child_parent",
        null=True,
        blank=True
    )

    def __str__(self) -> str:
        return f"{self.author} comment about --> {self.text}|24"


class PostLike(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="postLike_user")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="postLike_post")
    
    class Meta:
        constraints = [ ### this is for being unique
            UniqueConstraint(
                fields=["author", "post"],
                name="postLike_constraint"
            )
        ]
    
    def __str__(self) -> str:
        return f"{self.author} liked post --> {self.post}"


class CommentLike(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="CommentLike_user")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="commentLike_post")
    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["author", "comment"],
                name="commentLike_constraint"
            )
        ]

    def __str__(self) -> str:
        return f"{self.author} like comment --> {self.comment.text}"