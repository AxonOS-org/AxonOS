# AxonOS Makefile
# Удобные команды для разработки и деплоя

.PHONY: install install-dev install-all test lint run run-dev docker clean

# Цвета для вывода
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Установка core зависимостей
install:
	@echo "$(BLUE)Установка core зависимостей...$(NC)"
	pip install -r requirements-core.txt
	@echo "$(GREEN)✅ Core зависимости установлены$(NC)"

# Установка dev зависимостей
install-dev: install
	@echo "$(BLUE)Установка dev зависимостей...$(NC)"
	pip install -r requirements-dev.txt
	@echo "$(GREEN)✅ Dev зависимости установлены$(NC)"

# Установка hardware зависимостей
install-hardware: install
	@echo "$(BLUE)Установка hardware зависимостей...$(NC)"
	pip install -r requirements-hardware.txt
	@echo "$(GREEN)✅ Hardware зависимости установлены$(NC)"

# Установка API зависимостей
install-api: install
	@echo "$(BLUE)Установка API зависимостей...$(NC)"
	pip install -r requirements-api.txt
	@echo "$(GREEN)✅ API зависимости установлены$(NC)"

# Установка всего стека
install-all: install install-hardware install-api install-dev
	@echo "$(GREEN)✅ Все зависимости установлены$(NC)"

# Запуск тестов
test:
	@echo "$(BLUE)Запуск тестов...$(NC)"
	pytest tests/ -v --tb=short
	@echo "$(GREEN)✅ Тесты завершены$(NC)"

# Запуск тестов с покрытием
test-cov:
	@echo "$(BLUE)Запуск тестов с покрытием...$(NC)"
	pytest tests/ --cov=src/axonos --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)✅ Тесты с покрытием завершены$(NC)"

# Линтинг кода
lint:
	@echo "$(BLUE)Запуск линтеров...$(NC)"
	@echo "$(YELLOW)Ruff check...$(NC)"
	ruff check src/
	@echo "$(YELLOW)Ruff format...$(NC)"
	ruff format src/
	@echo "$(YELLOW)MyPy...$(NC)"
	mypy src/ --ignore-missing-imports
	@echo "$(GREEN)✅ Линтинг завершен$(NC)"

# Запуск API сервера
run:
	@echo "$(BLUE)Запуск API сервера...$(NC)"
	cd src && uvicorn axonos.api.main:app --host 0.0.0.0 --port 8000

# Запуск API сервера в режиме разработки
run-dev:
	@echo "$(BLUE)Запуск API сервера (dev mode)...$(NC)"
	cd src && uvicorn axonos.api.main:app --reload --host 0.0.0.0 --port 8000

# Запуск демо
run-demo:
	@echo "$(BLUE)Запуск демо...$(NC)"
	python demo_axonos_platform_v2.py

# Сборка Docker образа
docker-build:
	@echo "$(BLUE)Сборка Docker образа...$(NC)"
	docker build -t axonos:latest .
	@echo "$(GREEN)✅ Docker образ собран$(NC)"

# Запуск в Docker
docker-run:
	@echo "$(BLUE)Запуск в Docker...$(NC)"
	docker run -p 8000:8000 axonos:latest

# Запуск через docker-compose
docker-compose:
	@echo "$(BLUE)Запуск через docker-compose...$(NC)"
	docker-compose up

# Очистка временных файлов
clean:
	@echo "$(BLUE)Очистка временных файлов...$(NC)"
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name ".ruff_cache" -exec rm -r {} +
	rm -rf htmlcov/
	rm -rf .coverage
	@echo "$(GREEN)✅ Очистка завершена$(NC)"

# Форматирование кода
format:
	@echo "$(BLUE)Форматирование кода...$(NC)"
	ruff format src/ tests/
	@echo "$(GREEN)✅ Форматирование завершено$(NC)"

# Установка pre-commit hooks
setup-hooks:
	@echo "$(BLUE)Установка pre-commit hooks...$(NC)"
	pre-commit install
	@echo "$(GREEN)✅ Pre-commit hooks установлены$(NC)"

# Генерация документации
docs:
	@echo "$(BLUE)Генерация документации...$(NC)"
	cd docs && make html
	@echo "$(GREEN)✅ Документация сгенерирована$(NC)"

# Проверка безопасности (security audit)
security-audit:
	@echo "$(BLUE)Проверка безопасности...$(NC)"
	@echo "$(YELLOW)Проверка зависимостей...$(NC)"
	pip-audit
	@echo "$(YELLOW)Проверка секретов...$(NC)"
	gitleaks detect
	@echo "$(GREEN)✅ Security audit завершен$(NC)"

# Справка
help:
	@echo "$(BLUE)AxonOS Makefile Commands:$(NC)"
	@echo "  $(GREEN)install$(NC)       - Установить core зависимости"
	@echo "  $(GREEN)install-dev$(NC)    - Установить dev зависимости"
	@echo "  $(GREEN)install-hardware$(NC) - Установить hardware зависимости"
	@echo "  $(GREEN)install-api$(NC)     - Установить API зависимости"
	@echo "  $(GREEN)install-all$(NC)     - Установить все зависимости"
	@echo "  $(GREEN)test$(NC)           - Запустить тесты"
	@echo "  $(GREEN)test-cov$(NC)       - Запустить тесты с покрытием"
	@echo "  $(GREEN)lint$(NC)           - Запустить линтеры"
	@echo "  $(GREEN)format$(NC)         - Отформатировать код"
	@echo "  $(GREEN)run$(NC)            - Запустить API сервер"
	@echo "  $(GREEN)run-dev$(NC)        - Запустить API сервер (dev mode)"
	@echo "  $(GREEN)run-demo$(NC)       - Запустить демо"
	@echo "  $(GREEN)docker-build$(NC)   - Собрать Docker образ"
	@echo "  $(GREEN)docker-run$(NC)     - Запустить в Docker"
	@echo "  $(GREEN)docker-compose$(NC) - Запустить через docker-compose"
	@echo "  $(GREEN)clean$(NC)          - Очистить временные файлы"
	@echo "  $(GREEN)security-audit$(NC) - Проверка безопасности"
	@echo "  $(GREEN)help$(NC)           - Показать эту справку"
