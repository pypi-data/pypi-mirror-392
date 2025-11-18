# Test Structure

This directory contains the test suite for `pobapi-extended`, organized into unit and integration tests.

## Directory Structure

```
tests/
├── unit/              # Unit tests for individual components
│   ├── conftest.py    # Shared fixtures for unit tests
│   └── test_*.py      # Unit test files
├── integrations/      # Integration tests for component interactions
│   ├── conftest.py    # Shared fixtures for integration tests
│   └── test_*.py      # Integration test files
└── conftest.py        # Root-level fixtures (if needed)
```

## Running Tests

### Run all tests
```bash
uv run pytest
```

### Run only unit tests
```bash
uv run pytest tests/unit
```

### Run only integration tests
```bash
uv run pytest tests/integrations
```

### Run tests by marker
```bash
# Unit tests
uv run pytest -m unit

# Integration tests
uv run pytest -m integration
```

### Run specific test file
```bash
uv run pytest tests/unit/test_api.py
```

### Run with coverage
```bash
# Unit test coverage (code coverage)
uv run pytest tests/unit --cov=pobapi --cov-report=html

# Integration test coverage (integration coverage)
python scripts/generate_integration_coverage_report.py
```

## Test Categories

### Unit Tests (`tests/unit/`)

Unit tests focus on testing individual components in isolation:
- API classes (`test_api.py`)
- Parsers (`test_parsers.py`)
- Validators (`test_validators.py`)
- Calculators (`test_calculator_*.py`)
- Builders (`test_builders.py`, `test_build_builder.py`)
- Serializers (`test_serializers.py`)
- Models (`test_model_validators.py`)
- Utilities (`test_util.py`, `test_cache.py`)

### Integration Tests (`tests/integrations/`)

Integration tests verify that multiple components work together correctly:
- **API and CalculationEngine** (`test_api_calculation_engine_integration.py`)
  - Loading builds from API into calculation engine
  - Calculating stats from API build data
  - Converting API data to engine modifiers

- **Parser and Serializer** (`test_parser_serializer_integration.py`)
  - XML parsing and serialization round-trips
  - Import code generation and parsing
  - Build modifications and serialization

- **Calculator Components** (`test_calculator_components_integration.py`)
  - Modifier system with different calculators
  - GameDataLoader with parsers
  - Multiple calculators working together

- **Component Integration** (`test_integration.py`)
  - Validators and parsers
  - Factory and builders
  - End-to-end workflows

## Test Markers

Tests are marked for easy filtering:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests

## Fixtures

### Unit Test Fixtures (`tests/unit/conftest.py`)

- `build` - PathOfBuildingAPI instance from test data
- `sample_xml_root` - Sample XML root element
- `sample_xml` - Sample XML string
- `minimal_xml` - Minimal valid XML
- `modifier_system` - ModifierSystem instance
- `damage_calculator`, `defense_calculator`, etc. - Calculator instances
- `mock_jewel`, `mock_build`, `mock_item`, etc. - Mock objects

### Integration Test Fixtures (`tests/integrations/conftest.py`)

- `build` - PathOfBuildingAPI instance from test data
- `sample_xml_root` - Sample XML root element
- `sample_xml` - Sample XML string
- `minimal_xml` - Minimal valid XML

## Writing New Tests

### Unit Test Example

```python
"""Tests for MyComponent."""

import pytest

from pobapi.my_module import MyComponent


class TestMyComponent:
    """Tests for MyComponent."""

    def test_basic_functionality(self):
        """Test basic functionality."""
        component = MyComponent()
        result = component.do_something()
        assert result is not None
```

### Integration Test Example

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

## Integration Test Coverage

Integration test coverage is different from code coverage. It measures which component pairs are tested together, not which lines of code are executed.

### Analyzing Integration Coverage

```bash
# Generate coverage report
python scripts/generate_integration_coverage_report.py

# View reports
cat tests/integrations/COVERAGE_REPORT.md
cat tests/integrations/coverage_report.json
```

### Coverage Metrics

- **Component Pairs**: Which pairs of components are tested together
- **Integration Scenarios**: Real-world workflows
- **Coverage Percentage**: Percentage of possible component pairs covered

See `tests/integrations/README.md` for detailed information about integration coverage.

## Best Practices

1. **Unit tests** should test one component in isolation
2. **Integration tests** should test multiple components working together
3. Use fixtures for common setup/teardown
4. Mark tests appropriately (`@pytest.mark.unit` or `@pytest.mark.integration`)
5. Keep tests focused and readable
6. Use descriptive test names that explain what is being tested
7. **For integration tests**: Document which component pairs are being tested
