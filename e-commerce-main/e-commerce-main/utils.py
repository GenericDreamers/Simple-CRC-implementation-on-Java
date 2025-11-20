# utils.py
import functools
from flask import session, redirect, url_for, flash


# Decorator yêu cầu đăng nhập
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để tiếp tục!', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Lấy giỏ hàng từ session
def get_cart():
    if 'cart' not in session:
        session['cart'] = {}  # {product_id (str): quantity}
    return session['cart']


# Thêm sản phẩm vào giỏ
def add_to_cart(product_id, quantity=1):
    cart = get_cart()
    product_id = str(product_id)  # luôn lưu dưới dạng chuỗi
    cart[product_id] = cart.get(product_id, 0) + quantity
    session['cart'] = cart
    session.modified = True


# Xóa sản phẩm khỏi giỏ
def remove_from_cart(product_id):
    cart = get_cart()
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]
        session['cart'] = cart
        session.modified = True


# Tính tổng tiền giỏ hàng (dùng trong cart và booking)
def get_cart_total(conn):
    cart = get_cart()
    if not cart:
        return 0.0

    # Lấy danh sách ID và chuyển thành chuỗi để query
    product_ids = [int(pid) for pid in cart.keys()]
    placeholders = ','.join(['?'] * len(product_ids))

    cursor = conn.cursor()
    cursor.execute(f"SELECT product_id, price_usd FROM products WHERE product_id IN ({placeholders})", product_ids)
    rows = cursor.fetchall()

    total = 0.0
    for row in rows:
        pid, price = row
        qty = cart.get(str(pid), 0)
        total += price * qty
    return round(total, 2)


# Xóa toàn bộ giỏ hàng (dùng sau khi đặt hàng thành công)
def clear_cart():
    if 'cart' in session:
        session.pop('cart')
        session.modified = True