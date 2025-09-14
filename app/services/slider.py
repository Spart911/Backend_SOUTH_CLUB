from typing import List
from sqlalchemy.orm import Session
from ..repositories.slider import SliderPhotoRepository
from ..schemas.slider import SliderPhotoCreate, SliderPhotoUpdate, SliderPhotoResponse, SliderListResponse


class SliderService:
    """
    Сервис для работы с фотографиями слайдера
    """
    
    def __init__(self):
        self.repository = SliderPhotoRepository()
    
    def get_slider_photos(self, db: Session) -> SliderListResponse:
        """
        Получить все фотографии слайдера
        """
        photos = self.repository.get_ordered(db)
        return SliderListResponse(
            photos=[SliderPhotoResponse.model_validate(photo) for photo in photos],
            total=len(photos)
        )
    
    def get_slider_photo(self, db: Session, photo_id: str) -> SliderPhotoResponse:
        """
        Получить фотографию слайдера по ID
        """
        photo = self.repository.get(db, photo_id)
        if not photo:
            from ..core.exceptions import SliderPhotoNotFoundException
            raise SliderPhotoNotFoundException(str(photo_id))
        return SliderPhotoResponse.model_validate(photo)
    
    def create_slider_photo(self, db: Session, photo_data: SliderPhotoCreate) -> SliderPhotoResponse:
        """
        Создать новую фотографию слайдера
        """
        from ..core.logging import get_logger
        logger = get_logger("SliderService")
        
        logger.info(f"Создание фотографии слайдера: {photo_data.name}")
        try:
            photo = self.repository.create(db, photo_data)
            logger.info(f"Фотография слайдера успешно создана с ID: {photo.id}")
            return SliderPhotoResponse.model_validate(photo)
        except Exception as e:
            logger.error(f"Ошибка при создании фотографии слайдера: {str(e)}")
            raise
    
    def update_slider_photo(self, db: Session, photo_id: str, photo_data: SliderPhotoUpdate) -> SliderPhotoResponse:
        """
        Обновить фотографию слайдера
        """
        photo = self.repository.update(db, photo_id, photo_data)
        if not photo:
            from ..core.exceptions import SliderPhotoNotFoundException
            raise SliderPhotoNotFoundException(str(photo_id))
        return SliderPhotoResponse.model_validate(photo)
    
    def delete_slider_photo(self, db: Session, photo_id: str) -> bool:
        """
        Удалить фотографию слайдера
        """
        photo = self.repository.get(db, photo_id)
        if not photo:
            from ..core.exceptions import SliderPhotoNotFoundException
            raise SliderPhotoNotFoundException(str(photo_id))
        return self.repository.delete(db, photo_id)
