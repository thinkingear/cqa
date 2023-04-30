import os
from celery import Celery
from django.conf import settings
from cqa import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cqa.settings')

app = Celery('cqa')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

