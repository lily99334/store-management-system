# 檔案位置：backend/check_stock.py
from db_config import get_db_connection

def show_stock():
    # 1. 連線資料庫
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 2. 查詢商品 ID、名稱、庫存
        sql = "SELECT id, name, current_stock FROM Products ORDER BY id ASC"
        cursor.execute(sql)
        products = cursor.fetchall()

        # 3. 漂亮地印出來
        print("-" * 40)
        print(f"{'ID':<6} {'商品名稱':<15} {'目前庫存'}")
        print("-" * 40)

        for p in products:
            # <6 代表靠左對齊佔6格，讓排版整齊
            print(f"{p['id']:<6} {p['name']:<15} {p['current_stock']}")
            
        print("-" * 40)

    except Exception as e:
        print("查詢失敗:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    show_stock()