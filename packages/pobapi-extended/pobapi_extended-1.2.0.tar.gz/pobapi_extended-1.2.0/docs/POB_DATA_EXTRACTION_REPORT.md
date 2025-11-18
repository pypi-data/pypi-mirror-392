# Отчет о логике извлечения данных в Path of Building

## Краткое резюме

Path of Building использует модульную систему загрузки данных через Lua-скрипты. Основной файл загрузки - `src/Modules/Data.lua`, который координирует загрузку всех игровых данных.

### Ключевые файлы:

- **Gems (gems.json):**
  - `src/Data/Gems.lua` - основной файл с данными о гемах
  - `src/Data/Skills/act_str.lua`, `act_dex.lua`, `act_int.lua`, и т.д. - навыки
  - Логика загрузки: `LoadModule("Data/Gems")` → `setupGem()` → связывание с skills

- **Nodes (nodes.json):**
  - `PassiveSkills.dat` - бинарный файл игры (требует парсинга)
  - Tree JSON файлы (если доступны)
  - Встроенные Lua таблицы (если есть)

### Процесс извлечения:

1. **Gems:** Lua таблицы → парсинг → JSON
2. **Nodes:** .dat файлы или JSON → парсинг → JSON

## Обзор

## 1. Загрузка данных о скилл-гемах (gems.json)

### Структура загрузки в Data.lua

```lua
-- Определение типов скиллов
local skillTypes = {
    "act_str",    -- Active Strength skills
    "act_dex",    -- Active Dexterity skills
    "act_int",    -- Active Intelligence skills
    "other",      -- Other active skills
    "glove",      -- Glove skills
    "minion",     -- Minion skills
    "spectre",    -- Spectre skills
    "sup_str",    -- Support Strength gems
    "sup_dex",    -- Support Dexterity gems
    "sup_int",    -- Support Intelligence gems
}

-- Загрузка Skill Stat Map (маппинг статистик к модификаторам)
data.skillStatMap = LoadModule("Data/SkillStatMap", makeSkillMod, makeFlagMod, makeSkillDataMod)

-- Загрузка скиллов по типам
data.skills = { }
for _, type in pairs(skillTypes) do
    LoadModule("Data/Skills/"..type, data.skills, makeSkillMod, makeFlagMod, makeSkillDataMod)
end

-- Обработка загруженных скиллов
for skillId, grantedEffect in pairs(data.skills) do
    grantedEffect.name = sanitiseText(grantedEffect.name)
    grantedEffect.id = skillId
    grantedEffect.modSource = "Skill:"..skillId
    -- Обработка модификаторов (baseMods, qualityMods, levelMods)
    -- Установка statMap metatable
end

-- Загрузка гемов
data.gems = LoadModule("Data/Gems")
data.gemForSkill = { }
data.gemForBaseName = { }
data.gemsByGameId = { }

-- Функция настройки гема
local function setupGem(gem, gemId)
    gem.id = gemId
    gem.grantedEffect = data.skills[gem.grantedEffectId]  -- Связь с skill
    data.gemForSkill[gem.grantedEffect] = gemId
    data.gemsByGameId[gem.gameId] = data.gemsByGameId[gem.gameId] or {}
    data.gemsByGameId[gem.gameId][gem.variantId] = gem
    -- Обработка базового имени
    -- Обработка Vaal гемов
    -- Установка naturalMaxLevel
end

-- Обработка всех гемов
for gemId, gem in pairs(data.gems) do
    gem.name = sanitiseText(gem.name)
    setupGem(gem, gemId)
    -- Обработка Vaal гемов и альтернативных версий
end
```

### Логика извлечения gems.json

1. **Загрузка Skills (навыков):**
   - Загружаются из файлов `Data/Skills/act_str.lua`, `Data/Skills/act_dex.lua`, и т.д.
   - Каждый файл содержит Lua-таблицы с данными о навыках
   - Структура: `data.skills[skillId] = { name, baseMods, qualityMods, levelMods, statMap, ... }`

2. **Загрузка Gems (гемов):**
   - Загружаются из `Data/Gems.lua`
   - Структура: `data.gems[gemId] = { name, gameId, variantId, grantedEffectId, reqStr, reqDex, reqInt, ... }`

