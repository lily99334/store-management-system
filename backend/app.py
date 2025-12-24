import os
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from db_config import get_db_connection

# 匯入 Blueprints
from routes.sales_api import sales_bp
from routes.inventory_api import inventory_bp
from routes.product_api import product_bp
from routes.restock_api import restock_bp

base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, "..", "frontend")
app = Flask(__name__, template_folder=template_dir, static_folder="static")
CORS(app)

# 註冊 Blueprints
app.register_blueprint(sales_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(product_bp)
app.register_blueprint(restock_bp)


# === 頁面路由 ===
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/pos")
def pos_page():
    return render_template("pos.html")


@app.route("/products")  # <--- New! (新增商品管理頁面)
def product_page():
    return render_template("products.html")


@app.route("/inventory")
def inventory_page():
    return render_template("restock.html")


@app.route("/report")
def report_page():
    # ⚠️ 關鍵修改：這裡改成 inventory.html
    return render_template("inventory.html")


@app.route("/sales_history")  # <--- 新增這個
def sales_history_page():
    return render_template("sales_history.html")


if __name__ == "__main__":
    print("🚀 系統啟動中...")
    app.run(debug=True, host="0.0.0.0", port=5000)
