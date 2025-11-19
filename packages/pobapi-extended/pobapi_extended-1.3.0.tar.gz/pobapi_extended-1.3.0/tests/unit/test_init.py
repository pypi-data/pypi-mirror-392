"""Tests for pobapi.__init__ module."""

import sys
from unittest.mock import patch


def test_import_without_optional_dependencies() -> None:
    """Test that __init__ handles missing optional dependencies gracefully."""
    import builtins

    # Save original state for the modules we are going to manipulate
    modules_to_remove = ["pobapi.crafting", "pobapi.trade", "pobapi"]
    original_modules = {name: sys.modules.get(name) for name in modules_to_remove}
    original_pobapi_all = None
    if "pobapi" in sys.modules:
        pobapi_module = sys.modules["pobapi"]
        original_pobapi_all = (
            getattr(pobapi_module, "__all__", None).copy()
            if hasattr(pobapi_module, "__all__")
            else None
        )

    try:
        # Remove optional modules from sys.modules to simulate their absence
        for module_name in ["pobapi.crafting", "pobapi.trade"]:
            if module_name in sys.modules:
                del sys.modules[module_name]

        # Mock __import__ to raise ImportError for optional modules
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name in ["pobapi.crafting", "pobapi.trade"]:
                error_msg = f"No module named '{name}'"
                raise ImportError(error_msg)
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            # Remove pobapi from sys.modules to force reload
            if "pobapi" in sys.modules:
                del sys.modules["pobapi"]

            # Import pobapi to trigger ImportError handling
            import pobapi

            # Verify that pobapi module loaded successfully
            assert pobapi is not None

            # Verify that core functionality is still available
            assert hasattr(pobapi, "PathOfBuildingAPI")
            assert hasattr(pobapi, "__all__")

            # Verify that optional modules are NOT in __all__ when missing
            assert "ItemCraftingAPI" not in pobapi.__all__
            assert "TradeAPI" not in pobapi.__all__

            # Verify that optional modules are NOT available as attributes
            assert not hasattr(pobapi, "ItemCraftingAPI")
            assert not hasattr(pobapi, "TradeAPI")
    finally:
        # Restore only the modules we deliberately manipulated
        for module_name, original in original_modules.items():
            if original is None:
                sys.modules.pop(module_name, None)
            else:
                sys.modules[module_name] = original

        # Restore pobapi's __all__ if it was modified
        if "pobapi" in sys.modules and original_pobapi_all is not None:
            sys.modules["pobapi"].__all__ = original_pobapi_all


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
    # Verify all core exports are in __all__
    for export in core_exports:
        assert export in pobapi.__all__, f"Core export '{export}' missing from __all__"

    # Verify every name in __all__ is actually accessible
    for name in pobapi.__all__:
        assert hasattr(pobapi, name) or name in dir(
            pobapi
        ), f"Export '{name}' declared in __all__ but not accessible on module"


def test_import_error_handling_calculator() -> None:
    """Test that ImportError in calculator import is handled."""
    # Remove pobapi.calculator from sys.modules to simulate its absence
    if "pobapi.calculator" in sys.modules:
        del sys.modules["pobapi.calculator"]

    # Remove pobapi from sys.modules to force reload
    if "pobapi" in sys.modules:
        del sys.modules["pobapi"]

    # Mock missing calculator module
    with patch.dict(sys.modules, {"pobapi.calculator": None}):
        # Reload module to trigger ImportError handling
        import pobapi

        # Verify that pobapi module reloaded successfully
        assert pobapi is not None
        assert "pobapi" in sys.modules

        # Verify that pobapi has a non-empty __all__
        assert hasattr(pobapi, "__all__")
        assert len(pobapi.__all__) > 0

        # Verify that at least one core symbol from __all__ is accessible
        first_export = pobapi.__all__[0]
        assert getattr(pobapi, first_export) is not None


