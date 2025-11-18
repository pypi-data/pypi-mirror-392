# Загрузка игровых данных в Path of Building

## Как Path of Building (Lua) получает игровые данные

### 1. Источники данных

Path of Building получает игровые данные из нескольких источников:

#### A. Бинарные файлы игры Path of Exile (.dat файлы)
- **Расположение**: В папке установленной игры Path of Exile
- **Формат**: Бинарные файлы `.dat` (например, `Mods.dat`, `Items.dat`, `PassiveSkills.dat`)
- **Парсинг**: PoB использует Lua-скрипты для чтения и парсинга этих бинарных файлов
- **Обновление**: При каждом патче игры файлы обновляются, PoB нужно обновлять парсеры

#### B. Встроенные данные в PoB
- **Расположение**: `src/Data/` в репозитории Path of Building
- **Формат**: Lua-таблицы с данными
- **Содержимое**:
  - База данных узлов пассивного дерева
  - База данных скилл-гемов
  - База данных уникальных предметов
  - База данных базовых типов предметов
  - База данных модификаторов
  - База данных аур и проклятий

### 2. Структура загрузки в PoB (Lua)

```lua
-- Пример структуры загрузки данных в PoB
-- Файл: src/Data.lua или src/LoadData.lua

-- Загрузка узлов пассивного дерева
function LoadPassiveTreeData()
    -- Загрузка из встроенных Lua-таблиц
    local nodes = {}
    -- ... парсинг данных ...
    return nodes
end

-- Загрузка данных гемов
function LoadGemData()
    -- Загрузка из встроенных Lua-таблиц или .dat файлов
    local gems = {}
    -- ... парсинг данных ...
    return gems
end

-- Загрузка данных уникальных предметов
function LoadUniqueData()
    -- Загрузка из встроенных Lua-таблиц
    local uniques = {}
    -- ... парсинг данных ...
    return uniques
end
```

### 3. Формат данных в PoB

#### Узлы пассивного дерева
```lua
-- Пример структуры узла в PoB
nodes[123] = {
    name = "Node Name",
    stats = {"+10 to Strength", "5% increased Life"},
    isKeystone = false,
    isNotable = false,
    isJewelSocket = false,
    classStart = false
}
```

#### Скилл-гемы
```lua
-- Пример структуры гема в PoB
gems["Arc"] = {
    baseDamage = {
        Lightning = {10, 50}  -- min, max
    },
    damageEffectiveness = 100.0,
    castTime = 0.75,
    isSpell = true
}
```

#### Уникальные предметы
```lua
-- Пример структуры уникального предмета в PoB
uniques["Headhunter"] = {
    baseType = "Leather Belt",
    specialEffects = {"Steals mods from rare monsters"},
    implicitMods = {},
    explicitMods = {}
}
```

### 4. Наша реализация (Python)

#### Текущая структура

Мы реализовали `GameDataLoader` который может загружать данные из JSON файлов.
Загрузчик автоматически ищет файлы в стандартных местах (как в PoB):

```python
from pobapi.calculator import GameDataLoader

# Автоматический поиск файлов в стандартных местах
loader = GameDataLoader()
nodes = loader.load_passive_tree_data()  # Ищет nodes.json автоматически
gems = loader.load_skill_gem_data()      # Ищет gems.json автоматически
uniques = loader.load_unique_item_data()  # Ищет uniques.json автоматически

# Или указать конкретную директорию
loader = GameDataLoader(data_directory="./my_data/")
nodes = loader.load_passive_tree_data()

# Или указать конкретный путь к файлу
nodes = loader.load_passive_tree_data("path/to/nodes.json")
```

#### Стандартные места поиска файлов

`GameDataLoader` автоматически ищет файлы в следующих местах (в порядке приоритета):

1. **Явно указанная директория** (через `data_directory` параметр)
2. **Переменная окружения** `POBAPI_DATA_DIR`
3. **Текущая директория** (`.`)
4. **`./data/`**
5. **`./pobapi/data/`**
6. **`pobapi/calculator/data/`** (внутри пакета)

#### Формат JSON файлов

**nodes.json:**
```json
{
  "nodes": {
    "123": {
      "name": "Node Name",
      "stats": ["+10 to Strength", "5% increased Life"],
      "isKeystone": false,
      "isNotable": false,
      "isJewelSocket": false,
      "classStart": false,
      "masteryEffects": null
    }
  }
}
```

**gems.json:**
```json
{
  "gems": {
    "Arc": {
      "baseDamage": {
        "Lightning": [10, 50]
      },
      "damageEffectiveness": 100.0,
      "castTime": 0.75,
      "isSpell": true,
      "isAttack": false,
      "manaCost": 20.0
    }
  }
}
```

**uniques.json:**
```json
{
  "uniques": {
    "Headhunter": {
      "baseType": "Leather Belt",
      "specialEffects": ["Steals mods from rare monsters"],
      "implicitMods": [],
      "explicitMods": []
    }
  }
}
```

### 5. Отличия от PoB (Lua)

| Аспект | Path of Building (Lua) | Наша реализация (Python) |
|--------|------------------------|--------------------------|
| **Формат данных** | Lua-таблицы (встроенные) | JSON файлы (внешние) |
| **Источник данных** | Встроенные в код или парсинг .dat | JSON файлы (требуют создания) |
| **Обновление данных** | Обновление Lua-кода | Обновление JSON файлов |
| **Парсинг .dat файлов** | Есть (Lua-скрипты) | Нет (требует реализации) |

### 6. Что нужно для полной функциональности

#### Вариант 1: Использовать готовые данные из PoB
- Извлечь Lua-таблицы из репозитория PoB
- Конвертировать их в JSON формат
- Использовать в нашей реализации

#### Вариант 2: Парсинг .dat файлов игры
- Реализовать парсер для бинарных .dat файлов Path of Exile
- Извлекать данные напрямую из файлов игры
- Конвертировать в наш формат

#### Вариант 3: Использовать сторонние источники
- Использовать API Path of Exile (если доступно)
- Использовать данные из других проектов (например, poedb.tw)
- Использовать данные из trade sites

### 7. Рекомендации

1. **Краткосрочное решение**: Создать JSON файлы с базовыми данными (узлы, гемы, уникальные предметы) на основе данных из PoB репозитория

2. **Долгосрочное решение**: Реализовать парсер для .dat файлов игры для автоматического обновления данных при патчах

3. **Альтернатива**: Использовать готовые JSON файлы из сообщества или других проектов

### 8. Следующие шаги

1. Изучить структуру `src/Data/` в репозитории Path of Building
2. Извлечь данные из Lua-таблиц
3. Конвертировать в JSON формат
4. Интегрировать в `GameDataLoader`
5. (Опционально) Реализовать парсер для .dat файлов
