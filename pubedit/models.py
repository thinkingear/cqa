from django.db import models
from core.models import Content
from account.models import User
from core.models import Content, Tag, ContentFollower
# Create your models here.


class Article(Content):
    title = models.CharField(max_length=128, null=False, blank=False)
    followers = models.ManyToManyField(User, through='ArticleFollower', related_name='followed_articles')
    views = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, through='ArticleTag', related_name='tagged_articles')

    def __str__(self):
        return self.title

    @classmethod
    def get_tag_relation_model(cls):
        return ArticleTag

    @property
    def latest_article_feed(self):
        return self.feeds.filter(is_pending=False).order_by('-created').first()

    @property
    def feed(self):
        latest_feed = self.latest_article_feed
        if latest_feed is None:
            return ''
        else:
            return latest_feed.feed

    class Meta:
        ordering = ['-created', '-updated']


class ArticleFeed(Content):
    article = models.ForeignKey('pubedit.Article', on_delete=models.CASCADE, related_name='feeds')
    parent = models.ForeignKey('pubedit.ArticleFeed', on_delete=models.SET_NULL, null=True, related_name='child')
    is_initial = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=False)
    feed = models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-created', '-updated']


class ArticleFollower(ContentFollower):
    article = models.ForeignKey('pubedit.Article', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'article'], name='article_follower')
        ]
        ordering = ['-created']


class ArticleTag(models.Model):
    article = models.ForeignKey('pubedit.Article', on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
