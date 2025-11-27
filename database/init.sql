-- ==========================================
-- 超商門市庫存採購管理系統 - 資料庫初始化腳本(含圖片版)
-- ==========================================

DROP DATABASE IF EXISTS store_db;
-- 1. 建立資料庫 (如果不存在才建，避免重複報錯)
CREATE DATABASE IF NOT EXISTS store_db;
USE store_db;

-- 2. 建立【商品主檔】 (Products)
-- 用途：儲存商品基本資料、當前庫存、以及智慧演算法需要的參數
CREATE TABLE IF NOT EXISTS Products (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '商品編號 (PK)',
    name VARCHAR(100) NOT NULL COMMENT '商品名稱',
    category VARCHAR(50) COMMENT '分類 (如: 鮮食/飲料/用品)',
    price INT NOT NULL COMMENT '售價',
    current_stock INT DEFAULT 0 COMMENT '當前庫存量 (核心數據)',
    safe_stock INT DEFAULT 10 COMMENT '預設安全庫存 (演算法用)',
    lead_time INT DEFAULT 2 COMMENT '補貨前置天數 (演算法用)',
    image_url VARCHAR(255) COMMENT '商品圖片網址 (存 URL 字串)'
);

-- 3. 建立【銷售單主檔】 (Sales_Orders)
-- 用途：POS 結帳時產生的訂單頭，記錄時間與客層
CREATE TABLE IF NOT EXISTS Sales_Orders (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '銷售單號 (PK)',
    sale_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '銷售時間 (演算法用)',
    total_amount INT COMMENT '整單總金額',
    customer_tag VARCHAR(20) COMMENT '客層標籤 (如: 學生/上班族)'
);

-- 4. 建立【銷售單明細】 (Sales_Items)
-- 用途：記錄每一筆訂單買了哪些商品
CREATE TABLE IF NOT EXISTS Sales_Items (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '流水號 (PK)',
    order_id INT NOT NULL COMMENT '歸屬訂單ID (FK)',
    product_id INT NOT NULL COMMENT '商品ID (FK)',
    quantity INT NOT NULL COMMENT '銷售數量',
    subtotal INT COMMENT '小計 (單價x數量)',
    FOREIGN KEY (order_id) REFERENCES Sales_Orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Products(id)
);

-- 5. 建立【進貨單主檔】 (Restock_Orders)
-- 用途：店長叫貨的單據，記錄狀態 (運送中/已到貨)
CREATE TABLE IF NOT EXISTS Restock_Orders (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '進貨單號 (PK)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '叫貨時間',
    status VARCHAR(20) DEFAULT 'Pending' COMMENT '狀態: Pending(運送中), Completed(已點收)'
);

-- 6. 建立【進貨單明細】 (Restock_Items)
-- 用途：記錄每一張進貨單進了哪些商品
CREATE TABLE IF NOT EXISTS Restock_Items (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '流水號 (PK)',
    restock_id INT NOT NULL COMMENT '歸屬進貨單ID (FK)',
    product_id INT NOT NULL COMMENT '商品ID (FK)',
    quantity INT NOT NULL COMMENT '進貨數量',
    FOREIGN KEY (restock_id) REFERENCES Restock_Orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Products(id)
);
