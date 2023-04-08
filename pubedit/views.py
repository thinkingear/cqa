from django.shortcuts import redirect, render
from .forms import ArticleForm
from .models import Article

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
