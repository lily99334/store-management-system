from db_config import get_db_connection


def fix_items_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("🚀 正在修復銷售明細表 (Sales_Items)...")

    # 1. 補上 item_price (單價)
    try:
        print("正在加入 item_price 欄位...")
        cursor.execute("ALTER TABLE Sales_Items ADD COLUMN item_price INT DEFAULT 0")
        print("✅ item_price 新增成功！")
    except Exception as e:
        if "1060" in str(e):
            print("ℹ️ item_price 已經存在，跳過。")
        else:
            print(f"⚠️ item_price 錯誤: {e}")

    # 2. 補上 item_total (小計)
    try:
        print("正在加入 item_total 欄位...")
        cursor.execute("ALTER TABLE Sales_Items ADD COLUMN item_total INT DEFAULT 0")
        print("✅ item_total 新增成功！")
    except Exception as e:
        if "1060" in str(e):
            print("ℹ️ item_total 已經存在，跳過。")
        else:
            print(f"⚠️ item_total 錯誤: {e}")

    conn.commit()
    conn.close()
    print("🎉 全部修復完成！這次真的可以結帳了。")


if __name__ == "__main__":
    fix_items_table()
