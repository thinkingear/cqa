from django.urls import path, include
from . import views

app_name = 'pubedit'

urlpatterns = [
    path('create/', views.article_create_page, name='article_create'),
]
