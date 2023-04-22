from django.forms import ModelForm
from .models import Article, ArticleFeed


class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ['title']


class ArticleFeedForm(ModelForm):
    class Meta:
        model = ArticleFeed
        fields = ['feed', 'comment']
