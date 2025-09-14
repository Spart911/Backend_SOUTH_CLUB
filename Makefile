.PHONY: help install run test clean docker-up docker-down docker-build docker-logs init-db

# Переменные
PYTHON = python3
PIP = pip3
APP_NAME = south_club_backend

# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Показать справку
	@echo "$(GREEN)SOUTH CLUB Backend - Команды управления$(NC)"
	@echo "=========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Установить зависимости
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	$(PIP) install -r requirements.txt

install-dev: ## Установить зависимости для разработки
	@echo "$(GREEN)Установка зависимостей для разработки...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-asyncio httpx

run: ## Запустить приложение
	@echo "$(GREEN)Запуск SOUTH CLUB Backend...$(NC)"
	$(PYTHON) run.py

run-prod: ## Запустить приложение в продакшн режиме
	@echo "$(GREEN)Запуск SOUTH CLUB Backend в продакшн режиме...$(NC)"
	uvicorn app.main:app --host 0.0.0.0 --port 8000

test: ## Запустить тесты
	@echo "$(GREEN)Запуск тестов...$(NC)"
	pytest -v

test-coverage: ## Запустить тесты с покрытием
	@echo "$(GREEN)Запуск тестов с покрытием...$(NC)"
	pytest --cov=app --cov-report=html

clean: ## Очистить временные файлы
	@echo "$(GREEN)Очистка временных файлов...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -name ".coverage" -delete

docker-up: ## Запустить Docker контейнеры
	@echo "$(GREEN)Запуск Docker контейнеров...$(NC)"
	cd docker && docker-compose up -d

docker-down: ## Остановить Docker контейнеры
	@echo "$(GREEN)Остановка Docker контейнеров...$(NC)"
	cd docker && docker-compose down

docker-build: ## Пересобрать Docker образы
	@echo "$(GREEN)Пересборка Docker образов...$(NC)"
	cd docker && docker-compose up -d --build

docker-logs: ## Показать логи Docker контейнеров
	@echo "$(GREEN)Логи Docker контейнеров:$(NC)"
	cd docker && docker-compose logs -f

docker-clean: ## Очистить Docker контейнеры и образы
	@echo "$(GREEN)Очистка Docker...$(NC)"
	cd docker && docker-compose down -v --rmi all

init-db: ## Инициализировать базу данных
	@echo "$(GREEN)Инициализация базы данных...$(NC)"
	$(PYTHON) init_db.py

setup: ## Первоначальная настройка проекта
	@echo "$(GREEN)Первоначальная настройка проекта...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Создание .env файла...$(NC)"; \
		cp env.example .env; \
		echo "$(GREEN)Отредактируйте .env файл с вашими настройками$(NC)"; \
	else \
		echo "$(GREEN).env файл уже существует$(NC)"; \
	fi
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Создание директорий для загрузок...$(NC)"
	mkdir -p uploads/products uploads/slider
	@echo "$(GREEN)Настройка завершена!$(NC)"

dev-setup: setup install-dev ## Настройка для разработки
	@echo "$(GREEN)Настройка для разработки завершена!$(NC)"

status: ## Показать статус проекта
	@echo "$(GREEN)Статус SOUTH CLUB Backend:$(NC)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Pip: $(shell $(PIP) --version)"
	@if [ -f .env ]; then echo "Environment: $(GREEN)Настроен$(NC)"; else echo "Environment: $(RED)Не настроен$(NC)"; fi
	@if [ -d "venv" ] || [ -d ".venv" ]; then echo "Virtual Environment: $(GREEN)Активен$(NC)"; else echo "Virtual Environment: $(RED)Не активен$(NC)"; fi

format: ## Форматировать код
	@echo "$(GREEN)Форматирование кода...$(NC)"
	black app/ tests/
	isort app/ tests/

lint: ## Проверить код линтером
	@echo "$(GREEN)Проверка кода линтером...$(NC)"
	flake8 app/ tests/
	black --check app/ tests/
	isort --check-only app/ tests/

security: ## Проверить безопасность
	@echo "$(GREEN)Проверка безопасности...$(NC)"
	bandit -r app/
	safety check

full-check: lint test security ## Полная проверка проекта
	@echo "$(GREEN)Полная проверка завершена!$(NC)"

