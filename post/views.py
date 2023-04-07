from django.shortcuts import redirect, render


# Create your views here.

def post_create_page(request):

    return render(request, 'post/article_create.html')