3. **Связывание Gems и Skills:**
   - Каждый гем ссылается на skill через `grantedEffectId`
   - `setupGem()` создает связи: `gem.grantedEffect = data.skills[gem.grantedEffectId]`

4. **Обработка модификаторов:**
   - `processMod()` добавляет источники модификаторов
   - Обрабатываются `baseMods`, `qualityMods`, `levelMods`
   - Устанавливается `statMap` для динамических модификаторов

5. **Специальная обработка:**
   - Vaal гемы (гибридные гемы с двумя эффектами)
   - Альтернативные версии (AltX, AltY)
   - Support гемы (добавляется " Support" к имени)

### Формат данных для gems.json

```json
{
  "gems": {
    "Arc": {
      "name": "Arc",
      "gameId": "Metadata/Items/Gems/Arc",
      "grantedEffectId": "Arc",
      "reqStr": 0,
      "reqDex": 0,
      "reqInt": 64,
      "baseDamage": {
        "Lightning": [10, 50]
      },
      "damageEffectiveness": 100.0,
      "castTime": 0.75,
      "isSpell": true,
      "isAttack": false,
      "manaCost": 20.0,
      "qualityStats": ["1% increased Cast Speed per 1% Quality"],
      "levelStats": ["Deals 8 to 47 Lightning Damage"]
    }
  }
}
```

## 2. Загрузка данных о пассивных узлах (nodes.json)

### Структура загрузки

В `Data.lua` нет явной загрузки PassiveSkills, но логика следующая:

1. **Источники данных:**
   - Встроенные Lua-таблицы (если есть `Data/PassiveSkills.lua`)
   - Парсинг из `PassiveSkills.dat` файла игры (через специальные парсеры)
   - Данные из дерева навыков (tree JSON)

2. **Структура узла в PoB:**
   ```lua
   node = {
       id = 123,
       name = "Node Name",
       stats = {"+10 to Strength", "5% increased Life"},
       isKeystone = false,
       isNotable = false,
       isJewelSocket = false,
       classStart = false,
       masteryEffects = nil,
       -- Координаты и связи
       x = 100,
       y = 200,
       connections = {124, 125}
   }
   ```

3. **Обработка узлов:**
   - Узлы загружаются при инициализации дерева
   - Модификаторы извлекаются из поля `stats`
   - Keystones обрабатываются отдельно (список в `data.keystones`)

### Формат данных для nodes.json

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
      "masteryEffects": null,
      "x": 100,
      "y": 200,
      "connections": [124, 125]
    }
  }
}
```

## 3. Механизм LoadModule

### Как работает LoadModule

```lua
-- LoadModule загружает Lua файл и выполняет его
-- Файл должен возвращать таблицу или функцию
LoadModule("Data/Gems")  -- Загружает Data/Gems.lua
LoadModule("Data/Skills/act_str", data.skills, ...)  -- Передает параметры в модуль
```

### Структура модуля данных

```lua
-- Пример: Data/Gems.lua
return {
    ["Metadata/Items/Gems/Arc"] = {
        name = "Arc",
        gameId = "Metadata/Items/Gems/Arc",
        variantId = "Arc",
        grantedEffectId = "Arc",
        reqStr = 0,
        reqDex = 0,
        reqInt = 64,
        -- ... другие поля
    },
    -- ... другие гемы
}
```

## 4. Процесс обработки данных

### Для Skills (Gems):

1. **Загрузка:** `LoadModule("Data/Skills/"..type)` → загружает навыки по типу
2. **Обработка:**
   - `sanitiseText()` - очистка текста
   - `processMod()` - обработка модификаторов
   - Установка `statMap` metatable для динамических модификаторов
3. **Связывание:** `setupGem()` связывает гемы с навыками
4. **Специальные случаи:** Vaal гемы, альтернативные версии

### Для Passive Nodes:

1. **Загрузка:** Из Lua-таблиц или парсинг .dat файлов
2. **Обработка:**
   - Извлечение статистик из поля `stats`
   - Парсинг модификаторов через `ModParser`
   - Определение типа узла (keystone, notable, jewel socket)
3. **Применение:** Модификаторы применяются к `modDB` при выделении узла

## 5. Ключевые функции обработки

### makeSkillMod, makeFlagMod, makeSkillDataMod

```lua
local function makeSkillMod(modName, modType, modVal, flags, keywordFlags, ...)
    return {
        name = modName,
        type = modType,
        value = modVal,
        flags = flags or 0,
        keywordFlags = keywordFlags or 0,
        ...
    }
