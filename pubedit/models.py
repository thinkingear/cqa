from django.db import models
from core.models import Content
from account.models import User
from core.models import Content
from tinymce.models import HTMLField
from account.models import ArticleFollower
# Create your models here.


class Article(Content):
    title = models.CharField(max_length=128, null=False, blank=False)
    followers = models.ManyToManyField(User, through=ArticleFollower, related_name='followed_articles')
    feed = HTMLField(null=True, blank=True)

    def __str__(self):
        return self.title
