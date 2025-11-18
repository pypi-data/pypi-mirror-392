# Логика парсинга DAT файлов в PyPoE

## Обзор

DAT файлы в Path of Exile представляют собой бинарные базы данных, используемые для хранения игровых данных. PyPoE реализует сложную систему парсинга этих файлов с использованием архитектуры на основе композиции (Composition over Inheritance).

## Архитектура парсинга

### Компоненты системы

Система парсинга DAT файлов состоит из следующих основных компонентов:

1. **DatFile** - Главный интерфейс для работы с DAT файлами
2. **DatReader** - Координирует работу всех компонентов
3. **DatParser** - Парсит бинарную структуру файла
4. **DatCaster** - Выполняет приведение типов данных
5. **DatIndexer** - Строит индексы для быстрого поиска
6. **DatRecord** - Представляет отдельную строку данных
7. **DatValue** - Представляет отдельное значение (может быть указателем или списком)

### Структура DAT файла

DAT файл состоит из двух основных секций:

```
┌─────────────────────────────────┐
│ Header (4 bytes)                │
│ - Количество строк (uint32)     │
├─────────────────────────────────┤
│ Table Section (фиксированная)   │
│ - Массив указателей на данные   │
│ - Размер = rows × row_size      │
├─────────────────────────────────┤
│ Magic Number (8 bytes)           │
│ 0xBBBBBBBBBBBBBBBB              │
├─────────────────────────────────┤
│ Data Section (переменная)       │
│ - Строки (UTF-16)               │
│ - Списки значений                │
│ - Вложенные структуры           │
└─────────────────────────────────┘
```

## Процесс парсинга

### Этап 1: Инициализация (DatReader.__init__)

1. **Загрузка спецификации**: Спецификация загружается из SQLite базы данных или Python модулей
2. **Создание компонентов**:
   - `DatCaster` - для приведения типов
   - `DatParser` - для парсинга бинарных данных
   - `DatIndexer` - для построения индексов

3. **Подготовка спецификации**:
   - Извлечение спецификации для конкретного файла
   - Подготовка информации о колонках
   - Определение уникальных колонок для индексации

### Этап 2: Парсинг структуры файла (DatParser.parse_file)

```python
def parse_file(self, raw: bytes | BytesIO):
    # 1. Найти magic number (разделитель между table и data секциями)
    data_offset = file_raw.find(DAT_FILE_MAGIC_NUMBER)

    # 2. Прочитать количество строк из заголовка
    table_rows = struct.unpack("<I", file_raw[0:4])[0]

    # 3. Вычислить размер одной строки в table секции
    table_length = data_offset - _TABLE_OFFSET
    table_record_length = table_length // table_rows

    # 4. Валидация: проверить соответствие размера спецификации реальному
    if self.cast_size != table_record_length:
        raise SpecificationError(...)
```

**Ключевые моменты:**
- Magic number `0xBBBBBBBBBBBBBBBB` разделяет фиксированную и переменную секции
- Размер строки в table секции должен точно соответствовать спецификации
- Это критическая проверка целостности данных

### Этап 3: Подготовка спецификации типов (DatParser.__init__)

Для каждой колонки из спецификации:

```python
for i, key in enumerate(specification.columns_data):
    k = specification.fields[key]
    casts = []
    remainder = k.type

    # Рекурсивный парсинг типа (например, "ref|list|int")
    while remainder:
        remainder, cast_type = self.caster.parse_cast_string(remainder)
        casts.append(cast_type)

    # Сохранить информацию о кастинге
    self.cast_spec.append((k, casts))
    self.cast_size += casts[0][1]  # Размер первого элемента
```

**Примеры типов:**
- `"int"` → `CastTypes.VALUE`, размер 4 байта
- `"ref|string"` → `CastTypes.POINTER` → `CastTypes.STRING`
- `"ref|list|int"` → `CastTypes.POINTER_LIST` → `CastTypes.VALUE`
- `"ref|ref|ref|int"` → Вложенные указатели

