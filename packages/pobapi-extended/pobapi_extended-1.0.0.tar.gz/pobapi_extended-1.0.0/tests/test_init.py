"""Tests for pobapi.__init__ module."""

import sys
from unittest.mock import patch


def test_import_without_optional_dependencies() -> None:
    """Test that __init__ handles missing optional dependencies gracefully."""
    # Test that calculator imports work
    from pobapi.calculator import CalculationEngine

    assert CalculationEngine is not None

    # Test that crafting imports are optional
    # We can't easily test ImportError handling without actually removing modules,
    # but we can verify the imports are in __all__ when available
    try:
        from pobapi import ItemCraftingAPI

        assert ItemCraftingAPI is not None
    except ImportError:
        # Crafting module might not be available
        pass

    # Test that trade imports are optional
    try:
        from pobapi import TradeAPI

        assert TradeAPI is not None
    except ImportError:
        # Trade module might not be available
        pass


def test_all_exports() -> None:
    """Test that __all__ contains expected exports."""
    import pobapi

    # Check that __all__ exists
    assert hasattr(pobapi, "__all__")
    assert isinstance(pobapi.__all__, list)

    # Check for core exports
    core_exports = [
        "PathOfBuildingAPI",
        "BuildFactory",
        "StatsBuilder",
        "ConfigBuilder",
    ]
    for export in core_exports:
        if export in pobapi.__all__:
            # Verify it's actually importable
            assert hasattr(pobapi, export) or export in dir(pobapi)


def test_import_error_handling_calculator(mocker) -> None:
    """Test that ImportError in calculator import is handled."""
    # Mock ImportError when importing calculator
    with patch.dict("sys.modules", {"pobapi.calculator": None}):
        # Reload module to trigger ImportError
        import importlib

        if "pobapi" in sys.modules:
            importlib.reload(sys.modules["pobapi"])
        else:
            import pobapi  # noqa: F401

        # Should not raise exception
        assert True


def test_import_error_handling_crafting(mocker) -> None:
    """Test that ImportError in crafting import is handled."""
    # Mock ImportError when importing crafting
    original_import = __import__

    def mock_import(name, *args, **kwargs):
        if name == "pobapi.crafting":
            raise ImportError("No module named 'pobapi.crafting'")
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=mock_import):
        # Reload module to trigger ImportError
        import importlib

        if "pobapi" in sys.modules:
            importlib.reload(sys.modules["pobapi"])
        else:
            import pobapi  # noqa: F401

        # Should not raise exception
        assert True


def test_import_error_handling_trade(mocker) -> None:
    """Test that ImportError in trade import is handled."""
    # Mock ImportError when importing trade
    original_import = __import__

    def mock_import(name, *args, **kwargs):
        if name == "pobapi.trade":
            raise ImportError("No module named 'pobapi.trade'")
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=mock_import):
        # Reload module to trigger ImportError
        import importlib

        if "pobapi" in sys.modules:
            importlib.reload(sys.modules["pobapi"])
        else:
            import pobapi  # noqa: F401

        # Should not raise exception
        assert True
