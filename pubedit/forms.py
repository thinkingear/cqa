from django.forms import ModelForm
from .models import Article, ArticleFeed


class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ['title']


class ArticleFeedForm(ModelForm):
    class Meta:
        model = ArticleFeed
        fields = ['feed']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['feed'].widget.attrs.update({'class': 'tinymce-editor'})
