from django.urls import path
from . import views

app_name = 'course'

urlpatterns = [
    path('my/', views.my_course, name='my_course'),
    path('new/', views.new_course, name='new_course'),
    path('detial/<str:pk>/', views.course_detial, name='course_detial'),
    path('<str:pk>/', views.course_delete, name='course_delete'),
    path('course/follow/', views.course_follow, name='course_follow'),
    path('update/<str:course_id>', views.update_course, name='update_course'),
]
