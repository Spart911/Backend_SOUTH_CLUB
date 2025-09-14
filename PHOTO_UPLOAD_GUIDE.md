# Загрузка изображений товара для фронтенда

## Общая информация

Для загрузки изображений товара используется отдельный API эндпоинт, который работает независимо от создания/редактирования товара. Сначала создается товар, затем к нему загружаются фотографии.

## Аутентификация

Все операции с загрузкой изображений требуют аутентификации админа. Необходимо сначала получить JWT токен через `/api/v1/auth/login`.

## API эндпоинты

### 1. Загрузка фотографии товара

**POST** `/api/v1/photos/upload-photo`

**Параметры:**
- `product_id` (query parameter) - UUID товара, к которому привязывается фотография
- `photo` (form-data file) - файл изображения
- `priority` (query parameter, опциональный) - приоритет фотографии (0-2, по умолчанию 0)

**Заголовки:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: multipart/form-data
```

**Пример запроса:**
```javascript
const formData = new FormData();
formData.append('photo', fileInput.files[0]);

const response = await fetch('/api/v1/photos/upload-photo?product_id=123e4567-e89b-12d3-a456-426614174000&priority=1', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
```

**Ответ (201 Created):**
```json
{
  "id": "456e7890-e89b-12d3-a456-426614174001",
  "product_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "product_photo.jpg",
  "file_path": "/app/uploads/products/123e4567-e89b-12d3-a456-426614174000/photo_123.jpg",
  "priority": 1
}
```

### 2. Получение фотографий товара

**GET** `/api/v1/photos/product/{product_id}`

**Пример запроса:**
```javascript
const response = await fetch('/api/v1/photos/product/123e4567-e89b-12d3-a456-426614174000');
const photos = await response.json();
```

**Ответ:**
```json
[
  {
    "id": "456e7890-e89b-12d3-a456-426614174001",
    "product_id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "product_photo.jpg",
    "file_path": "/app/uploads/products/123e4567-e89b-12d3-a456-426614174000/photo_123.jpg",
    "priority": 1
  }
]
```

### 3. Обновление фотографии

**PUT** `/api/v1/photos/{photo_id}`

**Тело запроса:**
```json
{
  "name": "new_name.jpg",
  "priority": 2
}
```

### 4. Удаление фотографии

**DELETE** `/api/v1/photos/{photo_id}`

## Workflow для фронтенда

### Создание товара с фотографиями:

1. **Создать товар** через `POST /api/v1/products/`
2. **Получить ID созданного товара** из ответа
3. **Загрузить фотографии** через `POST /api/v1/photos/upload-photo` с полученным `product_id`
4. **При необходимости обновить приоритеты** фотографий

### Редактирование товара:

1. **Обновить данные товара** через `PUT /api/v1/products/{product_id}`
2. **При необходимости добавить новые фотографии** через `POST /api/v1/photos/upload-photo`
3. **При необходимости удалить старые фотографии** через `DELETE /api/v1/photos/{photo_id}`
4. **При необходимости изменить приоритеты** через `PUT /api/v1/photos/{photo_id}`

## Ограничения файлов

- **Поддерживаемые форматы:** JPG, JPEG, PNG, WEBP
- **Максимальный размер:** 10MB
- **Приоритеты:** 0-2 (0 - обычная, 1 - важная, 2 - главная)

## Доступ к загруженным файлам

Загруженные файлы доступны по URL:
```
GET /app/uploads/products/{product_id}/{filename}
```

## Пример полного workflow на JavaScript:

```javascript
// 1. Создание товара
const productData = {
  name: "Худи SOUTH CLUB",
  color: "Черный",
  composition: "80% хлопок, 20% полиэстер",
  print_technology: "Вышивка",
  size: [1, 2, 3],
  price: 4500,
  order_number: 1,
  soon: false
};

const productResponse = await fetch('/api/v1/products/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(productData)
});

const product = await productResponse.json();
const productId = product.id;

// 2. Загрузка фотографий
const photos = [file1, file2, file3]; // массив файлов
const uploadedPhotos = [];

for (let i = 0; i < photos.length; i++) {
  const formData = new FormData();
  formData.append('photo', photos[i]);
  
  const photoResponse = await fetch(`/api/v1/photos/upload-photo?product_id=${productId}&priority=${i}`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  
  const uploadedPhoto = await photoResponse.json();
  uploadedPhotos.push(uploadedPhoto);
}

console.log('Товар создан:', product);
console.log('Фотографии загружены:', uploadedPhotos);
```

## Коды ошибок

- **400 Bad Request** - Неверный формат файла или превышен размер
- **401 Unauthorized** - Отсутствует или неверный JWT токен
- **404 Not Found** - Товар или фотография не найдены
- **422 Unprocessable Entity** - Ошибка валидации данных
- **500 Internal Server Error** - Внутренняя ошибка сервера

## Примечания

- Все операции с фотографиями требуют аутентификации админа
- Фотографии автоматически сохраняются в папку `/app/uploads/products/{product_id}/`
- При удалении товара все связанные фотографии также удаляются (каскадное удаление)
- Рекомендуется загружать фотографии в порядке приоритета (0, 1, 2)
