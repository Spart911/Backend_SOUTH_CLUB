-- Миграция: Добавление колонки sku в таблицу products
-- Дата: 2025-11-05
-- Описание: Добавляет поле sku (артикул товара) в таблицу products

-- Добавляем колонку sku, если она еще не существует
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'products' 
        AND column_name = 'sku'
    ) THEN
        ALTER TABLE products 
        ADD COLUMN sku TEXT;
        
        COMMENT ON COLUMN products.sku IS 'Артикул товара';
        
        RAISE NOTICE 'Колонка sku успешно добавлена в таблицу products';
    ELSE
        RAISE NOTICE 'Колонка sku уже существует в таблице products';
    END IF;
END $$;

