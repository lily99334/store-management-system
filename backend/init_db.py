import mysql.connector
import os

# 設定資料庫連線資訊 (這裡手動設定，為了先建立資料庫)
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
}


def init_db():
    # 1. 先連線到 MySQL (注意：這裡故意不指定 database，為了能執行 CREATE 指令)
    print("嘗試連線到 MySQL...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✅ MySQL 連線成功！")

        # 2. 建立資料庫 (如果不存在才建)
        print("正在建立資料庫 store_db...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS store_db")
        print("✅ 資料庫 store_db 已準備就緒！")

        # 3. 切換到該資料庫
        conn.database = "store_db"

    except mysql.connector.Error as err:
        print(f"❌ 連線失敗: {err}")
        return

    # ==========================================
    # 4. 讀取 SQL 檔案並執行
    # ==========================================
    current_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(current_dir, "..", "database", "init.sql")
    seed_path = os.path.join(current_dir, "..", "database", "seed.sql")

    print(f"讀取 SQL 檔案: {schema_path}")

    try:
        # 讀取 init.sql
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        # 讀取 seed.sql
        with open(seed_path, "r", encoding="utf-8") as f:
            seed_sql = f.read()

        print("正在建立資料表...")
        # 依據分號切個指令執行 (init.sql)
        for statement in schema_sql.split(";"):
            if statement.strip():
                # 跳過 USE store_db; 因為我們已經切換了，且有些驅動不支援切換
                if "USE store_db" in statement.upper():
                    continue
                cursor.execute(statement)

        print("正在寫入測試資料...")
        # 執行 seed.sql (塞資料)
        for statement in seed_sql.split(";"):
            if statement.strip():
                if "USE store_db" in statement.upper():
                    continue
                cursor.execute(statement)

        conn.commit()
        print("🎉 大功告成！資料庫重置成功！")

    except FileNotFoundError:
        print(f"❌ 找不到 SQL 檔案，請確認路徑: {schema_path}")
    except Exception as e:
        print(f"❌ 執行 SQL 發生錯誤: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    init_db()
