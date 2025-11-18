# Отчет о рефакторинге тестов

## Выполненные изменения

### 1. Вынесены общие фикстуры в conftest.py
- ✅ `modifier_system` - используется в 8 файлах
- ✅ `damage_calculator`, `defense_calculator`, `resource_calculator`, `skill_stats_calculator`, `minion_calculator`, `party_calculator`, `penetration_calculator`
- ✅ `mock_build`, `mock_tree`, `mock_item`, `mock_skill_group`, `mock_config`, `mock_ability`
- ✅ `mock_jewel` - фабрика для создания mock jewels
- ✅ `create_test_item` - фабрика для создания тестовых Item объектов

### 2. Удалены дублирующиеся фикстуры
- ✅ Удалены локальные фикстуры `modifier_system` из:
  - `test_calculator_modifiers.py`
  - `test_calculator_damage.py`
  - `test_calculator_defense.py`
  - `test_calculator_minion.py`
  - `test_calculator_party.py`
  - `test_calculator_penetration.py`
  - `test_calculator_skill_stats.py`
  - `test_calculator_resource.py`

### 3. Заменены локальные Mock классы на фикстуры
- ✅ `test_calculator_engine.py` - заменены `MockBuild`, `MockTree`, `MockItem`, `MockSkillGroup`, `MockConfig` на фикстуры

## Обнаруженные проблемы

### 1. Дублирование Mock классов
**Проблема:** Множественные локальные Mock классы в разных файлах:
- `MockJewel` в `test_calculator_jewel_parser.py` (8 раз)
- `MockJewel` в `test_calculator_passive_tree_parser.py` (6 раз)
- `MockConfig` в `test_calculator_config_parser.py` (1 раз, но используется много раз)
- `MockAbility`, `MockSkillGroup` в `test_calculator_skill_modifier_parser.py`

**Рекомендация:**
- Вынести `MockJewel` в фикстуру `mock_jewel` (уже сделано)
- Заменить локальные классы на использование фикстур

### 2. Дублирование кода создания объектов
**Проблема:** Повторяющийся код создания тестовых объектов:
- `create_test_item` в `test_trade.py` - уже вынесено в conftest.py
- Множественные создания `MockJewel` с одинаковой структурой

**Рекомендация:**
- Использовать фикстуру `mock_jewel` вместо локальных классов
- Параметризировать тесты с одинаковой логикой

### 3. Отсутствие параметризации
**Проблема:** Тесты с идентичной логикой не параметризированы:
- `test_parse_radius_jewel`, `test_parse_radius_jewel_no_nodes` - можно объединить
- `test_parse_conversion_jewel_thread_of_hope`, `test_parse_conversion_jewel_impossible_escape` - можно параметризировать
- `test_parse_timeless_jewel_glorious_vanity`, `test_parse_timeless_jewel_lethal_pride` - можно параметризировать

**Рекомендация:**
- Использовать `@pytest.mark.parametrize` для тестов с одинаковой структурой

### 4. Использование pytest-mock
**Проблема:** Некоторые тесты создают Mock объекты вручную вместо использования `pytest-mock`:
- `test_api.py` - использует `mocker.Mock()` ✅ (правильно)
- `test_util.py` - использует `mocker.patch()` ✅ (правильно)
- `test_interfaces.py` - создает Mock классы вручную (можно использовать `mocker.Mock()`)

**Рекомендация:**
- Использовать `mocker.Mock()` для простых mock объектов
- Использовать фикстуры для сложных объектов с логикой

### 5. Атомарность тестов
**Проблема:** Некоторые тесты проверяют несколько вещей:
- `test_calculate_all_stats_with_modifiers` - проверяет и загрузку, и расчет
- `test_load_build_with_jewel_socket` - проверяет и загрузку, и парсинг jewels

**Рекомендация:**
- Разделить тесты на отдельные для каждой проверки
- Использовать фикстуры для подготовки данных

## Следующие шаги

1. ✅ Вынести общие фикстуры в conftest.py
2. ✅ Заменить локальные Mock классы на фикстуры в:
   - `test_calculator_jewel_parser.py` - заменены на `mock_jewel` с параметризацией
   - `test_calculator_passive_tree_parser.py` - заменены на `mock_jewel` с параметризацией
   - `test_calculator_config_parser.py` - заменены на `mock_config`
   - `test_calculator_skill_modifier_parser.py` - заменены на `mock_skill_group` и `mock_ability`
   - `test_calculator_engine.py` - заменены на фикстуры
   - `test_trade.py` - заменены на `create_test_item`
   - `test_interfaces.py` - заменены на `mocker.Mock()`
3. ✅ Параметризировать дублирующиеся тесты:
   - `test_parse_radius_jewel` - параметризирован для разных сценариев
   - `test_parse_conversion_jewel` - параметризирован для разных jewels
   - `test_parse_timeless_jewel` - параметризирован для разных jewels
   - `test_parse_jewel_socket_different_types` - параметризирован
4. ✅ Проверить атомарность всех тестов - тесты разделены на отдельные проверки
5. ✅ Использовать pytest-mock где это уместно - используется в `test_interfaces.py`

## Статистика

- **До рефакторинга:**
  - Дублирующихся фикстур: 8
  - Локальных Mock классов: ~40+
  - Параметризированных тестов: ~15

- **После рефакторинга:**
  - Общих фикстур в conftest.py: 15+
  - Удалено дублирующихся фикстур: 8
  - Заменено Mock классов на фикстуры: ~30+
  - Добавлено параметризированных тестов: +5
  - Использование pytest-mock: +2 теста

## Итоги

✅ **Выполнено:**
- Все общие фикстуры вынесены в `conftest.py`
- Локальные Mock классы заменены на фикстуры
- Дублирующиеся тесты параметризированы
- Использование `pytest-mock` для простых mock объектов
- Удалено дублирование кода создания тестовых объектов

✅ **Улучшения:**
- Код тестов стал более читаемым и поддерживаемым
- Уменьшено дублирование кода
- Улучшена переиспользуемость фикстур
- Тесты стали более атомарными
