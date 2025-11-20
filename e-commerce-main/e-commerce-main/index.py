# index.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from utils import login_required, add_to_cart, remove_from_cart, get_cart_total
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret-key'

# =============== DATABASE ===============
def get_db():
    conn = sqlite3.connect('Database.db')
    conn.row_factory = sqlite3.Row
    return conn

# =============== TRANG CHỦ ===============
@app.route('/')
def index():
    conn = get_db()
    featured = conn.execute("SELECT * FROM products WHERE product_id IN (1,3,10,20)").fetchall()
    conn.close()
    return render_template('index.html', featured=featured)

@app.route('/collections')
def collections():
    conn = get_db()
    products = conn.execute("SELECT * FROM products ORDER BY product_id").fetchall()
    conn.close()
    return render_template('collections.html', products=products)

# =============== GIỎ HÀNG ===============
@app.route('/cart')
@login_required
def cart():
    cart = session.get('cart', [])
    total_price = sum(item['price_usd'] * item.get('quantity', 1) for item in cart)
    return render_template('cart.html', cart=cart, total_price=total_price)


# CÓ THỂ THAY ĐỔI TỶ LỆ THUÊ TẠI ĐÂY – CHỈ 1 CHỖ DUYỆT!
RENTAL_PERCENT_OF_BUY_PRICE = 0.05  # 5% giá mua → muốn đổi thành 10% thì sửa thành 0.10

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart(action_text=None):
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập!', 'warning')
        return redirect(url_for('login'))

    product_id = request.form.get('product_id')
    action = request.form.get('action', 'buy')  # buy hoặc rent
    rental_days = int(request.form.get('rental_days', 7))

    if not product_id:
        flash('Lỗi sản phẩm!', 'danger')
        return redirect(url_for('collections'))

    conn = get_db()
    product = conn.execute('SELECT * FROM products WHERE product_id = ?', (product_id,)).fetchone()
    conn.close()
    if not product:
        flash('Sản phẩm không tồn tại!', 'danger')
        return redirect(url_for('collections'))

    cart = session.get('cart', [])
    found = False

    for item in cart:
        if item['product_id'] == int(product_id) and item.get('action') == action:
            item['quantity'] += 1
            found = True
            break

    if not found:
        if action == 'buy':
            price = float(product['price_usd'] or 0)
            cart.append({
                'product_id': product['product_id'],
                'name': product['name'],
                'image_url': product['image_url'] or 'images/placeholder.jpg',
                'price_usd': price,
                'quantity': 1,
                'action': 'buy',
                'note': 'Mua đứt',
            })
            action_text = "Mua đứt"
        else:  # rent
            buy_price = float(product['price_usd'] or 0)
            rent_per_day = buy_price * RENTAL_PERCENT_OF_BUY_PRICE
            total_rent = rent_per_day * rental_days
            cart.append({
                'product_id': product['product_id'],
                'name': product['name'],
                'image_url': product['image_url'] or 'images/placeholder.jpg',
                'price_usd': total_rent,
                'quantity': 1,
                'action': 'rent',
                'rental_days': rental_days,
                'note': f'Thuê {rental_days} ngày',
                'original_buy_price': float(product['price_usd'] or 0),  # lưu giá mua gốc để tính 5%
            })
            action_text = f"Thuê {rental_days} ngày"

        session['cart'] = cart
        flash(f'Đã thêm "{product["name"]}" ({action_text}) vào giỏ!', 'success')
    else:
        session['cart'] = cart
        flash(f'Đã tăng số lượng "{product["name"]}" ({action_text})!', 'success')

    return redirect(request.referrer or url_for('collections'))


@app.route('/update_rental_days', methods=['POST'])
def update_rental_days():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    product_id = request.form.get('product_id')
    rental_days = int(request.form.get('rental_days', 7))

    if rental_days < 1: rental_days = 1
    if rental_days > 90: rental_days = 90

    cart = session.get('cart', [])
    for item in cart:
        if item['product_id'] == int(product_id) and item.get('action') == 'rent':
            # Tính lại giá thuê theo số ngày mới
            buy_price = item.get('original_buy_price', item['price_usd'] * 20)  # fallback
            rent_per_day = buy_price * 0.05
            item['price_usd'] = rent_per_day * rental_days
            item['rental_days'] = rental_days
            break

    session['cart'] = cart
    flash(f'Đã cập nhật thuê {rental_days} ngày!', 'success')
    return redirect(url_for('cart'))

@app.route('/product/<int:pid>')
def product_detail(pid):
    conn = get_db()
    product = conn.execute('SELECT * FROM products WHERE product_id = ?', (pid,)).fetchone()
    conn.close()
    if not product:
        flash('Sản phẩm không tồn tại!', 'danger')
        return redirect(url_for('collections'))
    return render_template('product_detail.html', product=product)

