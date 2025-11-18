# Анализ непокрытых строк тестами - ФИНАЛЬНЫЙ ОТЧЕТ

## Резюме

Из 5 групп непокрытых строк:
- ✅ 1 группа - формула корректна, строка математически недостижима (safety fallback)
- ⚠️ 2 группы - защитные блоки, требуют мокирования методов для покрытия
- ⚠️ 1 группа - возможно dead code, требует решения об удалении или исправлении логики
- ⚠️ 1 группа - 51 строка редких паттернов, требует решения о необходимости покрытия

---

## 1. `pobapi/calculator/defense.py:226` ✅ ФОРМУЛА КОРРЕКТНА

**Строка:** `return total_pool * 2.0` (fallback при `discriminant < 0`)

**Формула:**
```python
discriminant = b² - 4ac
где a = 10, b = -10*total_pool, c = -total_pool*armour
discriminant = (-10*total_pool)² - 4*10*(-total_pool*armour)
             = 100*total_pool² + 40*total_pool*armour
```

**Вывод:** Дискриминант **всегда положительный** для положительных `total_pool` и `armour`. Проверено математически.

**Статус:** Строка 226 математически недостижима при корректных входных данных. Является **safety fallback** для edge cases (floating point errors, некорректные входные данные).

**Решение:**
- ✅ Формула корректна, оставить как есть
- ⚠️ Текущий тест мокает весь метод → реальная строка 226 не выполняется
- **Рекомендация:** Принять 99% покрытия как достаточное для этого модуля

---

## 2. `pobapi/calculator/engine.py:268-270` ⚠️ ЗАЩИТНЫЙ БЛОК

**Строки:**
```python
except AttributeError:
    # If build_data doesn't have party information, skip
    pass
```

**Проблема:** Код использует `hasattr()` для проверок на строках 193, 199, 218:
```python
config = build_data.config if hasattr(build_data, "config") else None
if config and hasattr(config, "party_members"):
if not party_members and hasattr(build_data, "party_members"):
```

Поэтому `AttributeError` не возникает при обычном доступе к атрибутам.

**Когда покрывается:** Внешний `except AttributeError` (строки 268-270) ловит ошибки из:
- `self.party_calc.calculate_party_aura_effectiveness(temp_context)` (строка 255)
- `self.party_calc.process_party(...)` (строка 259)
- `self.modifiers.add_modifiers(party_modifiers)` (строка 266)

**Решение:** Мокировать методы `self.party_calc` или `self.modifiers`, чтобы они вызывали `AttributeError`.

**Статус:** Частично исправлено в tests/test_calculator_engine.py

---

## 3. `pobapi/calculator/engine.py:492-493` ⚠️ ЗАЩИТНЫЙ БЛОК

**Строки:**
```python
except AttributeError:
    pass
```

**Проблема:** Аналогично пункту 2, код не использует `hasattr()` на строке 467, но внутренний `try-except` на строках 466-491 уже ловит `AttributeError` и `TypeError`.

**Когда покрывается:** Строки 492-493 ловят `AttributeError` из:
- `build_data.skill_groups` (строка 467) - если `build_data` это `None` или объект без метода `__getattribute__`
- Других операций вне внутреннего `try-except`

**Решение:** Аналогично пункту 2, нужно создать ситуацию, когда `AttributeError` возникает вне внутреннего блока.

**Статус:** Частично исправлено в tests/test_calculator_engine.py

---

## 4. `pobapi/api.py:640` ⚠️ ВОЗМОЖНО DEAD CODE

**Строка:** `item_sets_list.append(modified_set)` (когда `index == len(item_sets_list)`)

**Логика:**
```python
while len(item_sets_list) <= index:  # Строка 635
    item_sets_list.append(ItemSetBuilder._build_single(empty_set_data))
# После цикла: len(item_sets_list) > index ВСЕГДА
if index == len(item_sets_list):  # Строка 639 - ВСЕГДА FALSE
    item_sets_list.append(modified_set)  # Строка 640 - НЕДОСТИЖИМА
else:
    item_sets_list[index] = modified_set  # Строка 642
```

**Математическое доказательство:**
- Цикл `while` выполняется пока `len <= index`
- Цикл завершается когда `len > index`
- После цикла: `len(item_sets_list) > index`
- Поэтому: `index == len(item_sets_list)` не может быть `True`

**Вывод:** Строка 640 **логически недостижима** при текущей реализации.

**Решение:**
1. **Удалить строки 639-640** как dead code
2. Или **пересмотреть логику**, если есть сценарий, когда `index == len`

**Рекомендация:** Удалить строки 639-640 и оставить только `item_sets_list[index] = modified_set`

---

## 5. `pobapi/calculator/item_modifier_parser.py` (51 непокрытых строк) ⚠️ РЕДКИЕ ПАТТЕРНЫ

**Непокрытые диапазоны:**
- 305-315: `TO_MAXIMUM_PATTERN` - паттерн "+X to maximum Y"
- 359-360: `else` ветка в обработке "per attribute" паттернов
- 407-432: `PER_PATTERN` - обработка паттернов "X per Y" (level, charge, unknown)
- 480-496: `PER_ATTRIBUTE_PATTERN` - обработка паттернов "X per Y attribute"
- 517-526: `CHANCE_WHEN_PATTERN` - обработка паттернов "X% chance to Y when Z" (когда effect не найден в mappings)
- 546-555: `CHANCE_ON_PATTERN` - обработка паттернов "X% chance to Y on Z" (когда effect не найден в mappings)
- 575-584: Внутренний парсинг для "veiled" модификаторов
- 620-631: Внутренний парсинг для "corrupted" модификаторов
- 666-677: Обработка уникальных предметов в `parse_item_text`
- 696-929: Множество `else` веток для "to all" паттернов с различными типами статов

**Проблема:** Многие из этих строк являются:
- `else` ветками, которые выполняются когда паттерн не совпадает
- Обработкой редких паттернов модификаторов
- Некоторые могут быть недостижимыми при текущей логике парсинга

**Решение:** Нужны конкретные примеры item text с этими паттернами для написания тестов.

**Статус:** Требует решения - нужно ли покрывать все 51 строку или принять текущее покрытие (86%)

---

## Рекомендации

1. **defense.py:226**: Принять 99% покрытия, добавить комментарий о математической недостижимости
2. **engine.py:268-270, 492-493**: Завершить исправление тестов с мокированием методов
3. **api.py:640**: Удалить как dead code или пересмотреть логику
4. **item_modifier_parser.py**: Решить, нужно ли покрывать все редкие паттерны или принять 86% покрытия

**Текущее общее покрытие:** ~95%

**Цель:** 95-97% (достижимо без покрытия математически/логически недостижимых строк)
