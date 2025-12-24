from flask import Blueprint, jsonify, request
from db_config import get_db_connection

product_bp = Blueprint("product_bp", __name__)


# 1. 取得所有商品 (Read)
@product_bp.route("/api/products", methods=["GET"])
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Products ORDER BY id DESC")
    products = cursor.fetchall()
    conn.close()
    return jsonify(products)


# 2. 新增商品 (Create)
@product_bp.route("/api/products", methods=["POST"])
def add_product():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """INSERT INTO Products (name, category, price, current_stock, safe_stock, lead_time, image_url) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        val = (
            data["name"],
            data["category"],
            data["price"],
            data["current_stock"],
            data["safe_stock"],
            data["lead_time"],
            data["image_url"],
        )
        cursor.execute(sql, val)
        conn.commit()
        return jsonify({"message": "新增成功"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        conn.close()


# 3. 修改商品 (Update)
@product_bp.route("/api/products/<int:id>", methods=["PUT"])
def update_product(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """UPDATE Products SET name=%s, category=%s, price=%s, 
                 safe_stock=%s, lead_time=%s, image_url=%s WHERE id=%s"""
        val = (
            data["name"],
            data["category"],
            data["price"],
            data["safe_stock"],
            data["lead_time"],
            data["image_url"],
            id,
        )
        cursor.execute(sql, val)
        conn.commit()
        return jsonify({"message": "更新成功"})
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        conn.close()


# 4. 刪除商品 (Delete) - 含防呆檢查
@product_bp.route("/api/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 先檢查有沒有賣過 (如果有賣過就不能刪，不然報表會壞掉)
        cursor.execute("SELECT count(*) FROM Sales_Items WHERE product_id = %s", (id,))
        count = cursor.fetchone()[0]
        if count > 0:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "此商品已有銷售紀錄，無法刪除！(請改用下架功能)",
                    }
                ),
                400,
            )

        cursor.execute("DELETE FROM Products WHERE id = %s", (id,))
        conn.commit()
        return jsonify({"status": "success", "message": "刪除成功"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()
