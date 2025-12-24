from flask import Blueprint, jsonify
from db_config import get_db_connection
from datetime import datetime
import math

inventory_bp = Blueprint("inventory_bp", __name__)


@inventory_bp.route("/api/inventory/alerts", methods=["GET"])
def get_inventory_alerts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 🔥 關鍵修正：SQL 修改
    # 我們多 JOIN 了 'Sales_Orders' (so)，因為時間 (created_at) 是記在訂單上，而不是明細上
    sql = """
        SELECT 
            p.*,
            COALESCE(SUM(CASE WHEN so.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN si.quantity ELSE 0 END), 0) as total_sold_7d,
            COALESCE(SUM(CASE WHEN so.created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY) THEN si.quantity ELSE 0 END), 0) as sold_yesterday,
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
        # 轉換數字格式
        p["total_sold_7d"] = float(p["total_sold_7d"])
        p["sold_yesterday"] = float(p["sold_yesterday"])

        # ==========================================
        # 🧠 演算法邏輯
        # ==========================================

        # Step A: 計算基礎日均銷量
        avg_daily_sales = p["total_sold_7d"] / 7.0

        # Step B: 決定預測基準 (是否爆紅)
        is_trending = False
        if (
            avg_daily_sales > 0
            and p["sold_yesterday"] > (avg_daily_sales * 1.5)
            and p["sold_yesterday"] > 2
        ):
            predict_basis = float(p["sold_yesterday"])
            status_text = "🔥爆紅熱銷"
        else:
            predict_basis = avg_daily_sales
            status_text = "平穩銷售"

        # Step C: 計算應有庫存標準
        dynamic_threshold = predict_basis * (p["lead_time"] + 1)

        # 保底機制
        base_safe_stock = float(p["safe_stock"])
        GLOBAL_MIN_STOCK = 5.0

        if base_safe_stock < GLOBAL_MIN_STOCK:
            base_safe_stock = GLOBAL_MIN_STOCK

        # 取最大值
        final_threshold = max(dynamic_threshold, base_safe_stock)
        final_threshold = math.ceil(final_threshold)

        # ==========================================
        # 🚦 判斷紅燈
        # ==========================================
        if p["current_stock"] < final_threshold:
            shortage = final_threshold - p["current_stock"]

            p["suggestion"] = f"建議補貨 {int(shortage)} 個"
            p["status_text"] = status_text
            p["calc_info"] = f"標準:{final_threshold} (庫存:{p['current_stock']})"

            p["avg_sales"] = round(avg_daily_sales, 1)
            p["yesterday"] = int(p["sold_yesterday"])

            red_lights.append(p)

        # ==========================================
        # 🟡 判斷黃燈
        # ==========================================
        is_stagnant = False
        if p["current_stock"] > 0:
            if p["last_sold_date"] is None:
                is_stagnant = True
                p["msg"] = "新品或冷門 (未售出)"
            else:
                days_diff = (datetime.now() - p["last_sold_date"]).days
                if days_diff > 14:
                    is_stagnant = True
                    p["msg"] = f"已滯銷 {days_diff} 天"

        if is_stagnant:
            yellow_lights.append(p)

    return jsonify({"red_lights": red_lights, "yellow_lights": yellow_lights})
