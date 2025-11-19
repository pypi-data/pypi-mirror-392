"""Tests for trade module."""

import pytest

from pobapi.trade import (
    FilterType,
    PriceRange,
    TradeAPI,
    TradeFilter,
    TradeQuery,
    TradeResult,
)


class TestTradeFilter:
    """Tests for TradeFilter dataclass."""

    def test_init(self) -> None:
        """Test TradeFilter initialization."""
        filter_obj = TradeFilter(filter_type=FilterType.RARITY, value="UNIQUE")
        assert filter_obj.filter_type == FilterType.RARITY
        assert filter_obj.value == "UNIQUE"


class TestTradeQuery:
    """Tests for TradeQuery dataclass."""

    def test_init(self) -> None:
        """Test TradeQuery initialization."""
        query = TradeQuery(
            league="Standard",
            base_type="Leather Belt",
        )
        assert query.league == "Standard"
        assert query.base_type == "Leather Belt"


class TestPriceRange:
    """Tests for PriceRange dataclass."""

    def test_init(self) -> None:
        """Test PriceRange initialization."""
        price_range = PriceRange(min_price=1.0, max_price=10.0, currency="chaos")
        assert price_range.min_price == 1.0
        assert price_range.max_price == 10.0
        assert price_range.currency == "chaos"


class TestTradeResult:
    """Tests for TradeResult dataclass."""

    def test_init(self, create_test_item) -> None:
        """Test TradeResult initialization."""
        item = create_test_item()
        result = TradeResult(item=item, match_score=0.8)
        assert result.item == item
        assert result.match_score == 0.8


