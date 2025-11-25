# store-management-system

# 超商門市庫存採購管理系統 (Store Management System)

這是一個針對超商門市設計的智慧化管理系統，整合了前台 POS 銷售、後台進貨管理以及智慧決策支援功能。


## 🛠️ 技術架構
* **Backend**: Python, Flask
* **Frontend**: HTML5, Bootstrap 5, Vue.js (CDN)
* **Database**: MySQL 8.0

## 🚀 快速開始 (Installation)

### 1. 環境準備
請確保你的電腦已安裝以下軟體：
* Python 3.x
* MySQL Server & Workbench

### 2. 資料庫設定
1. 開啟 MySQL Workbench。
2. 開啟 `database/init.sql` 檔案。
3. 執行腳本以建立 `store_db` 資料庫與相關表格。
4. 確認 `backend/db_config.py` 中的密碼與你的 MySQL 設定一致。

### 3. 安裝依賴套件
在專案根目錄執行以下指令：
```bash
pip install -r requirements.txt