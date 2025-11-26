from flask import Blueprint, jsonify, request
from db_config import get_db_connection

sales_bp = Blueprint('sales_bp', __name__)

@sales_bp.route('/api/sales/checkout', methods=['POST'])
def checkout():
    data = request.json
    # 這裡會收到類似這樣的資料：
    # {
    #   "customer_tag": "學生",
    #   "total_amount": 100,
    #   "items": [ {"id": 1, "quantity": 2, "price": 25}, ... ]
    # }
    
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. 寫入 Sales_Orders (訂單主檔)
        # sql_order = "INSERT INTO Sales_Orders ..."
        # cursor.execute(sql_order, (...))
        # order_id = cursor.lastrowid  <-- 拿到剛建好的訂單編號

        # 2. 跑迴圈處理 Sales_Items (明細) 和 扣庫存
        # for item in data['items']:
            # 寫入 Sales_Items
            # 更新 Products 庫存

        conn.commit() # 確認交易
        return jsonify({"status": "success", "message": "結帳完成"})

    except Exception as e:
        conn.rollback() # 發生錯誤就回滾
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()