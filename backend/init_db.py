from db_config import get_db_connection
import os

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # ==========================================
    # 👇 核心修改：自動抓取正確的路徑
    # ==========================================
    
    # 1. 取得這支程式 (init_db.py) 目前所在的資料夾 (就是 backend)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. 組合路徑：往上一層 (..) 找 database 資料夾
    # 請確認你的檔名是 init.sql 還是 schema.sql (看截圖是 init.sql)
    schema_path = os.path.join(current_dir, '..', 'database', 'init.sql')
    seed_path = os.path.join(current_dir, '..', 'database', 'seed.sql')

    print(f"正在讀取 SQL 檔案: {schema_path}")

    # ==========================================

    try:
        # 讀取 Schema (建表)
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            
        # 讀取 Seed (測試資料)
        with open(seed_path, 'r', encoding='utf-8') as f:
            seed_sql = f.read()

        print("正在建立資料表...")
        # 依據分號切個指令執行
        for statement in schema_sql.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        print("正在寫入測試資料...")
        for statement in seed_sql.split(';'):
            if statement.strip():
                cursor.execute(statement)
                
        conn.commit()
        print("✅ 資料庫重置成功！")
        
    except FileNotFoundError as e:
        print(f"❌ 找不到檔案: {e}")
        print("請檢查 database 資料夾內的檔名是否正確 (init.sql vs schema.sql)")
    except Exception as e:
        print(f"❌ 資料庫錯誤: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    init_db()