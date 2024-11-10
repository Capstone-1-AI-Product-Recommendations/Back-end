import requests
import cloudinary
import cloudinary.uploader
from django.core.files.base import ContentFile
from django.conf import settings
from django.http import JsonResponse

cloudinary.config( 
    cloud_name = settings.CLOUDINARY['CLOUD_NAME'], 
    api_key = settings.CLOUDINARY['API_KEY'],
    api_secret = settings.CLOUDINARY['API_SECRET'],
    secure=True
)

def validate_file_size(file):
    """Kiểm tra kích thước tệp."""
    if file.size > settings.MAX_FILE_SIZE:
        raise Exception("File size exceeds the 10MB limit.")

def upload_to_cloudinary(image_url=None, video_url=None, public_id="default"):
    """Tải ảnh từ URL và upload lên Cloudinary."""
    try:
        # Nếu là URL ảnh, gọi upload cho ảnh
        if image_url:
            upload_result = cloudinary.uploader.upload(image_url, public_id=public_id)
            secure_url = upload_result["secure_url"]
            print(f"Image uploaded successfully: {secure_url}")
            return secure_url        
        # Nếu là URL video, gọi upload cho video
        if video_url:
            upload_result = cloudinary.uploader.upload(video_url, resource_type="video", public_id=public_id)
            secure_url = upload_result["secure_url"]
            print(f"Video uploaded successfully: {secure_url}")
            return secure_url
        # Nếu không có URL hợp lệ
        print("Error: No valid URL provided.")
        return None        
    except Exception as e:
        print(f"Error: {e}")
        return None

def handle_image_video_upload(request):
    """API endpoint to handle image upload from user (either URL or file)"""    
    if request.method == 'POST':
        # Kiểm tra xem có URL ảnh không
        image_url = request.data.get('image_url')  # Người dùng gửi URL ảnh từ web
        video_url = request.data.get('video_url')  # Người dùng gửi URL video từ web
        if image_url:
            # Tải ảnh từ URL lên Cloudinary
            uploaded_image_url = upload_to_cloudinary(image_url=image_url)
            if uploaded_image_url:
                return JsonResponse({"image_url": uploaded_image_url}, status=200)
            else:
                return JsonResponse({"error": "Image upload failed."}, status=400)        
        if video_url:
            # Tải video từ URL lên Cloudinary
            uploaded_video_url = upload_to_cloudinary(image_url=video_url, public_id="video")  # Thay đổi public_id cho video
            if uploaded_video_url:
                return JsonResponse({"video_url": uploaded_video_url}, status=200)
            else:
                return JsonResponse({"error": "Video upload failed."}, status=400)        
        # Nếu không có URL ảnh, thì có thể người dùng upload ảnh từ thiết bị
        image_file = request.FILES.get('image')  # Người dùng upload ảnh
        video_file = request.FILES.get('video')  # Người dùng upload video        
        if image_file:
            # Kiểm tra kích thước tệp trước khi upload
            try:
                validate_file_size(image_file)
                upload_result = cloudinary.uploader.upload(image_file)
                uploaded_image_url = upload_result["secure_url"]
                return JsonResponse({"image_url": uploaded_image_url}, status=200)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=400)        
        if video_file:
            # Kiểm tra kích thước tệp trước khi upload
            try:
                validate_file_size(video_file)
                upload_result = cloudinary.uploader.upload(video_file)
                uploaded_video_url = upload_result["secure_url"]
                return JsonResponse({"video_url": uploaded_video_url}, status=200)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=400)        
        return JsonResponse({"error": "No image or video provided."}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)