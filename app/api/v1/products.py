from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from ...dependencies import get_db_session, get_current_admin
from ...services.product import ProductService
from ...schemas.product import (
    ProductCreate, 
    ProductUpdate, 
    ProductResponse, 
    ProductListResponse
)
from ...core.logging import get_logger

router = APIRouter(prefix="/products", tags=["Товары"])
product_service = ProductService()
logger = get_logger("ProductsAPI")


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать товар",
    description="Создает новый товар. Поле size — массив чисел (0-4). Требуется авторизация админа."
)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db_session),
    current_admin: str = Depends(get_current_admin)
):
    """
    Создать новый товар (требует аутентификации)
    """
    logger.info(f"Создание товара '{product_data.name}' админом {current_admin}")
    
    try:
        result = product_service.create_product(db, product_data)
        logger.info(f"Товар '{product_data.name}' успешно создан с ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"Ошибка при создании товара '{product_data.name}': {str(e)}")
        raise


@router.get(
    "/",
    response_model=ProductListResponse,
    summary="Список товаров",
    description="Возвращает список товаров с пагинацией. Поле size — массив чисел (0-4)."
)
async def get_products(
    skip: int = Query(0, ge=0, description="Количество пропущенных записей"),
    limit: int = Query(100, ge=1, le=1000, description="Количество записей")
):
    """
    Получить список товаров с пагинацией
    """
    logger.info(f"Запрос списка товаров: skip={skip}, limit={limit}")
    
    try:
        # Получаем сессию БД напрямую
        from ...database import SessionLocal
        db = SessionLocal()
        try:
            result = product_service.get_products(db, skip, limit)
            logger.info(f"Возвращено {len(result.products)} товаров")
            return result
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Ошибка при получении списка товаров: {str(e)}")
        raise


# @router.get("/{product_id}", response_model=ProductResponse)
# async def get_product(
#     product_id: UUID,
#     db: Session = Depends(get_db_session)
# ):
#     """
#     Получить товар по ID
#     """
#     return product_service.get_product(db, product_id)


# @router.put("/{product_id}", response_model=ProductResponse)
# async def update_product(
#     product_id: UUID,
#     product_data: ProductUpdate,
#     db: Session = Depends(get_db_session),
#     current_admin: str = Depends(get_current_admin)
# ):
#     """
#     Обновить товар (требует аутентификации)
#     """
#     return product_service.update_product(db, product_id, product_data)


# @router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_product(
#     product_id: UUID,
#     db: Session = Depends(get_db_session),
#     current_admin: str = Depends(get_current_admin)
# ):
#     """
#     Удалить товар (требует аутентификации)
#     """
#     product_service.delete_product(db, product_id)


@router.get(
    "/search/",
    response_model=ProductListResponse,
    summary="Поиск товаров",
    description="Поиск по названию и цвету."
)
async def search_products(
    q: str = Query(..., min_length=1, description="Поисковый запрос"),
    skip: int = Query(0, ge=0, description="Количество пропущенных записей"),
    limit: int = Query(100, ge=1, le=1000, description="Количество записей"),
    db: Session = Depends(get_db_session)
):
    """
    Поиск товаров по названию, характеристикам или цвету
    """
    logger.info(f"Поиск товаров: query='{q}', skip={skip}, limit={limit}")
    
    try:
        result = product_service.search_products(db, q, skip, limit)
        logger.info(f"Поиск по '{q}' вернул {len(result.products)} товаров")
        return result
    except Exception as e:
        logger.error(f"Ошибка при поиске товаров по '{q}': {str(e)}")
        raise


@router.get(
    "/size/{size}",
    response_model=ProductListResponse,
    summary="Товары по размеру",
    description="Возвращает товары, содержащие указанный размер в массиве size."
)
async def get_products_by_size(
    size: int = Path(..., ge=0, le=4, description="Размер товара"),
    skip: int = Query(0, ge=0, description="Количество пропущенных записей"),
    limit: int = Query(100, ge=1, le=1000, description="Количество записей"),
    db: Session = Depends(get_db_session)
):
    """
    Получить товары по размеру
    """
    logger.info(f"Запрос товаров по размеру {size}: skip={skip}, limit={limit}")
    
    try:
        result = product_service.get_products_by_size(db, size, skip, limit)
        logger.info(f"Возвращено {len(result.products)} товаров размера {size}")
        return result
    except Exception as e:
        logger.error(f"Ошибка при получении товаров размера {size}: {str(e)}")
        raise


@router.get(
    "/price/range",
    response_model=ProductListResponse,
    summary="Товары по диапазону цен",
    description="Возвращает товары в заданном диапазоне цен."
)
async def get_products_by_price_range(
    min_price: int = Query(..., ge=0, description="Минимальная цена"),
    max_price: int = Query(..., ge=0, description="Максимальная цена"),
    skip: int = Query(0, ge=0, description="Количество пропущенных записей"),
    limit: int = Query(100, ge=1, le=1000, description="Количество записей"),
    db: Session = Depends(get_db_session)
):
    """
    Получить товары по диапазону цен
    """
    logger.info(f"Запрос товаров по цене: {min_price}-{max_price}, skip={skip}, limit={limit}")
    
    if min_price > max_price:
        logger.warning(f"Некорректный диапазон цен: min_price={min_price} > max_price={max_price}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Минимальная цена не может быть больше максимальной"
        )
    
    try:
        result = product_service.get_products_by_price_range(db, min_price, max_price, skip, limit)
        logger.info(f"Возвращено {len(result.products)} товаров в диапазоне цен {min_price}-{max_price}")
        return result
    except Exception as e:
        logger.error(f"Ошибка при получении товаров по диапазону цен {min_price}-{max_price}: {str(e)}")
        raise


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Получить товар",
    description="Возвращает товар по ID."
)
async def get_product(
    product_id: UUID,
    db: Session = Depends(get_db_session)
):
    """
    Получить товар по ID
    """
    logger.info(f"Запрос товара по ID: {product_id}")
    
    try:
        result = product_service.get_product(db, product_id)
        logger.info(f"Товар {product_id} успешно найден")
        return result
    except Exception as e:
        logger.error(f"Ошибка при получении товара {product_id}: {str(e)}")
        raise


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Обновить товар",
    description="Обновляет товар. Поле size — массив чисел (0-4). Требуется авторизация админа."
)
async def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    db: Session = Depends(get_db_session),
    current_admin: str = Depends(get_current_admin)
):
    """
    Обновить товар (требует аутентификации)
    """
    logger.info(f"Обновление товара {product_id} админом {current_admin}")
    
    try:
        result = product_service.update_product(db, product_id, product_data)
        logger.info(f"Товар {product_id} успешно обновлен")
        return result
    except Exception as e:
        logger.error(f"Ошибка при обновлении товара {product_id}: {str(e)}")
        raise


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить товар",
    description="Удаляет товар по ID. Требуется авторизация админа."
)
async def delete_product(
    product_id: UUID,
    current_admin: str = Depends(get_current_admin)
):
    """
    Удалить товар (требует аутентификации)
    """
    logger.info(f"Удаление товара {product_id} админом {current_admin}")
    
    try:
        # Локально открываем сессию, чтобы исключить проблемы с Depends
        from ...database import SessionLocal
        db = SessionLocal()
        try:
            product_service.delete_product(db, product_id)
            logger.info(f"Товар {product_id} успешно удален")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Ошибка при удалении товара {product_id}: {str(e)}")
        raise
