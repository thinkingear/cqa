from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from qa.models import Question

# Create your views here.

def search_page(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    # rooms = Room.objects.filter(
    #     Q(topic__name__icontains=q) |
    #     Q(name__icontains=q) |
    #     Q(description__icontains=q)
    # )
    contents = []

    questions = Question.objects.filter(
        Q(title__icontains=q)
    )

    contents += questions

    context = {'search_query': q, 'contents': contents}
    return render(request, 'search/search.html', context)
