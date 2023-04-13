from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

app_name = 'account'

urlpatterns = [
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('follow/', views.follow, name='follow'),
    path('profile/<str:user_id>/bio/', csrf_exempt(views.profile_bio), name='profile_bio'),
    path('profile/<str:user_id>/description/', csrf_exempt(views.profile_description), name='profile_description'),
    path('profile/<str:user_id>/', views.profile_page, name='profile'),
    path('profile/<str:user_id>/<str:content_type>/', views.profile_page, name='profile_content_type'),
]
