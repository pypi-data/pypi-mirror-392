"""Trade integration API for Path of Building.

This module provides functionality for trade search, item filtering,
and price calculations, replicating Path of Building's trade system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pobapi.models import Item
from pobapi.parsers.item_modifier import ItemModifierParser

__all__ = [
    "TradeFilter",
    "PriceRange",
    "TradeQuery",
    "TradeResult",
    "TradeAPI",
]


class FilterType(Enum):
    """Types of trade filters."""

    RARITY = "rarity"
    BASE_TYPE = "base_type"
    ITEM_LEVEL = "item_level"
    QUALITY = "quality"
    SOCKETS = "sockets"
    LINKED_SOCKETS = "linked_sockets"
    SHAPER = "shaper"
    ELDER = "elder"
    CRAFTED = "crafted"
    UNIQUE_ID = "unique_id"
    MODIFIER = "modifier"
    STAT_VALUE = "stat_value"


@dataclass
class TradeFilter:
    """Represents a trade filter.

    :param filter_type: Type of filter.
    :param value: Filter value (can be str, int, float, bool, or dict).
    :param min_value: Minimum value (for range filters).
    :param max_value: Maximum value (for range filters).
    """

    filter_type: FilterType
    value: Any = None
    min_value: Any = None
    max_value: Any = None


@dataclass
class PriceRange:
    """Represents a price range.

    :param min_price: Minimum price (in chaos orbs).
    :param max_price: Maximum price (in chaos orbs).
    :param currency: Currency type (default: "chaos").
    """

    min_price: float = 0.0
    max_price: float = float("inf")
    currency: str = "chaos"


@dataclass
class TradeQuery:
    """Represents a trade search query.

    :param base_type: Base item type to search for.
    :param filters: List of TradeFilter objects.
    :param price_range: Optional PriceRange for price filtering.
    :param league: League name (e.g., "Standard", "Hardcore").
    :param online_only: Whether to search only for online players.
    """

    base_type: str = ""
    filters: list[TradeFilter] = field(default_factory=list)
    price_range: PriceRange | None = None
    league: str = "Standard"
    online_only: bool = True


@dataclass
class TradeResult:
    """Represents a trade search result.

    :param item: Item object.
    :param price: Item price (in chaos orbs).
    :param currency: Currency type.
    :param seller: Seller name (optional).
    :param listing_id: Trade listing ID (optional).
    :param match_score: Match score (0-100, higher is better).
    """

    item: Item
    price: float = 0.0
    currency: str = "chaos"
    seller: str = ""
    listing_id: str = ""
    match_score: float = 0.0


class TradeAPI:
    """API for trade search and filtering.

    This class provides functionality to search and filter items,
    generate trade queries, and calculate prices.
    """

    @staticmethod
    def filter_items(items: list[Item], filters: list[TradeFilter]) -> list[Item]:
        """Filter items based on trade filters.

        :param items: List of items to filter.
        :param filters: List of TradeFilter objects.
        :return: Filtered list of items.
        :raises TypeError: If items or filters is None.
        """
        if items is None:
            raise TypeError("items parameter cannot be None. Expected list[Item].")
        if filters is None:
            raise TypeError(
                "filters parameter cannot be None. Expected list[TradeFilter]."
            )
        filtered_items = items.copy()

        for trade_filter in filters:
            if trade_filter.filter_type == FilterType.RARITY:
                if trade_filter.value:
                    filtered_items = [
                        item
                        for item in filtered_items
                        if item.rarity.lower() == str(trade_filter.value).lower()
                    ]

            elif trade_filter.filter_type == FilterType.BASE_TYPE:
                if trade_filter.value:
                    filtered_items = [
                        item
                        for item in filtered_items
                        if trade_filter.value.lower() in item.base.lower()
                    ]

            elif trade_filter.filter_type == FilterType.ITEM_LEVEL:
                if trade_filter.min_value is not None:
                    filtered_items = [
                        item
                        for item in filtered_items
                        if item.item_level >= trade_filter.min_value
                    ]
                if trade_filter.max_value is not None:
                    filtered_items = [
                        item
                        for item in filtered_items
                        if item.item_level <= trade_filter.max_value
                    ]

            elif trade_filter.filter_type == FilterType.QUALITY:
                if trade_filter.min_value is not None:
                    filtered_items = [
                        item
                        for item in filtered_items
                        if item.quality is not None
                        and item.quality >= trade_filter.min_value
                    ]
                if trade_filter.max_value is not None:
                    filtered_items = [
                        item
                        for item in filtered_items
                        if item.quality is not None
                        and item.quality <= trade_filter.max_value
                    ]

            elif trade_filter.filter_type == FilterType.SOCKETS:
                if trade_filter.min_value is not None:
                    filtered_items = [
                        item
                        for item in filtered_items
                        if item.sockets is not None
                        and sum(len(group) for group in item.sockets)
                        >= trade_filter.min_value
                    ]

            elif trade_filter.filter_type == FilterType.LINKED_SOCKETS:
                if trade_filter.min_value is not None:
                    filtered_items = [
                        item
                        for item in filtered_items
                        if item.sockets is not None
                        and max((len(group) for group in item.sockets), default=0)
                        >= trade_filter.min_value
                    ]

            elif trade_filter.filter_type == FilterType.SHAPER:
                if trade_filter.value is not None:
                    filtered_items = [
                        item
                        for item in filtered_items
                        if item.shaper == trade_filter.value
                    ]

            elif trade_filter.filter_type == FilterType.ELDER:
                if trade_filter.value is not None:
                    filtered_items = [
                        item
                        for item in filtered_items
                        if item.elder == trade_filter.value
                    ]

            elif trade_filter.filter_type == FilterType.CRAFTED:
                if trade_filter.value is not None:
                    filtered_items = [
                        item
                        for item in filtered_items
                        if item.crafted == trade_filter.value
                    ]

            elif trade_filter.filter_type == FilterType.UNIQUE_ID:
                if trade_filter.value:
                    filtered_items = [
                        item
                        for item in filtered_items
                        if item.uid.lower() == str(trade_filter.value).lower()
                    ]

            elif trade_filter.filter_type == FilterType.MODIFIER:
                if trade_filter.value:
                    # Search for modifier in item text
                    modifier_text = str(trade_filter.value).lower()
                    filtered_items = [
                        item
                        for item in filtered_items
                        if modifier_text in item.text.lower()
                    ]

            elif trade_filter.filter_type == FilterType.STAT_VALUE:
                if trade_filter.value and trade_filter.min_value is not None:
                    # Search for stat with minimum value
                    stat_name = str(trade_filter.value).lower()
                    min_value = trade_filter.min_value
                    filtered_items = [
                        item
                        for item in filtered_items
                        if TradeAPI._has_stat_value(item, stat_name, min_value)
                    ]

        return filtered_items

    @staticmethod
    def _has_stat_value(item: Item, stat_name: str, min_value: float) -> bool:
        """Check if item has a stat with at least the specified value.

        :param item: Item to check.
        :param stat_name: Stat name to search for.
        :param min_value: Minimum stat value.
        :return: True if item has the stat with at least min_value.
        """
        # Parse item modifiers
        modifiers = ItemModifierParser.parse_item_text(item.text, source="trade_filter")

        # Check if any modifier matches the stat and value
        for mod in modifiers:
            if stat_name.lower() in mod.stat.lower() and mod.value >= min_value:
                return True

        return False

    @staticmethod
    def search_items(items: list[Item], query: TradeQuery) -> list[TradeResult]:
        """Search items based on trade query.

        :param items: List of items to search.
        :param query: TradeQuery object.
        :return: List of TradeResult objects.
        :raises TypeError: If items is None or query is None.
        """
        if items is None:
            raise TypeError("items parameter cannot be None. Expected list[Item].")
        if query is None:
            raise TypeError("query parameter cannot be None. Expected TradeQuery.")
        # Filter items
        filtered_items = TradeAPI.filter_items(items, query.filters)

        # Filter by base type if specified
        if query.base_type:
            filtered_items = [
                item
                for item in filtered_items
                if query.base_type.lower() in item.base.lower()
            ]

        # Convert to TradeResult objects
        results: list[TradeResult] = []
        for item in filtered_items:
            # Calculate match score (simplified)
            match_score = TradeAPI._calculate_match_score(item, query)

            result = TradeResult(
                item=item,
                match_score=match_score,
            )
            results.append(result)

        # Sort by match score (descending)
        results.sort(key=lambda x: x.match_score, reverse=True)

        return results

    @staticmethod
    def _calculate_match_score(item: Item, query: TradeQuery) -> float:
        """Calculate match score for an item based on query.

        :param item: Item to score.
        :param query: TradeQuery object.
        :return: Match score (0-100).
        """
        score = 50.0  # Base score

        # Base type match
        if query.base_type:
            if query.base_type.lower() in item.base.lower():
                score += 20.0
            else:
                score -= 10.0

        # Filter matches
        for trade_filter in query.filters:
            if trade_filter.filter_type == FilterType.ITEM_LEVEL:
                if trade_filter.min_value is not None:
                    if item.item_level >= trade_filter.min_value:
                        score += 5.0
                    else:
                        score -= 5.0

            elif trade_filter.filter_type == FilterType.QUALITY:
                if trade_filter.min_value is not None and item.quality:
                    if item.quality >= trade_filter.min_value:
                        score += 5.0
                    else:
                        score -= 5.0

            elif trade_filter.filter_type == FilterType.SOCKETS:
                if trade_filter.min_value is not None and item.sockets:
                    socket_count = sum(len(group) for group in item.sockets)
                    if socket_count >= trade_filter.min_value:
                        score += 5.0
                    else:
                        score -= 5.0

        # Normalize to 0-100
        return max(0.0, min(100.0, score))

    @staticmethod
    def generate_trade_url(query: TradeQuery) -> str:
        """Generate a trade URL for Path of Exile trade site.

        This generates a URL that can be used to search for items
        on the official Path of Exile trade site.

        :param query: TradeQuery object.
        :return: Trade URL string.
        """
        # Base URL for Path of Exile trade site
        base_url = "https://www.pathofexile.com/api/trade/search"

        # Build query parameters
        params: list[str] = []

        # Base type
        if query.base_type:
            params.append(f"type={query.base_type}")

        # Online only
        if query.online_only:
            params.append("online=x")

        # Price range
        if query.price_range:
            if query.price_range.min_price > 0:
                params.append(f"min={query.price_range.min_price}")
            if query.price_range.max_price < float("inf"):
                params.append(f"max={query.price_range.max_price}")
            params.append(f"currency={query.price_range.currency}")

        # Build URL
        url = f"{base_url}/{query.league}?"
        if params:
            url += "&".join(params)

        return url

    @staticmethod
    def estimate_item_price(item: Item, league: str = "Standard") -> PriceRange:
        """Estimate item price based on its properties.

        This is a simplified price estimation. Real prices would require
        integration with trade APIs or price databases.

        :param item: Item to estimate price for.
        :param league: League name.
        :return: Estimated PriceRange.
        """
        # Base price estimation logic
        # This is a placeholder - real implementation would use
        # actual trade data or price databases

        base_price = 1.0  # Base price in chaos

        # Rarity multiplier
        rarity_multipliers = {
            "normal": 0.1,
            "magic": 0.5,
            "rare": 1.0,
            "unique": 5.0,
        }
        rarity_mult = rarity_multipliers.get(item.rarity.lower(), 1.0)

        # Item level multiplier
        ilvl_mult = 1.0 + (item.item_level - 1) * 0.01

        # Quality multiplier
        quality_mult = 1.0
        if item.quality:
            quality_mult = 1.0 + (item.quality / 100.0)

        # Socket multiplier
        socket_mult = 1.0
        if item.sockets:
            socket_count = sum(len(group) for group in item.sockets)
            max_links = max((len(group) for group in item.sockets), default=0)
            socket_mult = 1.0 + (socket_count * 0.1) + (max_links * 0.2)

        # Shaper/Elder multiplier
        influence_mult = 1.0
        if item.shaper or item.elder:
            influence_mult = 1.5

        # Calculate estimated price
        estimated_price = (
            base_price
            * rarity_mult
            * ilvl_mult
            * quality_mult
            * socket_mult
            * influence_mult
        )

        # Return price range (estimated price ± 50%)
        return PriceRange(
            min_price=estimated_price * 0.5,
            max_price=estimated_price * 1.5,
            currency="chaos",
        )

    @staticmethod
    def compare_items(item1: Item, item2: Item) -> dict[str, Any]:
        """Compare two items and return differences.

        :param item1: First item.
        :param item2: Second item.
        :return: Dictionary of differences.
        """
        differences: dict[str, Any] = {}

        if item1.rarity != item2.rarity:
            differences["rarity"] = (item1.rarity, item2.rarity)

        if item1.base != item2.base:
            differences["base"] = (item1.base, item2.base)

        if item1.item_level != item2.item_level:
            differences["item_level"] = (item1.item_level, item2.item_level)

        if item1.quality != item2.quality:
            differences["quality"] = (item1.quality, item2.quality)

        if item1.shaper != item2.shaper:
            differences["shaper"] = (item1.shaper, item2.shaper)

        if item1.elder != item2.elder:
            differences["elder"] = (item1.elder, item2.elder)

        if item1.crafted != item2.crafted:
            differences["crafted"] = (item1.crafted, item2.crafted)

        # Compare sockets
        sockets1 = (
            tuple(tuple(group) for group in item1.sockets) if item1.sockets else None
        )
        sockets2 = (
            tuple(tuple(group) for group in item2.sockets) if item2.sockets else None
        )
        if sockets1 != sockets2:
            differences["sockets"] = (sockets1, sockets2)

        return differences
