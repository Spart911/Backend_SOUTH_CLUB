# 🌐 SOUTH CLUB Frontend API Documentation

## 📋 Обзор

Документация API для фронтенд разработчиков SOUTH CLUB. Содержит все необходимые эндпоинты, схемы данных, примеры запросов и ответов.

## 🚀 Быстрый старт

### Базовый URL
```
http://localhost:8000
```

### Документация API
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔐 Аутентификация

### Получение JWT токена

#### POST /api/v1/auth/login
Вход в админку через форму (OAuth2)

```typescript
interface LoginRequest {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  expires_in: number; // секунды
}
```

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Пример ответа:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST /api/v1/auth/login-json
Вход в админку через JSON

```typescript
interface LoginJsonRequest {
  username: string;
  password: string;
}

interface LoginJsonResponse {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
}
```

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Использование токена

Все защищенные эндпоинты требуют заголовок:
```typescript
Authorization: Bearer <your_jwt_token>
```

## 🛍️ Товары (Products)

### Получение списка товаров

#### GET /api/v1/products/
Получить список товаров с пагинацией

**Параметры:**
- `skip` (query): Количество пропущенных записей (по умолчанию: 0)
- `limit` (query): Максимальное количество записей (по умолчанию: 100, максимум: 1000)

**Пример запроса:**
```bash
curl "http://localhost:8000/api/v1/products/?skip=0&limit=10"
```

**Пример ответа:**
```json
{
  "products": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Футболка SOUTH CLUB",
      "characteristics": "100% хлопок, дышащая ткань",
      "color": "Белый",
      "composition": "100% хлопок",
      "print_technology": "Термотрансфер",
      "size": 2,
      "price": 2500,
      "photos": [
        {
          "id": "550e8400-e29b-41d4-a716-446655440001",
          "product_id": "550e8400-e29b-41d4-a716-446655440000",
          "name": "main_photo.jpg",
          "file_path": "/uploads/products/abc123.jpg",
          "priority": 0
        }
      ]
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

### Поиск товаров

#### GET /api/v1/products/search/
Поиск товаров по названию, характеристикам или цвету

**Параметры:**
- `q` (query): Поисковый запрос (обязательный, минимум 1 символ)
- `skip` (query): Количество пропущенных записей (по умолчанию: 0)
- `limit` (query): Максимальное количество записей (по умолчанию: 100, максимум: 1000)

**Пример запроса:**
```bash
curl "http://localhost:8000/api/v1/products/search/?q=футболка&limit=5"
```

### Фильтрация по размеру

#### GET /api/v1/products/size/{size}
Получить товары по размеру

**Параметры:**
- `size` (path): Размер товара (0-4, где 0=XS, 1=S, 2=M, 3=L, 4=XL)
- `skip` (query): Количество пропущенных записей (по умолчанию: 0)
- `limit` (query): Максимальное количество записей (по умолчанию: 100, максимум: 1000)

**Пример запроса:**
```bash
curl "http://localhost:8000/api/v1/products/size/2?limit=20"
```

### Фильтрация по цене

#### GET /api/v1/products/price/range
Получить товары по диапазону цен

**Параметры:**
- `min_price` (query): Минимальная цена (обязательный, >= 0)
- `max_price` (query): Максимальная цена (обязательный, >= 0)
- `skip` (query): Количество пропущенных записей (по умолчанию: 0)
- `limit` (query): Максимальное количество записей (по умолчанию: 100, максимум: 1000)

**Пример запроса:**
```bash
curl "http://localhost:8000/api/v1/products/price/range?min_price=1000&max_price=5000&limit=50"
```

### Получение товара по ID

#### GET /api/v1/products/{product_id}
Получить товар по ID

**Параметры:**
- `product_id` (path): UUID товара

**Пример запроса:**
```bash
curl "http://localhost:8000/api/v1/products/550e8400-e29b-41d4-a716-446655440000"
```

**Пример ответа:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Футболка SOUTH CLUB",
  "characteristics": "100% хлопок, дышащая ткань",
  "color": "Белый",
  "composition": "100% хлопок",
  "print_technology": "Термотрансфер",
  "size": 2,
  "price": 2500,
  "photos": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "product_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "main_photo.jpg",
      "file_path": "/uploads/products/abc123.jpg",
      "priority": 0
    }
  ]
}
```

## 📸 Фотографии товаров (Product Photos)

