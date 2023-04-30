"""
WSGI config for cqa project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""
import os
from django.core.wsgi import get_wsgi_application
from qa.recommendations.question.recommend import start_question_recommendation_for_user_task
from django.core.cache import cache
from account.models import User
from cqa import settings
import json
from qa.recommendations.question.recommend import update_question_all_id_similarity_df


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cqa.settings')

application = get_wsgi_application()


if settings.DEBUG:
    # 初始化 question 相似度矩阵
    update_question_all_id_similarity_df()

    # 初始化 user to task_id 散列表
    user_2_question_task_ids = cache.get("user_questions_recommendation_task_ids_json")
    if user_2_question_task_ids is None:
        user_2_question_task_ids = {}
        cache.set("user_questions_recommendation_task_ids_json", json.dumps(user_2_question_task_ids), timeout=None)

    # 为每个 user 单独创建一个 task
    for user in User.objects.all():
        start_question_recommendation_for_user_task(user)
