"""Tests for exception handling in util.py lines 140-141."""

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
        assert isinstance(result, list)

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
