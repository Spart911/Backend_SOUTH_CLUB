#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных SOUTH CLUB
"""

import os
import sys
from sqlalchemy import text
from app.database import engine, create_tables
from app.config import settings

def init_database():
    """
    Инициализация базы данных
    """
    try:
        print("🔧 Инициализация базы данных...")
        
        # Создаем таблицы
        create_tables()
        print("✅ Таблицы созданы успешно")
        
        # Проверяем подключение
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"📊 Подключение к PostgreSQL: {version}")
            
            # Проверяем количество таблиц
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            table_count = result.fetchone()[0]
            print(f"📋 Количество таблиц: {table_count}")
            
            # Проверяем таблицу товаров
            result = conn.execute(text("SELECT COUNT(*) FROM products"))
            product_count = result.fetchone()[0]
            print(f"🛍️ Количество товаров: {product_count}")
            
        print("🎉 База данных инициализирована успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка инициализации базы данных: {e}")
        sys.exit(1)

def check_environment():
    """
    Проверка переменных окружения
    """
    print("🔍 Проверка переменных окружения...")
    
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'ADMIN_USERNAME',
        'ADMIN_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var.lower(), None):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        print("📝 Создайте файл .env на основе env.example")
        return False
    
    print("✅ Все необходимые переменные окружения настроены")
    return True

if __name__ == "__main__":
    print("🚀 SOUTH CLUB Backend - Инициализация базы данных")
    print("=" * 50)
    
    if not check_environment():
        sys.exit(1)
    
    init_database()