end

local function makeFlagMod(modName, ...)
    return makeSkillMod(modName, "FLAG", true, 0, 0, ...)
end

local function makeSkillDataMod(dataKey, dataValue, ...)
    return makeSkillMod("SkillData", "LIST", { key = dataKey, value = dataValue }, 0, 0, ...)
end
```

### processMod

```lua
local function processMod(grantedEffect, mod, statName)
    mod.source = grantedEffect.modSource
    -- Обработка вложенных модификаторов
    -- Проверка на GlobalEffect
    -- Обработка notMinionStat условий
end
```

## 6. Рекомендации для извлечения данных

### Для gems.json:

1. **Клонировать репозиторий PoB:**
   ```bash
   git clone https://github.com/PathOfBuildingCommunity/PathOfBuilding
   ```

2. **Извлечь данные из Lua файлов:**
   - `src/Data/Gems.lua` - основной файл с гемами
   - `src/Data/Skills/act_str.lua`, `act_dex.lua`, и т.д. - навыки
   - Использовать Lua парсер для конвертации в JSON

3. **Структура извлечения:**
   ```python
   # Псевдокод
   gems = {}
   for gemId, gem in data.gems.items():
       gems[gemId] = {
           "name": gem.name,
           "grantedEffectId": gem.grantedEffectId,
           "reqStr": gem.reqStr,
           "reqDex": gem.reqDex,
           "reqInt": gem.reqInt,
           # ... другие поля
       }
   ```

### Для nodes.json:

1. **Источники:**
   - Официальный JSON дерева навыков от GGG (если доступен)
   - Парсинг из `PassiveSkills.dat` файла игры
   - Извлечение из PoB's tree data

2. **Структура извлечения:**
   ```python
   # Псевдокод
   nodes = {}
   for nodeId, node in passiveTree.nodes.items():
       nodes[str(nodeId)] = {
           "name": node.name,
           "stats": node.stats,
           "isKeystone": node.isKeystone,
           "isNotable": node.isNotable,
           # ... другие поля
       }
   ```

## 7. Альтернативные источники данных

### Для gems.json:

1. **Path of Exile API** (если доступен)
2. **poedb.tw** - база данных Path of Exile
3. **Trade sites** - могут содержать данные о гемах
4. **Community projects** - другие проекты могут иметь JSON данные

### Для nodes.json:

1. **Официальный tree JSON** от GGG (если публикуется)
2. **poedb.tw** - может иметь данные дерева
3. **Community tools** - другие инструменты могут экспортировать данные

## 8. Текущая реализация в нашем проекте

### GameDataLoader

Наш `GameDataLoader` готов к загрузке данных из JSON файлов:

```python
loader = GameDataLoader()
nodes = loader.load_passive_tree_data()  # Ищет nodes.json
gems = loader.load_skill_gem_data()      # Ищет gems.json
```

### Требуется:

1. **Создать/извлечь nodes.json:**
   - Из PoB Lua файлов
   - Из .dat файлов игры
   - Из других источников

2. **Создать/извлечь gems.json:**
   - Из PoB Lua файлов (`Data/Gems.lua` + `Data/Skills/*.lua`)
   - Из других источников

3. **Скрипт извлечения:**
   - `scripts/fetch_pob_data.py` - базовая структура готова
   - Требуется реализация парсинга Lua файлов или использования других источников

## 9. Детальная структура данных

### Структура Skills (из Data/Skills/*.lua)

```lua
-- Пример: Data/Skills/act_str.lua
return {
    ["Arc"] = {
        name = "Arc",
        baseMods = {
            { name = "LightningDamageMin", type = "BASE", value = 8 },
            { name = "LightningDamageMax", type = "BASE", value = 47 },
        },
        qualityMods = {
            { name = "CastSpeed", type = "INC", value = 1, perLevel = 1 },
        },
        levelMods = {
            { name = "LightningDamageMin", type = "BASE", value = 1, perLevel = 1 },
            { name = "LightningDamageMax", type = "BASE", value = 3, perLevel = 1 },
        },
        statMap = {
            ["Damage"] = {
                { name = "LightningDamage", type = "BASE" }
            }
        },
        levels = {
            { 1, 0, 0, 0, 0 },  -- level, manaCost, damageEffectiveness, etc.
            { 2, 0, 0, 0, 0 },
            -- ...
        },
        castTime = 0.75,
        isSpell = true,
        isAttack = false,
    }
}
```

### Структура Gems (из Data/Gems.lua)

```lua
-- Пример: Data/Gems.lua
return {
    ["Metadata/Items/Gems/Arc"] = {
        name = "Arc",
        gameId = "Metadata/Items/Gems/Arc",
        variantId = "Arc",
        grantedEffectId = "Arc",  -- Ссылка на skill
        reqStr = 0,
        reqDex = 0,
        reqInt = 64,
        tags = {"spell", "lightning", "projectile"},
        tagString = "spell,lightning,projectile",
        naturalMaxLevel = 20,
        -- Vaal gems имеют secondaryGrantedEffectId
    }
}
```

### Структура Passive Nodes

```lua
-- Пример структуры узла (из PassiveSkills.dat или tree JSON)
node = {
    id = 123,
    name = "Node Name",
    stats = {
        "+10 to Strength",
        "5% increased Life"
    },
    isKeystone = false,
    isNotable = false,
    isJewelSocket = false,
    classStart = false,
    masteryEffects = nil,
    -- Геометрия дерева
    x = 100,
    y = 200,
    connections = {124, 125},
    -- Дополнительные поля
    group = 1,
    orbit = 0,
    orbitIndex = 0,
}
```

## 10. Процесс конвертации Lua → JSON

### Шаг 1: Парсинг Lua файлов

```python
# Псевдокод для парсинга Gems.lua
import lupa  # или другой Lua парсер

lua = lupa.LuaRuntime()
with open("Data/Gems.lua", "r") as f:
    content = f.read()
    # Выполнить Lua код
    gems_table = lua.execute(content)

    # Конвертировать в Python dict
    gems = {}
    for gem_id, gem_data in gems_table.items():
        gems[gem_id] = {
            "name": gem_data.name,
            "gameId": gem_data.gameId,
            "grantedEffectId": gem_data.grantedEffectId,
            # ... другие поля
        }
```

### Шаг 2: Обработка связей

```python
# Связать gems с skills
for gem_id, gem in gems.items():
    skill_id = gem["grantedEffectId"]
    if skill_id in skills:
        gem["skill"] = skills[skill_id]
```

### Шаг 3: Сохранение в JSON

```python
import json

with open("data/gems.json", "w") as f:
    json.dump({"gems": gems}, f, indent=2)
```

## 11. Альтернативные методы извлечения

### Метод 1: Использование PoB's export

Path of Building может экспортировать данные в XML/JSON формате через UI или API.

### Метод 2: Парсинг .dat файлов игры

Использовать парсеры для бинарных .dat файлов Path of Exile:
- `PassiveSkills.dat` → nodes.json
- `Skills.dat` → gems.json (частично)

### Метод 3: Community sources

- **poedb.tw** - веб-скрапинг данных
- **Path of Exile Wiki** - парсинг HTML
- **Trade sites** - извлечение данных о гемах

## Заключение

Path of Building использует модульную систему загрузки данных через `LoadModule()`. Данные хранятся в Lua-таблицах в файлах `src/Data/`.

**Ключевые выводы:**

1. **Gems загружаются из:**
   - `Data/Gems.lua` - основной файл с гемами
   - `Data/Skills/*.lua` - навыки, на которые ссылаются гемы
   - Связывание через `grantedEffectId`

2. **Nodes загружаются из:**
   - `PassiveSkills.dat` файла игры (парсинг)
   - Tree JSON файлов (если доступны)
   - Встроенных Lua таблиц (если есть)

3. **Для извлечения требуется:**
   - Lua парсер (lupa, lua-parser) или ручной парсинг
   - Конвертация в JSON формат
   - Сохранение в структуре, совместимой с `GameDataLoader`

4. **Наша реализация готова:**
   - `GameDataLoader` поддерживает загрузку из JSON
   - Структура данных совместима
   - Требуется только извлечение данных из PoB или альтернативных источников

**Следующие шаги:**
1. Реализовать Lua парсер для извлечения данных
2. Или использовать альтернативные источники (poedb.tw, API)
3. Создать nodes.json и gems.json файлы
4. Интегрировать в проект
