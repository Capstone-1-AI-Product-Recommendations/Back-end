from PIL import Image
from io import BytesIO
from cloudinary.uploader import upload

def compress_and_upload_image(image_file):
    try:
        # Nén ảnh
        image = Image.open(image_file)
        image = image.convert('RGB')  # Chuyển ảnh sang RGB nếu cần thiết
        output = BytesIO()
        image.save(output, format="JPEG", quality=85)  # Chất lượng ảnh 85%
        output.seek(0)

        # Upload ảnh lên Cloudinary
        response = upload(output, folder='products/images/')
        return response['secure_url']
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None

def compress_and_upload_video(video_file):
    try:
        # Upload video lên Cloudinary
        response = upload(video_file, resource_type="video", folder='products/videos/')
        return response['secure_url']
    except Exception as e:
        print(f"Error uploading video: {e}")
        return None