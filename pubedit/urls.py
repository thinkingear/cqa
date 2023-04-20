from django.urls import path
from . import views

app_name = 'pubedit'

urlpatterns = [
    path('create/', views.article_create_page, name='article_create'),
    path('article/follow/', views.article_follow, name='article_follow'),
    path('article/tag/', views.article_tags_handler, name='article_tags_handler')
]
