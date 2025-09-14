-- Инициализация базы данных SOUTH CLUB
-- Создаем расширения
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Создаем таблицу товаров
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    characteristics TEXT,
    color TEXT,
    composition TEXT,
    print_technology TEXT,
    size INTEGER NOT NULL CHECK (size >= 0 AND size <= 4),
    price INTEGER NOT NULL CHECK (price > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создаем таблицу фотографий товаров
CREATE TABLE IF NOT EXISTS product_photos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 0 CHECK (priority >= 0 AND priority <= 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создаем таблицу фотографий слайдера
CREATE TABLE IF NOT EXISTS slider_photos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    order_number INTEGER NOT NULL DEFAULT 0 CHECK (order_number >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создаем индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_size ON products(size);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
CREATE INDEX IF NOT EXISTS idx_product_photos_product_id ON product_photos(product_id);
CREATE INDEX IF NOT EXISTS idx_product_photos_priority ON product_photos(priority);
CREATE INDEX IF NOT EXISTS idx_slider_photos_order ON slider_photos(order_number);

-- Создаем функцию для обновления времени изменения
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Создаем триггер для автоматического обновления времени
CREATE TRIGGER update_products_updated_at 
    BEFORE UPDATE ON products 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Вставляем тестовые данные (опционально)
INSERT INTO products (name, characteristics, color, composition, print_technology, size, price) VALUES
('Футболка SOUTH CLUB', '100% хлопок, свободный крой', 'Белый', '100% хлопок', 'Термопечать', 2, 2500),
('Худи SOUTH CLUB', 'Теплое, уютное', 'Черный', '80% хлопок, 20% полиэстер', 'Вышивка', 3, 4500),
('Кепка SOUTH CLUB', 'Регулируемый размер', 'Красный', '100% хлопок', 'Вышивка', 1, 1200)
ON CONFLICT DO NOTHING;

-- Создаем пользователя для приложения (если нужно)
-- CREATE USER south_club_app WITH PASSWORD 'app_password';
-- GRANT ALL PRIVILEGES ON DATABASE south_club_db TO south_club_app;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO south_club_app;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO south_club_app;