# =============== ĐĂNG NHẬP / ĐĂNG XUẤT ===============
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Demo account: admin / 123456
        if username == 'admin' and password == '123456':
            session['user_id'] = 1
            session['username'] = username
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Sai tài khoản hoặc mật khẩu!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất', 'info')
    return redirect(url_for('index'))

@app.route('/partners')
def partners_map():
    return render_template('partners_map.html')

@app.route('/update_cart_item', methods=['POST'])
def update_cart_item():
    data = request.get_json()
    product_id = int(data['product_id'])
    action = data['action']              # 'buy' hoặc 'rent'
    quantity = max(1, int(data.get('quantity', 1)))
    rental_days = max(1, min(90, int(data.get('rental_days', 7))))

    cart = session.get('cart', [])
    total = 0.0

    for item in cart:
        if item['product_id'] == product_id:
            # Lưu giá mua gốc lần đầu (để tính thuê 5%)
            if 'original_price' not in item:
                item['original_price'] = float(item['price_usd'])

            item['action'] = action
            item['quantity'] = quantity

            if action == 'rent':
                rent_per_day = item['original_price'] * 0.05
                item['price_usd'] = rent_per_day * rental_days
                item['rental_days'] = rental_days
            else:
                item['price_usd'] = item['original_price']
                item.pop('rental_days', None)

        total += item['price_usd'] * item['quantity']

    session['cart'] = cart
    session.modified = True

    # Trả về dữ liệu chính xác cho JS
    for item in cart:
        if item['product_id'] == product_id:
            if action == 'rent':
                price_display = f"${item['original_price'] * 0.05:.2f}/ngày"
            else:
                price_display = f"${item['original_price']:.2f}"

            return jsonify({
                'item_total': item['price_usd'] * quantity,
                'price_display': price_display,
                'grand_total': total
            })

    return jsonify({'grand_total': total})

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    data = request.get_json()
    product_id = int(data['product_id'])
    action = data['action']

    cart = session.get('cart', [])
    cart = [i for i in cart if not (i['product_id'] == product_id and i.get('action') == action)]
    session['cart'] = cart

    total = sum(i['price_usd'] * i['quantity'] for i in cart)
    return jsonify({'total': total, 'cart_length': len(cart)})


# ──────────────────────────────
# 1. TRANG ĐẶT HÀNG – HIỂN THỊ FORM (GET)
# ──────────────────────────────
@app.route('/order')
def order():
    if not session.get('cart') or len(session['cart']) == 0:
        flash('Giỏ hàng trống! Vui lòng thêm sản phẩm trước.', 'warning')
        return redirect(url_for('collections'))

    cart = session['cart']
    total_price = sum(item['price_usd'] * item['quantity'] for item in cart)
    return render_template('order.html', cart=cart, total_price=total_price)


# ──────────────────────────────
# 2. XỬ LÝ ĐƠN HÀNG KHI KHÁCH BẤM XÁC NHẬN (POST)
# ──────────────────────────────
@app.route('/order_success', methods=['POST'])
def order_success_post():   # ← Tên hàm khác để không trùng!
    if not session.get('cart') or len(session['cart']) == 0:
        flash('Giỏ hàng trống!', 'danger')
        return redirect(url_for('cart'))

    full_name = request.form.get('full_name', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    note = request.form.get('note', '').strip()

    if not all([full_name, phone, address]):
        flash('Vui lòng điền đầy đủ thông tin!', 'danger')
        return redirect(url_for('order'))

    cart = session['cart']
    total_price = sum(item['price_usd'] * item['quantity'] for item in cart)

    # Tạo mã đơn tự động
    order_code = f"NOIR{datetime.now().strftime('%d%m%Y%H%M%S')}"

    session['current_order'] = {
        'order_code': order_code,
        'full_name': full_name,
        'phone': phone,
        'address': address,
        'note': note,
        'cart': cart.copy(),
        'total_price': total_price,
        'created_at': datetime.now().strftime('%d/%m/%Y %H:%M')
    }

    # XÓA GIỎ HÀNG
    session['cart'] = []
    session.modified = True

    flash(f'Đặt hàng thành công! Mã đơn: {order_code}', 'success')
    return redirect(url_for('payment'))  # ← Chuyển sang trang payment.html (bạn muốn)


# ──────────────────────────────
# 3. TRANG THANH TOÁN – HIỆN QR + MÃ ĐƠN (GET) – DÙNG TRANG payment.html
# ──────────────────────────────
@app.route('/payment')
def payment():
    if not session.get('current_order'):
        flash('Không tìm thấy đơn hàng!', 'danger')
        return redirect(url_for('cart'))

    order = session['current_order']
    return render_template('payment.html', order=order)


if __name__ == '__main__':
    app.run(debug=True)