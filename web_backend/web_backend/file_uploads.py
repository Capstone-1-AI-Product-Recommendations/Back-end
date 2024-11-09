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

def upload_to_cloudinary(image_url, public_id="default"):
    """Tải ảnh từ URL và upload lên Cloudinary."""
    try:
        # Tải ảnh từ URL lên Cloudinary
        upload_result = cloudinary.uploader.upload(image_url, public_id=public_id)
        # Lấy URL bảo mật của ảnh
        secure_url = upload_result["secure_url"]
        
        print(f"Image uploaded successfully: {secure_url}")
        return secure_url
    except Exception as e:
        print(f"Error: {e}")
        return None

def handle_image_upload(request):
    """API endpoint to handle image upload from user (either URL or file)"""
    
    if request.method == 'POST':
        # Kiểm tra xem có URL ảnh không
        image_url = request.data.get('image_url')  # Người dùng gửi URL ảnh từ web

        if image_url:
            # Tải ảnh từ URL lên Cloudinary
            uploaded_image_url = upload_image_from_url(image_url)
            if uploaded_image_url:
                return JsonResponse({"image_url": uploaded_image_url}, status=200)
            else:
                return JsonResponse({"error": "Image upload failed."}, status=400)
        
        # Nếu không có URL ảnh, thì có thể người dùng upload ảnh từ thiết bị
        image_file = request.FILES.get('image')  # Người dùng upload ảnh

        if image_file:
            # Tải ảnh từ file lên Cloudinary
            upload_result = cloudinary.uploader.upload(image_file)
            uploaded_image_url = upload_result["secure_url"]
            return JsonResponse({"image_url": uploaded_image_url}, status=200)
        
        return JsonResponse({"error": "No image provided."}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)