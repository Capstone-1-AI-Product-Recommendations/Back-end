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

from django.db import connections
from django.db.utils import OperationalError

@shared_task
def sync_to_backup():
    """
    Đồng bộ dữ liệu từ database 'default' sang database 'backup', chỉ chèn hoặc cập nhật dữ liệu mới.
    """
    try:
        source_connection = connections['default']
        backup_connection = connections['backup']

        with source_connection.cursor() as source_cursor, backup_connection.cursor() as backup_cursor:
            # Danh sách các bảng cần đồng bộ
            tables = [
                'ad', 'cart', 'cart_item', 'category', 'subcategory',
                'comment', 'notification', '`order`', 'order_item',
                'payment', 'product', 'product_ad', 'product_image',
                'product_recommendation', 'product_video', 'role',
                'seller_profile', 'shop', 'shop_info', 'user',
                'user_bank_account', 'user_browsing_behavior',
                'shipping_address', 'purchased_product', 'user_behavior'
            ]

            for table in tables:
                # Lấy danh sách cột từ bảng
                source_cursor.execute(f"SHOW COLUMNS FROM {table}")
                columns = [col[0] for col in source_cursor.fetchall()]

                # Lấy tất cả dữ liệu từ bảng chính
                source_cursor.execute(f"SELECT * FROM {table}")
                rows = source_cursor.fetchall()

                if rows:
                    column_list = ', '.join([f"`{col}`" for col in columns])  # Thêm ` cho các cột
                    placeholders = ', '.join(['%s'] * len(columns))
                    
                    # Câu lệnh INSERT với `ON DUPLICATE KEY UPDATE`
                    insert_query = f"""
                        INSERT INTO {table} ({column_list})
                        VALUES ({placeholders})
                        ON DUPLICATE KEY UPDATE {', '.join([f"`{col}`=VALUES(`{col}`)" for col in columns])};
                    """
                    
                    # Chèn dữ liệu chỉ khi chưa tồn tại hoặc cập nhật nếu cần
                    backup_cursor.executemany(insert_query, rows)

        return "Data synchronization completed successfully."
    except Exception as e:
        return f"Data synchronization failed: {str(e)}"
