import json
import celery
from celery import shared_task
from celery.result import AsyncResult
from django.utils import timezone
from account.models import User
from qa.recommendations.question.recommend import _update_questions_recommendation_for_user
from django.core.cache import cache
import numpy as np
from datetime import datetime


