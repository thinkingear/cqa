from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('search/', views.search_page, name='search'),
    path('vote/', views.vote, name='vote'),
    path('comment/', views.comment, name='comment'),
    path('history/', views.history_handler, name='history'),
]

