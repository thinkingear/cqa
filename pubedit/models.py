from django.db import models
from core.models import Content
from account.models import User
from core.models import Content
from tinymce.models import HTMLField
# Create your models here.


class Article(Content):
    title = models.CharField(max_length=128, null=False, blank=False)
    followers = models.ManyToManyField(User, through='ArticleFollower', related_name='followed_articles')
    feed = HTMLField(null=True, blank=True)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class ArticleFollower(models.Model):
    article = models.ForeignKey('pubedit.Article', on_delete=models.CASCADE)
    follower = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'article'], name='article_follower')
        ]
