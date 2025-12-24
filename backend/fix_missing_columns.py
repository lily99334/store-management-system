from db_config import get_db_connection


def fix_columns():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("🚀 正在檢查並修復資料庫缺少的欄位...")

    # 1. 補上 total_price (總金額)
    try:
        print("正在為 Sales_Orders 加入 total_price...")
        cursor.execute("ALTER TABLE Sales_Orders ADD COLUMN total_price INT DEFAULT 0")
        print("✅ total_price 新增成功！")
    except Exception as e:
        if "1060" in str(e):  # 錯誤代碼 1060 代表欄位已存在
            print("ℹ️ total_price 已經存在，跳過。")
        else:
            print(f"⚠️ total_price 錯誤: {e}")

    # 2. 順便補上 customer_type (顧客類型)，以免等下又報錯
    try:
        print("正在為 Sales_Orders 加入 customer_type...")
        cursor.execute(
            "ALTER TABLE Sales_Orders ADD COLUMN customer_type VARCHAR(50) DEFAULT 'General'"
        )
        print("✅ customer_type 新增成功！")
    except Exception as e:
        if "1060" in str(e):
            print("ℹ️ customer_type 已經存在，跳過。")
        else:
            print(f"⚠️ customer_type 錯誤: {e}")

    # 3. 再順便檢查 Sales_Items 有沒有缺欄位 (item_price, item_total)
    try:
        cursor.execute("ALTER TABLE Sales_Items ADD COLUMN item_price INT DEFAULT 0")
        print("✅ Sales_Items 加入 item_price 成功")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE Sales_Items ADD COLUMN item_total INT DEFAULT 0")
        print("✅ Sales_Items 加入 item_total 成功")
    except:
        pass

    conn.commit()
    conn.close()
    print("🎉 資料庫修復完成！現在可以正常結帳了。")


if __name__ == "__main__":
    fix_columns()
