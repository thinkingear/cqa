from diff_match_patch import diff_match_patch
from django.forms import model_to_dict
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


def compare_feeds(feed1, feed2):
    dmp = diff_match_patch()

    # 计算两个 feeds 之间的差异
    diffs = dmp.diff_main(feed1, feed2)

    # 标准化差异结果
    dmp.diff_cleanupSemantic(diffs)

    # 将差异结果转换为 HTML 格式
    html_diff = dmp.diff_prettyHtml(diffs)

    # 删除 "¶" 字符
    html_diff = html_diff.replace("&para;", "")

    return html_diff


def article_log(request, pk):
    article = Article.objects.get(id=pk)
    article_feeds = [article_feed for article_feed in article.feeds.all().filter(is_pending=False)]

    article_feeds_with_last_twice = article_feeds + [article_feeds[-1]]

    article_diff_htmls = []

    for i in range(1, len(article_feeds_with_last_twice), 1):
        article_diff_htmls.append(compare_feeds(article_feeds_with_last_twice[i - 1].feed, article_feeds_with_last_twice[i].feed))

    combined_data = zip(article_feeds, article_diff_htmls)
    context = {'article': article, 'combined_data': combined_data}
    return render(request, 'pubedit/article_log.html', context)


def article_update(request, pk):
    article = Article.objects.get(id=pk)
    if request.method == 'GET':
        article_dict = model_to_dict(article)
        article_form = ArticleForm(article_dict)

        article_feed_dict = model_to_dict(article.latest_article_feed)
        article_feed_form = ArticleFeedForm(article_feed_dict)

        blank_article_feed_form = ArticleFeedForm()

        context = {'article': article, 'article_form': article_form, 'article_feed_form': article_feed_form, 'blank_article_feed_form': blank_article_feed_form}
        return render(request, 'pubedit/article_update.html', context)
    elif request.method == 'POST':
        article_form = ArticleForm(request.POST)
        article_feed_form = ArticleFeedForm(request.POST)
        if article_form.is_valid() and article_feed_form.is_valid():
            article_new = article_form.save(commit=False)
            if article_new.title != article.title:
                article.title = article_new.title
                article.save()

            article_feed = article_feed_form.save(commit=False)
            article_feed.article = article
            article_feed.parent = article.latest_article_feed
            # article_feed the actual poster
            # need to revise when the 'pull requeset' function completed
            article_feed.poster = article.poster

            article_feed.save()

            return redirect('core:home')


