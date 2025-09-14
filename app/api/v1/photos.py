from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Path, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ...dependencies import get_db_session, get_current_admin
from ...services.file_service import FileService
from ...schemas.photo import (
    ProductPhotoCreate,
    ProductPhotoUpdate,
    ProductPhotoResponse,
    ProductPhotoUpload
)
from ...repositories.photo import ProductPhotoRepository
from ...core.logging import get_logger

router = APIRouter(prefix="/photos", tags=["Фотографии товаров"])
file_service = FileService()
photo_repo = ProductPhotoRepository()
logger = get_logger("PhotosAPI")


@router.post("/upload-photo/", response_model=ProductPhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_product_photo(
    product_id: UUID = Query(..., description="ID товара"),
    photo: UploadFile = File(...),
    priority: int = Query(0, ge=0, le=2, description="Приоритет фотографии (0-2)"),
    db: Session = Depends(get_db_session),
    current_admin: str = Depends(get_current_admin)
):
    """
    Загрузить фотографию для товара (требует аутентификации)
    """
    logger.info(f"Загрузка фотографии для товара {product_id} от админа {current_admin}")
    
    try:
        # Валидация файла
        file_service.validate_file(photo)
        
        # Сохранение файла
        file_path = file_service.save_product_photo(photo, str(product_id))
        
        # Создание записи в БД
        from ...models.photo import ProductPhoto
        obj = ProductPhoto(
            product_id=product_id,
            name=photo.filename or "unnamed",
            file_path=file_path,
            priority=priority
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)

        logger.info(f"Фотография {photo.filename} успешно загружена для товара {product_id}")

        return ProductPhotoResponse.model_validate(obj)
    except Exception as e:
        logger.error(f"Ошибка при загрузке фотографии для товара {product_id}: {str(e)}")
        raise


@router.get("/product/{product_id}", response_model=List[ProductPhotoResponse])
async def get_product_photos(
    product_id: UUID,
    db: Session = Depends(get_db_session)
):
    """
    Получить все фотографии товара
    """
    logger.info(f"Запрос фотографий для товара {product_id}")
    
    try:
        photos = photo_repo.get_by_product_id(db, product_id)
        logger.info(f"Возвращено {len(photos)} фотографий для товара {product_id}")
        return [ProductPhotoResponse.model_validate(p) for p in photos]
    except Exception as e:
        logger.error(f"Ошибка при получении фотографий товара {product_id}: {str(e)}")
        raise


@router.get("/{photo_id}", response_model=ProductPhotoResponse)
async def get_product_photo(
    photo_id: UUID,
    db: Session = Depends(get_db_session)
):
    """
    Получить фотографию по ID
    """
    logger.info(f"Запрос фотографии {photo_id}")
    
    try:
        from sqlalchemy import select
        from ...models.photo import ProductPhoto
        stmt = select(ProductPhoto).where(ProductPhoto.id == photo_id)
        res = db.execute(stmt).scalar_one_or_none()
        if not res:
            logger.warning(f"Фотография {photo_id} не найдена")
            raise HTTPException(status_code=404, detail="Фотография не найдена")
        return ProductPhotoResponse.model_validate(res)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении фотографии {photo_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.put("/{photo_id}", response_model=ProductPhotoResponse)
async def update_product_photo(
    photo_id: UUID,
    photo_data: ProductPhotoUpdate,
    db: Session = Depends(get_db_session),
    current_admin: str = Depends(get_current_admin)
):
    """
    Обновить фотографию товара (требует аутентификации)
    """
    logger.info(f"Обновление фотографии {photo_id} админом {current_admin}")
    
    try:
        from sqlalchemy import select
        from ...models.photo import ProductPhoto
        stmt = select(ProductPhoto).where(ProductPhoto.id == photo_id)
        obj = db.execute(stmt).scalar_one_or_none()
        if not obj:
            logger.warning(f"Фотография {photo_id} не найдена для обновления")
            raise HTTPException(status_code=404, detail="Фотография не найдена")
        if photo_data.name is not None:
            obj.name = photo_data.name
        if photo_data.priority is not None:
            obj.priority = photo_data.priority
        db.commit()
        db.refresh(obj)
        return ProductPhotoResponse.model_validate(obj)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении фотографии {photo_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_photo(
    photo_id: UUID,
    db: Session = Depends(get_db_session),
    current_admin: str = Depends(get_current_admin)
):
    """
    Удалить фотографию товара (требует аутентификации)
    """
    logger.info(f"Удаление фотографии {photo_id} админом {current_admin}")
    
    try:
        from sqlalchemy import select
        from ...models.photo import ProductPhoto
        stmt = select(ProductPhoto).where(ProductPhoto.id == photo_id)
        obj = db.execute(stmt).scalar_one_or_none()
        if not obj:
            logger.warning(f"Фотография {photo_id} не найдена для удаления")
            raise HTTPException(status_code=404, detail="Фотография не найдена")
        # Удаляем файл с диска (мягко)
        file_service.delete_file(obj.file_path)
        # Удаляем запись
        db.delete(obj)
        db.commit()
        return
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при удалении фотографии {photo_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
