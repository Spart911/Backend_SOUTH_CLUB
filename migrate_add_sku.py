#!/usr/bin/env python3
"""
Скрипт для миграции: добавление колонки sku в таблицу products
"""
import sys
from sqlalchemy import text
from app.database import engine
from app.core.logging import get_logger

logger = get_logger("Migration")


def add_sku_column():
    """
    Добавляет колонку sku в таблицу products, если она еще не существует
    """
    try:
        logger.info("Начало миграции: добавление колонки sku...")
        
        with engine.connect() as conn:
            # Проверяем, существует ли колонка
            check_query = text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = 'products' 
                AND column_name = 'sku'
            """)
            result = conn.execute(check_query)
            exists = result.scalar() > 0
            
            if exists:
                logger.info("Колонка sku уже существует в таблице products")
                return True
            
            # Добавляем колонку
            alter_query = text("""
                ALTER TABLE products 
                ADD COLUMN sku TEXT;
            """)
            conn.execute(alter_query)
            
            # Добавляем комментарий
            comment_query = text("""
                COMMENT ON COLUMN products.sku IS 'Артикул товара';
            """)
            conn.execute(comment_query)
            
            conn.commit()
            logger.info("✅ Колонка sku успешно добавлена в таблицу products")
            return True
            
    except Exception as e:
        logger.error(f"❌ Ошибка при выполнении миграции: {e}")
        return False


if __name__ == "__main__":
    success = add_sku_column()
    sys.exit(0 if success else 1)

