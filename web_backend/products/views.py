from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from web_backend.models import Product, ProductAd, ProductRecommendation, Comment
from .serializer import CRUDProductSerializer
from web_backend.file_uploads import validate_file_size, upload_to_cloudinary


@api_view(['GET'])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    # Lấy danh sách các đề xuất sản phẩm
    recommendations = ProductRecommendation.objects.filter(product=product)
    unique_recommendations = {rec.user.username: rec for rec in recommendations}.values()
     # Tạo dữ liệu đề xuất với trường description từ ProductRecommendation
    recommendation_data = [{
        "user": recommendation.user.username,
        "description": recommendation.description
    } for recommendation in unique_recommendations]
    # Lấy danh sách các quảng cáo (ads) liên quan đến sản phẩm
    ads = ProductAd.objects.filter(product=product)
    unique_ads = {ad.product_ad_id: ad for ad in ads}.values()
    ad_data = [{
        "ad_title": ad.ad.title if ad.ad else "No Title"
    } for ad in unique_ads]
    # Lấy danh sách các comment liên quan đến sản phẩm
    comments = Comment.objects.filter(product=product)
    unique_comments = {comment.comment_id: comment for comment in comments}.values()
    comment_data = [{
        "user": comment.user.username,
        "comment": comment.comment,
        "rating": comment.rating,
        "created_at": comment.created_at
    } for comment in unique_comments]
    # Tạo dữ liệu sản phẩm
    product_data = {
        "name": product.name,
        "price": product.price,
        "category": product.category.category_name if product.category else None,
        "description": product.description,
        "seller": product.seller.username if product.seller else None,
        "quantity": product.quantity,
        "image_url": product.image_url,   
        "video_url": product.video_url,
        "recommendations": recommendation_data,
        "ads": ad_data,
        "comments": comment_data
    }

    return Response(product_data, status=status.HTTP_200_OK)

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def product_crud(request, pk=None):
    if request.method == 'GET' and pk:
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CRUDProductSerializer(product)
        return Response(serializer.data)

    if request.method == 'POST':
        product_data = request.data
        image_url = product_data.get('image_url')
        video_url = product_data.get('video_url')
        # Kiểm tra và tải ảnh lên Cloudinary từ URL nếu có
        if image_url:
            try:
                uploaded_image_url = upload_to_cloudinary(image_url)
                product_data['image_url'] = uploaded_image_url  # Lưu URL ảnh sau khi tải lên Cloudinary
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # Kiểm tra nếu sản phẩm đã tồn tại
        if Product.objects.filter(name=product_data.get('name')).exists():
            return Response({"error": "Product already exists."}, status=status.HTTP_400_BAD_REQUEST)
        # Lưu sản phẩm mới
        serializer = CRUDProductSerializer(data=product_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT' and pk:
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        # Cập nhật sản phẩm
        serializer = CRUDProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE' and pk:
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        # Xóa sản phẩm
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    return Response({"error": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    