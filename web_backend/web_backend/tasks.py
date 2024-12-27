import json
import redis
from celery import shared_task
from django.conf import settings
from web_backend.models import UserBehavior
from django.utils.timezone import now
import logging
from celery import Celery

logger = logging.getLogger(__name__)

app = Celery('web_backend')

@shared_task(name="web_backend.tasks.sync_user_behavior")
def sync_user_behavior():
    """
    Đồng bộ dữ liệu từ Redis xuống bảng UserBehavior
    """
    try:
        r = redis.Redis(host='127.0.0.1', port=6379, db=1)
        redis_key_pattern = "user_behavior:*"  # Pattern to match all user behavior keys
        print(redis_key_pattern)
        for key in r.scan_iter(redis_key_pattern):
            while r.llen(key) > 0:
                action_data = r.lpop(key)
                if action_data:
                    action = json.loads(action_data)
                    UserBehavior.objects.create(
                        user_id=action.get("user_id"),
                        session_id=action.get("session_id"),
                        action_type=action.get("action_type"),
                        product_id=action.get("product_id"),
                        quantity=action.get("quantity", 1),
                        search_query=action.get("search_query"),
                        created_at=now(),
                    )
                    logger.debug(f"Synced action: {action} from key: {key}")
    except redis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")

