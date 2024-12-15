import mysql.connector
db = mysql.connector.connect(user='root', password='nhc171103', host='localhost', database='capstone1')
# RUN
mycursor = db.cursor()

try:
    # # Thêm dữ liệu vào bảng Category
    # mycursor.execute("""
    # INSERT INTO category (category_name, description) 
    # VALUES 
    #     ('Nhà Sách Tiki', NULL),
    #     ('Nhà Cửa - Đời Sống', NULL),
    #     ('Điện Thoại - Máy Tính Bảng', NULL),
    #     ('Đồ Chơi - Mẹ & Bé', NULL),
    #     ('Thiết Bị Số - Phụ Kiện Số', NULL),
    #     ('Điện Gia Dụng', NULL),
    #     ('Làm Đẹp - Sức Khỏe', NULL),
    #     ('Ô Tô - Xe Máy - Xe Đạp', NULL),
    #     ('Thời trang nữ', NULL),
    #     ('Thể Thao - Dã Ngoại', NULL),
    #     ('Thời trang nam', NULL),
    #     ('Laptop - Máy Vi Tính - Linh kiện', NULL),
    #     ('Giày - Dép nam', NULL),
    #     ('Điện Tử - Điện Lạnh', NULL),
    #     ('Giày - Dép nữ', NULL),
    #     ('Máy Ảnh - Máy Quay Phim', NULL),
    #     ('Phụ kiện thời trang', NULL),
    #     ('Đồng hồ và Trang sức', NULL),
    #     ('Balo và Vali', NULL),
    #     ('Túi thời trang nữ', NULL),
    #     ('Túi thời trang nam', NULL);
    # """)
    
    # mycursor.execute("""INSERT INTO subcategory (category_id, subcategory_name, description) 
    # VALUES 
    #     -- 2. Nhà Sách Tiki
    #     (2, 'English Books', 'Books and resources in English.'),
    #     (2, 'Sách tiếng Việt', 'Sách, tài liệu học tập tiếng Việt.'),
    #     (2, 'Văn phòng phẩm', 'Các loại dụng cụ học tập và làm việc.'),

    #     -- 3. Nhà Cửa - Đời Sống
    #     (3, 'Dụng cụ nhà bếp', 'Dụng cụ hỗ trợ nấu ăn và làm bếp.'),
    #     (3, 'Đồ dùng phòng ăn', 'Đồ dùng phục vụ cho ăn uống.'),
    #     (3, 'Nội thất', 'Đồ nội thất trang trí trong nhà.'),
    #     (3, 'Đồ dùng phòng ngủ', 'Các sản phẩm dành cho phòng ngủ.'),

    #     -- 4. Điện Thoại - Máy Tính Bảng
    #     (4, 'Điện thoại Smartphone', 'Điện thoại thông minh từ nhiều thương hiệu.'),
    #     (4, 'Máy tính bảng', 'Thiết bị máy tính bảng hiện đại.'),
    #     (4, 'Điện thoại phổ thông', 'Các loại điện thoại cơ bản.'),

    #     -- 5. Đồ Chơi - Mẹ & Bé
    #     (5, 'Tã, Bỉm', 'Các sản phẩm dành riêng cho bé.'),
    #     (5, 'Dinh dưỡng cho bé', 'Các sản phẩm hỗ trợ dinh dưỡng cho trẻ nhỏ.'),
    #     (5, 'Đồ chơi', 'Đồ chơi an toàn cho bé mọi lứa tuổi.'),

    #     -- 6. Thiết Bị Số - Phụ Kiện Số
    #     (6, 'Thiết Bị Âm Thanh và Phụ Kiện', 'Tai nghe, loa và phụ kiện âm thanh.'),
    #     (6, 'Thiết Bị Chơi Game và Phụ Kiện', 'Phụ kiện chơi game chất lượng.'),
    #     (6, 'Thiết Bị Đeo Thông Minh và Phụ Kiện', 'Thiết bị đeo công nghệ hiện đại.'),
    #     (6, 'Phụ kiện máy tính và Laptop', 'Các loại phụ kiện cho máy tính và laptop.'),

    #     -- 7. Điện Gia Dụng
    #     (7, 'Đồ dùng nhà bếp', 'Sản phẩm thiết yếu cho căn bếp hiện đại.'),
    #     (7, 'Thiết bị gia đình', 'Dụng cụ và thiết bị hỗ trợ trong gia đình.'),

    #     -- 8. Làm Đẹp - Sức Khỏe
    #     (8, 'Chăm sóc da mặt', 'Các sản phẩm dưỡng và chăm sóc da.'),
    #     (8, 'Trang điểm', 'Mỹ phẩm trang điểm đa dạng.'),
    #     (8, 'Nước hoa', 'Nước hoa từ các thương hiệu nổi tiếng.'),

    #     -- 9. Ô Tô - Xe Máy - Xe Đạp
    #     (9, 'Xe máy', 'Xe máy các dòng và thương hiệu khác nhau.'),
    #     (9, 'Xe điện', 'Xe điện thông minh tiết kiệm nhiên liệu.'),
    #     (9, 'Xe đạp', 'Xe đạp cho thể thao và di chuyển.'),
    #     (9, 'Ô tô', 'Các loại xe hơi hiện đại.'),

    #     -- 10. Thời trang nữ
    #     (10, 'Đầm nữ', 'Đầm nữ thời trang và hiện đại.'),
    #     (10, 'Chân váy', 'Chân váy đa phong cách cho nữ.'),
    #     (10, 'Quần nữ', 'Quần nữ từ các thương hiệu thời trang.'),
    #     (10, 'Áo vest - Áo khoác nữ', 'Áo khoác và vest nữ thanh lịch.'),
    #     (10, 'Áo sơ mi nữ', 'Sơ mi nữ dành cho công sở.'),

    #     -- 11. Thể Thao - Dã Ngoại
    #     (11, 'Các môn thể thao chơi vợt', 'Dụng cụ chơi tennis, cầu lông, bóng bàn.'),
    #     (11, 'Thể thao dưới nước', 'Các dụng cụ bơi lội và thể thao dưới nước.'),
    #     (11, 'Đồ dùng dã ngoại & Leo núi', 'Dụng cụ hỗ trợ dã ngoại và leo núi.'),
    #     (11, 'Chạy bộ và đi bộ', 'Trang phục và phụ kiện cho chạy bộ, đi bộ.'),

    #     -- 12. Thời trang nam
    #     (12, 'Áo thun nam', 'Áo thun đa dạng phong cách dành cho nam.'),
    #     (12, 'Áo sơ mi nam', 'Sơ mi nam thanh lịch và chuyên nghiệp.'),
    #     (12, 'Áo vest - Áo khoác nam', 'Áo khoác và vest nam.'),
    #     (12, 'Áo nỉ - Áo len nam', 'Áo nỉ và len giữ ấm dành cho nam.'),

    #     -- 13. Laptop - Máy Vi Tính - Linh kiện
    #     (13, 'Laptop', 'Laptop các thương hiệu.'),
    #     (13, 'Thiết Bị Văn Phòng - Thiết Bị Ngoại Vi', 'Dụng cụ hỗ trợ công việc văn phòng.'),
    #     (13, 'Thiết Bị Lưu Trữ', 'Ổ cứng, SSD, và thiết bị lưu trữ khác.'),
    #     (13, 'Thiết Bị Mạng', 'Modem, router và thiết bị mạng.'),
    #     (13, 'PC - Máy Tính Bộ', 'Máy tính bàn phục vụ học tập, công việc.'),
    #     (13, 'Linh Kiện Máy Tính - Phụ Kiện Máy Tính', 'Linh kiện, phụ kiện máy tính đa dạng.'),

    #     -- 14. Giày - Dép nam
    #     (14, 'Giày thể thao nam', 'Giày thể thao dành cho nam.'),
    #     (14, 'Giày tây nam', 'Giày da sang trọng cho nam.'),
    #     (14, 'Giày sandals nam', 'Sandals nam đa dụng.'),
    #     (14, 'Dép nam', 'Dép thoải mái và tiện dụng cho nam.'),

    #     -- 15. Điện Tử - Điện Lạnh
    #     (15, 'Tivi', 'Tivi từ các thương hiệu nổi tiếng.'),
    #     (15, 'Máy giặt', 'Máy giặt đa năng và tiện lợi.'),
    #     (15, 'Máy rửa chén', 'Máy rửa bát tự động.'),
    #     (15, 'Máy lạnh - Máy điều hòa', 'Điều hòa cho không khí mát lạnh.'),
    #     (15, 'Máy nước nóng', 'Thiết bị cung cấp nước nóng.'),
    #     (15, 'Tủ lạnh', 'Tủ lạnh hiện đại và tiết kiệm điện.'),

    #     -- 16. Giày - Dép nữ
    #     (16, 'Giày cao gót', 'Giày cao gót dành cho nữ.'),
    #     (16, 'Giày sandals nữ', 'Sandals nữ nhẹ nhàng.'),
    #     (16, 'Dép - Guốc nữ', 'Dép guốc sang trọng và tiện lợi.'),

    #     -- 17. Máy Ảnh - Máy Quay Phim
    #     (17, 'Máy Ảnh', 'Máy ảnh chụp hình chuyên nghiệp.'),
    #     (17, 'Balo - Túi Đựng - Bao Da', 'Balo và túi đựng phụ kiện.'),
    #     (17, 'Thiết Bị Quay Phim', 'Phụ kiện hỗ trợ quay phim.'),
    #     (17, 'Camera Hành Trình - Action Camera và Phụ Kiện', 'Camera hành trình tiện dụng.'),

    #     -- 18. Phụ kiện thời trang
    #     (18, 'Đồng hồ nam', 'Đồng hồ cao cấp cho nam.'),
    #     (18, 'Đồng hồ nữ', 'Đồng hồ thời trang dành cho nữ.'),
    #     (18, 'Trang sức', 'Trang sức lấp lánh dành cho mọi phong cách.'),

    #     -- 19. Balo và Vali
    #     (20, 'Balo', 'Balo thời trang và tiện ích.'),
    #     (20, 'Balo, cặp, túi chống sốc laptop', 'Cặp và túi laptop chống sốc.'),
    #     (20, 'Vali, phụ kiện vali', 'Vali và các phụ kiện liên quan.');

    # """)
    
    # mycursor.execute(""" 
    # INSERT INTO user (username, password, email, full_name, address, phone_number, role_id, reset_token, reset_token_expiry, created_at, updated_at) 
    # VALUES 
    # ('nha_sach_tiki', '123456', 'nhasach_tiki@gmail.com', 'Smart House Store', NULL, '0956b91926', 2, NULL, NULL, NOW(), NOW()),
    # ('dao_tao_tin_hoc', '654321', 'daotao_tinhoc@gmail.com', 'Đào Tạo Tin Học', NULL, '07f0d9b076', 2, NULL, NULL, NOW(), NOW()),
    # ('huyhoang_camera', 'abcdef', 'huyhoang_camera@gmail.com', 'HuyHoang Camera', NULL, '089a95a7e2', 2, NULL, NULL, NOW(), NOW()),
    # ('kim_ngoc_thuy', '789012', 'kimngocthuy@gmail.com', 'Kim Ngọc Thủy', NULL, '08b5dd5f4c', 2, NULL, NULL, NOW(), NOW()),
    # ('cua_hang_linh_linh', '345678', 'cualinhlinh@gmail.com', 'CỬA HÀNG LINH LINH', NULL, '053306cc72', 2, NULL, NULL, NOW(), NOW()),
    # ('thang_camera', '567890', 'thang_camera@gmail.com', 'Thăng Camera', NULL, '06570587b9', 2, NULL, NULL, NOW(), NOW()),
    # ('gu_bag_official', '234567', 'gubag_official@gmail.com', 'Gu Bag Official Store', NULL, '082343b11e', 2, NULL, NULL, NOW(), NOW()),
    # ('hxsj_official', '890123', 'hxsj_official@gmail.com', 'HXSJ Official Store', NULL, '03e8eed83f', 2, NULL, NULL, NOW(), NOW());
    # """)

    mycursor.execute("""
    INSERT INTO shop (shop_name, user_id) 
    VALUES 
    ('Smart House Store', 1),
    ('Đào Tạo Tin Học', 2),
    ('HuyHoang Camera', 3),
    ('Kim Ngọc Thủy', 4),
    ('CỬA HÀNG LINH LINH', 5),
    ('Thăng Camera', 6),
    ('Gu Bag Official Store', 7),
    ('HXSJ Official Store', 8);
    """)

    mycursor.execute("""
    #     INSERT INTO product (name, description, price, quantity, subcategory_id, detail_product, shop_id, created_at, updated_at)
    #     VALUES 
    (),
    """)
    # # Thêm dữ liệu vào bảng role
    # mycursor.execute("INSERT INTO role (role_name) VALUES ('Admin'), ('User'), ('Seller');")
    
    # # Thêm dữ liệu vào bảng User
    # mycursor.execute("""
    #     INSERT INTO user (username, password, email, full_name, address, phone_number, role_id, reset_token, reset_token_expiry, created_at, updated_at)
    #     VALUES 
    #     ('admin_user', 'adminpassword', 'admin@example.com', 'Admin User', 'Admin Street', '1234567890', 1, NULL, NULL, NOW(), NOW()),
    #     ('normal_user', 'userpassword', 'user@example.com', 'Normal User', 'User Road', '2345678901', 2, NULL, NULL, NOW(), NOW()),
    #     ('seller1_user', 'sellerpassword1', 'seller1@example.com', 'Seller One', 'Seller St 1', '3456789012', 3, NULL, NULL, NOW(), NOW()),
    #     ('seller2_user', 'sellerpassword2', 'seller2@example.com', 'Seller Two', 'Seller St 2', '4567890123', 3, NULL, NULL, NOW(), NOW());
    # """)

    

    # # Thêm dữ liệu vào bảng Product
    # mycursor.execute("""
    #     INSERT INTO product (name, description, price, seller_id, category_id, created_at, updated_at, quantity)
    #     VALUES 
    #     ('Laptop', 'High performance laptop', 1000.00, 3, 1, NOW(), NOW(), 10),
    #     ('Smartphone', 'Latest model smartphone', 800.00, 3, 1, NOW(), NOW(), 15),
    #     ('Novel', 'Interesting book to read', 20.00, 2, 2, NOW(), NOW(), 50),
    #     ('T-shirt', 'Comfortable cotton T-shirt', 15.00, 4, 3, NOW(), NOW(), 100);
    # """)

    # # Thêm dữ liệu vào bảng Ad
    # mycursor.execute("""
    #     INSERT INTO ad (title, description, discount_percentage, start_date, end_date, created_at, updated_at)
    #     VALUES 
    #     ('Summer Sale', 'Huge discount on electronics', 30.00, '2024-06-01', '2024-06-30', NOW(), NOW()),
    #     ('Book Fair', 'Up to 50% off on books', 50.00, '2024-07-01', '2024-07-15', NOW(), NOW()),
    #     ('Fashion Week', 'Exclusive clothing collection', 25.00, '2024-08-01', '2024-08-15', NOW(), NOW()),
    #     ('Food Bonanza', 'Special offers on food items', 10.00, '2024-09-01', '2024-09-30', NOW(), NOW());
    # """)

    # # Thêm dữ liệu vào bảng AdView
    # mycursor.execute("""
    #     INSERT INTO ad_view (ad_id, user_id, viewed_at)
    #     VALUES 
    #     (1, 1, NOW()),
    #     (2, 2, NOW()),
    #     (3, 3, NOW()),
    #     (4, 4, NOW());
    # """)

    # # Thêm dữ liệu vào bảng Cart
    # mycursor.execute("""
    #     INSERT INTO cart (user_id, created_at, updated_at)
    #     VALUES 
    #     (1, NOW(), NOW()),
    #     (2, NOW(), NOW()),
    #     (3, NOW(), NOW()),
    #     (4, NOW(), NOW());
    # """)

    # # Thêm dữ liệu vào bảng CartItem
    # mycursor.execute("""
    #     INSERT INTO cart_item (cart_id, product_id, quantity, added_at)
    #     VALUES 
    #     (1, 1, 2, NOW()),
    #     (2, 3, 1, NOW()),
    #     (3, 2, 3, NOW()),
    #     (4, 4, 2, NOW());
    # """)

    # # Thêm dữ liệu vào bảng Comment
    # mycursor.execute("""
    #     INSERT INTO comment (user_id, product_id, comment, rating, created_at)
    #     VALUES 
    #     (1, 1, 'Great laptop!', 5, NOW()),
    #     (2, 3, 'Loved this book!', 4, NOW()),
    #     (3, 2, 'Good phone!', 5, NOW()),
    #     (4, 4, 'Comfortable T-shirt', 4, NOW());
    # """)

    # # Thêm dữ liệu vào bảng Notification
    # mycursor.execute("""
    #     INSERT INTO notification (user_id, message, is_read, created_at)
    #     VALUES 
    #     (1, 'Your order has been shipped!', 0, NOW()),
    #     (2, 'Discount offer on books available!', 1, NOW()),
    #     (3, 'New products available in your store!', 0, NOW()),
    #     (4, 'Your payment was successful!', 1, NOW());
    # """)

    # # Thêm dữ liệu vào bảng Order
    # mycursor.execute("""
    #     INSERT INTO `order` (user_id, total, status, created_at, updated_at)
    #     VALUES 
    #     (1, 1200.00, 'Processing', NOW(), NOW()),
    #     (2, 35.00, 'Shipped', NOW(), NOW()),
    #     (3, 850.00, 'Delivered', NOW(), NOW()),
    #     (4, 1000.00, 'Cancelled', NOW(), NOW());
    # """)

    # # Thêm dữ liệu vào bảng OrderItem
    # mycursor.execute("""
    #     INSERT INTO order_item (order_id, product_id, quantity, price)
    #     VALUES 
    #     (1, 1, 2, 1000.00),
    #     (2, 3, 1, 20.00),
    #     (3, 2, 3, 800.00),
    #     (4, 4, 2, 15.00);
    # """)

    # # Thêm dữ liệu vào bảng Payment
    # mycursor.execute("""
    #     INSERT INTO payment (user_id, order_id, amount, status, payment_method, transaction_id, created_at, updated_at)
    #     VALUES 
    #     (1, 1, 1200.00, 'COMPLETED', 'Credit Card', 'TRANS123', NOW(), NOW()),
    #     (2, 2, 35.00, 'COMPLETED', 'E-Wallet', 'TRANS456', NOW(), NOW()),
    #     (3, 3, 850.00, 'COMPLETED', 'Bank Transfer', 'TRANS789', NOW(), NOW()),
    #     (4, 4, 1000.00, 'REFUNDED', 'Credit Card', 'TRANS101', NOW(), NOW());
    # """)

    # # Thêm dữ liệu vào bảng ProductAd
    # mycursor.execute("""
    #     INSERT INTO product_ad (product_id, ad_id)
    #     VALUES 
    #     (1, 1),
    #     (2, 2),
    #     (3, 3),
    #     (4, 4);
    # """)

    # # Thêm dữ liệu vào bảng ProductImage
    # mycursor.execute("""
    #     INSERT INTO product_image (product_id, file, uploaded_at)
    #     VALUES 
    #     (1, 'https://example.com/laptop.jpg', NOW()),
    #     (2, 'https://example.com/smartphone.jpg', NOW()),
    #     (3, 'https://example.com/book.jpg', NOW()),
    #     (4, 'https://example.com/tshirt.jpg', NOW());
    # """)

    # # Thêm dữ liệu vào bảng ProductVideo
    # mycursor.execute("""
    #     INSERT INTO product_video (product_id, file, uploaded_at)
    #     VALUES 
    #     (1, 'https://example.com/laptop_video.mp4', NOW()),
    #     (2, 'https://example.com/smartphone_video.mp4', NOW()),
    #     (3, 'https://example.com/book_video.mp4', NOW()),
    #     (4, 'https://example.com/tshirt_video.mp4', NOW());
    # """)

    # # Thêm dữ liệu vào bảng ProductRecommendation
    # mycursor.execute("""
    #     INSERT INTO product_recommendation (user_id, session_id, product_id, category_id, recommended_at, description)
    #     VALUES 
    #     (1, 'session123', 1, 1, NOW(), 'Recommended electronics for you'),
    #     (2, 'session456', 3, 2, NOW(), 'Top books for reading'),
    #     (3, 'session789', 2, 1, NOW(), 'Latest smartphones'),
    #     (4, 'session101', 4, 3, NOW(), 'Recommended clothing');
    # """)

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