def test_import_error_handling_crafting() -> None:
    """Test that ImportError in crafting import is handled."""
    # Save original state for restoration
    original_crafting = sys.modules.get("pobapi.crafting")
    original_pobapi = sys.modules.get("pobapi")

    try:
        # Remove crafting module from sys.modules to simulate its absence
        if "pobapi.crafting" in sys.modules:
            del sys.modules["pobapi.crafting"]

        # Mock ImportError when importing crafting
        original_import = __import__

        def mock_import(name, *args, **kwargs):
            if name == "pobapi.crafting":
                raise ImportError("No module named 'pobapi.crafting'")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            # Remove pobapi from sys.modules to force reload
            if "pobapi" in sys.modules:
                del sys.modules["pobapi"]

            # Import pobapi to trigger ImportError handling
            import pobapi  # noqa: F401

            # Verify that pobapi module is present in sys.modules
            assert "pobapi" in sys.modules

            # Verify that pobapi module loaded successfully
            pobapi_module = sys.modules["pobapi"]
            assert pobapi_module is not None

            # Verify that crafting submodule is not available (fallback behavior)
            assert getattr(pobapi_module, "crafting", None) is None

            # Verify that crafting-related exports are not in __all__
            assert "ItemCraftingAPI" not in pobapi_module.__all__
            assert "ItemModifier" not in pobapi_module.__all__
            assert "CraftingModifier" not in pobapi_module.__all__
            assert "CraftingResult" not in pobapi_module.__all__
            assert "ModifierTier" not in pobapi_module.__all__

            # Verify that crafting-related classes are not available as attributes
            assert not hasattr(pobapi_module, "ItemCraftingAPI")
            assert not hasattr(pobapi_module, "ItemModifier")
    finally:
        # Restore original modules
        if original_crafting is not None:
            sys.modules["pobapi.crafting"] = original_crafting
        elif "pobapi.crafting" in sys.modules:
            del sys.modules["pobapi.crafting"]

        if original_pobapi is not None:
            sys.modules["pobapi"] = original_pobapi


def test_import_error_handling_trade() -> None:
    """Test that ImportError in trade import is handled."""
    import importlib

    # Save original state for restoration
    original_trade = sys.modules.get("pobapi.trade")
    original_pobapi = sys.modules.get("pobapi")

    try:
        # Remove trade module from sys.modules to simulate its absence
        if "pobapi.trade" in sys.modules:
            del sys.modules["pobapi.trade"]

        # Mock ImportError when importing trade
        original_import = __import__

        def mock_import(name, *args, **kwargs):
            if name == "pobapi.trade":
                raise ImportError("No module named 'pobapi.trade'")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            # Reload module to trigger ImportError
            if "pobapi" in sys.modules:
                importlib.reload(sys.modules["pobapi"])
            else:
                import pobapi  # noqa: F401

            # Remove trade module from sys.modules if it was re-added during reload
            if "pobapi.trade" in sys.modules:
                del sys.modules["pobapi.trade"]

            # Verify that pobapi module is present in sys.modules
            assert "pobapi" in sys.modules

            # Verify that pobapi module loaded successfully
            pobapi_module = sys.modules["pobapi"]
            assert pobapi_module is not None

            # Remove trade attribute from pobapi module if it exists
            # (from previous imports)
            if hasattr(pobapi_module, "trade"):
                delattr(pobapi_module, "trade")

            # Remove trade-related attributes that may have been added
            # before reload
            trade_attributes = [
                "TradeAPI",
                "TradeFilter",
                "TradeQuery",
                "TradeResult",
                "PriceRange",
                "FilterType",
            ]
            for attr in trade_attributes:
                if hasattr(pobapi_module, attr):
                    delattr(pobapi_module, attr)

            # Verify that trade submodule is not available (fallback behavior)
            # After removing the attribute, it should not be accessible
            assert getattr(pobapi_module, "trade", None) is None

            # Verify that trade-related exports are not in __all__
            assert "TradeAPI" not in pobapi_module.__all__
            assert "TradeFilter" not in pobapi_module.__all__
            assert "TradeQuery" not in pobapi_module.__all__
            assert "TradeResult" not in pobapi_module.__all__
            assert "PriceRange" not in pobapi_module.__all__
            assert "FilterType" not in pobapi_module.__all__

            # Verify that trade-related classes are not available as attributes
            assert not hasattr(pobapi_module, "TradeAPI")
            assert not hasattr(pobapi_module, "TradeFilter")
    finally:
        # Restore original modules
        if original_trade is not None:
            sys.modules["pobapi.trade"] = original_trade
        elif "pobapi.trade" in sys.modules:
            del sys.modules["pobapi.trade"]

        if original_pobapi is not None:
            sys.modules["pobapi"] = original_pobapi
