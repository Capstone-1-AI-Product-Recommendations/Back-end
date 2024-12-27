from django.core.cache import cache 
from rest_framework.response import Response
from rest_framework.views import APIView
from products.views import get_user_id_from_cookie
from .tasks import generate_recommendations, recommend_behavior
from celery.result import AsyncResult
from rest_framework.decorators import api_view
import time
class BatchRecommendationsView(APIView):
    def get(self, request, user_id):
        # Kiểm tra user_id hợp lệ
        if not user_id:
            return Response({"error": "Invalid user_id"}, status=400)

        # Tạo cache key để ánh xạ user_id -> task_id
        user_task_key = f"user_task_map:{user_id}"
        task_user_key = f"task_user_map"

        # Kiểm tra xem user_id đã có task_id chưa
        existing_task_id = cache.get(user_task_key)
        if existing_task_id:
            print(f"User {user_id} đã có task_id: {existing_task_id}, trả về task cũ")
            return Response({"user_id": user_id, "task_id": existing_task_id})

        # Nếu chưa có trong cache, tạo task mới
        print(f"User {user_id} chưa có task, tạo task mới")
        task = generate_recommendations.delay(user_id)

        # Lưu ánh xạ user_id -> task_id và task_id -> user_id
        cache.set(user_task_key, task.id, timeout=3600)  # Lưu user_id -> task_id
        cache.set(f"{task_user_key}:{task.id}", {"user_id": user_id}, timeout=3600)  # Lưu task_id -> user_id

        print(f"New task_id={task.id} created for user_id={user_id}")
        return Response({"task_id": task.id})

class GetBatchRecommendationsView(APIView):
    def get(self, request, task_id):
        # Tạo cache key để ánh xạ task_id -> user_id
        task_user_key = f"task_user_map:{task_id}"

        # Lấy user_id từ cache dựa trên task_id
        user_data = cache.get(task_user_key)
        user_id = user_data.get("user_id") if user_data else None
        if not user_id:
            return Response({"error": "User ID not found for this task ID"}, status=404)

        # Kiểm tra trạng thái task
        result = AsyncResult(task_id)
        print(f"Checking status for task_id={task_id}, user_id={user_id}")

        # Nếu task đã hoàn thành và kết quả không phải là None, kiểm tra cache
        if result.status == "SUCCESS" and result.result is not None:
            # Lưu kết quả vào cache nếu chưa có
            result_cache_key = f"recommendation_result:{user_id}"
            cached_result = cache.get(result_cache_key)
            if not cached_result:
                cache.set(result_cache_key, result.result, timeout=86400)
                print(f"Kết quả đã được lưu vào cache với key: {result_cache_key}")

        # Trả về trạng thái và kết quả
        response = {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.status == "SUCCESS" else None,
        }
        return Response(response)
    
@api_view(['GET'])
def trigger_recommend_behavior(request):
    print("Received request to trigger recommend_behavior task")
    session_id = request.COOKIES.get('session_id')
    print("session_id", session_id)
    
    user_id = get_user_id_from_cookie(request)
    print("user_id", user_id)
    print(f"Received request with session_id={session_id}, user_id={user_id}")
    if not session_id and not user_id:
        return Response({"error": "Missing session_id or user_id"}, status=400)

    # Gửi task tới Celery
    task = recommend_behavior.apply_async(kwargs={'session_id': session_id, 'user_id': user_id})

    # Đợi kết quả tối đa 15 giây
    timeout = 15
    elapsed = 0
    while elapsed < timeout:
        task_result = AsyncResult(task.id)
        if task_result.state == 'SUCCESS':
            return Response({"status": "success", "result": task_result.result}, status=200)
        elif task_result.state == 'FAILURE':
            return Response({"status": "failed", "error": str(task_result.info)}, status=500)
        time.sleep(1)  # Đợi 1 giây
        elapsed += 1

    # Nếu tác vụ chưa hoàn thành, trả về `task_id` để kiểm tra sau
    return Response({"status": "pending", "task_id": task.id}, status=202)
