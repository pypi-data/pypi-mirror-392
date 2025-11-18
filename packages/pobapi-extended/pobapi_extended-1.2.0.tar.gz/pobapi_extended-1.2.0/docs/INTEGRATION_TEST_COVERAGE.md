# Integration Test Coverage

This document provides an overview of integration test coverage in the `pobapi-extended` project.

## Overview

Integration tests verify that multiple components work together correctly. Unlike unit tests (which test individual components in isolation), integration tests verify component interactions and real-world workflows.

## Coverage Summary

### Current Statistics

- **Total Integration Test Files:** 11
- **Total Test Classes:** 33
- **Total Test Methods:** 98
- **Covered Component Pairs:** 108 out of 351 possible
- **Coverage Percentage:** 30.8%

### Coverage by Component Group

| Group | Components | Coverage Status |
|-------|------------|-----------------|
| **API** | 3/3 | ✅ 100% |
| **Parsers** | 5/5 | ✅ 100% |
| **Serializers** | 2/2 | ✅ 100% |
| **Validators** | 2/2 | ✅ 100% |
| **Factory** | 1/1 | ✅ 100% |
| **Calculation** | 8/8 | ✅ 100% |
| **Parsers_Calc** | 5/5 | ✅ 100% |
| **Data** | 1/1 | ✅ 100% |
| **Trade** | 1/1 | ✅ 100% |
| **Crafting** | 1/1 | ✅ 100% |
| **Infrastructure** | 3/3 | ✅ 100% |

**All component groups are fully covered!**

## Covered Integrations

### API ↔ Calculation Engine
- ✅ `PathOfBuildingAPI` ↔ `CalculationEngine`
- ✅ `BuildModifier` ↔ `CalculationEngine`

### Parser ↔ Serializer
- ✅ `PathOfBuildingAPI` ↔ `BuildXMLSerializer`
- ✅ `PathOfBuildingAPI` ↔ `ImportCodeGenerator`
- ✅ `BuildBuilder` ↔ `BuildXMLSerializer`
- ✅ `BuildModifier` ↔ `BuildXMLSerializer`

### Calculator Components
- ✅ `ModifierSystem` ↔ `DamageCalculator`
- ✅ `ModifierSystem` ↔ `DefenseCalculator`
- ✅ `ModifierSystem` ↔ `ResourceCalculator`
- ✅ `ModifierSystem` ↔ `SkillStatsCalculator`
- ✅ `ModifierSystem` ↔ `MinionCalculator`
- ✅ `ModifierSystem` ↔ `PartyCalculator`
- ✅ `CalculationEngine` ↔ `ModifierSystem`

### Data ↔ Parsers
- ✅ `GameDataLoader` ↔ `PassiveTreeParser`
- ✅ `GameDataLoader` ↔ `ItemModifierParser`

### Validator ↔ Parser
- ✅ `InputValidator` ↔ `BuildInfoParser`
- ✅ `XMLValidator` ↔ `BuildInfoParser`

### Factory ↔ Builder
- ✅ `BuildFactory` ↔ `BuildBuilder`

### Trade API
- ✅ `TradeAPI` ↔ `PathOfBuildingAPI`

### Crafting API
- ✅ `ItemCraftingAPI` ↔ `PathOfBuildingAPI`
- ✅ `ItemCraftingAPI` ↔ `CalculationEngine`

### Infrastructure
- ✅ `BuildFactory` ↔ `HTTPClient`
- ✅ `BuildFactory` ↔ `AsyncHTTPClient`
- ✅ `Cache` ↔ `PathOfBuildingAPI`

### Parsers
- ✅ `TreesParser` ↔ `PathOfBuildingAPI`
- ✅ `TreesParser` ↔ `DefaultBuildParser`
- ✅ `TreesParser` ↔ `BuildFactory`
- ✅ `TreesParser` ↔ `CalculationEngine`
- ✅ `TreesParser` ↔ `PassiveTreeParser`

## Test Files

### test_api_calculation_engine_integration.py
- **Test Classes:** 2
- **Test Methods:** 7
- **Components:** BuildModifier, CalculationEngine, PathOfBuildingAPI
- **Coverage:** API ↔ Calculation Engine integration

### test_build_modifier_serializer_integration.py
- **Test Classes:** 2
- **Test Methods:** 6
- **Components:** BuildBuilder, BuildFactory, BuildModifier, BuildXMLSerializer, ImportCodeGenerator, PathOfBuildingAPI
- **Coverage:** BuildModifier ↔ Serializers, Factory ↔ Builder

### test_calculator_components_integration.py
- **Test Classes:** 3
- **Test Methods:** 15
- **Components:** CalculationEngine, ConfigModifierParser, DamageCalculator, GameDataLoader, ItemModifierParser, PassiveTreeParser, SkillModifierParser
- **Coverage:** Calculator components, Data ↔ Parsers

### test_calculator_modifier_integration.py
- **Test Classes:** 3
- **Test Methods:** 10
- **Components:** CalculationEngine, DamageCalculator, DefenseCalculator, MinionCalculator, ModifierSystem, PartyCalculator, ResourceCalculator, SkillStatsCalculator
- **Coverage:** Explicit ModifierSystem ↔ Calculator integrations

