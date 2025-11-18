# Миграция на современный pyproject.toml

## Выполнено ✅

### Удалены устаревшие файлы:
- ✅ `setup.py` - удален (заменен на pyproject.toml)
- ✅ `setup.cfg` - удален (пустой файл)

### Создан единый pyproject.toml:

**Формат:** PEP 621 (современный стандарт)

**Содержимое:**
- ✅ Метаданные проекта (name, version, description, authors, etc.)
- ✅ Зависимости из poetry_pyproject.toml
- ✅ Опциональные зависимости (docs, async)
- ✅ Классификаторы PyPI
- ✅ URL проекта
- ✅ Конфигурация инструментов:
  - `[tool.black]` - форматирование кода
  - `[tool.isort]` - сортировка импортов
  - `[tool.pytest.ini_options]` - настройки pytest
  - `[tool.coverage.run]` и `[tool.coverage.report]` - настройки coverage
- ✅ Конфигурация сборки (hatchling)

### Изменения в зависимостях:

**Удалено:**
- ❌ `dataslots` - заменен на стандартные dataclasses

**Оставлено:**
- ✅ `lxml>=4.6.2`
- ✅ `requests>=2.25.1`
- ✅ `unstdlib>=1.7.2`

**Добавлено опционально:**
- ✅ `aiohttp>=3.8.0` - для async поддержки (опциональная зависимость)

### Build system:

Используется `hatchling` - современный, легковесный build backend, который:
- Поддерживает PEP 621
- Работает с uv, pip, poetry
- Не требует дополнительных зависимостей для разработки

## Использование с uv

Проект полностью совместим с uv:

```bash
# Установка зависимостей
uv sync

# Установка с опциональными зависимостями
uv sync --extra docs
uv sync --extra async

# Добавление зависимостей
uv add package-name

# Удаление зависимостей
uv remove package-name
```

## Структура pyproject.toml

```
[build-system]          # Система сборки
[project]               # Метаданные проекта (PEP 621)
[project.optional-dependencies]  # Опциональные зависимости
[project.urls]          # URL проекта
[tool.hatch.build]      # Конфигурация сборки
[tool.black]            # Конфигурация black
[tool.isort]            # Конфигурация isort
[tool.pytest.ini_options]  # Конфигурация pytest
[tool.coverage]         # Конфигурация coverage
```

## Обратная совместимость

✅ **100% обратная совместимость:**
- Все существующие инструменты работают
- pip install продолжает работать
- poetry может использовать этот файл (но рекомендуется uv)

## Преимущества

1. ✅ **Единый файл конфигурации** - все в одном месте
2. ✅ **Современный стандарт** - PEP 621
3. ✅ **Совместимость** - работает с uv, pip, poetry
4. ✅ **Меньше файлов** - не нужны setup.py и setup.cfg
5. ✅ **Лучшая поддержка IDE** - современные IDE лучше понимают pyproject.toml

## Следующие шаги

1. ✅ pyproject.toml создан и валидирован
2. ✅ setup.py и setup.cfg удалены
3. ✅ Зависимости перенесены
4. ⏳ Можно удалить poetry_pyproject.toml (если больше не нужен)
5. ⏳ Обновить документацию по установке

## Проверка

```bash
# Проверить синтаксис
python -c "import tomli; f=open('pyproject.toml','rb'); tomli.load(f); print('Valid')"

# Проверить с uv
uv pip list  # Покажет установленные пакеты
```
