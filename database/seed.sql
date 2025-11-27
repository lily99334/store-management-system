-- ==========================================
-- 檔案名稱：seed.sql
-- 用途：塞入初始測試資料 (可重複執行)
-- ==========================================

USE store_db;

-- 1. 清空舊資料 (選用，避免 ID 衝突或重複)
-- 注意順序：先刪明細 (有外鍵)，再刪主檔
DELETE FROM Sales_Items;
DELETE FROM Sales_Orders;
DELETE FROM Products;
-- 重置 AUTO_INCREMENT (讓 ID 從 1 開始)
ALTER TABLE Products AUTO_INCREMENT = 1;
ALTER TABLE Sales_Orders AUTO_INCREMENT = 1;
ALTER TABLE Sales_Items AUTO_INCREMENT = 1;


-- 2. 新增測試商品 (含圖片網址)
INSERT INTO Products (name, category, price, current_stock, safe_stock, lead_time, image_url) VALUES 
('可口可樂', '飲料', 25, 5, 20, 2, 'http://127.0.0.1:5000/static/images/cola.png'),
('養樂多', '飲料', 20, 0, 15, 2, 'http://127.0.0.1:5000/static/images/yakult.png'),
('統一布丁', '甜點', 12, 50, 10, 1, 'http://127.0.0.1:5000/static/images/pudding.png'),
('御飯糰-鮭魚', '鮮食', 49, 2, 10, 1, 'http://127.0.0.1:5000/static/images/salmon_rice_ball.png'),
('茶葉蛋', '熟食', 10, 100, 50, 1, 'http://127.0.0.1:5000/static/images/tea_egg.png'),
('科學麵', '零食', 10, 0, 20, 3, 'http://127.0.0.1:5000/static/images/science_noodles.png');

-- 3. 新增一筆假銷售紀錄 (讓報表不要空白)
INSERT INTO Sales_Orders (sale_time, total_amount, customer_tag) VALUES (NOW(), 35, '學生');

-- 假設剛才插入的 ID 分別是 1 (可樂) 和 4 (茶葉蛋)，訂單 ID 是 1
INSERT INTO Sales_Items (order_id, product_id, quantity, subtotal) VALUES 
(1, 1, 1, 25),
(1, 4, 1, 10);