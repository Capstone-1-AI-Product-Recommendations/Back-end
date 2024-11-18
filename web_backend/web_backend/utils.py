import cloudinary
import cloudinary.uploader
import io
from PIL import Image

def compress_and_upload_image(image_file):
    img = Image.open(image_file)
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG', quality=85)  # Giảm chất lượng để nén
    img_io.seek(0)

    response = cloudinary.uploader.upload(
        img_io,
        folder="products/images/",
        resource_type="image",
    )
    return response.get('secure_url')

def compress_and_upload_video(video_file):
    response = cloudinary.uploader.upload(
        video_file,
        folder="products/videos/",
        resource_type="video",
        chunk_size=10 * 1024 * 1024  # Đảm bảo từng chunk nhỏ hơn 10MB
    )
    return response.get('secure_url')
