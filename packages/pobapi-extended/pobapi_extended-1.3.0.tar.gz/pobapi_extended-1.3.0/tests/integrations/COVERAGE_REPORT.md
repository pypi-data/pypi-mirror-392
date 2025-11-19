# Integration Test Coverage Report

This report shows which component integrations are covered by integration tests.

## Summary

- **Total Integration Test Files:** 11
- **Total Test Classes:** 33
- **Total Test Methods:** 98

## Coverage by Component Group

> **Note:** [FULL] indicates each listed component has at least one test, whereas the overall coverage percentage (see line 125) reflects the fraction of possible component-pair integrations exercised by tests.

| Group | Components | Coverage Status |
|-------|------------|-----------------|
| API | 3/3 | [FULL] |
| Parsers | 5/5 | [FULL] |
| Serializers | 2/2 | [FULL] |
| Validators | 2/2 | [FULL] |
| Factory | 1/1 | [FULL] |
| Calculation | 8/8 | [FULL] |
| Parsers_Calc | 5/5 | [FULL] |
| Data | 1/1 | [FULL] |
| Trade | 1/1 | [FULL] |
| Crafting | 1/1 | [FULL] |
| Infrastructure | 3/3 | [FULL] |

## Covered Integrations

| Component A | Component B | Test File |
|------------|-------------|-----------|
| BuildBuilder | BuildXMLSerializer | test_parser_serializer_integration.py |
| BuildFactory | BuildBuilder | test_build_modifier_serializer_integration.py |
| BuildModifier | BuildXMLSerializer | test_build_modifier_serializer_integration.py |
| BuildModifier | CalculationEngine | test_api_calculation_engine_integration.py |
| CalculationEngine | ModifierSystem | test_parser_api_integration.py |
| GameDataLoader | ItemModifierParser | test_calculator_components_integration.py |
| GameDataLoader | PassiveTreeParser | test_calculator_components_integration.py |
| InputValidator | BuildInfoParser | test_integration.py |
| ModifierSystem | DamageCalculator | test_calculator_modifier_integration.py |
| ModifierSystem | DefenseCalculator | test_calculator_modifier_integration.py |
| ModifierSystem | MinionCalculator | test_calculator_modifier_integration.py |
| ModifierSystem | PartyCalculator | test_calculator_modifier_integration.py |
| ModifierSystem | ResourceCalculator | test_calculator_modifier_integration.py |
| ModifierSystem | SkillStatsCalculator | test_calculator_modifier_integration.py |
| PathOfBuildingAPI | BuildXMLSerializer | test_parser_serializer_integration.py |
| PathOfBuildingAPI | CalculationEngine | test_trees_parser_integration.py |
| PathOfBuildingAPI | ImportCodeGenerator | test_parser_serializer_integration.py |
| XMLValidator | BuildInfoParser | test_integration.py |

## Test Files

### test_api_calculation_engine_integration.py

- **Test Classes:** 2
- **Test Methods:** 7
- **Components:** BuildModifier, CalculationEngine, PathOfBuildingAPI

### test_build_modifier_serializer_integration.py

- **Test Classes:** 2
- **Test Methods:** 6
- **Components:** BuildBuilder, BuildFactory, BuildModifier, BuildXMLSerializer, ImportCodeGenerator, PathOfBuildingAPI

### test_calculator_components_integration.py

- **Test Classes:** 3
- **Test Methods:** 15
- **Components:** CalculationEngine, ConfigModifierParser, DamageCalculator, GameDataLoader, ItemModifierParser, PassiveTreeParser, SkillModifierParser

### test_calculator_modifier_integration.py

- **Test Classes:** 3
- **Test Methods:** 10
- **Components:** CalculationEngine, DamageCalculator, DefenseCalculator, MinionCalculator, ModifierSystem, PartyCalculator, ResourceCalculator, SkillStatsCalculator

### test_crafting_api_integration.py

- **Test Classes:** 1
- **Test Methods:** 6
- **Components:** CalculationEngine, ItemCraftingAPI, PathOfBuildingAPI

### test_infrastructure_integration.py

- **Test Classes:** 4
- **Test Methods:** 10
- **Components:** AsyncHTTPClient, BuildFactory, Cache, HTTPClient, PathOfBuildingAPI

### test_integration.py

- **Test Classes:** 5
- **Test Methods:** 11
- **Components:** BuildFactory, BuildInfoParser, DefaultBuildParser, InputValidator, ItemsParser, SkillsParser, XMLValidator

### test_parser_api_integration.py

- **Test Classes:** 4
- **Test Methods:** 9
- **Components:** CalculationEngine, ItemModifierParser, ModifierSystem, PassiveTreeParser, PathOfBuildingAPI, UniqueItemParser

### test_parser_serializer_integration.py

- **Test Classes:** 2
- **Test Methods:** 6
- **Components:** BuildBuilder, BuildXMLSerializer, ImportCodeGenerator, PathOfBuildingAPI

### test_trade_api_integration.py

- **Test Classes:** 1
- **Test Methods:** 8
- **Components:** BuildModifier, PathOfBuildingAPI, TradeAPI

### test_trees_parser_integration.py

- **Test Classes:** 6
- **Test Methods:** 10
- **Components:** BuildFactory, CalculationEngine, DefaultBuildParser, PassiveTreeParser, PathOfBuildingAPI, TreesParser

## Coverage Statistics

- **Total Components:** 32
- **Total Possible Pairs:** 496
- **Covered Integrations:** 18
- **Coverage Percentage:** 3.6%
