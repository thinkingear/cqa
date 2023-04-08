from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from qa.models import Question
from pubedit.models import Article

# Create your views here.

def search_page(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''

    contents = []

    # questions = Question.objects.filter(
    #     Q(title__icontains=q)
    # )
    # contents += questions

    articles = Article.objects.filter(
        Q(title__icontains=q)
    )

    contents += articles

    context = {'search_query': q, 'contents': contents}
    return render(request, 'search/search.html', context)
