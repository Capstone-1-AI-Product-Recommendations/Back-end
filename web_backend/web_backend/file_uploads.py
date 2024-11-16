from PIL import Image
from io import BytesIO
from moviepy.editor import VideoFileClip
import os

def compress_image(image_file):
    """
    Nén ảnh trước khi upload.
    """
    img = Image.open(image_file)
    img = img.convert('RGB')  # Đảm bảo là ảnh RGB
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=85)  # Nén ảnh với chất lượng 85%
    buffer.seek(0)
    return buffer

def compress_video(self, video_file):
    temp_path = video_file.temporary_file_path()
    output_path = "/tmp/compressed_video.mp4"
    clip = VideoFileClip(temp_path)
    clip.write_videofile(output_path, bitrate="500k", audio_codec="aac")
    return open(output_path, 'rb')