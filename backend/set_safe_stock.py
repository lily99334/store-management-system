from db_config import get_db_connection


def set_default_safe_stock():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("正在更新保底庫存設定...")

    # 將所有商品的 safe_stock 強制設為 10 (你可以改成其他數字)
    # 這樣只要庫存低於 10，系統就會叫你補貨
    cursor.execute("UPDATE Products SET safe_stock = 10 WHERE safe_stock = 0")

    affected = cursor.rowcount
    conn.commit()
    conn.close()

    print(f"[OK] 更新完成！共有 {affected} 項商品的保底庫存已設為 10。")


if __name__ == "__main__":
    set_default_safe_stock()
