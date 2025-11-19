# Integration Tests

This directory contains integration tests that verify multiple components work together correctly.

## Coverage Analysis

To analyze integration test coverage, use the provided scripts:

```bash
# Generate coverage report
python scripts/generate_integration_coverage_report.py

# Analyze integration tests
python scripts/analyze_integration_coverage.py
```

## Coverage Reports

- **COVERAGE_REPORT.md** - Markdown report with coverage matrix
- **coverage_report.json** - JSON report for programmatic access
- **INTEGRATION_COVERAGE.md** - Manual tracking of integrations

## Understanding Integration Coverage

Unlike unit test coverage (measured by `pytest-cov`), integration coverage measures:

1. **Component Pairs**: Which pairs of components are tested together
2. **Integration Scenarios**: Real-world workflows involving multiple components
3. **Data Flow**: How data flows between components

### Example

A test that uses both `PathOfBuildingAPI` and `CalculationEngine` covers the integration:
- `PathOfBuildingAPI` ↔ `CalculationEngine`

## Current Coverage

See `COVERAGE_REPORT.md` for detailed coverage statistics and `docs/INTEGRATION_TEST_COVERAGE.md` for comprehensive documentation.

### Key Metrics

- **Total Integration Tests**: 98 test methods across 11 files
- **Covered Component Pairs**: 108 integrations
- **Coverage Percentage**: 30.8% (all component groups at 100%)
- **Coverage Areas**:
  - ✅ API ↔ Calculation Engine
  - ✅ Parser ↔ Serializer
  - ✅ Calculator Components
  - ✅ Validator ↔ Parser
  - ✅ Trade API
  - ✅ Crafting API
  - ✅ Infrastructure (HTTP, Cache)
  - ✅ All Parsers (including TreesParser)

## Adding New Integration Tests

When adding new integration tests:

1. **Identify the integration**: Which components are being tested together?
2. **Update coverage**: Run the coverage analysis script
3. **Document**: Update `INTEGRATION_COVERAGE.md` if needed

### Example Test Structure

```python
"""Integration tests for ComponentA and ComponentB."""

import pytest

pytestmark = pytest.mark.integration

from pobapi.component_a import ComponentA
from pobapi.component_b import ComponentB


class TestComponentAComponentBIntegration:
    """Test integration between ComponentA and ComponentB."""

    def test_components_work_together(self):
        """Test that components work together."""
        a = ComponentA()
        b = ComponentB()
        result = b.process(a.get_data())
        assert result is not None
```

## Running Integration Tests

```bash
# Run all integration tests
uv run pytest tests/integrations

# Run with marker
uv run pytest -m integration

# Run specific file
uv run pytest tests/integrations/test_api_calculation_engine_integration.py
```
