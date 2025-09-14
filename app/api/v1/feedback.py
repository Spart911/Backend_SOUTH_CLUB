from fastapi import APIRouter, HTTPException, status
from ...services.feedback import FeedbackService
from ...schemas.feedback import FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["Обратная связь"])
feedback_service = FeedbackService()


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def send_feedback(
    feedback_data: FeedbackCreate,
):
    """
    Отправить обратную связь в Telegram
    """
    try:
        success = await feedback_service.send_feedback(feedback_data)
        
        if success:
            return FeedbackResponse(
                success=True,
                message="Обратная связь успешно отправлена"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при отправке обратной связи"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при отправке обратной связи: {str(e)}"
        )


@router.post("/test", response_model=FeedbackResponse)
async def test_telegram_connection():
    """
    Тестирование подключения к Telegram (только для разработки)
    """
    try:
        success = await feedback_service.send_test_message()
        
        if success:
            return FeedbackResponse(
                success=True,
                message="Тестовое сообщение успешно отправлено в Telegram"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при отправке тестового сообщения"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при отправке тестового сообщения: {str(e)}"
        )
