from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Cấu hình Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_backend.settings')

# Tạo ứng dụng Celery
app = Celery('web_backend')

# Cấu hình Celery từ Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Tự động phát hiện task từ tất cả các ứng dụng đã cài đặt
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Cấu hình backend cho Celery
app.conf.update(
    broker_url='redis://localhost:6379/0',  # Ensure the broker URL is correct
    result_backend='redis://localhost:6379/0',  # Ensure the result backend URL is correct
)