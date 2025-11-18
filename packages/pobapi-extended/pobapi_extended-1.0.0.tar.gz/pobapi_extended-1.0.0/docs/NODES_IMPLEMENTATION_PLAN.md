# План реализации nodes.json

## Анализ текущего состояния

### Что уже реализовано:

1. ✅ **PassiveNode dataclass** - базовая структура
   - `node_id`, `name`, `stats`
   - `is_keystone`, `is_notable`, `is_jewel_socket`, `class_start`
   - `mastery_effects`

2. ✅ **GameDataLoader.load_passive_tree_data()** - загрузка из JSON
   - Поиск файла в стандартных местах
   - Парсинг JSON структуры

3. ✅ **Базовая структура** - готовность к расширению

### Что НЕ реализовано:

1. ❌ **Парсер PassiveSkills.dat** - нет скрипта для извлечения данных
2. ❌ **Расширение PassiveNode** - отсутствуют поля из DAT файла
3. ❌ **Обработка виртуальных полей** - StatsZip и другие
4. ❌ **Генерация nodes.json** - нет скрипта

## Структура PassiveSkills.dat (из DAT_PARSING_LOGIC.md)

### Основные поля:

1. **Id** - Уникальный идентификатор пассивного навыка
2. **PassiveSkillGraphId** - ID в графе навыков
3. **Name** - Название навыка
4. **FlavourText** - Описательный текст
5. **Reminder_ClientStringsKeys** - Ключи напоминаний
6. **PassiveSkillBuffsKeys** - Ссылки на баффы
7. **StatsKeys** - Список ключей статистик (ref|list|ulong)
8. **Stat1Value, Stat2Value, ..., Stat5Value** - Значения статистик
9. **Icon_DDSFile** - Путь к иконке
10. **SkillPointsGranted** - Количество очков навыков

### Виртуальные поля:

- **StatValues** - объединяет Stat1Value...Stat5Value в список
- **StatsZip** - объединяет StatsKeys и StatValues в пары (stat_key, stat_value)

## Варианты реализации

### Вариант 1: Использование PyPoE (рекомендуется)

**Преимущества:**
- Готовая библиотека для парсинга DAT файлов
- Поддержка виртуальных полей (StatsZip)
- Автоматическая обработка типов данных
- Индексация для быстрого поиска

**Недостатки:**
- Требует установки PyPoE
- Нужна спецификация DAT файлов

**Время:** 8-12 часов

### Вариант 2: Использование готовых tree JSON

**Преимущества:**
- Простой парсинг JSON
- Не требует DAT файлов
- Быстрая реализация

**Недостатки:**
- Нужно найти источник tree JSON
- Может не содержать все данные из DAT

**Время:** 4-6 часов

### Вариант 3: Парсинг из Lua файлов PoB

**Преимущества:**
- Аналогично gems.json
- Использует уже имеющийся lupa

**Недостатки:**
- В PoB может не быть PassiveSkills.lua
- Нужно проверить наличие файла

**Время:** 6-8 часов

## Рекомендуемый подход: Гибридный

1. **Приоритет 1:** Использовать PyPoE для парсинга PassiveSkills.dat
2. **Приоритет 2:** Если PyPoE недоступен, использовать готовые tree JSON
3. **Приоритет 3:** Если есть PassiveSkills.lua в PoB, парсить из него

## План реализации

### Этап 1: Расширение PassiveNode (2 часа)

Добавить недостающие поля из PassiveSkills.dat:

```python
@dataclass
class PassiveNode:
    # Существующие поля...

    # Новые поля из PassiveSkills.dat:
    passive_skill_graph_id: int | None = None
    flavour_text: str | None = None
    reminder_text_keys: list[str] = field(default_factory=list)
    passive_skill_buffs_keys: list[str] = field(default_factory=list)
    stat_keys: list[str] = field(default_factory=list)  # StatsKeys
    stat_values: list[int | float] = field(default_factory=list)  # StatValues
    icon_path: str | None = None  # Icon_DDSFile
    skill_points_granted: int = 1  # SkillPointsGranted

    # Геометрия дерева (из tree JSON):
    x: float | None = None
    y: float | None = None
    connections: list[int] = field(default_factory=list)

    # Дополнительные флаги:
    is_mastery: bool = False
    is_ascendancy: bool = False
```

### Этап 2: Скрипт парсинга через PyPoE (8 часов)

**Файл:** `scripts/extract_nodes_from_pob.py`

