# Сбор уникальных предметов с poewiki.net

## Статус

Скрипт для автоматического сбора всех уникальных предметов с [poewiki.net](https://www.poewiki.net/wiki/Unique_item) создан и запущен.

## Скрипт

**Файл:** `utils/scrape_unique_items.py`

**Функциональность:**
- Автоматический сбор ссылок на уникальные предметы из всех категорий poewiki.net
- Парсинг каждой страницы уникального предмета
- Извлечение данных: base_type, implicit_mods, explicit_mods, special_effects
- Сохранение в JSON формат для `GameDataLoader`
- Поддержка возобновления работы (resume)

## Использование

### Запуск скрипта

```bash
# Установить зависимости (если еще не установлены)
uv add beautifulsoup4 --script utils/scrape_unique_items.py

# Запустить скрипт
python utils/scrape_unique_items.py data/uniques_scraped.json
```

### Проверка прогресса

```bash
# Быстрая проверка
python utils/check_scrape_progress.py

# Мониторинг в реальном времени (каждые 30 секунд)
python utils/monitor_scrape.py

# С другим интервалом (например, каждые 10 секунд)
python utils/monitor_scrape.py 10
```

## Прогресс

- **Всего ссылок собрано:** ~2,373 (включая дубликаты)
- **Ожидаемое время:** ~40 минут (1 секунда задержка между запросами)
- **Сохранение прогресса:** Каждые 10 предметов
- **Возобновление:** Можно безопасно прервать (Ctrl+C) и продолжить позже

## Формат выходного файла

Скрипт создает JSON файл в формате для `GameDataLoader`:

```json
{
  "uniques": {
    "Headhunter": {
      "name": "Headhunter",
      "base_type": "Leather Belt",
      "implicit_mods": [],
      "explicit_mods": [
        "+40-50 to maximum Life",
        "+(20-30)% to all Elemental Resistances",
        ...
      ],
      "special_effects": [
        "When you Kill a Rare monster, you gain its Modifiers for 20 seconds"
      ]
    },
    ...
  }
}
```

## Интеграция с GameDataLoader

После завершения сбора, данные можно загрузить через `GameDataLoader`:

```python
from pobapi.calculator import GameDataLoader

loader = GameDataLoader()
uniques = loader.load_unique_item_data("data/uniques_scraped.json")

# Использование
headhunter = loader.get_unique_item("Headhunter")
if headhunter:
    print(f"Base type: {headhunter.base_type}")
    print(f"Special effects: {headhunter.special_effects}")
```

## Примечания

- Скрипт вежливо обращается к серверу (1 секунда задержка между запросами)
- Прогресс сохраняется каждые 10 предметов
- Можно безопасно прервать и продолжить позже
- Скрипт автоматически пропускает уже собранные предметы при возобновлении
