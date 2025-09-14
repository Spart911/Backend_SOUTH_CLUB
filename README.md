# SOUTH CLUB Backend

Бекенд для сайта по продаже товаров SOUTH CLUB на FastAPI + SQLAlchemy + PostgreSQL

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd Backend_SOUTH_CLUB
```

### 2. Документация API
После запуска сервера документация API будет доступна по адресам:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Frontend Docs**: [FRONTEND_API_DOCS.md](FRONTEND_API_DOCS.md)

### 2. Настройка переменных окружения
```bash
cp env.example .env
# Отредактируйте .env файл с вашими настройками
```

### 3. Запуск через Docker (рекомендуется)
```bash
cd docker
docker-compose up -d
```

### 4. Запуск локально
```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt

# Запуск приложения
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📋 Требования

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (опционально)

## 📚 Документация

- **[Frontend API Documentation](FRONTEND_API_DOCS.md)** - Подробная документация API для фронтенд разработчиков
- **[Security Checklist](SECURITY_CHECKLIST.md)** - Чек-лист по безопасности
- **[Logging Guide](LOGGING_GUIDE.md)** - Руководство по логированию
- **[Security Audit Report](SECURITY_AUDIT_REPORT.md)** - Отчет об аудите безопасности

## 🔧 Конфигурация

### Переменные окружения (.env)

```bash
# База данных
DATABASE_URL=postgresql://user:password@localhost:5432/south_club_db

# Безопасность
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Учетные данные админа
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# Загрузка файлов
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

## 🗄️ База данных

### Структура таблиц

#### Products (Товары)
- `id` - UUID (Primary Key)
- `name` - Название товара
- `characteristics` - Характеристики
- `color` - Цвет
- `composition` - Состав
- `print_technology` - Технология печати
- `size` - Размер (0-4)
- `price` - Цена

#### ProductPhotos (Фотографии товаров)
- `id` - UUID (Primary Key)
- `product_id` - ID товара (Foreign Key)
- `name` - Имя фотографии
- `file_path` - Абсолютный путь к файлу
- `priority` - Приоритет (0-2)

#### SliderPhotos (Фотографии слайдера)
- `id` - UUID (Primary Key)
- `name` - Имя фотографии
- `file_path` - Абсолютный путь к файлу
- `order_number` - Порядковый номер

## 📡 API Endpoints

### Аутентификация
- `POST /api/v1/auth/login` - Вход в админку
- `POST /api/v1/auth/login-json` - Вход через JSON

### Товары
- `GET /api/v1/products` - Список товаров
- `GET /api/v1/products/{id}` - Товар по ID
- `POST /api/v1/products` - Создать товар
- `PUT /api/v1/products/{id}` - Обновить товар
- `DELETE /api/v1/products/{id}` - Удалить товар
- `GET /api/v1/products/search/` - Поиск товаров
- `GET /api/v1/products/size/{size}` - Товары по размеру
- `GET /api/v1/products/price/range` - Товары по цене

### Обратная связь
- `POST /api/v1/feedback` - Отправить обратную связь
- `POST /api/v1/feedback/test` - Тест Telegram

## 🔐 Аутентификация

Для доступа к защищенным эндпоинтам используйте JWT токен:

```bash
# Получение токена
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Использование токена
curl -H "Authorization: Bearer <your-token>" \
  "http://localhost:8000/api/v1/products"
```

## 📁 Структура проекта

```
Backend_SOUTH_CLUB/
├── app/                          # Основной код
│   ├── api/                      # API роуты
│   ├── core/                     # Ядро приложения
│   ├── models/                   # SQLAlchemy модели
│   ├── repositories/             # Репозитории
│   ├── schemas/                  # Pydantic схемы
│   ├── services/                 # Бизнес-логика
│   └── utils/                    # Утилиты
├── uploads/                      # Загруженные файлы
├── docker/                       # Docker файлы
├── tests/                        # Тесты
└── requirements.txt              # Зависимости
```

## 🐳 Docker

### Запуск всех сервисов
```bash
cd docker
docker-compose up -d
```

### Остановка
```bash
docker-compose down
```

### Просмотр логов
```bash
docker-compose logs -f backend
```

### Пересборка
```bash
docker-compose up -d --build
```

## 🧪 Тестирование

```bash
# Установка тестовых зависимостей
pip install pytest pytest-asyncio httpx

# Запуск тестов
pytest
```

## 📚 Документация API

После запуска приложения документация доступна по адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🚨 Безопасность

- Все пароли хешируются с помощью bcrypt
- JWT токены для аутентификации
- Валидация входных данных через Pydantic
- CORS настройки для фронтенда
- Статичные учетные данные админа (без БД)

## 🔄 Миграции

База данных создается автоматически при запуске приложения. Для продакшена рекомендуется использовать Alembic для управления миграциями.

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи приложения
2. Убедитесь в корректности настроек в .env
3. Проверьте подключение к базе данных
4. Создайте issue в репозитории

## 📄 Лицензия

MIT License
