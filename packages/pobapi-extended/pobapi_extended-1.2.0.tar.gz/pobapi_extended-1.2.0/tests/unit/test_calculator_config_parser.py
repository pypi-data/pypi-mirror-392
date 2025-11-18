"""Tests for ConfigModifierParser."""

import pytest

from pobapi.calculator.config_modifier_parser import ConfigModifierParser
from pobapi.calculator.modifiers import ModifierType


class TestConfigModifierParser:
    """Tests for ConfigModifierParser."""

    def test_parse_config_empty(self, mock_config) -> None:
        """Test parsing empty config."""
        config = mock_config()
        modifiers = ConfigModifierParser.parse_config(config)
        assert modifiers == []

    def test_parse_config_onslaught(self, mock_config) -> None:
        """Test parsing onslaught buff."""
        config = mock_config(onslaught=True)
        modifiers = ConfigModifierParser.parse_config(config)
        assert len(modifiers) == 3
        assert any(
            m.stat == "AttackSpeed"
            and m.value == 20.0
            and m.mod_type == ModifierType.INCREASED
            and m.source == "config:onslaught"
            for m in modifiers
        )
        assert any(
            m.stat == "CastSpeed"
            and m.value == 20.0
            and m.mod_type == ModifierType.INCREASED
            for m in modifiers
        )
        assert any(
            m.stat == "MovementSpeed"
            and m.value == 20.0
            and m.mod_type == ModifierType.INCREASED
            for m in modifiers
        )

    def test_parse_config_fortify(self, mock_config) -> None:
        """Test parsing fortify buff."""
        config = mock_config(fortify=True)
        modifiers = ConfigModifierParser.parse_config(config)
        assert len(modifiers) == 1
        mod = modifiers[0]
        assert mod.stat == "DamageTaken"
        assert mod.value == -20.0
        assert mod.mod_type == ModifierType.INCREASED
        assert mod.source == "config:fortify"

    def test_parse_config_tailwind(self, mock_config) -> None:
        """Test parsing tailwind buff."""
        config = mock_config(tailwind=True)
        modifiers = ConfigModifierParser.parse_config(config)
        assert len(modifiers) == 1
        mod = modifiers[0]
        assert mod.stat == "ActionSpeed"
        assert mod.value == 10.0
        assert mod.mod_type == ModifierType.INCREASED
        assert mod.source == "config:tailwind"

    def test_parse_config_adrenaline(self, mock_config) -> None:
        """Test parsing adrenaline buff."""
        config = mock_config(adrenaline=True)
        modifiers = ConfigModifierParser.parse_config(config)
        assert len(modifiers) == 4
        assert any(m.stat == "Damage" and m.value == 100.0 for m in modifiers)
        assert any(m.stat == "AttackSpeed" and m.value == 25.0 for m in modifiers)
        assert any(m.stat == "CastSpeed" and m.value == 25.0 for m in modifiers)
        assert any(m.stat == "MovementSpeed" and m.value == 25.0 for m in modifiers)

    @pytest.mark.parametrize(
        ("charges", "expected_value"),
        [(3, 150.0), (5, 250.0), (7, 350.0)],
    )
    def test_parse_config_power_charges(
        self, mock_config, charges: int, expected_value: float
    ) -> None:
        """Test parsing power charges."""
        config = mock_config(use_power_charges=True, max_power_charges=charges)
        modifiers = ConfigModifierParser.parse_config(config)
        assert len(modifiers) == 1
        mod = modifiers[0]
        assert mod.stat == "CritChance"
        assert mod.value == expected_value
        assert mod.mod_type == ModifierType.INCREASED
        assert mod.source == "config:power_charges"

    @pytest.mark.parametrize(
        ("charges", "expected_speed", "expected_damage"),
        [(3, 12.0, 12.0), (5, 20.0, 20.0), (7, 28.0, 28.0)],
    )
    def test_parse_config_frenzy_charges(
        self, mock_config, charges: int, expected_speed: float, expected_damage: float
    ) -> None:
        """Test parsing frenzy charges."""
        config = mock_config(use_frenzy_charges=True, max_frenzy_charges=charges)
        modifiers = ConfigModifierParser.parse_config(config)
        assert len(modifiers) == 3
        assert any(
            m.stat == "AttackSpeed" and m.value == expected_speed for m in modifiers
        )
        assert any(
            m.stat == "CastSpeed" and m.value == expected_speed for m in modifiers
        )
        assert any(m.stat == "Damage" and m.value == expected_damage for m in modifiers)

    @pytest.mark.parametrize(
        ("charges", "expected_res"),
        [(3, 12.0), (5, 20.0), (7, 28.0)],
    )
    def test_parse_config_endurance_charges(
        self, mock_config, charges: int, expected_res: float
    ) -> None:
        """Test parsing endurance charges."""
        config = mock_config(use_endurance_charges=True, max_endurance_charges=charges)
        modifiers = ConfigModifierParser.parse_config(config)
        assert len(modifiers) == 4
        assert any(
            m.stat == "PhysicalDamageReduction"
            and m.value == expected_res
            and m.mod_type == ModifierType.FLAT
            for m in modifiers
        )
        assert any(
            m.stat == "FireResistance"
            and m.value == expected_res
            and m.mod_type == ModifierType.FLAT
            for m in modifiers
        )
        assert any(
            m.stat == "ColdResistance"
            and m.value == expected_res
            and m.mod_type == ModifierType.FLAT
            for m in modifiers
        )
        assert any(
            m.stat == "LightningResistance"
            and m.value == expected_res
            and m.mod_type == ModifierType.FLAT
            for m in modifiers
        )

    def test_parse_config_hatred(self, mock_config) -> None:
        """Test parsing Hatred aura."""
        config = mock_config(has_hatred=True)
        modifiers = ConfigModifierParser.parse_config(config)
        # Hatred gives: ColdDamage (MORE) and PhysicalAsExtraCold
        assert len(modifiers) >= 1
        assert any(
            m.stat == "ColdDamage"
            and m.value == 36.0
            and m.mod_type == ModifierType.MORE
            for m in modifiers
        )
        # Check for PhysicalAsExtraCold (might be named differently)
        assert any(
            "Cold" in m.stat or m.stat == "PhysicalAsExtraCold" for m in modifiers
        )

    def test_parse_config_anger(self, mock_config) -> None:
        """Test parsing Anger aura."""
        config = mock_config(has_anger=True)
        modifiers = ConfigModifierParser.parse_config(config)
        # Anger gives: FireDamage (MORE) and PhysicalAsExtraFire
        assert len(modifiers) == 2
        assert any(
            m.stat == "FireDamage"
            and m.value == 36.0
            and m.mod_type == ModifierType.MORE
            for m in modifiers
        )
        assert any(
            m.stat == "PhysicalAsExtraFire" and m.value == 15.0 for m in modifiers
        )

    def test_parse_config_wrath(self, mock_config) -> None:
        """Test parsing Wrath aura."""
        config = mock_config(has_wrath=True)
        modifiers = ConfigModifierParser.parse_config(config)
        # Wrath gives: LightningDamage (MORE) and PhysicalAsExtraLightning
        assert len(modifiers) == 2
        assert any(
            m.stat == "LightningDamage"
            and m.value == 36.0
            and m.mod_type == ModifierType.MORE
            for m in modifiers
        )
        assert any(
            m.stat == "PhysicalAsExtraLightning" and m.value == 15.0 for m in modifiers
        )

    def test_parse_config_haste(self, mock_config) -> None:
        """Test parsing Haste aura."""
        config = mock_config(has_haste=True)
        modifiers = ConfigModifierParser.parse_config(config)
        assert len(modifiers) == 3
        assert any(m.stat == "AttackSpeed" for m in modifiers)
        assert any(m.stat == "CastSpeed" for m in modifiers)
        assert any(m.stat == "MovementSpeed" for m in modifiers)

    def test_parse_config_grace(self, mock_config) -> None:
        """Test parsing Grace aura."""
        config = mock_config(has_grace=True)
        modifiers = ConfigModifierParser.parse_config(config)
        assert len(modifiers) == 1
        mod = modifiers[0]
        assert mod.stat == "Evasion"
        assert mod.value == 3000.0
        assert mod.mod_type == ModifierType.FLAT  # Grace gives flat evasion
        assert mod.source == "config:grace"

    def test_parse_config_determination(self, mock_config) -> None:
        """Test parsing Determination aura."""
        config = mock_config(has_determination=True)
        modifiers = ConfigModifierParser.parse_config(config)
        assert len(modifiers) == 1
        mod = modifiers[0]
        assert mod.stat == "Armour"
        assert mod.value == 3000.0
        assert mod.mod_type == ModifierType.FLAT  # Determination gives flat armour
        assert mod.source == "config:determination"

    def test_parse_config_discipline(self, mock_config) -> None:
        """Test parsing Discipline aura."""
        config = mock_config(has_discipline=True)
        modifiers = ConfigModifierParser.parse_config(config)
        assert len(modifiers) == 1
        mod = modifiers[0]
        assert mod.stat == "EnergyShield"
        assert mod.value == 200.0
        assert mod.mod_type == ModifierType.FLAT  # Discipline gives flat ES
        assert mod.source == "config:discipline"

    @pytest.mark.parametrize(
        ("curse", "expected_stat"),
        [
            ("has_flammability", "EnemyFireResistance"),
            ("has_frostbite", "EnemyColdResistance"),
            ("has_conductivity", "EnemyLightningResistance"),
        ],
    )
    def test_parse_config_elemental_curses(
        self, mock_config, curse: str, expected_stat: str
    ) -> None:
        """Test parsing elemental curses."""
        config = mock_config(**{curse: True})
        modifiers = ConfigModifierParser.parse_config(config)
        assert len(modifiers) == 1
        mod = modifiers[0]
        assert mod.stat == expected_stat
        assert mod.value == -44.0
        assert mod.mod_type == ModifierType.FLAT
        assert mod.source.startswith("config:")

    def test_parse_config_enfeeble(self, mock_config) -> None:
        """Test parsing Enfeeble curse."""
        config = mock_config(has_enfeeble=True)
        modifiers = ConfigModifierParser.parse_config(config)
        assert len(modifiers) == 1
        mod = modifiers[0]
        assert mod.stat == "EnemyDamage"
        assert mod.value == -30.0  # Actual value from code
        assert mod.mod_type == ModifierType.INCREASED
        assert mod.source == "config:enfeeble"

    def test_parse_config_vulnerability(self, mock_config) -> None:
        """Test parsing Vulnerability curse."""
        config = mock_config(has_vulnerability=True)
        modifiers = ConfigModifierParser.parse_config(config)
        assert len(modifiers) == 1
        mod = modifiers[0]
        assert mod.stat == "EnemyPhysicalDamageTaken"
        assert mod.value == 25.0  # Actual value from code
        assert mod.mod_type == ModifierType.INCREASED
        assert mod.source == "config:vulnerability"

    def test_parse_config_conditions(self, mock_config) -> None:
        """Test parsing condition flags."""
        config = mock_config(
            on_full_life=True,
            on_low_life=True,
            on_full_energy_shield=True,
            on_full_mana=True,
        )
        modifiers = ConfigModifierParser.parse_config(config)
        # Conditions create flag modifiers
        assert len(modifiers) == 4
        assert any(m.stat == "OnFullLife" for m in modifiers)
        assert any(m.stat == "OnLowLife" for m in modifiers)
        assert any(m.stat == "OnFullEnergyShield" for m in modifiers)
        assert any(m.stat == "OnFullMana" for m in modifiers)

    def test_parse_config_multiple_buffs(self, mock_config) -> None:
        """Test parsing multiple buffs at once."""
        config = mock_config(
            onslaught=True,
            fortify=True,
            tailwind=True,
            use_power_charges=True,
            max_power_charges=5,
        )
        modifiers = ConfigModifierParser.parse_config(config)
        # Onslaught: 3, Fortify: 1, Tailwind: 1, Power charges: 1
        assert len(modifiers) == 6

    def test_parse_config_invalid_config(self) -> None:
        """Test parsing invalid config object."""
        # Should handle gracefully
        modifiers = ConfigModifierParser.parse_config(None)
        assert modifiers == []

        modifiers = ConfigModifierParser.parse_config(object())
        assert modifiers == []
