import os
import uuid
from typing import Optional
from fastapi import UploadFile
from PIL import Image
from ..config import settings
from ..core.exceptions import InvalidFileTypeException, FileSizeExceededException
from ..core.logging import get_logger


class FileService:
    """
    Сервис для работы с файлами
    """
    
    ALLOWED_IMAGE_TYPES = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg", 
        "image/png": ".png",
        "image/webp": ".webp"
    }
    
    def __init__(self):
        self.upload_dir = settings.upload_dir
        self.logger = get_logger("FileService")
    
    def validate_file(self, file: UploadFile) -> None:
        """
        Валидация загружаемого файла
        """
        # Определяем размер файла безопасно (у UploadFile нет гарантированного поля size)
        try:
            current_pos = file.file.tell()
        except Exception:
            current_pos = None
        try:
            file.file.seek(0, os.SEEK_END)
            detected_size = file.file.tell()
        except Exception:
            detected_size = None
        finally:
            try:
                if current_pos is not None:
                    file.file.seek(current_pos, os.SEEK_SET)
            except Exception:
                pass

        self.logger.info(f"Валидация файла: {file.filename}, тип: {file.content_type}, размер: {detected_size}")
        
        # Проверка типа файла
        if not file.content_type or file.content_type not in self.ALLOWED_IMAGE_TYPES:
            self.logger.warning(f"Недопустимый тип файла: {file.content_type}")
            raise InvalidFileTypeException(file.content_type or "unknown")
        
        # Проверка размера файла
        if detected_size is not None and detected_size > settings.max_file_size:
            self.logger.warning(f"Файл превышает максимальный размер: {detected_size} > {settings.max_file_size}")
            raise FileSizeExceededException(settings.max_file_size)
        
        # Проверка имени файла на безопасность
        if file.filename:
            # Проверяем расширение файла
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                self.logger.warning(f"Недопустимое расширение файла: {file_ext}")
                raise InvalidFileTypeException(f"Недопустимое расширение файла: {file_ext}")
            
            # Проверяем имя файла на path traversal
            if '..' in file.filename or '/' in file.filename or '\\' in file.filename:
                self.logger.warning(f"Попытка path traversal в имени файла: {file.filename}")
                raise InvalidFileTypeException("Недопустимое имя файла")
        
        self.logger.info(f"Файл {file.filename} успешно валидирован")
    
    def save_product_photo(self, file: UploadFile, product_id: str) -> str:
        """
        Сохранить фотографию товара
        """
        self.validate_file(file)
        
        # Создаем уникальное имя файла
        file_extension = self.ALLOWED_IMAGE_TYPES[file.content_type]
        filename = f"{uuid.uuid4()}{file_extension}"
        
        # Путь для сохранения
        product_upload_dir = os.path.join(self.upload_dir, "products")
        file_path = os.path.join(product_upload_dir, filename)
        
        # Проверяем безопасность пути
        if not os.path.abspath(file_path).startswith(os.path.abspath(product_upload_dir)):
            raise InvalidFileTypeException("Недопустимый путь для сохранения файла")
        
        # Создаем директорию если её нет
        os.makedirs(product_upload_dir, exist_ok=True)
        
        # Сохраняем файл
        try:
            with open(file_path, "wb") as buffer:
                content = file.file.read()
                buffer.write(content)
            self.logger.info(f"Файл {filename} успешно сохранен для товара {product_id}")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении файла {filename}: {str(e)}")
            raise InvalidFileTypeException(f"Ошибка при сохранении файла: {str(e)}")
        
        # Возвращаем абсолютный путь
        return os.path.abspath(file_path)
    
    def save_slider_photo(self, file: UploadFile) -> str:
        """
        Сохранить фотографию слайдера
        """
        self.validate_file(file)
        
        # Создаем уникальное имя файла
        file_extension = self.ALLOWED_IMAGE_TYPES[file.content_type]
        filename = f"{uuid.uuid4()}{file_extension}"
        
        # Путь для сохранения
        slider_upload_dir = os.path.join(self.upload_dir, "slider")
        file_path = os.path.join(slider_upload_dir, filename)
        
        # Проверяем безопасность пути
        if not os.path.abspath(file_path).startswith(os.path.abspath(slider_upload_dir)):
            raise InvalidFileTypeException("Недопустимый путь для сохранения файла")
        
        # Создаем директорию если её нет
        os.makedirs(slider_upload_dir, exist_ok=True)
        
        # Сохраняем файл
        try:
            with open(file_path, "wb") as buffer:
                content = file.file.read()
                buffer.write(content)
            self.logger.info(f"Файл {filename} успешно сохранен для слайдера")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении файла {filename}: {str(e)}")
            raise InvalidFileTypeException(f"Ошибка при сохранении файла: {str(e)}")
        
        # Возвращаем абсолютный путь
        return os.path.abspath(file_path)
    
    def delete_file(self, file_path: str) -> bool:
        """
        Удалить файл
        """
        try:
            # Проверяем безопасность пути
            if not file_path or not os.path.exists(file_path):
                self.logger.warning(f"Попытка удаления несуществующего файла: {file_path}")
                return False
            
            # Проверяем что файл находится в разрешенной директории
            upload_dir_abs = os.path.abspath(self.upload_dir)
            file_path_abs = os.path.abspath(file_path)
            
            if not file_path_abs.startswith(upload_dir_abs):
                self.logger.warning(f"Попытка удаления файла вне разрешенной директории: {file_path}")
                return False
            
            os.remove(file_path)
            self.logger.info(f"Файл {file_path} успешно удален")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при удалении файла {file_path}: {str(e)}")
            return False
    
    def optimize_image(self, file_path: str, max_size: tuple = (1920, 1080)) -> None:
        """
        Оптимизировать изображение
        """
        try:
            with Image.open(file_path) as img:
                # Изменяем размер если изображение слишком большое
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    img.save(file_path, quality=85, optimize=True)
                    self.logger.info(f"Изображение {file_path} оптимизировано до размера {max_size}")
        except Exception as e:
            self.logger.warning(f"Не удалось оптимизировать изображение {file_path}: {str(e)}")
            # Если не удалось оптимизировать, оставляем как есть
            pass
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Получить информацию о файле
        """
        if not os.path.exists(file_path):
            self.logger.warning(f"Попытка получить информацию о несуществующем файле: {file_path}")
            return None
        
        try:
            stat = os.stat(file_path)
            with Image.open(file_path) as img:
                info = {
                    "size": stat.st_size,
                    "width": img.size[0],
                    "height": img.size[1],
                    "format": img.format,
                    "mode": img.mode
                }
                self.logger.debug(f"Получена информация о файле {file_path}: {info}")
                return info
        except Exception as e:
            self.logger.error(f"Ошибка при получении информации о файле {file_path}: {str(e)}")
            return None