### test_crafting_api_integration.py
- **Test Classes:** 1
- **Test Methods:** 6
- **Components:** CalculationEngine, ItemCraftingAPI, PathOfBuildingAPI
- **Coverage:** Crafting API ↔ API integration

### test_infrastructure_integration.py
- **Test Classes:** 4
- **Test Methods:** 10
- **Components:** AsyncHTTPClient, BuildFactory, Cache, HTTPClient, PathOfBuildingAPI
- **Coverage:** Infrastructure components

### test_integration.py
- **Test Classes:** 5
- **Test Methods:** 11
- **Components:** BuildFactory, BuildInfoParser, DefaultBuildParser, InputValidator, ItemsParser, SkillsParser, TreesParser, XMLValidator
- **Coverage:** Validator ↔ Parser, Factory workflows

### test_parser_api_integration.py
- **Test Classes:** 4
- **Test Methods:** 9
- **Components:** CalculationEngine, ItemModifierParser, ModifierSystem, PassiveTreeParser, PathOfBuildingAPI, UniqueItemParser
- **Coverage:** Parser ↔ API integrations

### test_parser_serializer_integration.py
- **Test Classes:** 2
- **Test Methods:** 6
- **Components:** BuildBuilder, BuildXMLSerializer, ImportCodeGenerator, PathOfBuildingAPI
- **Coverage:** Parser ↔ Serializer round-trips

### test_trade_api_integration.py
- **Test Classes:** 1
- **Test Methods:** 8
- **Components:** BuildModifier, PathOfBuildingAPI, TradeAPI
- **Coverage:** Trade API ↔ API integration

### test_trees_parser_integration.py
- **Test Classes:** 6
- **Test Methods:** 10
- **Components:** BuildFactory, CalculationEngine, DefaultBuildParser, PassiveTreeParser, PathOfBuildingAPI, TreesParser
- **Coverage:** TreesParser integrations

## Understanding Integration Coverage

Integration coverage measures **component pair coverage** - which pairs of components are tested together. This is different from code coverage (which measures which lines of code are executed).

### Key Metrics

- **Component Pairs**: The fundamental unit of integration coverage. A pair `(A, B)` is considered "covered" if there's at least one test that involves both component `A` and component `B`.
- **Integration Scenarios**: Beyond just pairs, the reports also give an overview of how many test methods exist, providing a sense of the depth of testing.
- **Coverage Percentage**: The ratio of covered component pairs to the total possible component pairs. Note that a low percentage might be acceptable if many theoretical pairs don't represent meaningful integration points.

### Why 30.8% Coverage is Good

The 30.8% coverage percentage may seem low, but this is normal because:

1. **Not all pairs are meaningful**: Many component pairs don't have direct integration points
2. **Components work through layers**: Many components interact through intermediate layers (e.g., through `PathOfBuildingAPI`)
3. **Quality over quantity**: It's more important to cover critical integrations than all possible pairs
4. **All groups are covered**: Every component group has 100% coverage, meaning all components in each group are tested

## How to Analyze Integration Coverage

### Generate Coverage Reports

Run the following script from the project root:

```bash
python scripts/generate_integration_coverage_report.py
```

This script will:
- Scan all files in `tests/integrations/` to identify which components are mentioned in each test
- Determine which pairs of components are tested together
- Generate two report files in `tests/integrations/`:
  - `COVERAGE_REPORT.md`: A human-readable Markdown report
  - `coverage_report.json`: A machine-readable JSON report

### View Reports

You can view the generated reports:

```bash
cat tests/integrations/COVERAGE_REPORT.md
cat tests/integrations/coverage_report.json
```

### Analyze Missing Integrations

The `COVERAGE_REPORT.md` will highlight:
- **Coverage by Component Group**: A high-level overview of how well different functional groups are covered
- **Covered Integrations**: A list of component pairs that have at least one integration test
- **Missing Integrations**: A list of component pairs that *could* be integrated but currently lack dedicated tests

## Contributing to Integration Tests

When adding new integration tests:

1. **Place them in `tests/integrations/`**
2. **Use the `@pytest.mark.integration` marker**
3. **Clearly document which components are being tested together** in the test name, docstring, or comments
4. **Run the coverage analysis script** to update reports
5. **Review the updated coverage report** to see how coverage improved

## Running Integration Tests

```bash
# Run all integration tests
uv run pytest tests/integrations

# Run with marker
uv run pytest -m integration

# Run specific file
uv run pytest tests/integrations/test_api_calculation_engine_integration.py

# Run with coverage (code coverage, not integration coverage)
uv run pytest tests/integrations --cov=pobapi --cov-report=html
```

## Related Documentation

- **[Integration Coverage Analysis](INTEGRATION_COVERAGE_ANALYSIS.md)** - Research on integration coverage vs code coverage
- **[Tests README](../tests/README.md)** - General testing documentation
- **[API Reference](API_REFERENCE.md)** - Complete API documentation