### Этап 4: Парсинг строк (DatParser.parse_row)

Для каждой строки в table секции:

```python
def parse_row(self, file_raw, data_offset, rowid, table_record_length, parent):
    # 1. Вычислить смещение строки в table секции
    offset = _TABLE_OFFSET + rowid * table_record_length

    # 2. Извлечь сырые данные строки
    data_raw = file_raw[offset : offset + table_record_length]

    # 3. Распаковать всю строку одним вызовом struct.unpack
    row_unpacked = struct.unpack(self.cast_row, data_raw)

    # 4. Для каждой колонки применить кастинг
    for spec, casts in self.cast_spec:
        if casts[0][0] == CastTypes.POINTER_LIST:
            # Список: размер + указатель
            cell_data = row_unpacked[i : i + 2]
        else:
            # Обычное значение или указатель
            cell_data = (row_unpacked[i],)

        # Применить кастинг (может быть рекурсивным)
        row_data.append(
            self.caster.cast_from_spec(
                file_raw, data_offset, spec, casts,
                data=cell_data, offset=offset
            )
        )
```

**Оптимизация:**
- Использование `struct.unpack` для всей строки сразу вместо отдельных вызовов
- Это значительно быстрее, чем парсинг каждого поля отдельно

### Этап 5: Приведение типов (DatCaster.cast_from_spec)

Это рекурсивная функция, которая обрабатывает различные типы данных:

#### 5.1 Простые значения (VALUE)

```python
if casts[0][0] == CastTypes.VALUE:
    # Распаковать значение из бинарных данных
    ivalue = struct.unpack("<" + casts[0][2], file_raw[offset:offset+size])[0]

    # Обработать специальные null-значения
    if ivalue in (0xFEFEFEFE, 0xFFFFFFFF, ...):
        ivalue = None

    return DatValue(ivalue, offset, size, parent, specification)
```

#### 5.2 Строки (STRING)

```python
elif casts[0][0] == CastTypes.STRING:
    # Найти конец строки (4 нулевых байта)
    offset_new = file_raw.find(b"\x00\x00\x00\x00", offset)

    # Декодировать UTF-16
    string = file_raw[offset:offset_new].decode("utf-16")

    return DatValue(string, offset, offset_new - offset + 4, ...)
```

**Особенности:**
- Строки в DAT файлах хранятся в UTF-16
- Завершаются последовательностью `\x00\x00\x00\x00`
- Длина строки может быть нулевой (пустая строка)

#### 5.3 Указатели (POINTER)

```python
elif casts[0][0] == CastTypes.POINTER:
    # Прочитать указатель (4 или 8 байт)
    pointer_value = struct.unpack("<I", file_raw[offset:offset+4])[0]

    # Вычислить реальный offset в data секции
    data_offset_actual = pointer_value + data_offset

    # Рекурсивно обработать данные по указателю
    if not casts[1:]:  # ref|string
        string_casts = [(CastTypes.STRING, 0, "")]
        result.child = self.cast_from_spec(..., string_casts, ...)
    else:  # ref|int, ref|ref|int, etc.
        result.child = self.cast_from_spec(..., casts[1:], ...)
```

**Рекурсивность:**
- Указатели могут быть вложенными: `ref|ref|ref|int`
- Каждый уровень указателя разыменовывается рекурсивно
- Специальная обработка для `ref|string` (указатель на строку)

#### 5.4 Списки (POINTER_LIST)

```python
elif casts[0][0] == CastTypes.POINTER_LIST:
    # Прочитать размер списка и указатель
    list_size, list_pointer = struct.unpack("<II", file_raw[offset:offset+8])

    data_offset_actual = list_pointer + data_offset

    # Обработать каждый элемент списка
    result.children = []
    for i in range(0, list_size):
        result.children.append(
            self.cast_from_spec(
                file_raw, data_offset, specification,
                casts[1:],  # Тип элементов списка
                result,
                data_offset_actual + i * element_size
            )
        )
```

