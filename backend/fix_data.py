from db_config import get_db_connection


def fix_negative_stock():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("Checking negative stock...")
    # 把所有小於 0 的庫存都改成 0
    cursor.execute("UPDATE Products SET current_stock = 0 WHERE current_stock < 0")

    affected = cursor.rowcount
    conn.commit()
    conn.close()

    # 把勾勾拿掉，避免編碼錯誤
    print(f"[OK] 修正完成！共有 {affected} 項商品的負庫存已被歸零。")


if __name__ == "__main__":
    fix_negative_stock()
