-- ==========================================
-- 超商門市庫存採購管理系統 - 資料庫初始化腳本
-- ==========================================

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
    safe_stock INT DEFAULT 10 COMMENT '預設安全庫存 (可被演算法覆蓋)',
    lead_time INT DEFAULT 2 COMMENT '補貨前置天數 (智慧演算法用)'
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

-- ==========================================
-- 初始測試資料 (讓系統一開始有點東西可以看)
-- ==========================================

-- 新增幾個測試商品
INSERT INTO Products (name, category, price, current_stock, safe_stock, lead_time) VALUES 
('可口可樂', '飲料', 25, 5, 20, 2),
('統一布丁', '甜點', 12, 50, 10, 1),
('御飯糰-肉鬆', '鮮食', 30, 2, 10, 1),
('茶葉蛋', '熟食', 10, 100, 50, 1),
('科學麵', '零食', 10, 0, 20, 3);

-- 新增一筆測試銷售紀錄 (假裝有人買了東西)
-- 1. 先建訂單主檔
INSERT INTO Sales_Orders (sale_time, total_amount, customer_tag) VALUES (NOW(), 35, '學生');
-- 2. 再建訂單明細 (假設這張單買了 1個可樂 + 1個茶葉蛋)
-- 注意：這裡假設上面的訂單 ID 是 1，商品 ID 是 1 和 4
INSERT INTO Sales_Items (order_id, product_id, quantity, subtotal) VALUES 
(1, 1, 1, 25),
(1, 4, 1, 10);