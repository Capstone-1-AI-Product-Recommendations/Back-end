import cloudinary
import cloudinary.uploader
import os
from PIL import Image
import tempfile

cloudinary.config(
    cloud_name='dkleeailh',  # Thay bằng cloud_name của bạn
    api_key='171326873511271',  # Thay bằng api_key của bạn
    api_secret='aIwwnuXsnlhQYM0VsavcR_l56kQ'  # Thay bằng api_secret của bạn
)

def compress_and_upload_image(image):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        img = Image.open(image)
        
        # Kiểm tra và chuyển đổi sang chế độ RGB nếu ảnh có kênh alpha (RGBA)
        if img.mode in ("RGBA", "P"):  
            img = img.convert("RGB")
        
        # Lưu ảnh tạm với chất lượng nén 80%
        img.save(tmp_file.name, format="JPEG", quality=80)
        tmp_file.flush()

        # Upload lên Cloudinary
        response = cloudinary.uploader.upload(tmp_file.name)
    
    # Xóa file tạm
    os.remove(tmp_file.name)
    
    # Trả về URL của ảnh
    return response["url"]

def compress_and_upload_video(video_file):
    response = cloudinary.uploader.upload(
        video_file,
        folder="products/videos/",
        resource_type="video",
        chunk_size=10 * 1024 * 1024  # Đảm bảo từng chunk nhỏ hơn 10MB
    )
    return response.get('secure_url')