**Структура списка:**
- Первые 4 байта: размер списка (количество элементов)
- Следующие 4 байта: указатель на данные в data секции
- Элементы расположены последовательно в data секции

## Особенности PassiveSkills.dat

### Структура файла

`PassiveSkills.dat` содержит информацию о пассивных навыках в дереве навыков Path of Exile. Файл имеет интересную структуру с виртуальными полями.

### Виртуальные поля

Виртуальные поля - это вычисляемые поля, которые не хранятся напрямую в файле, а создаются на основе других полей:

```python
"PassiveSkills.dat": [
    VirtualField(
        name="StatValues",
        fields=("Stat1Value", "Stat2Value", "Stat3Value", "Stat4Value", "Stat5Value"),
    ),
    VirtualField(
        name="StatsZip",
        fields=("Stats", "StatValues"),
        zip=True,  # Объединяет два списка в пары
    ),
]
```

### Обработка виртуальных полей

Виртуальные поля обрабатываются в `DatRecord.__getitem__`:

```python
def __getitem__(self, item: str | int):
    if isinstance(item, str):
        if item in self.parent.table_columns:
            # Обычное поле
            return list.__getitem__(self, self.parent.table_columns[item]["index"])
        elif item in self.parent.specification["virtual_fields"]:
            # Виртуальное поле
            field = self.parent.specification["virtual_fields"][item]

            # Получить значения из исходных полей
            value = [self[fn] for fn in field["fields"]]

            # Если zip=True, объединить в пары
            if field["zip"]:
                value = zip(*value, strict=False)

            return value
```

### Пример использования StatsZip

Для `PassiveSkills.dat` виртуальное поле `StatsZip` объединяет:
- `Stats` - список ключей статистик (ссылки на `Stats.dat`)
- `StatValues` - список значений для этих статистик

Результат - итератор пар `(stat_key, stat_value)`:

```python
passive = reader[0]  # Первый пассивный навык

# Доступ к виртуальному полю
for stat_key, stat_value in passive["StatsZip"]:
    print(f"Stat: {stat_key}, Value: {stat_value}")
```

**Преимущества:**
- Упрощает работу с парными данными
- Не требует ручного сопоставления индексов
- Автоматически обрабатывает случаи с разным количеством элементов

### Типичные поля в PassiveSkills.dat

На основе анализа кода экспортера, файл содержит следующие поля:

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

### Обработка списков статистик

В экспортере используется следующий подход:

```python
stat_ids = []
values = []

for i in range(0, self._MAX_STAT_ID):  # MAX_STAT_ID = 5
    try:
        stat = passive["StatsKeys"][i]
    except IndexError:
        break

    stat_ids.append(stat["Id"])
    values.append(passive[f"Stat{i+1}Value"])

# Использование виртуального поля было бы проще:
for stat_key, stat_value in passive["StatsZip"]:
    stat_ids.append(stat_key["Id"])
    values.append(stat_value)
```

## Рекурсивная обработка указателей

### Пример: ref|ref|ref|int

Для типа `ref|ref|ref|int` происходит следующее:

1. **Первый уровень** (`ref|`):
   - Читается указатель (4 байта)
   - Вычисляется offset в data секции
   - Переход к следующему уровню

2. **Второй уровень** (`ref|`):
   - По указателю читается следующий указатель
   - Вычисляется новый offset
   - Переход к следующему уровню

3. **Третий уровень** (`ref|`):
   - По указателю читается еще один указатель
   - Вычисляется финальный offset
   - Переход к значению

4. **Финальное значение** (`int`):
   - По финальному offset читается 32-битное целое число
   - Возвращается как `DatValue`

**Визуализация:**
```
Table Section:
  [pointer1] → Data Section offset 1000

Data Section (offset 1000):
  [pointer2] → Data Section offset 2000

Data Section (offset 2000):
  [pointer3] → Data Section offset 3000

Data Section (offset 3000):
  [int value: 42]
```

