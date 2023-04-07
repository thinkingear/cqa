from django.db import models
from core.models import Content, ContentVote
from account.models import User
from core.models import Content
from tinymce.models import HTMLField
from django.db.models import Sum
# Create your models here.


class Article(Content):
    title = models.CharField(max_length=128, null=False, blank=False)
    feed = HTMLField(null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def sum(self):
        total_votes = ArticleVote.objects.filter(answer=self).aggregate(sum_of_votes=Sum('vote'))
        return total_votes


class ArticleVote(ContentVote):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'article'], name='article_vote')
        ]
