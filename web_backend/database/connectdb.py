import mysql.connector
db = mysql.connector.connect(user='root', password='nhc171103', host='localhost', database='web_backend')
# RUN
mycursor = db.cursor()

try:
    # Thêm dữ liệu vào bảng role
    mycursor.execute("INSERT INTO role (role_name) VALUES ('Admin'), ('User'), ('Seller');")

    # Thêm dữ liệu vào bảng User
    mycursor.execute("""
        INSERT INTO user (username, password, email, full_name, address, phone_number, role_id, reset_token, reset_token_expiry, created_at, updated_at)
        VALUES 
        ('admin_user', 'adminpassword', 'admin@example.com', 'Admin User', 'Admin Street', '1234567890', 1, NULL, NULL, NOW(), NOW()),
        ('normal_user', 'userpassword', 'user@example.com', 'Normal User', 'User Road', '2345678901', 2, NULL, NULL, NOW(), NOW()),
        ('seller1_user', 'sellerpassword1', 'seller1@example.com', 'Seller One', 'Seller St 1', '3456789012', 3, NULL, NULL, NOW(), NOW()),
        ('seller2_user', 'sellerpassword2', 'seller2@example.com', 'Seller Two', 'Seller St 2', '4567890123', 3, NULL, NULL, NOW(), NOW());
    """)

    # Thêm dữ liệu vào bảng Category
    mycursor.execute("""
        INSERT INTO category (category_name, description) 
        VALUES 
        ('Electronics', 'Devices and gadgets'),
        ('Books', 'Wide range of books'),
        ('Clothing', 'Apparel and accessories'),
        ('Food', 'Edible items and beverages');
    """)

    # Thêm dữ liệu vào bảng Product
    mycursor.execute("""
        INSERT INTO product (name, description, price, seller_id, category_id, created_at, updated_at, quantity)
        VALUES 
        ('Laptop', 'High performance laptop', 1000.00, 3, 1, NOW(), NOW(), 10),
        ('Smartphone', 'Latest model smartphone', 800.00, 3, 1, NOW(), NOW(), 15),
        ('Novel', 'Interesting book to read', 20.00, 2, 2, NOW(), NOW(), 50),
        ('T-shirt', 'Comfortable cotton T-shirt', 15.00, 4, 3, NOW(), NOW(), 100);
    """)

    # Thêm dữ liệu vào bảng Ad
    mycursor.execute("""
        INSERT INTO ad (title, description, discount_percentage, start_date, end_date, created_at, updated_at)
        VALUES 
        ('Summer Sale', 'Huge discount on electronics', 30.00, '2024-06-01', '2024-06-30', NOW(), NOW()),
        ('Book Fair', 'Up to 50% off on books', 50.00, '2024-07-01', '2024-07-15', NOW(), NOW()),
        ('Fashion Week', 'Exclusive clothing collection', 25.00, '2024-08-01', '2024-08-15', NOW(), NOW()),
        ('Food Bonanza', 'Special offers on food items', 10.00, '2024-09-01', '2024-09-30', NOW(), NOW());
    """)

    # Thêm dữ liệu vào bảng AdView
    mycursor.execute("""
        INSERT INTO ad_view (ad_id, user_id, viewed_at)
        VALUES 
        (1, 1, NOW()),
        (2, 2, NOW()),
        (3, 3, NOW()),
        (4, 4, NOW());
    """)

    # Thêm dữ liệu vào bảng Cart
    mycursor.execute("""
        INSERT INTO cart (user_id, created_at, updated_at)
        VALUES 
        (1, NOW(), NOW()),
        (2, NOW(), NOW()),
        (3, NOW(), NOW()),
        (4, NOW(), NOW());
    """)

    # Thêm dữ liệu vào bảng CartItem
    mycursor.execute("""
        INSERT INTO cart_item (cart_id, product_id, quantity, added_at)
        VALUES 
        (1, 1, 2, NOW()),
        (2, 3, 1, NOW()),
        (3, 2, 3, NOW()),
        (4, 4, 2, NOW());
    """)

    # Thêm dữ liệu vào bảng Comment
    mycursor.execute("""
        INSERT INTO comment (user_id, product_id, comment, rating, created_at)
        VALUES 
        (1, 1, 'Great laptop!', 5, NOW()),
        (2, 3, 'Loved this book!', 4, NOW()),
        (3, 2, 'Good phone!', 5, NOW()),
        (4, 4, 'Comfortable T-shirt', 4, NOW());
    """)

    # Thêm dữ liệu vào bảng Notification
    mycursor.execute("""
        INSERT INTO notification (user_id, message, is_read, created_at)
        VALUES 
        (1, 'Your order has been shipped!', 0, NOW()),
        (2, 'Discount offer on books available!', 1, NOW()),
        (3, 'New products available in your store!', 0, NOW()),
        (4, 'Your payment was successful!', 1, NOW());
    """)

    # Thêm dữ liệu vào bảng Order
    mycursor.execute("""
        INSERT INTO `order` (user_id, total, status, created_at, updated_at)
        VALUES 
        (1, 1200.00, 'Processing', NOW(), NOW()),
        (2, 35.00, 'Shipped', NOW(), NOW()),
        (3, 850.00, 'Delivered', NOW(), NOW()),
        (4, 1000.00, 'Cancelled', NOW(), NOW());
    """)

    # Thêm dữ liệu vào bảng OrderItem
    mycursor.execute("""
        INSERT INTO order_item (order_id, product_id, quantity, price)
        VALUES 
        (1, 1, 2, 1000.00),
        (2, 3, 1, 20.00),
        (3, 2, 3, 800.00),
        (4, 4, 2, 15.00);
    """)

    # Thêm dữ liệu vào bảng Payment
    mycursor.execute("""
        INSERT INTO payment (user_id, order_id, amount, status, payment_method, transaction_id, created_at, updated_at)
        VALUES 
        (1, 1, 1200.00, 'COMPLETED', 'Credit Card', 'TRANS123', NOW(), NOW()),
        (2, 2, 35.00, 'COMPLETED', 'E-Wallet', 'TRANS456', NOW(), NOW()),
        (3, 3, 850.00, 'COMPLETED', 'Bank Transfer', 'TRANS789', NOW(), NOW()),
        (4, 4, 1000.00, 'REFUNDED', 'Credit Card', 'TRANS101', NOW(), NOW());
    """)

    # Thêm dữ liệu vào bảng ProductAd
    mycursor.execute("""
        INSERT INTO product_ad (product_id, ad_id)
        VALUES 
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4);
    """)

    # Thêm dữ liệu vào bảng ProductImage
    mycursor.execute("""
        INSERT INTO product_image (product_id, file, uploaded_at)
        VALUES 
        (1, 'https://example.com/laptop.jpg', NOW()),
        (2, 'https://example.com/smartphone.jpg', NOW()),
        (3, 'https://example.com/book.jpg', NOW()),
        (4, 'https://example.com/tshirt.jpg', NOW());
    """)

    # Thêm dữ liệu vào bảng ProductVideo
    mycursor.execute("""
        INSERT INTO product_video (product_id, file, uploaded_at)
        VALUES 
        (1, 'https://example.com/laptop_video.mp4', NOW()),
        (2, 'https://example.com/smartphone_video.mp4', NOW()),
        (3, 'https://example.com/book_video.mp4', NOW()),
        (4, 'https://example.com/tshirt_video.mp4', NOW());
    """)

    # Thêm dữ liệu vào bảng ProductRecommendation
    mycursor.execute("""
        INSERT INTO product_recommendation (user_id, session_id, product_id, category_id, recommended_at, description)
        VALUES 
        (1, 'session123', 1, 1, NOW(), 'Recommended electronics for you'),
        (2, 'session456', 3, 2, NOW(), 'Top books for reading'),
        (3, 'session789', 2, 1, NOW(), 'Latest smartphones'),
        (4, 'session101', 4, 3, NOW(), 'Recommended clothing');
    """)

    # Xác nhận tất cả thay đổi vào cơ sở dữ liệu
    db.commit()
    print("Data inserted successfully.")

except mysql.connector.Error as err:
    print(f"Error: {err}")
    db.rollback()  # Hoàn tác nếu có lỗi

finally:
    # Đóng kết nối
    mycursor.close()
    db.close()