### Получение фотографий товара

#### GET /api/v1/photos/product/{product_id}
Получить все фотографии товара

**Параметры:**
- `product_id` (path): UUID товара

**Пример запроса:**
```bash
curl "http://localhost:8000/api/v1/photos/product/550e8400-e29b-41d4-a716-446655440000"
```

**Пример ответа:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "product_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "main_photo.jpg",
    "file_path": "/uploads/products/abc123.jpg",
    "priority": 0
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "product_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "detail_photo.jpg",
    "file_path": "/uploads/products/def456.jpg",
    "priority": 1
  }
]
```

### Получение фотографии по ID

#### GET /api/v1/photos/{photo_id}
Получить фотографию по ID

**Параметры:**
- `photo_id` (path): UUID фотографии

**Пример запроса:**
```bash
curl "http://localhost:8000/api/v1/photos/550e8400-e29b-41d4-a716-446655440001"
```

## 🖼️ Слайдер (Slider Photos)

### Получение фотографий слайдера

#### GET /api/v1/slider/
Получить все фотографии слайдера

**Пример запроса:**
```bash
curl "http://localhost:8000/api/v1/slider/"
```

**Пример ответа:**
```json
{
  "photos": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "name": "slider_main.jpg",
      "file_path": "/uploads/slider/slider1.jpg",
      "order_number": 0
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440004",
      "name": "slider_secondary.jpg",
      "file_path": "/uploads/slider/slider2.jpg",
      "order_number": 1
    }
  ]
}
```

### Получение фотографии слайдера по ID

#### GET /api/v1/slider/{photo_id}
Получить фотографию слайдера по ID

**Параметры:**
- `photo_id` (path): UUID фотографии

**Пример запроса:**
```bash
curl "http://localhost:8000/api/v1/slider/550e8400-e29b-41d4-a716-446655440003"
```

## 🔧 Административные эндпоинты

> ⚠️ **Внимание**: Все административные эндпоинты требуют JWT токен в заголовке `Authorization: Bearer <token>`

### Создание товара

#### POST /api/v1/products/
Создать новый товар

**Тело запроса:**
```typescript
interface ProductCreate {
  name: string;
  characteristics: string;
  color: string;
  composition: string;
  print_technology: string;
  size: number; // 0-4
  price: number;
}
```

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Новая футболка",
    "characteristics": "100% хлопок",
    "color": "Черный",
    "composition": "100% хлопок",
    "print_technology": "Шелкография",
    "size": 2,
    "price": 3000
  }'
```

### Обновление товара

#### PUT /api/v1/products/{product_id}
Обновить товар

**Тело запроса:**
```typescript
interface ProductUpdate {
  name?: string;
  characteristics?: string;
  color?: string;
  composition?: string;
  print_technology?: string;
  size?: number; // 0-4
  price?: number;
}
```

**Пример запроса:**
```bash
curl -X PUT "http://localhost:8000/api/v1/products/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 3500
  }'
```

### Удаление товара

#### DELETE /api/v1/products/{product_id}
Удалить товар

**Параметры:**
- `product_id` (path): UUID товара

**Пример запроса:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/products/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer <your_jwt_token>"
```

### Загрузка фотографии товара

#### POST /api/v1/photos/upload
Загрузить фотографию для товара

**Параметры:**
- `product_id` (query): UUID товара
- `photo` (file): Файл изображения (JPG, PNG, WebP)
- `priority` (query): Приоритет фотографии (0-2, по умолчанию: 0)

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/api/v1/photos/upload" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -F "product_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "photo=@/path/to/photo.jpg" \
  -F "priority=0"
```

### Загрузка фотографии слайдера

#### POST /api/v1/slider/upload
Загрузить фотографию для слайдера

**Параметры:**
- `photo` (file): Файл изображения (JPG, PNG, WebP)
- `order_number` (query): Порядковый номер (по умолчанию: 0)

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/api/v1/slider/upload" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -F "photo=@/path/to/slider.jpg" \
  -F "order_number=1"
```

## 📁 Работа с файлами

### Доступ к загруженным файлам

Все загруженные файлы доступны по URL:
```
http://localhost:8000/uploads/products/{filename}
http://localhost:8000/uploads/slider/{filename}
```

### Поддерживаемые форматы
- **Изображения**: JPG, JPEG, PNG, WebP
- **Максимальный размер**: 10MB
- **Автоматическая оптимизация**: Да (максимум 1920x1080)

### Примеры URL файлов
```typescript
// Фотография товара
const productPhotoUrl = "http://localhost:8000/uploads/products/abc123.jpg";

