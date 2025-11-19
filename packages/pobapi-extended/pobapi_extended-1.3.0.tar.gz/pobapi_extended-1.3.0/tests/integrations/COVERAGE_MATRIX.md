# Integration Coverage Matrix

This matrix shows which component integrations are covered by tests.

## Component Integration Matrix

| Component A | Component B | Coverage | Test File |
|------------|-------------|----------|-----------|
| BuildBuilder | BuildXMLSerializer | ✅ | test_*.py |
| BuildFactory | BuildBuilder | ✅ | test_*.py |
| BuildModifier | BuildXMLSerializer | ✅ | test_*.py |
| BuildModifier | CalculationEngine | ✅ | test_*.py |
| CalculationEngine | ModifierSystem | ✅ | test_*.py |
| GameDataLoader | ItemModifierParser | ✅ | test_*.py |
| GameDataLoader | PassiveTreeParser | ✅ | test_*.py |
| InputValidator | BuildInfoParser | ✅ | test_*.py |
| ModifierSystem | DamageCalculator | ✅ | test_*.py |
| ModifierSystem | DefenseCalculator | ✅ | test_*.py |
| ModifierSystem | MinionCalculator | ✅ | test_*.py |
| ModifierSystem | PartyCalculator | ✅ | test_*.py |
| ModifierSystem | ResourceCalculator | ✅ | test_*.py |
| ModifierSystem | SkillStatsCalculator | ✅ | test_*.py |
| PathOfBuildingAPI | BuildXMLSerializer | ✅ | test_*.py |
| PathOfBuildingAPI | CalculationEngine | ✅ | test_*.py |
| PathOfBuildingAPI | ImportCodeGenerator | ✅ | test_*.py |
| XMLValidator | BuildInfoParser | ✅ | test_*.py |

## Coverage Statistics

- **Total Possible Pairs:** 496
- **Covered Pairs:** 18
- **Coverage Percentage:** 3.6%
