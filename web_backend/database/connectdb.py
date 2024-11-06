import mysql.connector
db = mysql.connector.connect(user='root', password='nhc171103', host='localhost', database='web_backend')
# RUN
mycursor = db.cursor()

try:
    # Bảng role
    mycursor.execute("INSERT INTO role (role_name) VALUES ('Admin'), ('User'), ('Seller');")

    # Bảng user
    mycursor.execute("INSERT INTO user (username, password, email, full_name, role_id) VALUES ('john_doe', '123456', 'john@example.com', 'John Doe', 1), ('jane_doe', 'abcdef', 'jane@example.com', 'Jane Doe', 2);")

    # Bảng category
    mycursor.execute("INSERT INTO category (category_name, description) VALUES ('Electronics', 'Thiết bị điện tử'), ('Books', 'Các loại sách');")

    # Bảng product
    mycursor.execute("INSERT INTO product (name, description, price, seller_id, category_id) VALUES ('Laptop', 'Máy tính xách tay', 1500.00, 1, 1), ('Smartphone', 'Điện thoại thông minh', 800.00, 2, 1);")

    # Bảng order
    mycursor.execute("INSERT INTO `order` (user_id, total, status) VALUES (1, 2300.00, 'completed'), (2, 800.00, 'pending');")

    # Bảng order_item
    mycursor.execute("INSERT INTO order_item (order_id, product_id, quantity, price) VALUES (1, 1, 1, 1500.00), (2, 2, 1, 800.00);")

    # Bảng cart
    mycursor.execute("INSERT INTO cart (user_id) VALUES (1), (2);")

    # Bảng cart_item
    mycursor.execute("INSERT INTO cart_item (cart_id, product_id, quantity) VALUES (1, 1, 1), (2, 2, 2);")

    # Bảng ad
    mycursor.execute("INSERT INTO ad (title, description, discount_percentage, start_date, end_date) VALUES ('Giảm giá Tết', 'Khuyến mãi lớn mừng Tết', 10.00, '2024-01-01', '2024-02-01'), ('Giảm giá Hè', 'Giảm giá mùa hè', 15.00, '2024-06-01', '2024-07-01');")

    # Bảng product_ad
    mycursor.execute("INSERT INTO product_ad (product_id, ad_id) VALUES (1, 1), (2, 2);")

    # Bảng ad_view
    mycursor.execute("INSERT INTO ad_view (ad_id, user_id) VALUES (1, 1), (2, 2);")

    # Bảng notification
    mycursor.execute("INSERT INTO notification (user_id, message, is_read) VALUES (1, 'Bạn có khuyến mãi mới', FALSE), (2, 'Đơn hàng của bạn đã hoàn thành', TRUE);")

    # Bảng comment
    mycursor.execute("INSERT INTO comment (user_id, product_id, comment, rating) VALUES (1, 1, 'Sản phẩm tốt', 5), (2, 2, 'Chất lượng tốt', 4);")

    # Bảng user_browsing_behavior
    mycursor.execute("INSERT INTO user_browsing_behavior (user_id, product_id, activity_type, interaction_value) VALUES (1, 1, 'view_product', 10.0), (2, 2, 'add_to_cart', 5.0);")

    # Bảng product_recommendation
    mycursor.execute("INSERT INTO product_recommendation (user_id, session_id, product_id, category_id) VALUES (1, 'session_123', 1, 1), (2, 'session_456', 2, 2);")

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