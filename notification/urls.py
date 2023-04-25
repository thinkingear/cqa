from django.urls import path
from . import views

app_name = 'notification'

# followed updates, content followed, invitation, reqeust pulled
urlpatterns = [
    path("", views.notification_page, name="notification_page"),
    path("invite/question/<str:question_id>/", views.invite_question, name="invite_question"),
    path("pull/request/article/judge/", views.pull_request_article_judge, name="pull_request_article_judge"),
    path("pull/request/article/<str:article_id>/", views.pull_request_article, name="pull_request_article"),
    path("invite/question/<str:question_id>/search/user/", views.search_user_for_invite_question, name="search_recipients_for_question"),
]