```python
from PyPoE.poe.file.dat import DatFile
from PyPoE.poe.file.specification.repository import SQLiteSpecRepository
from PyPoE.poe.constants import VERSION

def parse_passive_skills_dat(dat_path: Path) -> dict:
    """Parse PassiveSkills.dat using PyPoE."""
    # 1. Загрузить спецификацию
    repo = SQLiteSpecRepository(...)
    spec = repo.get_spec(VERSION.STABLE)

    # 2. Создать DatFile
    df = DatFile("PassiveSkills.dat")

    # 3. Прочитать файл
    with open(dat_path, "rb") as f:
        reader = df.read(f, specification=spec)

    # 4. Построить индекс
    reader.build_index("Id")

    # 5. Извлечь данные
    nodes = {}
    for passive in reader:
        # Использовать виртуальное поле StatsZip
        stats = []
        for stat_key, stat_value in passive["StatsZip"]:
            # Преобразовать stat_key в строку модификатора
            stat_string = format_stat(stat_key, stat_value)
            stats.append(stat_string)

        node = {
            "id": passive["Id"],
            "name": passive["Name"],
            "stats": stats,
            # ... другие поля
        }
        nodes[passive["Id"]] = node

    return nodes
```

### Этап 3: Альтернатива - парсинг tree JSON (4 часа)

Если PyPoE недоступен, парсить из tree JSON:

```python
def parse_tree_json(json_path: Path) -> dict:
    """Parse tree JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        tree_data = json.load(f)

    nodes = {}
    # Извлечь nodes из структуры tree JSON
    # Обычно: tree_data["nodes"] или tree_data["tree"]["nodes"]

    return nodes
```

### Этап 4: Объединение данных (2 часа)

Объединить данные из PassiveSkills.dat и tree JSON:

```python
def merge_node_data(passive_skills_data: dict, tree_data: dict) -> dict:
    """Merge data from PassiveSkills.dat and tree JSON."""
    nodes = {}

    for node_id, passive_data in passive_skills_data.items():
        # Добавить геометрию из tree JSON
        if node_id in tree_data:
            passive_data["x"] = tree_data[node_id].get("x")
            passive_data["y"] = tree_data[node_id].get("y")
            passive_data["connections"] = tree_data[node_id].get("connections", [])

        nodes[node_id] = passive_data

    return nodes
```

### Этап 5: Генерация nodes.json (2 часа)

```python
def generate_nodes_json(nodes: dict, output_path: Path) -> None:
    """Generate nodes.json from processed nodes."""
    nodes_json = {"nodes": {}}

    for node_id, node_data in nodes.items():
        nodes_json["nodes"][str(node_id)] = node_data

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(nodes_json, f, indent=2, ensure_ascii=False)
```

### Этап 6: Обновление GameDataLoader (1 час)

Обновить `load_passive_tree_data()` для поддержки новых полей.

## Итоговая оценка времени

| Этап | Время | Описание |
|------|-------|----------|
| 1. Расширение PassiveNode | 2 часа | Добавить поля из DAT |
| 2. Парсер через PyPoE | 8 часов | Парсинг PassiveSkills.dat |
| 3. Альтернатива tree JSON | 4 часа | Если PyPoE недоступен |
| 4. Объединение данных | 2 часа | Merge DAT + tree JSON |
| 5. Генерация nodes.json | 2 часа | Сохранение в JSON |
| 6. Обновление GameDataLoader | 1 час | Поддержка новых полей |
| **ИТОГО** | **19 часов** | **~2.5 дня работы** |

## Зависимости

Для реализации через PyPoE потребуется:

```bash
uv add PyPoE
```

Или использовать готовые tree JSON файлы (не требует зависимостей).

## Статус реализации

### ✅ Выполнено:

1. **Расширен PassiveNode dataclass** - добавлено 13 новых полей:
   - `passive_skill_graph_id`, `flavour_text`, `reminder_text_keys`
   - `passive_skill_buffs_keys`, `stat_keys`, `stat_values`
   - `icon_path`, `skill_points_granted`
   - `x`, `y`, `connections` (геометрия)
   - `is_mastery`, `is_ascendancy`

2. **Создан скрипт `scripts/extract_nodes_from_pob.py`**:
   - Базовый парсер DAT файлов (требует спецификацию для полной реализации)
   - Парсер tree JSON для геометрии
   - Объединение данных из DAT и tree JSON
   - Обработка StatsZip виртуального поля
   - Форматирование статистик в строки модификаторов
   - Генерация nodes.json

3. **Обновлен GameDataLoader** - поддержка всех новых полей PassiveNode

### ⚠️ Требует доработки:

1. **Полный парсер PassiveSkills.dat**:
   - Нужна полная спецификация полей и их типов
   - Нужен парсер Stats.dat для описаний статистик
   - Текущая реализация - заглушка с инструкциями

2. **Источники данных**:
   - PassiveSkills.dat нужно извлечь из Content.ggpk или найти готовый
   - Tree JSON нужно найти в PoB репозитории или сообществе

## Использование

```bash
# Использование скрипта
uv run python scripts/extract_nodes_from_pob.py --tree-json path/to/tree.json --output data/nodes.json

# Или с PassiveSkills.dat (когда будет доступен)
uv run python scripts/extract_nodes_from_pob.py --dat-path path/to/PassiveSkills.dat --tree-json path/to/tree.json
```

## Следующие шаги

1. Найти или создать спецификацию для PassiveSkills.dat
2. Реализовать полный парсер DAT файла
3. Найти источник tree JSON или PassiveSkills.dat
4. Протестировать генерацию nodes.json
