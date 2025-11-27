import os
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from db_config import get_db_connection

# from routes.product_api import product_bp
from routes.sales_api import sales_bp
# from routes.inventory_api import inventory_bp
# from routes.report_api import report_bp

# ==========================================
# 設定 HTML 範本路徑 (Template Folder)
# ==========================================

# 取得目前 app.py 所在的資料夾路徑 (就是 backend)
base_dir = os.path.abspath(os.path.dirname(__file__))

# frontend 資料夾的路徑
template_dir = os.path.join(base_dir, '..', 'frontend')

# 告訴 Flask 去那裡找 HTML
# static_folder='static' 代表圖片還是放在 backend/static
app = Flask(__name__, template_folder=template_dir, static_folder='static')

# 開啟 CORS：允許所有來源連線
CORS(app, resources={r"/*": {"origins": "*"}}) 

# ------------------------------------------------------
# 註冊藍圖 (將模組掛載到主程式)
# 這樣網址就會變成 /api/products/..., /api/sales/...
# ------------------------------------------------------
# app.register_blueprint(product_bp)
app.register_blueprint(sales_bp)
# app.register_blueprint(inventory_bp)
# app.register_blueprint(report_bp)

# 首頁 (入口儀表板)
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# POS 結帳頁面
@app.route('/pos')
def pos_page():
    return render_template('pos.html')



# --- 測試資料庫路由 (確認能不能連到 MySQL) ---
@app.route('/api/test-db', methods=['GET'])
def test_db():
    conn = get_db_connection()
    if conn and conn.is_connected():
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();") # 問 MySQL 現在是用哪個庫
        record = cursor.fetchone()
        conn.close()
        return jsonify({
            "status": "success",
            "message": f"成功連線到資料庫：{record[0]}"
        })
    else:
        return jsonify({
            "status": "error",
            "message": "無法連線到資料庫，請檢查 db_config.py 或 MySQL 是否有開"
        }), 500

# --- 未來區域：等組員寫好模組 API 後，要在這裡「註冊」進來 ---
# 例如：
# from routes.product_api import product_bp
# app.register_blueprint(product_bp)


if __name__ == '__main__':
# ------------------------------------------------------
    # 修改啟動設定
    # host='0.0.0.0' -> 讓同一 WiFi 下的其他裝置可以連進來
    # port=5000      -> 指定 Port 號
    # ------------------------------------------------------
    print("🚀 伺服器啟動中...")
    print("請使用 cmd 輸入 'ipconfig' 查詢你的 IPv4 位址")
    print("其他裝置請連線至：http://你的IPv4位址:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)