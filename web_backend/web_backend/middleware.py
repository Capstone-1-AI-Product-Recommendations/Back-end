import redis
import json
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)

# Kết nối Redis
def get_redis_connection():
    return redis.Redis(host='127.0.0.1', port=6379, db=1)

# Hàm ghi dữ liệu vào cache
def cache_action(session_id, action_type, user_id=None, product_id=None, quantity=1, search_query=None):
    try:
        r = get_redis_connection()
        key = f"user_behavior:{session_id}"  # Sử dụng session_id làm key
        action = {
            "user_id": user_id,
            "session_id": session_id,
            "action_type": action_type,
            "product_id": product_id,
            "quantity": quantity,
            "search_query": search_query,
            "timestamp": now().isoformat(),
        }
        r.rpush(key, json.dumps(action))  # Thêm dữ liệu vào danh sách
        r.expire(key, 3600 * 24)  # Đặt thời gian hết hạn là 1 ngày
        logger.info(f"Cached action: {action} under key: {key}")
    except redis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")