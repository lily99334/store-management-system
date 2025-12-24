import os
import time
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from db_config import get_db_connection

product_bp = Blueprint("product_bp", __name__)

# 設定允許的圖片格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 輔助函式：處理圖片存檔
def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        # 1. 產生安全且唯一的檔名 (加上時間戳記避免檔名重複)
        filename = secure_filename(file.filename)
        unique_filename = f"{int(time.time())}_{filename}"
        
        # 2. 確保儲存資料夾存在
        upload_folder = os.path.join(current_app.static_folder, 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # 3. 存檔
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        # 4. 回傳給前端用的網址路徑
        return f"/static/uploads/{unique_filename}"
    return None

# 1. 取得所有商品
@product_bp.route("/api/products", methods=["GET"])
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Products ORDER BY id DESC")
    products = cursor.fetchall()
    conn.close()
    return jsonify(products)

# 2. 新增商品 (支援圖片上傳)
@product_bp.route("/api/products", methods=["POST"])
def add_product():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 接收文字資料 (因為用了 FormData，所以要用 request.form 拿)
        name = request.form.get('name')
        category = request.form.get('category')
        price = request.form.get('price')
        current_stock = request.form.get('current_stock', 0) # 預設 0
        safe_stock = request.form.get('safe_stock', 10)      # 預設 10
        lead_time = request.form.get('lead_time', 2)         # 預設 2
        
        # 接收圖片檔案
        image_file = request.files.get('image_file')
        image_url = save_uploaded_file(image_file)
        
        # 如果沒上傳圖片，看有沒有填網址 (相容舊功能)
        if not image_url:
            image_url = request.form.get('image_url', '')

        sql = """INSERT INTO Products (name, category, price, current_stock, safe_stock, lead_time, image_url) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        val = (name, category, price, current_stock, safe_stock, lead_time, image_url)
        
        cursor.execute(sql, val)
        conn.commit()
        return jsonify({"message": "新增成功"}), 201
    except Exception as e:
        print(e)
        return jsonify({"message": str(e)}), 500
    finally:
        conn.close()

# 3. 修改商品 (支援圖片上傳)
@product_bp.route("/api/products/<int:id>", methods=["PUT"])
def update_product(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 接收文字資料
        name = request.form.get('name')
        category = request.form.get('category')
        price = request.form.get('price')
        safe_stock = request.form.get('safe_stock')
        lead_time = request.form.get('lead_time')
        
        # 處理圖片
        image_file = request.files.get('image_file')
        new_image_url = save_uploaded_file(image_file)
        
        # 如果有上傳新圖片，就用新的；不然就維持舊的 (原本的前端會把舊網址傳過來)
        if not new_image_url:
            new_image_url = request.form.get('image_url')

        sql = """UPDATE Products SET name=%s, category=%s, price=%s, 
                 safe_stock=%s, lead_time=%s, image_url=%s WHERE id=%s"""
        val = (name, category, price, safe_stock, lead_time, new_image_url, id)
        
        cursor.execute(sql, val)
        conn.commit()
        return jsonify({"message": "更新成功"})
    except Exception as e:
        print(e)
        return jsonify({"message": str(e)}), 500
    finally:
        conn.close()

# 4. 刪除商品 (不變)
@product_bp.route("/api/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT count(*) FROM Sales_Items WHERE product_id = %s", (id,))
        count = cursor.fetchone()[0]
        if count > 0:
            return jsonify({"status": "error", "message": "此商品已有銷售紀錄，無法刪除！(請改用下架功能)"}), 400

        cursor.execute("DELETE FROM Products WHERE id = %s", (id,))
        conn.commit()
        return jsonify({"status": "success", "message": "刪除成功"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()