# API Tests

## Описание

Эта папка содержит API тесты для `pobapi`, созданные на основе тест-кейсов из `test_cases/api/`.

## Структура файлов

- `test_factory_functions.py` - Тесты для factory функций (from_url, from_import_code)
- `test_initialization.py` - Тесты для инициализации PathOfBuildingAPI
- `test_build_properties.py` - Тесты для properties билда
- `test_build_modification.py` - Тесты для методов модификации билда
- `test_serialization.py` - Тесты для методов сериализации
- `test_build_builder.py` - Тесты для BuildBuilder API
- `test_edge_cases.py` - Тесты для edge cases и продвинутых сценариев
- `conftest.py` - Фикстуры для API тестов

## Покрытие тест-кейсов

**Всего тестов:** 46

**Покрытие тест-кейсов:**
- Factory Functions: 5 тестов (TC-API-003, 004, 005, 006, 007)
- Initialization: 3 теста (TC-API-008, 010, 013)
- Build Properties: 7 тестов (TC-API-031, 038, 042-044, 049-050)
- Build Modification: 15 тестов (TC-API-058, 060, 063-076)
- Serialization: 1 тест (TC-API-078)
- BuildBuilder API: 10 тестов (TC-API-081-090)
- Edge Cases: 4 теста (TC-API-097-100)

**Итого:** 45 тестов для непокрытых тест-кейсов

## Запуск тестов

```bash
# Запустить все API тесты
pytest tests/api

# Запустить конкретный файл
pytest tests/api/test_factory_functions.py

# Запустить с подробным выводом
pytest tests/api -v
```

## Связь с тест-кейсами

Все тесты соответствуют тест-кейсам из `test_cases/api/01_api_test_cases.md`.

Каждый тест содержит комментарий с ID тест-кейса, например:
```python
def test_from_url_with_custom_timeout(self, mocker):
    """TC-API-003: Load build from URL with custom timeout."""
```

## Фикстуры

- `simple_build` - Создает простой билд для тестирования
- `sample_xml` - Пример XML строки (из conftest.py)
- `minimal_xml` - Минимальный валидный XML (из conftest.py)
- `create_test_item` - Функция для создания тестовых предметов (из conftest.py)

## Примечания

- Тесты используют моки для сетевых запросов
- Тесты изолированы и не требуют внешних зависимостей
- Все тесты соответствуют структуре существующих тестов в `tests/unit/`
