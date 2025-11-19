"""Tests for PartyCalculator."""

from typing import TYPE_CHECKING, Any

import pytest

from pobapi.calculator.modifiers import ModifierType
from pobapi.calculator.party import PartyMember

if TYPE_CHECKING:
    from pobapi.calculator.modifiers import ModifierSystem
    from pobapi.calculator.party import PartyCalculator


class TestPartyMember:
    """Tests for PartyMember dataclass."""

    def test_init_default(self) -> None:
        """Test PartyMember initialization with defaults."""
        member = PartyMember()
        assert member.name == "Party Member"
        assert member.aura_effectiveness == 100.0
        assert member.auras == []
        assert member.buffs == []
        assert member.support_gems == []

    def test_init_custom(self) -> None:
        """Test PartyMember initialization with custom values."""
        member = PartyMember(
            name="Support Build",
            auras=["Hatred", "Anger"],
            aura_effectiveness=50.0,
        )
        assert member.name == "Support Build"
        assert member.auras is not None
        assert len(member.auras) == 2
        assert member.aura_effectiveness == 50.0


class TestPartyCalculator:
    """Tests for PartyCalculator."""

    def test_init(self, party_calculator: "PartyCalculator") -> None:
        """Test PartyCalculator initialization."""
        assert party_calculator.modifiers is not None

    def test_add_party_member_auras_empty(
        self, party_calculator: "PartyCalculator"
    ) -> None:
        """Test adding party member with no auras."""
        member = PartyMember(auras=[])
        modifiers = party_calculator.add_party_member_auras(member)
        assert modifiers == []

    def test_add_party_member_auras_hatred(
        self, party_calculator: "PartyCalculator"
    ) -> None:
        """Test adding Hatred aura from party member."""
        member = PartyMember(auras=["Hatred"])
        modifiers = party_calculator.add_party_member_auras(member)
        assert len(modifiers) >= 1
        assert any(
            m.stat == "ColdDamage" and m.mod_type == ModifierType.MORE
            for m in modifiers
        )

    @pytest.mark.parametrize(
        ("aura_name", "expected_stats"),
        [
            ("Hatred", ["ColdDamage", "PhysicalAsExtraCold"]),
            ("Anger", ["FireDamage", "PhysicalAsExtraFire"]),
            ("Wrath", ["LightningDamage", "PhysicalAsExtraLightning"]),
            ("Haste", ["AttackSpeed", "CastSpeed", "MovementSpeed"]),
            ("Grace", ["Evasion"]),
            ("Determination", ["Armour"]),
            ("Discipline", ["EnergyShield"]),
        ],
    )
    def test_add_party_member_auras_common(
        self,
        party_calculator: "PartyCalculator",
        aura_name: str,
        expected_stats: list[str],
    ) -> None:
        """Test adding common auras from party member."""
        member = PartyMember(auras=[aura_name])
        modifiers = party_calculator.add_party_member_auras(member)
        assert len(modifiers) >= 1
        for stat in expected_stats:
            assert any(
                m.stat == stat for m in modifiers
            ), f"Expected stat '{stat}' not found"

    def test_add_party_member_auras_effectiveness(
        self, party_calculator: "PartyCalculator"
    ) -> None:
        """Test aura effectiveness from party member."""
        from pobapi.calculator.party import PartyCalculator

        # Get base Hatred ColdDamage value from AURA_EFFECTS constant
        base_hatred_cold_damage = PartyCalculator.AURA_EFFECTS["Hatred"][0].value
        member = PartyMember(auras=["Hatred"], aura_effectiveness=50.0)
        # Pass 50.0 as aura_effectiveness parameter
        modifiers = party_calculator.add_party_member_auras(
            member, aura_effectiveness=50.0
        )
        # Auras from party members should have reduced effectiveness
        assert len(modifiers) >= 1
        # Check that values are reduced (50% effectiveness)
        # The method divides by 100.0, so 50.0 / 100.0 = 0.5
        expected_value = base_hatred_cold_damage * 0.5
        for mod in modifiers:
            if mod.stat == "ColdDamage":
                assert mod.value == pytest.approx(expected_value, rel=1e-6)

    def test_add_party_member_buffs_empty(
        self, party_calculator: "PartyCalculator"
    ) -> None:
        """Test adding party member with no buffs."""
        member = PartyMember(buffs=[])
        modifiers = party_calculator.add_party_member_buffs(member)
        assert modifiers == []

    def test_add_party_member_buffs_onslaught(
        self, party_calculator: "PartyCalculator"
    ) -> None:
        """Test adding Onslaught buff from party member."""
        member = PartyMember(buffs=["Onslaught"])
        modifiers = party_calculator.add_party_member_buffs(member)
        assert len(modifiers) >= 1
        assert any(m.stat == "AttackSpeed" for m in modifiers)

    def test_add_party_member_support_effects_empty(
        self, party_calculator: "PartyCalculator"
    ) -> None:
        """Test adding party member with no support gems."""
        member = PartyMember(support_gems=[])
        modifiers = party_calculator.add_party_member_support_effects(member)
        assert modifiers == []

    def test_add_party_member_support_effects(
        self, party_calculator: "PartyCalculator"
    ) -> None:
        """Test adding support gem effects from party member."""
        member = PartyMember(support_gems=["Added Fire Damage Support"])
        modifiers = party_calculator.add_party_member_support_effects(member)
        # Support effects from party members might be empty for now
        assert isinstance(modifiers, list)

    def test_calculate_party_aura_effectiveness_base(
        self, party_calculator: "PartyCalculator"
    ) -> None:
        """Test calculating base party aura effectiveness."""
        context: dict[str, Any] = {}
        effectiveness = party_calculator.calculate_party_aura_effectiveness(context)
        # Default should be 50% (party members share auras at 50% effectiveness)
        assert effectiveness == pytest.approx(50.0, rel=1e-6)

    def test_calculate_party_aura_effectiveness_with_modifiers(
        self,
        party_calculator: "PartyCalculator",
        modifier_system: "ModifierSystem",
    ) -> None:
        """Test calculating party aura effectiveness with modifiers."""
        from pobapi.calculator.modifiers import Modifier

        # Add modifier to party_calculator's modifier system
        party_calculator.modifiers.add_modifier(
            Modifier(
                stat="PartyAuraEffectiveness",
                value=20.0,
                mod_type=ModifierType.INCREASED,
                source="test",
            )
        )
        context: dict[str, Any] = {}
        effectiveness = party_calculator.calculate_party_aura_effectiveness(context)
        # Base is 50%, modifiers should increase it
        assert (
            effectiveness > 50.0
        )  # Verify modifiers were applied and increased effectiveness
        assert effectiveness <= 100.0  # Verify it remains within valid range

    def test_process_party_empty(self, party_calculator: "PartyCalculator") -> None:
        """Test processing empty party."""
        members = []
        modifiers = party_calculator.process_party(members)
        assert modifiers == []

    def test_process_party_multiple(self, party_calculator: "PartyCalculator") -> None:
        """Test processing multiple party members."""
        members: list[PartyMember] = [
            PartyMember(auras=["Hatred"]),
            PartyMember(auras=["Anger"]),
            PartyMember(buffs=["Onslaught"]),
        ]
        modifiers = party_calculator.process_party(members)
        assert len(modifiers) >= 3  # At least one modifier per member

    def test_add_party_member_auras_none(
        self, party_calculator: "PartyCalculator"
    ) -> None:
        """Test add_party_member_auras with None auras - covers line 348."""
        member = PartyMember(name="Player1", auras=None)
        # __post_init__ sets auras to [], so we need to set it to None after creation
        # to cover the None check on line 348
        object.__setattr__(member, "auras", None)
        modifiers = party_calculator.add_party_member_auras(member)
        assert modifiers == []

    def test_add_party_member_buffs_none(
        self, party_calculator: "PartyCalculator"
    ) -> None:
        """Test add_party_member_buffs with None buffs - covers line 381."""
        member = PartyMember(name="Player1", buffs=None)
        # __post_init__ sets buffs to [], so we need to set it to None after creation
        # to cover the None check on line 381
        object.__setattr__(member, "buffs", None)
        modifiers = party_calculator.add_party_member_buffs(member)
        assert modifiers == []

    def test_add_party_member_support_effects_none(
        self, party_calculator: "PartyCalculator"
    ) -> None:
        """Test add_party_member_support_effects with None support_gems.

        Covers line 416."""
        member = PartyMember(name="Player1", support_gems=None)
        # __post_init__ sets support_gems to [], so we
        # need to set it to None after creation
        # to cover the None check on line 416
        object.__setattr__(member, "support_gems", None)
        modifiers = party_calculator.add_party_member_support_effects(member)
        assert modifiers == []

    def test_calculate_party_aura_effectiveness_none_context(
        self, party_calculator: "PartyCalculator"
    ) -> None:
        """Test calculate_party_aura_effectiveness with None context.

        Covers line 486."""
        result = party_calculator.calculate_party_aura_effectiveness(None)
        assert result == 50.0  # Base effectiveness

    def test_calculate_party_aura_effectiveness_attribute_error(
        self, party_calculator: "PartyCalculator", mocker
    ) -> None:
        """Test calculate_party_aura_effectiveness handles AttributeError.

        Covers lines 501-503."""
        # Mock calculate_stat to raise AttributeError
        mocker.patch.object(
            party_calculator.modifiers,
            "calculate_stat",
            side_effect=AttributeError("No such attribute"),
        )
        result = party_calculator.calculate_party_aura_effectiveness({})
        # Should use 0.0 when AttributeError occurs
        assert result == 50.0  # base_effectiveness * (1.0 + 0.0 / 100.0) = 50.0

    def test_calculate_party_aura_effectiveness_key_error(
        self, party_calculator: "PartyCalculator", mocker
    ) -> None:
        """Test calculate_party_aura_effectiveness handles KeyError.

        Covers lines 501-503."""
        # Mock calculate_stat to raise KeyError
        mocker.patch.object(
            party_calculator.modifiers,
            "calculate_stat",
            side_effect=KeyError("No such key"),
        )
        result = party_calculator.calculate_party_aura_effectiveness({})
        # Should use 0.0 when KeyError occurs
        assert result == 50.0  # base_effectiveness * (1.0 + 0.0 / 100.0) = 50.0