// Фотография слайдера
const sliderPhotoUrl = "http://localhost:8000/uploads/slider/slider1.jpg";
```

## 📊 Схемы данных

### Product
```typescript
interface Product {
  id: string; // UUID
  name: string;
  characteristics: string;
  color: string;
  composition: string;
  print_technology: string;
  size: number; // 0-4 (XS, S, M, L, XL)
  price: number;
  photos: ProductPhoto[];
}
```

### ProductPhoto
```typescript
interface ProductPhoto {
  id: string; // UUID
  product_id: string; // UUID
  name: string;
  file_path: string;
  priority: number; // 0-2
}
```

### SliderPhoto
```typescript
interface SliderPhoto {
  id: string; // UUID
  name: string;
  file_path: string;
  order_number: number;
}
```

### ProductListResponse
```typescript
interface ProductListResponse {
  products: Product[];
  total: number;
  skip: number;
  limit: number;
}
```

## 🚨 Обработка ошибок

### Стандартные HTTP коды
- `200` - Успешный запрос
- `201` - Ресурс создан
- `204` - Ресурс удален
- `400` - Ошибка валидации
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Ресурс не найден
- `422` - Ошибка валидации данных
- `500` - Внутренняя ошибка сервера

### Пример ошибки
```json
{
  "detail": "Товар не найден",
  "status_code": 404
}
```

## 🔍 Поиск и фильтрация

### Поиск по тексту
Поиск осуществляется по полям:
- `name` (название товара)
- `characteristics` (характеристики)
- `color` (цвет)

### Фильтрация
- **По размеру**: `GET /api/v1/products/size/{size}`
- **По цене**: `GET /api/v1/products/price/range?min_price=X&max_price=Y`
- **По приоритету фото**: `priority` в фотографиях товаров
- **По порядку слайдера**: `order_number` в слайдере

### Пагинация
Все списки поддерживают пагинацию:
- `skip` - количество пропущенных записей
- `limit` - максимальное количество записей (максимум 1000)

## 📱 Примеры использования

### React/TypeScript
```typescript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Получение списка товаров
const getProducts = async (skip = 0, limit = 10) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/products/?skip=${skip}&limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error('Ошибка при получении товаров:', error);
    throw error;
  }
};

// Поиск товаров
const searchProducts = async (query: string, skip = 0, limit = 10) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/products/search/?q=${encodeURIComponent(query)}&skip=${skip}&limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error('Ошибка при поиске товаров:', error);
    throw error;
  }
};

// Получение товара по ID
const getProduct = async (id: string) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/products/${id}`);
    return response.data;
  } catch (error) {
    console.error('Ошибка при получении товара:', error);
    throw error;
  }
};

// Аутентификация
const login = async (username: string, password: string) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/v1/auth/login-json`, {
      username,
      password
    });
    return response.data;
  } catch (error) {
    console.error('Ошибка аутентификации:', error);
    throw error;
  }
};
```

### Vue.js
```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Получение товаров
const getProducts = async (skip = 0, limit = 10) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/products/?skip=${skip}&limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error('Ошибка при получении товаров:', error);
    throw error;
  }
};

// Поиск товаров
const searchProducts = async (query, skip = 0, limit = 10) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/products/search/?q=${encodeURIComponent(query)}&skip=${skip}&limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error('Ошибка при поиске товаров:', error);
    throw error;
  }
};
```

## 🔧 Настройка CORS

Сервер настроен для работы с фронтендом на:
- `http://localhost:3000` (React/Vue dev server)
- `http://localhost:8080` (Vue CLI dev server)

Для добавления других доменов отредактируйте `ALLOWED_ORIGINS` в `.env` файле.

## 📚 Дополнительные ресурсы

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI спецификация**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

## 🆘 Поддержка

При возникновении проблем:
1. Проверьте логи сервера
2. Убедитесь в корректности запросов
3. Проверьте статус сервера: `GET /health`
4. Обратитесь к команде backend разработки

---

**Версия API**: 1.0.0  
**Последнее обновление**: 3 сентября 2025  
**Статус**: ✅ Готово к использованию

