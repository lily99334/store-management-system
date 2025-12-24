from flask import Blueprint, jsonify, request
from db_config import get_db_connection

restock_bp = Blueprint('restock_bp', __name__)

# 1. 送出進貨單 (新增庫存)
@restock_bp.route('/api/restock', methods=['POST'])
def restock():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.start_transaction()
        # 建立主檔
        cursor.execute("INSERT INTO Restock_Orders (status) VALUES ('Completed')")
        restock_id = cursor.lastrowid
        
        # 建立明細並增加庫存
        for item in data['items']:
            cursor.execute("INSERT INTO Restock_Items (restock_id, product_id, quantity) VALUES (%s, %s, %s)",
                           (restock_id, item['product_id'], item['quantity']))
            cursor.execute("UPDATE Products SET current_stock = current_stock + %s WHERE id = %s",
                           (item['quantity'], item['product_id']))
            
        conn.commit()
        return jsonify({"message": "進貨成功"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        conn.close()

# 2. (新功能) 取得進貨紀錄
@restock_bp.route('/api/restock/orders', methods=['GET'])
def get_restock_history():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # 這裡用 GROUP_CONCAT 把買了什麼東西串成一個字串，方便前端顯示
    sql = """
        SELECT 
            ro.id, 
            ro.created_at, 
            GROUP_CONCAT(CONCAT(p.name, ' x', ri.quantity) SEPARATOR ', ') as details
        FROM Restock_Orders ro
        JOIN Restock_Items ri ON ro.id = ri.restock_id
        JOIN Products p ON ri.product_id = p.id
        GROUP BY ro.id
        ORDER BY ro.id DESC
    """
    cursor.execute(sql)
    orders = cursor.fetchall()
    conn.close()
    return jsonify(orders)

# 3. (新功能) 作廢進貨單 (扣回庫存)
@restock_bp.route('/api/restock/orders/<int:id>', methods=['DELETE'])
def delete_restock(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()
        
        # 先查這張單進了什麼，要把庫存扣回去
        cursor.execute("SELECT product_id, quantity FROM Restock_Items WHERE restock_id = %s", (id,))
        items = cursor.fetchall()
        
        if not items:
            return jsonify({"message": "找不到此進貨單"}), 404

        # 扣回庫存
        for item in items:
            cursor.execute("UPDATE Products SET current_stock = current_stock - %s WHERE id = %s",
                           (item['quantity'], item['product_id']))

        # 刪除紀錄 (因為有外鍵設定 CASCADE，刪主檔就會自動刪明細)
        cursor.execute("DELETE FROM Restock_Orders WHERE id = %s", (id,))
        
        conn.commit()
        return jsonify({"message": "已作廢進貨單，庫存已扣回"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        conn.close()