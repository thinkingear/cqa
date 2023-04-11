from django.urls import path
from . import views

app_name = 'qa'

urlpatterns = [
    path('question/create/', views.question_create_page, name='question_create'),
    path('answer/create/<str:pk>/', views.answer_create_page, name='answer_create'),
    path('question/<str:pk>/detail/', views.question_detial, name='question_detail'),
]