## Обработка специальных значений

### Null-значения

DAT файлы используют специальные значения для обозначения NULL:

- `0xFEFEFEFE` - 32-битный NULL
- `0xFFFFFFFF` - 32-битный NULL (альтернативный)
- `0xFEFEFEFEFEFEFEFE` - 64-битный NULL
- `-0x1010102` - Отрицательный NULL

При парсинге эти значения автоматически преобразуются в `None`.

### Пустые строки и списки

- **Пустые строки**: Занимают 4 байта (только терминатор `\x00\x00\x00\x00`)
- **Пустые списки**: Размер = 0, указатель может указывать на любое место
- **Несколько пустых списков**: Могут указывать на одно и то же место

## Индексация

### Построение индексов (DatIndexer)

Индексы строятся для быстрого поиска по колонкам:

```python
def build_index(self, table_data, column=None):
    # Определить тип колонки
    if column in self.columns_unique:
        # 1-to-1: словарь {value: DatRecord}
        self.index[column] = {}
        for row in table_data:
            self.index[column][row[column]] = row
    else:
        # 1-to-N: defaultdict {value: [DatRecord, ...]}
        self.index[column] = defaultdict(list)
        for row in table_data:
            self.index[column][row[column]].append(row)
```

### Использование индексов

```python
# Построить индекс по колонке "Id"
reader.build_index("Id")

# Быстрый поиск
passive = reader.index["Id"]["SomePassiveId"]
```

## Оптимизации

### 1. Единый unpack для строки

Вместо множественных вызовов `struct.unpack` для каждого поля, вся строка распаковывается одним вызовом:

```python
# Плохо (медленно):
for field in fields:
    value = struct.unpack("<I", data[offset:offset+4])[0]
    offset += 4

# Хорошо (быстро):
row_unpacked = struct.unpack("<IIIQQ...", data)
# Использовать значения из row_unpacked
```

### 2. Использование __slots__

`DatValue` и `DatRecord` используют `__slots__` для уменьшения потребления памяти:

```python
class DatValue:
    __slots__ = ["value", "size", "offset", "parent", "specification", "children", "child"]
```

Это дает ~35% ускорение при создании миллионов экземпляров.

### 3. Ленивая загрузка спецификаций

Спецификации загружаются из SQLite базы данных по требованию, а не все сразу. Это значительно уменьшает потребление памяти.

## Пример полного цикла парсинга

```python
# 1. Загрузка спецификации
from PyPoE.poe.file.specification.repository import SQLiteSpecRepository
from PyPoE.poe.constants import VERSION

repo = SQLiteSpecRepository(Path("data/specifications/stable.db"))
spec = repo.get_spec(VERSION.STABLE)

# 2. Создание DatFile
from PyPoE.poe.file.dat import DatFile

df = DatFile("PassiveSkills.dat")

# 3. Чтение файла
with open("PassiveSkills.dat", "rb") as f:
    reader = df.read(f, specification=spec)

# 4. Построение индекса
reader.build_index("Id")

# 5. Использование данных
passive = reader.index["Id"]["SomePassiveId"]

# Доступ к полям
print(passive["Name"])
print(passive["SkillPointsGranted"])

# Использование виртуального поля
for stat_key, stat_value in passive["StatsZip"]:
    print(f"{stat_key['Id']}: {stat_value}")
```

## Заключение

Система парсинга DAT файлов в PyPoE представляет собой сложную, но эффективную архитектуру:

- **Модульность**: Каждый компонент отвечает за свою задачу
- **Рекурсивность**: Поддержка вложенных структур любой глубины
- **Виртуальные поля**: Упрощение работы с парными данными
- **Оптимизация**: Минимизация вызовов функций и потребления памяти
- **Гибкость**: Поддержка различных типов данных и структур

Особенно интересна обработка `PassiveSkills.dat` с виртуальным полем `StatsZip`, которое автоматически объединяет списки статистик и их значений в удобные пары для обработки.
