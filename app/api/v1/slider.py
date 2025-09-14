from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Path, Query, Request, Form
import uuid
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ...dependencies import get_db_session, get_current_admin
from ...services.file_service import FileService
from ...services.slider import SliderService
from ...schemas.slider import (
    SliderPhotoCreate, 
    SliderPhotoUpdate, 
    SliderPhotoResponse, 
    SliderPhotoUpload,
    SliderListResponse,
    SliderPhotoSimple
)
from ...core.logging import get_logger

router = APIRouter(prefix="/slider", tags=["Слайдер"])
file_service = FileService()
slider_service = SliderService()
logger = get_logger("SliderAPI")

# Имя файла манифеста порядков
_SLIDER_MANIFEST_NAME = "_manifest.json"

def _slider_dir_path() -> Path:
    from pathlib import Path
    return Path("/app/uploads/slider")

def _manifest_path() -> Path:
    return _slider_dir_path() / _SLIDER_MANIFEST_NAME

def _read_manifest() -> dict:
    import json
    path = _manifest_path()
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def _write_manifest(data: dict) -> None:
    import json, os
    path = _manifest_path()
    os.makedirs(path.parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def _reindex_orders() -> None:
    """Пересобирает порядковые номера подряд начиная с 0 на основе текущего манифеста и существующих файлов."""
    manifest = _read_manifest()
    files = _iter_slider_files()
    existing_names = {p.name for p in files}
    # Оставляем только те записи, для которых есть физические файлы
    filtered = {fname: manifest[fname] for fname in existing_names if fname in manifest}
    # Сортируем по order (учитываем старый формат int и новый dict)
    def _order_of(v):
        if isinstance(v, dict):
            return int(v.get("order", 0))
        return int(v or 0)
    ordered_items = sorted(filtered.items(), key=lambda kv: _order_of(kv[1]))
    # Присваиваем новые порядковые без дырок
    new_manifest = manifest.copy()
    for idx, (fname, meta) in enumerate(ordered_items):
        if isinstance(meta, dict):
            meta["order"] = idx
            new_manifest[fname] = meta
        else:
            new_manifest[fname] = idx
    _write_manifest(new_manifest)

def _iter_slider_files():
    d = _slider_dir_path()
    if not d.exists():
        return []
    return [p for p in d.iterdir() if p.is_file() and p.suffix.lower() in [".jpg", ".jpeg", ".png", ".gif", ".webp"]]

def _split_prefixed_name(filename: str) -> tuple:
    # Возвращает (order_prefix:int|None, rest_name:str)
    if "_" in filename:
        first, rest = filename.split("_", 1)
        try:
            return int(first), rest
        except ValueError:
            return None, filename
    return None, filename

def _build_list_item(request: Request, file_path: Path, mval) -> SliderPhotoSimple:
    from uuid import UUID, uuid5, NAMESPACE_URL
    if isinstance(mval, dict):
        order_number = int(mval.get("order", 0))
        pid = mval.get("id")
    else:
        order_number = int(mval or 0)
        pid = None
    file_url = str(request.base_url).rstrip('/') + f"/app/uploads/slider/{file_path.name}"
    _, rest_name = _split_prefixed_name(file_path.name)
    photo_uuid = UUID(pid) if pid else uuid5(NAMESPACE_URL, file_path.name)
    return SliderPhotoSimple(
        id=photo_uuid,
        name=rest_name,
        file_path=file_url,
        order_number=order_number,
    )

def _find_file_by_id(photo_id: UUID) -> tuple:
    """Возвращает (Path|None, manifest_value|None). Учитывает id в манифесте и детерминированный uuid5."""
    from uuid import uuid5, NAMESPACE_URL
    manifest = _read_manifest()
    files = _iter_slider_files()
    # Сначала ищем по манифесту
    for fname, mval in manifest.items():
        if isinstance(mval, dict) and mval.get("id") == str(photo_id):
            p = _slider_dir_path() / fname
            if p.exists():
                return p, mval
    # Ищем по uuid5 от имени файла
    for p in files:
        # полное имя с префиксом
        if uuid5(NAMESPACE_URL, p.name) == photo_id:
            return p, manifest.get(p.name)
        # имя без префикса порядка
        _prefix, rest = _split_prefixed_name(p.name)
        if uuid5(NAMESPACE_URL, rest) == photo_id:
            return p, manifest.get(p.name)
    return None, None


@router.post(
    "/upload",
    response_model=SliderPhotoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Загрузить фото слайдера",
    description="Загружает файл изображения. Метаданные (id, name, order_number) сохраняются в манифесте. Требуется авторизация админа."
)
@router.post(
    "/upload/",
    response_model=SliderPhotoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Загрузить фото слайдера (со слешем)",
    description="Alias для совместимости с фронтом."
)
async def upload_slider_photo(
    photo: UploadFile = File(...),
    # Принимаем order_number из multipart/form-data (а не из query)
    order_number: int = Form(0, ge=0, description="Порядковый номер фотографии"),
    current_admin: str = Depends(get_current_admin)
):
    """
    Загрузить фотографию для слайдера (требует аутентификации)
    """
    logger.info(f"Загрузка фотографии для слайдера от админа {current_admin}")
    
    try:
        # Валидация файла
        file_service.validate_file(photo)

        # Сохранение файла (без префикса порядка в имени)
        file_path = file_service.save_slider_photo(photo)
        logger.info(f"Файл сохранен: {file_path}")

        # Имя файла и ID должны быть определены до записи манифеста и формирования ответа
        import os as _os
        file_name = _os.path.basename(file_path)
        photo_id = uuid.uuid4()

        # Сохраняем order_number в манифест, чтобы GET мог вернуть корректный порядок
        try:
            manifest = _read_manifest()
            # Храним расширенную информацию (обратная совместимость учитывается при чтении)
            manifest[file_name] = {"order": int(order_number), "id": str(photo_id), "name": (photo.filename or "unnamed")}
            _write_manifest(manifest)
        except Exception as e:
            logger.warning(f"Не удалось записать манифест порядка: {str(e)}")

        # Возвращаем информацию о загруженном файле (абсолютный URL)
        logger.info(f"Фотография {photo.filename} успешно загружена для слайдера с порядковым номером {order_number}")
        # Абсолютный путь в рамках сервера статики
        absolute_path = f"/app/uploads/slider/{file_name}"
        return SliderPhotoResponse(
            id=photo_id,
            name=photo.filename or "unnamed",
            file_path=absolute_path,
            order_number=order_number
        )
    except Exception as e:
        logger.error(f"Ошибка при загрузке фотографии для слайдера: {str(e)}")
        raise


@router.get(
    "/",
    response_model=SliderListResponse,
    summary="Список фото слайдера",
    description="Возвращает файлы из каталога /app/uploads/slider с данными из манифеста: id, name, order_number."
)
async def get_slider_photos(request: Request):
    """
    Получить все фотографии слайдера
    """
    logger.info("Запрос фотографий слайдера")
    
    try:
        import os
        from pathlib import Path
        
        # Путь к папке с фотографиями слайдера (файловая система)
        slider_dir = Path("/app/uploads/slider")
        
        photos = []
        logger.info(f"Проверка папки: {slider_dir}")
        logger.info(f"Папка существует: {slider_dir.exists()}")
        
        if slider_dir.exists():
            # Получаем все файлы из папки слайдера
            files = list(slider_dir.iterdir())
            manifest = _read_manifest()
            logger.info(f"Найдено файлов в папке: {len(files)}")
            
            for file_path in files:
                logger.info(f"Проверка файла: {file_path.name}, расширение: {file_path.suffix}")
                if file_path.is_file() and file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    # Читаем order_number из манифеста; если нет — 0
                    mval = manifest.get(file_path.name, 0)
                    if isinstance(mval, dict):
                        order_number = int(mval.get("order", 0))
                    else:
                        order_number = int(mval)
                    logger.info(f"Добавление файла: {file_path.name}")
                    
                    # Абсолютный URL для отдачи через статику
                    file_url = str(request.base_url).rstrip('/') + f"/app/uploads/slider/{file_path.name}"
                    # Имя отображаемое — из манифеста, иначе имя файла БЕЗ префикса порядка
                    from uuid import UUID, uuid5, NAMESPACE_URL
                    if isinstance(mval, dict) and mval.get("name"):
                        original_name = mval.get("name")
                    else:
                        _pref, original_name = _split_prefixed_name(file_path.name)
                    # id из манифеста (если нет — детерминированный uuid5 от имени файла)
                    pid = mval.get("id") if isinstance(mval, dict) else None
                    photo_uuid = UUID(pid) if pid else uuid5(NAMESPACE_URL, file_path.name)
                    photos.append(SliderPhotoSimple(
                        id=photo_uuid,
                        name=original_name,
                        file_path=file_url,
                        order_number=order_number
                    ))
            
            # Сортируем по порядковому номеру, затем по имени
            photos.sort(key=lambda x: (x.order_number, x.file_path))
        
        logger.info(f"Возвращено {len(photos)} фотографий слайдера")
        return SliderListResponse(photos=photos, total=len(photos))
    except Exception as e:
        logger.error(f"Ошибка при получении фотографий слайдера: {str(e)}")
        raise


@router.get(
    "/{photo_id}",
    response_model=SliderPhotoResponse,
    summary="Получить фото слайдера",
    description="Возвращает фото по ID. Ищет по манифесту и детерминированному uuid5 от имени файла."
)
async def get_slider_photo(
    photo_id: UUID,
    db: Session = Depends(get_db_session)
):
    """
    Получить фотографию слайдера по ID
    """
    logger.info(f"Запрос фотографии слайдера {photo_id}")
    
    try:
        p, mval = _find_file_by_id(photo_id)
        if not p:
            logger.warning(f"Фотография слайдера {photo_id} не найдена")
            raise HTTPException(status_code=404, detail="Фотография слайдера не найдена")
        # Формируем ответ
        order_number = 0
        if isinstance(mval, dict):
            order_number = int(mval.get("order", 0))
        elif isinstance(mval, int):
            order_number = mval
        # Имя без префикса
        _, rest_name = _split_prefixed_name(p.name)
        return SliderPhotoResponse(
            id=photo_id,
            name=rest_name,
            file_path=f"/app/uploads/slider/{p.name}",
            order_number=order_number,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении фотографии слайдера {photo_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.put(
    "/{photo_id}",
    response_model=SliderPhotoResponse,
    summary="Обновить фото слайдера",
    description="Обновляет name и/или order_number в манифесте. Файл не переименовывается. Требуется авторизация админа."
)
async def update_slider_photo(
    photo_id: UUID,
    photo_data: SliderPhotoUpdate,
    db: Session = Depends(get_db_session),
    current_admin: str = Depends(get_current_admin)
):
    """
    Обновить фотографию слайдера (требует аутентификации)
    """
    logger.info(f"Обновление фотографии слайдера {photo_id} админом {current_admin}")
    
    try:
        p, mval = _find_file_by_id(photo_id)
        if not p:
            logger.warning(f"Фотография слайдера {photo_id} не найдена для обновления")
            raise HTTPException(status_code=404, detail="Фотография слайдера не найдена")
        # Обновляем только meta в манифесте (физический файл не переименовываем)
        manifest = _read_manifest()
        mentry = manifest.get(p.name, {}) if isinstance(manifest.get(p.name, {}), dict) else {"order": manifest.get(p.name, 0)}
        if photo_data.name is not None and photo_data.name.strip():
            safe_name = photo_data.name.strip()
            # гарантируем расширение как у файла, если не указано
            from pathlib import Path as _P
            if _P(safe_name).suffix.lower() != p.suffix.lower():
                safe_name = safe_name + p.suffix.lower()
            mentry["name"] = safe_name
        # Обновление порядка в манифесте
        if photo_data.order_number is not None:
            mentry["order"] = int(photo_data.order_number)
        manifest[p.name] = mentry
        _write_manifest(manifest)
        # Ответ
        current_m = _read_manifest().get(p.name, {})
        current_order = int(current_m.get("order", 0)) if isinstance(current_m, dict) else int(current_m or 0)
        rest_name = current_m.get("name") if isinstance(current_m, dict) and current_m.get("name") else p.name
        return SliderPhotoResponse(
            id=photo_id,
            name=rest_name,
            file_path=f"/app/uploads/slider/{p.name}",
            order_number=current_order,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении фотографии слайдера {photo_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.delete(
    "/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить фото слайдера",
    description="Удаляет файл и запись в манифесте. После удаления пересобирает order_number без пропусков. Требуется авторизация админа."
)
async def delete_slider_photo(
    photo_id: UUID,
    db: Session = Depends(get_db_session),
    current_admin: str = Depends(get_current_admin)
):
    """
    Удалить фотографию слайдера (требует аутентификации)
    """
    logger.info(f"Удаление фотографии слайдера {photo_id} админом {current_admin}")
    
    try:
        p, mval = _find_file_by_id(photo_id)
        if not p:
            logger.warning(f"Фотография слайдера {photo_id} не найдена для удаления")
            raise HTTPException(status_code=404, detail="Фотография слайдера не найдена")
        # Удаляем файл
        try:
            p.unlink(missing_ok=True)
        except TypeError:
            # Python <3.8 совместимость
            if p.exists():
                p.unlink()
        # Удаляем запись из манифеста
        manifest = _read_manifest()
        if p.name in manifest:
            manifest.pop(p.name, None)
            _write_manifest(manifest)
        # Пересоберём порядковые номера, чтобы не было дырок
        try:
            _reindex_orders()
        except Exception as e:
            logger.warning(f"Не удалось переиндексировать порядок после удаления: {str(e)}")
        return
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при удалении фотографии слайдера {photo_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.put("/{photo_id}/order", response_model=SliderPhotoResponse)
async def update_slider_photo_order(
    photo_id: UUID,
    order_number: int = Query(..., ge=0, description="Новый порядковый номер"),
    db: Session = Depends(get_db_session),
    current_admin: str = Depends(get_current_admin)
):
    """
    Изменить порядок фотографии в слайдере (требует аутентификации)
    """
    logger.info(f"Изменение порядка фотографии слайдера {photo_id} на {order_number} админом {current_admin}")
    
    try:
        # TODO: Добавить логику обновления порядка в БД через сервис
        logger.warning(f"Фотография слайдера {photo_id} не найдена для изменения порядка")
        raise HTTPException(status_code=404, detail="Фотография слайдера не найдена")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при изменении порядка фотографии слайдера {photo_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
