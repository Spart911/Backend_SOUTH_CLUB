from fastapi import HTTPException, status


class ProductNotFoundException(HTTPException):
    """
    Исключение когда товар не найден
    """
    def __init__(self, product_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Товар с ID {product_id} не найден"
        )


class PhotoNotFoundException(HTTPException):
    """
    Исключение когда фотография не найдена
    """
    def __init__(self, photo_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Фотография с ID {photo_id} не найдена"
        )


class SliderPhotoNotFoundException(HTTPException):
    """
    Исключение когда фотография слайдера не найдена
    """
    def __init__(self, photo_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Фотография слайдера с ID {photo_id} не найдена"
        )


class InvalidFileTypeException(HTTPException):
    """
    Исключение когда тип файла не поддерживается
    """
    def __init__(self, file_type: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Тип файла {file_type} не поддерживается"
        )


class FileSizeExceededException(HTTPException):
    """
    Исключение когда размер файла превышает лимит
    """
    def __init__(self, max_size: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Размер файла превышает максимально допустимый: {max_size} байт"
        )


class TelegramBotException(HTTPException):
    """
    Исключение при ошибке отправки в Telegram
    """
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка отправки в Telegram: {message}"
        )

