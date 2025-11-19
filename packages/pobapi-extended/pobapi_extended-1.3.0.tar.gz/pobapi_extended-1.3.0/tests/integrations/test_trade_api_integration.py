"""Integration tests for TradeAPI and PathOfBuildingAPI components."""

import pytest

pytestmark = pytest.mark.integration

from pobapi import PathOfBuildingAPI  # noqa: E402
from pobapi.trade import (  # noqa: E402
    FilterType,
    PriceRange,
    TradeAPI,
    TradeFilter,
    TradeQuery,
)


class TestTradeAPIPathOfBuildingAPIIntegration:
    """Test integration between TradeAPI and PathOfBuildingAPI."""

    def test_filter_build_items_by_rarity(self, build: PathOfBuildingAPI) -> None:
        """Test filtering items from build by rarity."""
        items = list(build.items)

        if not items:
            pytest.skip("No items in build")

        # Filter for rare items
        filters = [TradeFilter(filter_type=FilterType.RARITY, value="Rare")]
        filtered = TradeAPI.filter_items(items, filters)

        # All filtered items should be rare
        assert all(item.rarity.lower() == "rare" for item in filtered)

    def test_filter_build_items_by_base_type(self, build: PathOfBuildingAPI) -> None:
        """Test filtering items from build by base type."""
        items = list(build.items)

        if not items:
            pytest.skip("No items in build")

        # Get first item's base type
        first_item = items[0]
        base_type = first_item.base

        # Filter by base type
        filters = [TradeFilter(filter_type=FilterType.BASE_TYPE, value=base_type)]
        filtered = TradeAPI.filter_items(items, filters)

        # All filtered items should contain the base type
        assert all(base_type.lower() in item.base.lower() for item in filtered)

    def test_filter_build_items_by_item_level(self, build: PathOfBuildingAPI) -> None:
        """Test filtering items from build by item level."""
        items = list(build.items)

        if not items:
            pytest.skip("No items in build")

        # Filter for items with level >= 80
        filters = [TradeFilter(filter_type=FilterType.ITEM_LEVEL, min_value=80)]
        filtered = TradeAPI.filter_items(items, filters)

        # All filtered items should have item_level >= 80
        assert all(item.item_level >= 80 for item in filtered)

    def test_search_build_items_with_query(self, build: PathOfBuildingAPI) -> None:
        """Test searching items from build with trade query."""
        items = list(build.items)

        if not items:
            pytest.skip("No items in build")

        # Create trade query
        query = TradeQuery(
            base_type="",
            filters=[TradeFilter(filter_type=FilterType.RARITY, value="Rare")],
            price_range=None,
            league="Standard",
            online_only=False,
        )

        # Search items
        results = TradeAPI.search_items(items, query)

        # Should return TradeResult objects (may be empty if no rare items)
        assert isinstance(results, list)
        if len(results) > 0:
            assert all(result.item.rarity.lower() == "rare" for result in results)

    def test_filter_build_items_by_quality(self, build: PathOfBuildingAPI) -> None:
        """Test filtering items from build by quality."""
        items = list(build.items)

        if not items:
            pytest.skip("No items in build")

        # Filter for items with quality >= 15
        filters = [TradeFilter(filter_type=FilterType.QUALITY, min_value=15)]
        filtered = TradeAPI.filter_items(items, filters)

        # All filtered items should have non-None quality >= 15
        assert all(item.quality is not None and item.quality >= 15 for item in filtered)

    def test_filter_build_items_by_sockets(self, build: PathOfBuildingAPI) -> None:
        """Test filtering items from build by socket count."""
        items = list(build.items)

        if not items:
            pytest.skip("No items in build")

        # Filter for items with at least 4 sockets
        filters = [TradeFilter(filter_type=FilterType.SOCKETS, min_value=4)]
        filtered = TradeAPI.filter_items(items, filters)

        # All filtered items should have at least 4 sockets
        assert all(
            item.sockets is not None and sum(len(group) for group in item.sockets) >= 4
            for item in filtered
        )

    def test_search_build_items_with_price_range(
        self, build: PathOfBuildingAPI
    ) -> None:
        """Test searching items from build with price range."""
        items = list(build.items)

        if not items:
            pytest.skip("No items in build")

        # Create trade query with price range
        price_range = PriceRange(min_price=1.0, max_price=10.0, currency="chaos")
        query = TradeQuery(
            base_type="",
            filters=[],
            price_range=price_range,
            league="Standard",
            online_only=False,
        )

        # Search items
        results = TradeAPI.search_items(items, query)

        # Should return results (price matching is simplified in current impl)
        assert isinstance(results, list)

    def test_trade_api_with_modified_build_items(
        self, build: PathOfBuildingAPI
    ) -> None:
        """Test TradeAPI with items added via BuildModifier."""
        from pobapi.models import Item

        # Add a new item via BuildModifier
        test_item = Item(
            name="Test Ring",
            base="Iron Ring",
            rarity="Rare",
            uid="test-ring-1",
            shaper=False,
            elder=False,
            crafted=False,
            quality=20,
            sockets=None,
            level_req=1,
            item_level=84,
            implicit=None,
            text="+20 to Strength\n+30 to maximum Life",
        )

        build._modifier.equip_item(test_item, "Ring1")

        # Get all items (including modified)
        items = list(build.items)

        # Filter for the new item
        filters = [TradeFilter(filter_type=FilterType.UNIQUE_ID, value="test-ring-1")]
        filtered = TradeAPI.filter_items(items, filters)

        # Should find the new item
        assert len(filtered) >= 1
        assert any(item.uid == "test-ring-1" for item in filtered)
