import os
from celery import Celery
from django.apps import apps
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('main', include=['main.tasks'])
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_connection_retry_on_startup = True
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])



