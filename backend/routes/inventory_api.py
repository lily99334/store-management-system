from flask import Blueprint, jsonify
from db_config import get_db_connection
from datetime import datetime
import math

inventory_bp = Blueprint("inventory_bp", __name__)


@inventory_bp.route("/api/inventory/alerts", methods=["GET"])
def get_inventory_alerts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1. SQL 查詢
    sql = """
        SELECT 
            p.*,
            COALESCE(SUM(CASE WHEN so.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN si.quantity ELSE 0 END), 0) as total_sold_7d,
            COALESCE(SUM(CASE WHEN so.created_at >= DATE_SUB(NOW(), INTERVAL 3 DAY) THEN si.quantity ELSE 0 END), 0) as total_sold_3d,
            MAX(so.created_at) as last_sold_date
        FROM Products p
        LEFT JOIN Sales_Items si ON p.id = si.product_id
        LEFT JOIN Sales_Orders so ON si.order_id = so.id
        GROUP BY p.id
    """

    cursor.execute(sql)
    products = cursor.fetchall()
    conn.close()

    red_lights = []
    yellow_lights = []

    for p in products:
        total_7d = float(p["total_sold_7d"])
        total_3d = float(p["total_sold_3d"])

        # ==========================================
        # 🧠 1. 智慧補貨 (庫存瘦身版)
        # ==========================================

        avg_7d = total_7d / 7.0
        avg_3d = total_3d / 3.0

        # 判斷爆紅
        if avg_3d > (avg_7d * 1.5) and avg_3d > 1:
            predict_daily_sales = avg_3d
            status_text = "🔥 爆紅"
        else:
            predict_daily_sales = avg_7d
            status_text = "平穩"

        # 🔥 修改：安全庫存「減半」 (0.5 天銷量)
        dynamic_safe_stock = avg_7d * 0.5 
        final_safe_stock = max(float(p["safe_stock"]), dynamic_safe_stock)

        # 計算建議水位
        target_level = (predict_daily_sales * p["lead_time"]) + final_safe_stock
        target_level = math.ceil(target_level)

        # 判斷紅燈
        if p["current_stock"] < target_level:
            shortage = target_level - p["current_stock"]
            p["suggestion"] = f"建議補貨 {int(shortage)} 個"
            p["status_text"] = status_text
            p["calc_info"] = f"預測日銷:{round(predict_daily_sales,1)} | 保底:{round(final_safe_stock,1)}"
            red_lights.append(p)

        # ==========================================
        # 🧠 冷門 vs 滯銷
        # ==========================================
        is_yellow = False
        msg = ""

        if p["current_stock"] > 0: # 有庫存才需要擔心滯銷
            
            # Case 1: 從來沒賣出去過 (或是資料庫沒紀錄)
            if p["last_sold_date"] is None:
                # 這裡很難判斷是剛進貨的新品，還是放很久的滯銷
                # 暫時標記為「無銷售紀錄」
                is_yellow = True
                msg = "⚠️ 無銷售紀錄 (可能為新品或嚴重滯銷)"
            
            else:
                # 計算距離上次賣出過了幾天
                days_diff = (datetime.now() - p["last_sold_date"]).days
                
                # Case 2: 滯銷 (Stagnant) - 超過 14 天完全沒動
                if days_diff > 14:
                    is_yellow = True
                    msg = f"🧊 已滯銷 {days_diff} 天 (完全沒動)"
                
                # Case 3: 冷門 (Slow Moving) - 有動，但 7 天賣不到 2 個
                elif total_7d < 2:
                    is_yellow = True
                    msg = f"🐢 冷門商品 (週銷量 {int(total_7d)})"

        if is_yellow:
            p["msg"] = msg
            yellow_lights.append(p)

    return jsonify({"red_lights": red_lights, "yellow_lights": yellow_lights})