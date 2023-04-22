from django.shortcuts import redirect, render
from .forms import ArticleForm, ArticleFeedForm
from .models import Article, ArticleTag
from core.views import content_follow, tags_handler
from django.views.decorators.csrf import csrf_exempt

# Create your views here.


def article_create_page(request):
    if request.method == 'POST':
        article_form = ArticleForm(request.POST)
        article_feed_form = ArticleFeedForm(request.POST)

        article = article_form.save(commit=False)
        article_feed = article_feed_form.save(commit=False)

        article.poster = request.user
        article.save()

        article_feed.article = article
        article_feed.is_initial = True
        article_feed.poster = request.user
        article_feed.save()

        return redirect('core:home')

    article_form = ArticleForm()
    article_feed_form = ArticleFeedForm()
    context = {'article_form': article_form, 'article_feed_form': article_feed_form}
    return render(request, 'pubedit/article_create.html', context)


@csrf_exempt
def article_follow(request):
    return content_follow(request, 'article', 'articlefollower')


@csrf_exempt
def article_tags_handler(request):
    return tags_handler(request, Article, ArticleTag)

