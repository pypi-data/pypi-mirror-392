# Тесты для Rodin Gen-2 MCP Server

Этот каталог содержит комплексный набор тестов для проекта Rodin Gen-2 MCP Server.

## Структура тестов

- `conftest.py` - Общие fixtures для всех тестов
- `test_main.py` - Тесты для FastAPI сервера (main.py)
- `test_rodin_gen2_server.py` - Тесты для MCP сервера (rodin_gen2_server.py)

## Запуск тестов

### Установка зависимостей

```bash
pip install -e ".[dev]"
```

### Запуск всех тестов

```bash
pytest
```

### Запуск с покрытием кода

```bash
pytest --cov=. --cov-report=html --cov-report=term
```

Отчет о покрытии будет сохранен в директории `htmlcov/`.

### Запуск конкретного файла тестов

```bash
pytest tests/test_main.py
pytest tests/test_rodin_gen2_server.py
```

### Запуск конкретного теста

```bash
pytest tests/test_main.py::TestRootEndpoint::test_root_returns_welcome_message
```

### Запуск с подробным выводом

```bash
pytest -v
```

### Запуск только быстрых тестов

```bash
pytest -m "not slow"
```

## Покрытие кода

Тесты покрывают следующие компоненты:

### main.py (FastAPI сервер)

- ✅ Корневой эндпоинт `/`
- ✅ Health check эндпоинт `/health`
- ✅ Генерация через `/generate`
- ✅ RodinClient класс и его методы
- ✅ Обработка ошибок
- ✅ Валидация конфигурации

### rodin_gen2_server.py (MCP сервер)

- ✅ `make_rodin_request()` - HTTP запросы к API
- ✅ `generate_3d_text_to_3d()` - Генерация из текста
- ✅ `generate_3d_image_to_3d()` - Генерация из изображений
- ✅ `check_task_status()` - Проверка статуса задачи
- ✅ `download_result()` - Синхронная загрузка результатов
- ✅ `start_download_result()` - Запуск фоновой загрузки
- ✅ `check_download_result_status()` - Проверка статуса загрузки
- ✅ Валидация параметров (seed, bbox_condition)
- ✅ Обработка ошибок и edge cases

## Типы тестов

### Unit тесты

Проверяют отдельные функции и методы в изоляции.

### Async тесты

Используют `pytest-asyncio` для тестирования асинхронного кода.

### Mock тесты

Используют моки для изоляции от внешних зависимостей (API вызовы, файловая система).

## CI/CD

Тесты можно интегрировать в CI/CD пайплайн:

```yaml
# Пример для GitHub Actions
- name: Run tests
  run: |
    pip install -e ".[dev]"
    pytest --cov=. --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Советы по разработке

1. Запускайте тесты перед коммитом изменений
2. Стремитесь к покрытию >80% для всего кода
3. Добавляйте тесты для новых функций
4. Обновляйте тесты при изменении API

## Переменные окружения для тестов

Тесты используют моки для переменных окружения, но при необходимости можно создать файл `.env.test`:

```env
RODIN_API_KEY=test_key_for_testing
RODIN_API_BASE_URL=https://api.test.rodin.com
```
