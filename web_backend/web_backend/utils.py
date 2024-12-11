import cloudinary
import cloudinary.uploader
import os
from PIL import Image
import tempfile
import requests

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


def transfer_funds(bank_name, account_number, account_holder_name, amount, description):
    
    # Args:
    #     bank_name (str): Tên ngân hàng của seller.
    #     account_number (str): Số tài khoản ngân hàng của seller.
    #     account_holder_name (str): Tên chủ tài khoản của seller.
    #     amount (float): Số tiền cần chuyển.
    #     description (str): Mô tả giao dịch (ví dụ: "Payment for order 123").
    
    # Returns:
    #     Response: Phản hồi từ API của PayOS hoặc lỗi nếu có.
    
    # URL của PayOS (hoặc hệ thống chuyển tiền bạn đang sử dụng)
    payos_url = "https://api.payos.com/transfer"  # Đây chỉ là ví dụ, thay thế bằng URL thật

    # Thông tin cần truyền vào API của PayOS
    payload = {
        "bank_name": bank_name,
        "account_number": account_number,
        "account_holder_name": account_holder_name,
        "amount": amount,
        "description": description,
    }

    # Thực hiện gọi API để chuyển tiền
    try:
        response = requests.post(payos_url, json=payload)

        # Kiểm tra nếu trả về mã thành công (200 OK)
        if response.status_code == 200:
            return response  # Thành công
        else:
            return response  # Trả lại phản hồi từ PayOS nếu thất bại

    except requests.exceptions.RequestException as e:
        # Xử lý lỗi khi không thể kết nối với API
        return {"error": str(e)}
