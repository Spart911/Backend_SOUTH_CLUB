from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from uuid import UUID
from ..database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Базовый репозиторий с общими CRUD операциями
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get(self, db: Session, id: UUID) -> Optional[ModelType]:
        """
        Получить объект по ID
        """
        return db.get(self.model, id)
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Получить все объекты с пагинацией
        """
        stmt = select(self.model).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()
    
    def create(self, db: Session, obj_in: Any) -> ModelType:
        """
        Создать новый объект
        """
        # Поддержка Pydantic v2
        if hasattr(obj_in, 'model_dump'):
            obj_data = obj_in.model_dump()
        else:
            obj_data = obj_in.dict()
        
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, id: UUID, obj_in: Any) -> Optional[ModelType]:
        """
        Обновить объект
        """
        db_obj = self.get(db, id)
        if db_obj:
            update_data = obj_in.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: UUID) -> bool:
        """
        Удалить объект
        """
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False
    
    def count(self, db: Session) -> int:
        """
        Подсчитать общее количество объектов
        """
        stmt = select(self.model)
        result = db.execute(stmt)
        return len(result.scalars().all())

