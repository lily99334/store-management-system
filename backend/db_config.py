import mysql.connector

# 連線設定函式
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',       # 因為大家都在自己電腦跑，所以是 localhost
            user='root',            # 預設帳號
            password='root',        # 這是我們安裝時約定好的密碼
            database='store_db'     # 這是我們 init.sql 建好的資料庫名稱
        )
        return connection
    except mysql.connector.Error as err:
        print(f"資料庫連線失敗: {err}")
        return None