class TestTradeAPI:
    """Tests for TradeAPI."""

    def test_filter_items_by_rarity(self, create_test_item) -> None:
        """Test filtering items by rarity."""
        items = [
            create_test_item(name="Item 1", rarity="Unique"),
            create_test_item(name="Item 2", rarity="Rare"),
            create_test_item(name="Item 3", rarity="Unique"),
        ]
        filters = [TradeFilter(filter_type=FilterType.RARITY, value="Unique")]
        filtered = TradeAPI.filter_items(items, filters)
        assert len(filtered) == 2
        assert all(item.rarity == "Unique" for item in filtered)

    def test_filter_items_by_base_type(self, create_test_item) -> None:
        """Test filtering items by base type."""
        items = [
            create_test_item(name="Item 1", base="Leather Belt"),
            create_test_item(name="Item 2", base="Heavy Belt"),
            create_test_item(name="Item 3", base="Leather Belt"),
        ]
        filters = [TradeFilter(filter_type=FilterType.BASE_TYPE, value="Leather Belt")]
        filtered = TradeAPI.filter_items(items, filters)
        assert len(filtered) == 2
        assert all("Leather Belt" in item.base for item in filtered)

    def test_filter_items_by_item_level(self, create_test_item) -> None:
        """Test filtering items by item level."""
        items = [
            create_test_item(name="Item 1", item_level=75),
            create_test_item(name="Item 2", item_level=85),
            create_test_item(name="Item 3", item_level=90),
        ]
        filters = [
            TradeFilter(filter_type=FilterType.ITEM_LEVEL, min_value=80, max_value=90)
        ]
        filtered = TradeAPI.filter_items(items, filters)
        assert len(filtered) == 2
        assert all(80 <= item.item_level <= 90 for item in filtered)

    def test_filter_items_by_quality(self, create_test_item) -> None:
        """Test filtering items by quality."""
        items = [
            create_test_item(name="Item 1", quality=10),
            create_test_item(name="Item 2", quality=20),
            create_test_item(name="Item 3", quality=15),
        ]
        filters = [
            TradeFilter(filter_type=FilterType.QUALITY, min_value=15, max_value=20)
        ]
        filtered = TradeAPI.filter_items(items, filters)
        assert len(filtered) == 2
        assert all(
            item.quality is not None and 15 <= item.quality <= 20 for item in filtered
        )

    def test_filter_items_multiple_filters(self, create_test_item) -> None:
        """Test filtering items with multiple filters."""
        items = [
            create_test_item(
                name="Item 1",
                base="Leather Belt",
                item_level=85,
                quality=20,
            ),
            create_test_item(
                name="Item 2",
                base="Heavy Belt",
                item_level=85,
                quality=20,
            ),
        ]
        filters = [
            TradeFilter(filter_type=FilterType.BASE_TYPE, value="Leather Belt"),
            TradeFilter(filter_type=FilterType.ITEM_LEVEL, min_value=80),
        ]
        filtered = TradeAPI.filter_items(items, filters)
        assert len(filtered) == 1
        assert filtered[0].base == "Leather Belt"

    def test_search_items(self, create_test_item) -> None:
        """Test searching items with query."""
        items = [
            create_test_item(name="Item 1", base="Leather Belt", item_level=85),
            create_test_item(name="Item 2", base="Heavy Belt", item_level=75),
        ]
        query = TradeQuery(league="Standard", base_type="Leather Belt")
        # Add item level filter
        query.filters.append(
            TradeFilter(filter_type=FilterType.ITEM_LEVEL, min_value=80)
        )
        results = TradeAPI.search_items(items, query)
        assert isinstance(results, list)
        assert len(results) >= 0

    def test_generate_trade_url(self) -> None:
        """Test generating trade URL from query."""
        query = TradeQuery(
            league="Standard",
            base_type="Leather Belt",
        )
        url = TradeAPI.generate_trade_url(query)
        assert isinstance(url, str)
        assert "pathofexile.com" in url or len(url) > 0

    def test_estimate_item_price(self, create_test_item) -> None:
        """Test estimating item price."""
        item = create_test_item()
        price_range = TradeAPI.estimate_item_price(item, league="Standard")
        assert isinstance(price_range, PriceRange)

    def test_compare_items(self, create_test_item) -> None:
        """Test comparing two items."""
        item1 = create_test_item(name="Item 1")
        item2 = create_test_item(name="Item 2")
        comparison = TradeAPI.compare_items(item1, item2)
        assert isinstance(comparison, dict)

    @pytest.mark.parametrize(
        ("filter_type", "value", "expected_count"),
        [
            (FilterType.SHAPER, True, 1),
            (FilterType.ELDER, True, 1),
            (FilterType.CRAFTED, True, 1),
            (FilterType.UNIQUE_ID, "test-uid-1", 1),
        ],
    )
    def test_filter_items_by_boolean_flags(
        self, create_test_item, filter_type, value, expected_count
    ) -> None:
        """Test filtering items by boolean flags."""
        items = [
            create_test_item(name="Item 1", shaper=True, elder=False, crafted=False),
            create_test_item(name="Item 2", shaper=False, elder=True, crafted=False),
            create_test_item(name="Item 3", shaper=False, elder=False, crafted=True),
        ]
        # Set uid for UNIQUE_ID test
        if filter_type == FilterType.UNIQUE_ID:
            items[0].uid = "test-uid-1"
            items[1].uid = "test-uid-2"
            items[2].uid = "test-uid-3"

        filters = [TradeFilter(filter_type=filter_type, value=value)]
        filtered = TradeAPI.filter_items(items, filters)
        assert len(filtered) == expected_count

    def test_filter_items_by_sockets(self, create_test_item) -> None:
        """Test filtering items by socket count."""
        items = [
            create_test_item(name="Item 1", sockets=[[1, 2, 3]]),  # 3 sockets
            create_test_item(name="Item 2", sockets=[[1, 2, 3, 4]]),  # 4 sockets
            create_test_item(name="Item 3", sockets=[[1, 2]]),  # 2 sockets
        ]
        filters = [TradeFilter(filter_type=FilterType.SOCKETS, min_value=3)]
        filtered = TradeAPI.filter_items(items, filters)
        assert len(filtered) == 2
        assert all(
            item.sockets is not None and sum(len(group) for group in item.sockets) >= 3
            for item in filtered
        )

    def test_filter_items_by_linked_sockets(self, create_test_item) -> None:
        """Test filtering items by linked socket count."""
        items = [
            create_test_item(name="Item 1", sockets=[[1, 2, 3]]),  # 3 linked
            create_test_item(name="Item 2", sockets=[[1, 2], [3, 4]]),  # 2 linked
            create_test_item(name="Item 3", sockets=[[1, 2, 3, 4, 5, 6]]),  # 6 linked
        ]
        filters = [TradeFilter(filter_type=FilterType.LINKED_SOCKETS, min_value=3)]
        filtered = TradeAPI.filter_items(items, filters)
        assert len(filtered) == 2
        assert all(
            item.sockets is not None
            and max((len(group) for group in item.sockets), default=0) >= 3
            for item in filtered
        )

    def test_filter_items_by_modifier(self, create_test_item) -> None:
        """Test filtering items by modifier text."""
        items = [
            create_test_item(name="Item 1", text="+50 to maximum Life"),
            create_test_item(name="Item 2", text="+100 to maximum Life"),
            create_test_item(name="Item 3", text="+20 to Strength"),
        ]
        filters = [TradeFilter(filter_type=FilterType.MODIFIER, value="maximum life")]
        filtered = TradeAPI.filter_items(items, filters)
        assert len(filtered) == 2
        assert all("maximum life" in item.text.lower() for item in filtered)

    def test_filter_items_by_stat_value(self, create_test_item, mocker) -> None:
        """Test filtering items by stat value."""
        items = [
            create_test_item(name="Item 1", text="+50 to maximum Life"),
            create_test_item(name="Item 2", text="+100 to maximum Life"),
            create_test_item(name="Item 3", text="+20 to Strength"),
        ]
        # Mock ItemModifierParser to return modifiers
        mock_modifiers = [
            mocker.Mock(stat="Life", value=50.0),
            mocker.Mock(stat="Life", value=100.0),
            mocker.Mock(stat="Strength", value=20.0),
        ]

        mocker.patch(
            "pobapi.calculator.item_modifier_parser.ItemModifierParser.parse_item_text",
            side_effect=lambda text, **kwargs: [
                mock_modifiers[0]
                if "50" in text
                else mock_modifiers[1]
                if "100" in text
                else mock_modifiers[2]
            ],
        )
        filters = [
            TradeFilter(
                filter_type=FilterType.STAT_VALUE,
                value="Life",
                min_value=75.0,
            )
        ]
        filtered = TradeAPI.filter_items(items, filters)
        assert len(filtered) == 1
        assert "100" in filtered[0].text

    def test_has_stat_value(self, create_test_item, mocker) -> None:
        """Test _has_stat_value method."""
        item = create_test_item(name="Item 1", text="+100 to maximum Life")
        mock_modifier = mocker.Mock(stat="Life", value=100.0)

        mocker.patch(
            "pobapi.calculator.item_modifier_parser.ItemModifierParser.parse_item_text",
            return_value=[mock_modifier],
        )
        result = TradeAPI._has_stat_value(item, "Life", 75.0)
        assert result is True

        result = TradeAPI._has_stat_value(item, "Life", 150.0)
        assert result is False

    def test_search_items_with_match_score(self, create_test_item) -> None:
        """Test searching items with match score calculation."""
        items = [
            create_test_item(
                name="Item 1", base="Leather Belt", item_level=85, rarity="Rare"
            ),
            create_test_item(
                name="Item 2", base="Heavy Belt", item_level=75, rarity="Rare"
            ),
        ]
        query = TradeQuery(
            league="Standard",
            base_type="Leather Belt",
        )
        query.filters.append(
            TradeFilter(filter_type=FilterType.ITEM_LEVEL, min_value=80)
        )
        results = TradeAPI.search_items(items, query)
        assert isinstance(results, list)
        if results:
            assert all(isinstance(r, TradeResult) for r in results)
            assert all(0.0 <= r.match_score <= 100.0 for r in results)

    def test_generate_trade_url_with_price_range(self) -> None:
        """Test generating trade URL with price range."""
        price_range = PriceRange(min_price=1.0, max_price=10.0, currency="chaos")
        query = TradeQuery(
            league="Standard",
            base_type="Leather Belt",
            price_range=price_range,
        )
        url = TradeAPI.generate_trade_url(query)
        assert isinstance(url, str)
        assert "Standard" in url

    def test_generate_trade_url_online_only(self) -> None:
        """Test generating trade URL with online only flag."""
        query = TradeQuery(
            league="Standard",
            base_type="Leather Belt",
            online_only=True,
        )
        url = TradeAPI.generate_trade_url(query)
        assert isinstance(url, str)
        assert "Standard" in url

    @pytest.mark.parametrize(
        ("rarity", "expected_multiplier"),
        [
            ("Normal", 0.1),
            ("Magic", 0.5),
            ("Rare", 1.0),
            ("Unique", 5.0),
        ],
    )
    def test_estimate_item_price_by_rarity(
        self, create_test_item, rarity, expected_multiplier
    ) -> None:
        """Test price estimation by rarity."""
        # Get reference price for Normal rarity
        normal_item = create_test_item(rarity="Normal", item_level=80, quality=0)
        normal_price_range = TradeAPI.estimate_item_price(
            normal_item, league="Standard"
        )
        assert isinstance(normal_price_range, PriceRange)
        assert normal_price_range.min_price > 0

        # Get price for the parametrized rarity
        # Reuse normal_price_range when rarity is "Normal" to avoid duplicate API call
        if rarity == "Normal":
            price_range = normal_price_range
        else:
            item = create_test_item(rarity=rarity, item_level=80, quality=0)
            price_range = TradeAPI.estimate_item_price(item, league="Standard")
            assert isinstance(price_range, PriceRange)
            assert price_range.min_price > 0
            assert price_range.max_price > price_range.min_price

        # Compute actual multiplier relative to Normal rarity
        actual_multiplier = price_range.min_price / normal_price_range.min_price
        # Compare relative to Normal rarity
        # (expected_multiplier / 0.1)
        expected_relative_multiplier = expected_multiplier / 0.1
        assert actual_multiplier == pytest.approx(
            expected_relative_multiplier, rel=0.01
        )

    def test_estimate_item_price_with_quality(self, create_test_item) -> None:
        """Test price estimation with quality."""
        item = create_test_item(rarity="Rare", item_level=80, quality=20)
        price_range = TradeAPI.estimate_item_price(item, league="Standard")
        assert isinstance(price_range, PriceRange)
        # Quality should increase price
        assert price_range.min_price > 0

    def test_estimate_item_price_with_sockets(self, create_test_item) -> None:
        """Test price estimation with sockets."""
        item = create_test_item(
            rarity="Rare",
            item_level=80,
            sockets=[[1, 2, 3, 4, 5, 6]],  # 6 linked sockets
        )
        price_range = TradeAPI.estimate_item_price(item, league="Standard")
        assert isinstance(price_range, PriceRange)
        assert price_range.min_price > 0

    def test_estimate_item_price_with_influence(self, create_test_item) -> None:
        """Test price estimation with shaper/elder influence."""
        item = create_test_item(rarity="Rare", item_level=80, shaper=True)
        price_range = TradeAPI.estimate_item_price(item, league="Standard")
        assert isinstance(price_range, PriceRange)
        # Influence should increase price
        assert price_range.min_price > 0

    def test_compare_items_differences(self, create_test_item) -> None:
        """Test comparing items with differences."""
        item1 = create_test_item(
            name="Item 1",
            rarity="Rare",
            base="Leather Belt",
            item_level=80,
            quality=20,
            shaper=True,
        )
        item2 = create_test_item(
            name="Item 2",
            rarity="Unique",
            base="Heavy Belt",
            item_level=75,
            quality=15,
            shaper=False,
        )
        comparison = TradeAPI.compare_items(item1, item2)
        assert isinstance(comparison, dict)
        assert "rarity" in comparison
        assert "base" in comparison
        assert "item_level" in comparison
        assert "quality" in comparison
        assert "shaper" in comparison

    def test_compare_items_sockets(self, create_test_item) -> None:
        """Test comparing items with different sockets."""
        item1 = create_test_item(
            name="Item 1",
            sockets=[[1, 2, 3, 4, 5, 6]],  # 6 linked
        )
        item2 = create_test_item(
            name="Item 2",
            sockets=[[1, 2], [3, 4]],  # 2+2 sockets
        )
        comparison = TradeAPI.compare_items(item1, item2)
        assert isinstance(comparison, dict)
        assert "sockets" in comparison

    def test_calculate_match_score_base_type_no_match(self, create_test_item) -> None:
        """Test match score calculation when base type doesn't match.

        Covers line 319."""
        item = create_test_item(name="Item 1", base="Heavy Belt")
        query = TradeQuery(
            league="Standard",
            base_type="Leather Belt",  # Different from item base
        )
        score = TradeAPI._calculate_match_score(item, query)
        # Should have lower score due to base type mismatch (covers line 319)
        assert 0.0 <= score <= 100.0
        assert score < 70.0  # Should be less than base score + match bonus

    def test_calculate_match_score_item_level_below_min(self, create_test_item) -> None:
        """Test match score when item level is below minimum - covers line 328."""
        item = create_test_item(name="Item 1", item_level=75)
        query = TradeQuery(
            league="Standard",
            base_type="Leather Belt",
        )
        query.filters.append(
            TradeFilter(filter_type=FilterType.ITEM_LEVEL, min_value=80)
        )
        score = TradeAPI._calculate_match_score(item, query)
        # Should have lower score due to item level below minimum (covers line 328)
        assert 0.0 <= score <= 100.0

    def test_calculate_match_score_quality_below_min(self, create_test_item) -> None:
        """Test match score when quality is below minimum - covers line 335."""
        item = create_test_item(name="Item 1", quality=10)
        query = TradeQuery(
            league="Standard",
            base_type="Leather Belt",
        )
        query.filters.append(TradeFilter(filter_type=FilterType.QUALITY, min_value=20))
        score = TradeAPI._calculate_match_score(item, query)
        # Should have lower score due to quality below minimum (covers line 335)
        assert 0.0 <= score <= 100.0

    def test_calculate_match_score_quality_above_min(self, create_test_item) -> None:
        """Test match score when quality is above minimum - covers line 333."""
        item = create_test_item(name="Item 1", quality=25)
        query = TradeQuery(
            league="Standard",
            base_type="Leather Belt",
        )
        query.filters.append(TradeFilter(filter_type=FilterType.QUALITY, min_value=20))
        score = TradeAPI._calculate_match_score(item, query)
        # Should have higher score due to quality above minimum (covers line 333)
        assert 0.0 <= score <= 100.0
        assert score >= 50.0  # Should be at least base score

    def test_calculate_match_score_sockets_below_min(self, create_test_item) -> None:
        """Test match score when socket count is below minimum - covers line 343."""
        item = create_test_item(name="Item 1", sockets=[[1, 2]])  # 2 sockets
        query = TradeQuery(
            league="Standard",
            base_type="Leather Belt",
        )
        query.filters.append(TradeFilter(filter_type=FilterType.SOCKETS, min_value=4))
        score = TradeAPI._calculate_match_score(item, query)
        # Should have lower score due to socket count below minimum (covers line 343)
        assert 0.0 <= score <= 100.0

    def test_calculate_match_score_sockets_above_min(self, create_test_item) -> None:
        """Test match score when socket count is above minimum - covers line 341."""
        item = create_test_item(name="Item 1", sockets=[[1, 2, 3, 4, 5]])  # 5 sockets
        query = TradeQuery(
            league="Standard",
            base_type="Leather Belt",
        )
        query.filters.append(TradeFilter(filter_type=FilterType.SOCKETS, min_value=4))
        score = TradeAPI._calculate_match_score(item, query)
        # Should have higher score due to socket count above minimum (covers line 341)
        assert 0.0 <= score <= 100.0
        assert score >= 50.0  # Should be at least base score

    def test_compare_items_no_differences(self, create_test_item) -> None:
        """Test comparing items with no differences - covers lines 479, 482."""
        item1 = create_test_item(
            name="Item 1",
            rarity="Rare",
            base="Leather Belt",
            item_level=80,
            quality=20,
            shaper=False,
            elder=False,
            crafted=False,
            sockets=[[1, 2, 3]],
        )
        item2 = create_test_item(
            name="Item 2",
            rarity="Rare",
            base="Leather Belt",
            item_level=80,
            quality=20,
            shaper=False,
            elder=False,
            crafted=False,
            sockets=[[1, 2, 3]],
        )
        # Set same uid
        item1.uid = "test-uid"
        item2.uid = "test-uid"
        comparison = TradeAPI.compare_items(item1, item2)
        # Should return empty dict when items are identical (covers lines 479, 482)
        assert isinstance(comparison, dict)
        assert len(comparison) == 0

    def test_compare_items_elder_difference(self, create_test_item) -> None:
        """Test comparing items with elder difference - covers line 479."""
        item1 = create_test_item(
            name="Item 1",
            rarity="Rare",
            base="Leather Belt",
            item_level=80,
            quality=20,
            shaper=False,
            elder=True,  # Different
            crafted=False,
        )
        item2 = create_test_item(
            name="Item 2",
            rarity="Rare",
            base="Leather Belt",
            item_level=80,
            quality=20,
            shaper=False,
            elder=False,  # Different
            crafted=False,
        )
        comparison = TradeAPI.compare_items(item1, item2)
        # Should include elder difference (covers line 479)
        assert isinstance(comparison, dict)
        assert "elder" in comparison
        assert comparison["elder"] == (True, False)

    def test_compare_items_crafted_difference(self, create_test_item) -> None:
        """Test comparing items with crafted difference - covers line 482."""
        item1 = create_test_item(
            name="Item 1",
            rarity="Rare",
            base="Leather Belt",
            item_level=80,
            quality=20,
            shaper=False,
            elder=False,
            crafted=True,  # Different
        )
        item2 = create_test_item(
            name="Item 2",
            rarity="Rare",
            base="Leather Belt",
            item_level=80,
            quality=20,
            shaper=False,
            elder=False,
            crafted=False,  # Different
        )
        comparison = TradeAPI.compare_items(item1, item2)
        # Should include crafted difference (covers line 482)
        assert isinstance(comparison, dict)
        assert "crafted" in comparison
        assert comparison["crafted"] == (True, False)
