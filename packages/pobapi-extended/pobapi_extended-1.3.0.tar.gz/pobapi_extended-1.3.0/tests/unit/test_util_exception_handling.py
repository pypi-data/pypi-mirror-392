"""Tests for exception handling in util.py lines 140-141."""

import pytest

from pobapi.util import _item_text


class TestItemTextExceptionHandling:
    """Tests for _item_text exception handling (lines 140-141)."""

    def test_item_text_keyerror_handling(self):
        """Test _item_text handles KeyError when slicing (line 140-141)."""

        # Create a custom list-like object that raises KeyError on slice
        class KeyErrorList:
            """List that raises KeyError on slice."""

            def __init__(self, items):
                self._items = list(items)
                self._index = 0

            def __iter__(self):
                return self

            def __next__(self):
                if self._index >= len(self._items):
                    raise StopIteration
                item = self._items[self._index]
                self._index += 1
                return item

            def __getitem__(self, key):
                if isinstance(key, slice):
                    # Simulate KeyError for slice operation
                    raise KeyError("Mock KeyError")
                return self._items[key]

        # Create list with Implicits
        text: list[str] = KeyErrorList(["Rarity: Unique", "Implicits: 2", "Test line"])  # type: ignore[assignment]
        result = list(_item_text(text))
        # Should handle KeyError gracefully and return empty
        assert result == []

    def test_item_text_indexerror_handling(self):
        """Test _item_text handles IndexError when slicing (line 140-141)."""

        # Create a custom list-like object that raises IndexError on slice
        class IndexErrorList:
            """List that raises IndexError on slice."""

            def __init__(self, items):
                self._items = list(items)
                self._index = 0

            def __iter__(self):
                return self

            def __next__(self):
                if self._index >= len(self._items):
                    raise StopIteration
                item = self._items[self._index]
                self._index += 1
                return item

            def __getitem__(self, key):
                if isinstance(key, slice):
                    # Simulate IndexError for slice operation
                    raise IndexError("Mock IndexError")
                return self._items[key]

        # Create list with Implicits
        text: list[str] = IndexErrorList(
            ["Rarity: Unique", "Implicits: 2", "Test line"]
        )  # type: ignore[assignment]
        result = list(_item_text(text))
        # Should handle IndexError gracefully and return empty
        assert isinstance(result, list)
        assert result == []


class TestUtilImportErrorHandling:
    """Tests for ImportError handling in util.py lines 87-88."""

    def test_get_default_http_client_import_error(self, monkeypatch):
        """Test _get_default_http_client raises ImportError when
        requests is not available.

        Covers lines 87-88 in util.py.
        """
        import sys
        from unittest.mock import patch

        from pobapi import util

        # Reset the module-level variable to force re-initialization
        monkeypatch.setattr(util, "_default_http_client", None)

        # Save original requests if it exists
        original_requests = sys.modules.get("requests")

        # Remove requests from sys.modules to simulate it not being installed
        if "requests" in sys.modules:
            del sys.modules["requests"]

        try:
            # Patch __import__ to raise ImportError for requests
            original_import = __import__

            def mock_import(name, globals=None, locals=None, fromlist=(), level=0):
                if name == "requests":
                    raise ImportError("No module named 'requests'")
                return original_import(name, globals, locals, fromlist, level)

            # Patch at the builtins level
            with patch("builtins.__import__", side_effect=mock_import):
                # Should raise ImportError with helpful message (covers lines 87-88)
                with pytest.raises(ImportError, match="requests library is required"):
                    util._get_default_http_client()
        finally:
            # Restore original requests if it existed
            if original_requests:
                sys.modules["requests"] = original_requests
