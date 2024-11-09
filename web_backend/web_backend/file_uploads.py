import requests
from django.conf import settings

def validate_file_size(file):
    """Kiểm tra kích thước tệp."""
    if file.size > settings.MAX_FILE_SIZE:
        raise Exception("File size exceeds the 10MB limit.")

def upload_to_cloudinary(file, resource_type='image'):
    """Upload a file (image or video) to Cloudinary."""
    url = f"https://api.cloudinary.com/v1_1/{settings.CLOUDINARY['CLOUD_NAME']}/upload"
    
    # Dữ liệu cho upload
    data = {
        'upload_preset': 'your_upload_preset',  # Đảm bảo đã cấu hình upload preset trên Cloudinary
        'api_key': settings.CLOUDINARY['API_KEY'],
        'api_secret': settings.CLOUDINARY['API_SECRET'],
    }

    # Gửi yêu cầu POST lên Cloudinary với tệp
    files = {
        'file': file,
    }

    response = requests.post(url, data=data, files=files)
    
    if response.status_code == 200:
        # Trả về URL của ảnh/video đã được tải lên
        return response.json().get('secure_url')
    else:
        raise Exception(f"Cloudinary upload failed: {response.text}")
    
