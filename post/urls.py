from django.urls import path, include
from . import views

app_name = 'post'

urlpatterns = [
    path('question/create/', views.post_create_page, name='post_create'),
]
