from flask import Blueprint, jsonify, request
from db_config import get_db_connection

sales_bp = Blueprint("sales_bp", __name__)


# 1. 結帳 (新增銷售單)
@sales_bp.route("/api/sales", methods=["POST"])
def create_sale():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        conn.start_transaction()

        total_price = 0
        items_to_process = []

        # 1. 計算金額並檢查庫存
        for item in data["items"]:
            pid = item["id"]
            qty = item["quantity"]

            cursor.execute(
                "SELECT price, current_stock, name FROM Products WHERE id = %s", (pid,)
            )
            product = cursor.fetchone()

            if not product:
                raise Exception(f"找不到商品 ID: {pid}")

            if product["current_stock"] < qty:
                raise Exception(
                    f"❌ '{product['name']}' 庫存不足！(剩 {product['current_stock']}，賣 {qty})"
                )

            item_total = product["price"] * qty
            total_price += item_total

            items_to_process.append(
                {"pid": pid, "qty": qty, "price": product["price"], "total": item_total}
            )

        # 2. 建立訂單主檔
        cursor.execute(
            "INSERT INTO Sales_Orders (total_price, customer_type) VALUES (%s, %s)",
            (total_price, data.get("customer_type", "General")),
        )
        order_id = cursor.lastrowid

        # 3. 寫入明細 & 扣庫存
        for item in items_to_process:
            cursor.execute(
                "INSERT INTO Sales_Items (order_id, product_id, quantity, item_price, item_total) VALUES (%s, %s, %s, %s, %s)",
                (order_id, item["pid"], item["qty"], item["price"], item["total"]),
            )

            cursor.execute(
                "UPDATE Products SET current_stock = current_stock - %s WHERE id = %s",
                (item["qty"], item["pid"]),
            )

        conn.commit()
        return jsonify({"message": "結帳成功", "order_id": order_id}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 400
    finally:
        conn.close()


# 🔥 2. (新功能) 查詢銷售紀錄
@sales_bp.route("/api/sales/history", methods=["GET"])
def get_sales_history():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 撈取訂單與明細摘要
    sql = """
        SELECT 
            o.id, 
            o.created_at, 
            o.total_price, 
            o.customer_type,
            GROUP_CONCAT(CONCAT(p.name, ' x', si.quantity) SEPARATOR ', ') as details
        FROM Sales_Orders o
        JOIN Sales_Items si ON o.id = si.order_id
        JOIN Products p ON si.product_id = p.id
        GROUP BY o.id
        ORDER BY o.created_at DESC
    """
    cursor.execute(sql)
    orders = cursor.fetchall()
    conn.close()

    # 轉型 decimal 避免報錯
    for o in orders:
        o["total_price"] = int(o["total_price"])

    return jsonify(orders)


# 🔥 3. (新功能) 作廢訂單 (退貨還庫存)
@sales_bp.route("/api/sales/orders/<int:id>", methods=["DELETE"])
def delete_sales_order(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()

        # 先查這張單賣了什麼，要把庫存加回去
        cursor.execute(
            "SELECT product_id, quantity FROM Sales_Items WHERE order_id = %s", (id,)
        )
        items = cursor.fetchall()

        if not items:
            return jsonify({"message": "找不到此訂單"}), 404

        # 加回庫存
        for item in items:
            cursor.execute(
                "UPDATE Products SET current_stock = current_stock + %s WHERE id = %s",
                (item["quantity"], item["product_id"]),
            )

        # 刪除訂單 (Cascade 會自動刪明細)
        cursor.execute("DELETE FROM Sales_Orders WHERE id = %s", (id,))

        conn.commit()
        return jsonify({"message": "訂單已作廢，庫存已還原"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        conn.close()
