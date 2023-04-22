from django.urls import path
from . import views

app_name = 'qa'

urlpatterns = [
    path('question/create/', views.question_create_page, name='question_create'),
    path('answer/create/<str:pk>/', views.answer_create_page, name='answer_create'),
    path('question/<str:pk>/detail/', views.question_detial, name='question_detail'),
    path('question/follow/', views.question_follow, name='question_follow'),
    path('answer/follow/', views.answer_follow, name='answer_follow'),
    path('question/tag/', views.question_tags_handler, name='question_tags_handler'),
    path('question/ai/', views.generate_answer, name='generate_answer_for_question'),
]
