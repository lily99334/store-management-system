from flask import Blueprint, jsonify, request
from db_config import get_db_connection # 連線資料庫的設定檔

sales_bp = Blueprint('sales_bp', __name__)

@sales_bp.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    
    # ⚠️ 重要：這裡要加 dictionary=True
    # 這樣抓出來的資料才會是 {'id': 1, 'name': '可樂'...} 這種 JSON 格式
    # 如果沒加，會變成 (1, '可樂'...) 這種 Tuple，前端會看不懂
    cursor = conn.cursor(dictionary=True) 
    
    try:
        # 抓取所有商品資料 (包含 image_url)
        cursor.execute("SELECT * FROM Products")
        products = cursor.fetchall()
        
        return jsonify(products), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
        
    finally:
        cursor.close()
        conn.close()

# 定義網址路徑 (API URL)
# 前端 axios.post('http://.../api/sales/checkout') 就是打到這裡
# methods=['POST'] 代表只接受 "傳送資料" 的請求，不接受一般的網頁瀏覽 (GET)
@sales_bp.route('/api/sales/checkout', methods=['POST'])
def checkout():
    data = request.json
    print("收到結帳請求:", data) # Debug: 印出收到的資料，檢查前端有沒有傳錯
    
    conn = get_db_connection() # 呼叫連線函式
    cursor = conn.cursor() # 建立游標物件，用來執行 SQL 指令

    try:
        # ========================================
        # 步驟 1: 建立訂單主檔 (Sales_Orders)
        # ========================================

        # 開始資料庫交易 (Transaction)
        # 只要中間有任何一步失敗，就會全部取消，不會只存一半
        conn.start_transaction()

        # SQL 指令：新增一筆訂單
        # %s 是 "佔位符"，這是為了防止駭客攻擊 (SQL Injection)，不要直接用字串串接
        # NOW()：自動填入當下時間
        sql_order = """
            INSERT INTO Sales_Orders (customer_tag, total_amount, sale_time) 
            VALUES (%s, %s, NOW())
        """
        cursor.execute(sql_order, (data['customer_tag'], data['total_amount']))

        order_id = cursor.lastrowid  # <-- 拿到剛建好的訂單編號
        print(f"訂單建立成功，ID: {order_id}")

        # ========================================
        # 步驟 2: 跑迴圈處理每一項商品
        # ========================================

        # 寫入訂單明細 (Sales_Items)
        sql_item = """
            INSERT INTO Sales_Items (order_id, product_id, quantity, subtotal) 
            VALUES (%s, %s, %s, %s)
        """
        # 扣除庫存 (Products)
        # 邏輯：更新 (UPDATE) Products 表格
        # 設定 新庫存 = 舊庫存 - 購買數量
        # 條件是 WHERE id = 商品ID
        sql_update_stock = """
            UPDATE Products 
            SET current_stock = current_stock - %s 
            WHERE id = %s
        """

        for item in data['items']:
            # 1. 寫入明細
            val_item = (order_id, item['product_id'], item['quantity'], item['subtotal'])
            cursor.execute(sql_item, val_item)

            # 2. 扣除庫存
            val_stock = (item['quantity'], item['product_id'])
            cursor.execute(sql_update_stock, val_stock)

            print(f"商品ID {item['product_id']} 庫存已更新，扣除數量: {item['quantity']}")
        # ========================================
        # 步驟 3: 沒問題就提交 (Commit)
        # ========================================

        conn.commit() # 確認交易
        print("交易成功，庫存已更新")
        return jsonify({"status": "success", "message": "結帳完成", "order_id": order_id}), 200

    except Exception as e:
        # ========================================
        # 發生錯誤：全部撤銷 (Rollback)
        # ========================================

        # 因為發生錯誤，所以要把剛剛步驟 1、2 做過的所有暫存修改全部撤銷
        # 避免發生 "訂單建立了，但明細沒寫入" 這種資料不一致的慘劇
        conn.rollback()
        print("❌ 發生錯誤，交易取消！")
        print("錯誤原因:", e) 

        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        print("關閉資料庫連線")

        # 關閉游標
        cursor.close()
        # 釋放資源，資料庫連線數滿了會出問題
        conn.close()