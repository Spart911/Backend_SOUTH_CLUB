# Repository pattern implementation
from .base import BaseRepository
from .product import ProductRepository
from .photo import ProductPhotoRepository
from .slider import SliderPhotoRepository
from .order import OrderRepository

__all__ = ["BaseRepository", "ProductRepository", "ProductPhotoRepository", "SliderPhotoRepository", "OrderRepository"]
