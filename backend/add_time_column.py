from db_config import get_db_connection


def fix_database_schema():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("正在修復資料庫欄位...")

    try:
        # 1. 嘗試幫 Sales_Orders 加上 created_at 欄位
        print("正在為 Sales_Orders 加入時間欄位...")
        cursor.execute(
            "ALTER TABLE Sales_Orders ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        )
        print("✅ Sales_Orders 修復成功！")
    except Exception as e:
        # 如果欄位已經存在 (錯誤代碼 1060)，就忽略
        if "1060" in str(e):
            print("ℹ️ Sales_Orders 已經有此欄位，跳過。")
        else:
            print(f"⚠️ Sales_Orders 訊息: {e}")

    try:
        # 2. 為了保險，我們也檢查 Sales_Items 有沒有 created_at (雖然現在主要用 Sales_Orders)
        # 但有些舊的程式碼可能還會看這裡，補上也無妨
        print("正在為 Sales_Items 加入時間欄位...")
        cursor.execute(
            "ALTER TABLE Sales_Items ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        )
        print("✅ Sales_Items 修復成功！")
    except Exception as e:
        if "1060" in str(e):
            print("ℹ️ Sales_Items 已經有此欄位，跳過。")
        else:
            print(f"⚠️ Sales_Items 訊息: {e}")

    conn.commit()
    conn.close()
    print("🎉 資料庫結構修復完成！")


if __name__ == "__main__":
    fix_database_schema()
