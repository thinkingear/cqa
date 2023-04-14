from django.shortcuts import redirect, render
from .forms import ArticleForm
from core.views import content_follow
from django.views.decorators.csrf import csrf_exempt

# Create your views here.


def article_create_page(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        article = form.save(commit=False)
        article.poster = request.user
        article.save()
        return redirect('core:home')

    form = ArticleForm()
    context = {'form': form}
    return render(request, 'pubedit/article_create.html', context)


@csrf_exempt
def article_follow(request):
    return content_follow(request, 'article', 'articlefollower')
