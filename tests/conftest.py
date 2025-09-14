import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db
from app.config import settings


# Создаем тестовую базу данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """
    Переопределяем зависимость для тестов
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Переопределяем зависимость
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """
    Фикстура для тестового клиента
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_session():
    """
    Фикстура для тестовой сессии БД
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def admin_credentials():
    """
    Фикстура с учетными данными админа
    """
    return {
        "username": settings.admin_username,
        "password": settings.admin_password
    }


@pytest.fixture
def admin_token(client, admin_credentials):
    """
    Фикстура с токеном админа
    """
    response = client.post("/api/v1/auth/login-json", json=admin_credentials)
    return response.json()["access_token"]


@pytest.fixture
def sample_product_data():
    """
    Фикстура с тестовыми данными товара
    """
    return {
        "name": "Тестовая футболка",
        "characteristics": "100% хлопок",
        "color": "Белый",
        "composition": "100% хлопок",
        "print_technology": "Термопечать",
        "size": 2,
        "price": 2500
    }


@pytest.fixture
def sample_feedback_data():
    """
    Фикстура с тестовыми данными обратной связи
    """
    return {
        "name": "Тестовый пользователь",
        "email": "test@example.com",
        "phone": "+79001234567",
        "message": "Тестовое сообщение для проверки API"
    }

