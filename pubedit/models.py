from django.db import models
from core.models import Content
from account.models import User
from core.models import Content, Tag
from tinymce.models import HTMLField
# Create your models here.


class Article(Content):
    title = models.CharField(max_length=128, null=False, blank=False)
    followers = models.ManyToManyField(User, through='ArticleFollower', related_name='followed_articles')
    feed = HTMLField(null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, through='ArticleTag', related_name='tagged_articles')

    def __str__(self):
        return self.title

    @classmethod
    def get_tag_relation_model(cls):
        return ArticleTag

    class Meta:
        ordering = ['-updated', '-created']


class ArticleFollower(models.Model):
    article = models.ForeignKey('pubedit.Article', on_delete=models.CASCADE)
    follower = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'article'], name='article_follower')
        ]


class ArticleTag(models.Model):
    article = models.ForeignKey('pubedit.Article', on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)