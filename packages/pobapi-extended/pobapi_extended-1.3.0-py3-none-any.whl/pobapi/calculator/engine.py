"""Main calculation engine for Path of Building.

This module provides the main CalculationEngine class that orchestrates
all calculations, replicating Path of Building's calculation flow.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pobapi.interfaces import BuildData

from pobapi import stats
from pobapi.calculator.config_modifier_parser import ConfigModifierParser
from pobapi.calculator.damage import DamageCalculator
from pobapi.calculator.defense import DefenseCalculator
from pobapi.calculator.minion import MinionCalculator
from pobapi.calculator.mirage import MirageCalculator
from pobapi.calculator.modifiers import ModifierSystem
from pobapi.calculator.pantheon import PantheonTools
from pobapi.calculator.party import PartyCalculator, PartyMember
from pobapi.calculator.passive_tree_parser import PassiveTreeParser
from pobapi.calculator.resource import ResourceCalculator
from pobapi.calculator.skill_modifier_parser import SkillModifierParser
from pobapi.calculator.skill_stats import SkillStatsCalculator

__all__ = ["CalculationEngine"]


class CalculationEngine:
    """Main calculation engine that replicates Path of Building's calculations.

    This engine processes all build data (items, passive tree, skills, config)
    and calculates all character statistics, matching Path of Building's
    Lua-based calculation engine.
    """

    def __init__(
        self,
        modifier_system: ModifierSystem | None = None,
        damage_calculator: DamageCalculator | None = None,
        defense_calculator: DefenseCalculator | None = None,
        resource_calculator: ResourceCalculator | None = None,
        skill_stats_calculator: SkillStatsCalculator | None = None,
        minion_calculator: MinionCalculator | None = None,
        party_calculator: PartyCalculator | None = None,
        mirage_calculator: MirageCalculator | None = None,
        pantheon_tools: PantheonTools | None = None,
    ):
        """
        Create a CalculationEngine and wire its dependent calculators
        to a shared modifier system.

        Parameters:
            modifier_system (ModifierSystem | None): Shared modifier system
                to use; a new instance is created when None.
            damage_calculator (DamageCalculator | None): Optional damage
                calculator to use; created and injected with the shared
                modifier system when None.
            defense_calculator (DefenseCalculator | None): Optional defense
                calculator to use; created and injected with the shared
                modifier system when None.
            resource_calculator (ResourceCalculator | None): Optional
                resource calculator to use; created and injected with the
                shared modifier system when None.
            skill_stats_calculator (SkillStatsCalculator | None): Optional
                skill-stats calculator to use; created and injected with
                the shared modifier system when None.
            minion_calculator (MinionCalculator | None): Optional minion
                calculator to use; created and injected with the shared
                modifier system when None.
            party_calculator (PartyCalculator | None): Optional party
                calculator to use; created and injected with the shared
                modifier system when None.
            mirage_calculator (MirageCalculator | None): Optional mirage
                calculator to use; created with references to the shared
                modifier system and the damage calculator when None.
            pantheon_tools (PantheonTools | None): Optional pantheon tools
                instance to use; created and injected with the shared
                modifier system when None.
        """
        # Initialize modifier system first (needed by other calculators)
        self.modifiers = modifier_system or ModifierSystem()

        # Initialize calculators with dependency injection support
        self.damage_calc = damage_calculator or DamageCalculator(self.modifiers)
        self.defense_calc = defense_calculator or DefenseCalculator(self.modifiers)
        self.resource_calc = resource_calculator or ResourceCalculator(self.modifiers)
        self.skill_stats_calc = skill_stats_calculator or SkillStatsCalculator(
            self.modifiers
        )
        self.minion_calc = minion_calculator or MinionCalculator(self.modifiers)
        self.party_calc = party_calculator or PartyCalculator(self.modifiers)

        # Mirage calculator depends on damage calculator
        self.mirage_calc = mirage_calculator or MirageCalculator(
            self.modifiers, self.damage_calc
        )

        # Pantheon tools
        self.pantheon_tools = pantheon_tools or PantheonTools(self.modifiers)

        # Ensure all calculators use the same modifier system
        if modifier_system:
            # Update modifier system references if custom system was provided
            if hasattr(self.damage_calc, "modifiers"):
                self.damage_calc.modifiers = self.modifiers
            if hasattr(self.defense_calc, "modifiers"):
                self.defense_calc.modifiers = self.modifiers
            if hasattr(self.resource_calc, "modifiers"):
                self.resource_calc.modifiers = self.modifiers
            if hasattr(self.skill_stats_calc, "modifiers"):
                self.skill_stats_calc.modifiers = self.modifiers
            if hasattr(self.minion_calc, "modifiers"):
                self.minion_calc.modifiers = self.modifiers
            if hasattr(self.party_calc, "modifiers"):
                self.party_calc.modifiers = self.modifiers
            if hasattr(self.mirage_calc, "modifiers"):
                self.mirage_calc.modifiers = self.modifiers
            if hasattr(self.pantheon_tools, "modifiers"):
                self.pantheon_tools.modifiers = self.modifiers

    def load_build(self, build_data: "BuildData | Any") -> None:
        """Load build data and extract all modifiers.

        :param build_data: PathOfBuildingAPI instance or similar build data
            implementing BuildData protocol.
        """
        self.modifiers.clear()

        # Load modifiers from passive tree
        self._load_passive_tree_modifiers(build_data)

        # Load modifiers from items
        self._load_item_modifiers(build_data)

        # Load modifiers from skills
        self._load_skill_modifiers(build_data)

        # Load modifiers from configuration
        self._load_config_modifiers(build_data)

        # Load modifiers from party members
        self._load_party_modifiers(build_data)

    def _load_passive_tree_modifiers(self, build_data: Any) -> None:
        """
        Load and add passive tree-related modifiers into the engine's
        modifier system.

        Parses the active passive tree, any additional trees, jewels
        socketed into those trees, and listed keystones from the provided
        build data and adds the resulting modifiers to self.modifiers.
        Missing build fields or invalid socket/item references are skipped
        silently.

        Parameters:
            build_data: Object containing passive tree(s), sockets, items,
                and keystones (as present in a BuildData-like structure).
        """
        try:
            # Get active tree
            active_tree = build_data.active_skill_tree
            if active_tree and active_tree.nodes:
                # Parse tree nodes
                tree_modifiers = PassiveTreeParser.parse_tree(active_tree.nodes)
                self.modifiers.add_modifiers(tree_modifiers)

                # Parse jewel sockets
                if active_tree.sockets:
                    items = build_data.items
                    allocated_nodes = active_tree.nodes or []
                    for socket_id, item_id in active_tree.sockets.items():
                        # item_id is 0-based index in items list
                        try:
                            if 0 <= item_id < len(items):
                                jewel_item = items[item_id]
                                # Parse jewel modifiers
                                # (pass allocated nodes for radius/conversion jewels)
                                jewel_modifiers = PassiveTreeParser.parse_jewel_socket(
                                    socket_id, jewel_item, allocated_nodes
                                )
                                self.modifiers.add_modifiers(jewel_modifiers)
                        except (AttributeError, IndexError, TypeError):
                            # If item_id is invalid or item doesn't exist, skip
                            pass

            # Get all trees (for multiple specs)
            trees = build_data.trees
            items = build_data.items
            for tree in trees:
                if tree.nodes:
                    tree_modifiers = PassiveTreeParser.parse_tree(tree.nodes)
                    self.modifiers.add_modifiers(tree_modifiers)

                # Parse jewel sockets for all trees
                if tree.sockets:
                    allocated_nodes = tree.nodes or []
                    for socket_id, item_id in tree.sockets.items():
                        try:
                            if 0 <= item_id < len(items):
                                jewel_item = items[item_id]
                                jewel_modifiers = PassiveTreeParser.parse_jewel_socket(
                                    socket_id, jewel_item, allocated_nodes
                                )
                                self.modifiers.add_modifiers(jewel_modifiers)
                        except (AttributeError, IndexError, TypeError):
                            pass

            # Get keystones
            keystones = build_data.keystones
            for keystone_name in keystones:
                keystone_modifiers = PassiveTreeParser.parse_keystone(keystone_name)
                self.modifiers.add_modifiers(keystone_modifiers)
        except AttributeError:
            # If build_data doesn't have these attributes, skip
            pass

    def _load_item_modifiers(self, build_data: Any) -> None:
        """Load modifiers from equipped items.

        :param build_data: Build data containing items.
        """
        try:
            items = build_data.items
            for item in items:
                # Parse item text to extract modifiers
                from pobapi.parsers.item_modifier import ItemModifierParser

                item_modifiers = ItemModifierParser.parse_item_text(
                    item.text, source=f"item:{item.name}"
                )
                self.modifiers.add_modifiers(item_modifiers)
        except AttributeError:
            # If build_data doesn't have items attribute, skip
            pass

    def _load_skill_modifiers(self, build_data: Any) -> None:
        """
        Add modifiers parsed from enabled skill groups in build_data to
        the engine's modifier system.

        Parameters:
            build_data (Any): Object expected to have a `skill_groups`
                iterable; enabled groups will be parsed for modifiers.
        """
        try:
            # Get skill groups
            skill_groups = build_data.skill_groups
            for skill_group in skill_groups:
                if skill_group.enabled:
                    # Parse skill group modifiers
                    skill_modifiers = SkillModifierParser.parse_skill_group(skill_group)
                    self.modifiers.add_modifiers(skill_modifiers)
        except AttributeError:
            # If build_data doesn't have skill_groups attribute, skip
            pass

    def _load_config_modifiers(self, build_data: Any) -> None:
        """Load modifiers from configuration settings.

        :param build_data: Build data containing configuration.
        """
        try:
            config = build_data.config
            if config:
                config_modifiers = ConfigModifierParser.parse_config(config)
                self.modifiers.add_modifiers(config_modifiers)
        except AttributeError:
            # If build_data doesn't have config attribute, skip
            pass

    def _load_party_modifiers(self, build_data: Any) -> None:
        """
        Load and apply modifiers contributed by party members to the
        engine's modifier system.

        Parses party member definitions from build_data.config.party_members
        or build_data.party_members (accepting either PartyMember objects
        or dicts), determines the active skill name when available,
        computes party aura effectiveness, and adds the resulting
        modifiers (from auras, buffs, and support-gem effects) to the
        shared modifiers system.

        Parameters:
            build_data (Any): Build data containing optional party
                configuration and active skill information.
        """
        try:
            # Check if party play is enabled
            # In Path of Building, this is typically configured in the config
            config = build_data.config if hasattr(build_data, "config") else None

            # Check for party members in config or build_data
            party_members: list[PartyMember] = []

            # Try to get party members from config
            if config and hasattr(config, "party_members"):
                party_members_data = config.party_members
                if isinstance(party_members_data, list):
                    for member_data in party_members_data:
                        if isinstance(member_data, dict):
                            party_member = PartyMember(
                                name=member_data.get("name", "Party Member"),
                                auras=member_data.get("auras", []),
                                buffs=member_data.get("buffs", []),
                                support_gems=member_data.get("support_gems", []),
                                aura_effectiveness=member_data.get(
                                    "aura_effectiveness", 100.0
                                ),
                            )
                            party_members.append(party_member)
                        elif isinstance(member_data, PartyMember):
                            party_members.append(member_data)

            # Try to get party members from build_data directly
            if not party_members and hasattr(build_data, "party_members"):
                party_members_data = build_data.party_members
                if isinstance(party_members_data, list):
                    for member_data in party_members_data:
                        if isinstance(member_data, PartyMember):
                            party_members.append(member_data)
                        elif isinstance(member_data, dict):
                            party_member = PartyMember(
                                name=member_data.get("name", "Party Member"),
                                auras=member_data.get("auras", []),
                                buffs=member_data.get("buffs", []),
                                support_gems=member_data.get("support_gems", []),
                                aura_effectiveness=member_data.get(
                                    "aura_effectiveness", 100.0
                                ),
                            )
                            party_members.append(party_member)

            # Process party members and add their modifiers
            if party_members:
                # Get active skill name for support gem effects
                active_skill_name = None
                try:
                    active_skill_group = build_data.active_skill_group
                    if active_skill_group and active_skill_group.abilities:
                        active_skill = active_skill_group.abilities[
                            (active_skill_group.active or 1) - 1
                        ]
                        if active_skill:
                            active_skill_name = active_skill.name
                except (AttributeError, IndexError):
                    pass

                # Calculate party aura effectiveness
                # Create a temporary context for this calculation
                temp_context: dict[str, Any] = {}
                party_aura_effectiveness = (
                    self.party_calc.calculate_party_aura_effectiveness(temp_context)
                )

                # Process party and get modifiers
                party_modifiers = self.party_calc.process_party(
                    party_members,
                    aura_effectiveness=party_aura_effectiveness,
                    supported_skill=active_skill_name,
                )

                # Add party modifiers to modifier system
                self.modifiers.add_modifiers(party_modifiers)

        except AttributeError:
            # If build_data doesn't have party information, skip
            pass

    def calculate_all_stats(
        self,
        context: dict[str, Any] | None = None,
        build_data: "BuildData | Any | None" = None,
    ) -> stats.Stats:
        """
        Compute the complete set of character statistics for the current
        modifier/context and optional build data.

        This replicates the engine's full stat calculation flow (defenses,
        resources, regen, leech, effective health, attributes,
        attack/cast/crit/hit stats, damage and DOTs for the active skill,
        minion-related stats, and various derived values). When provided,
        build_data is used for skill-specific calculations and enemy
        configuration.

        Parameters:
            context (dict[str, Any] | None): Calculation context values
                (enemy level, conditions, temporary overrides, etc.).
                Missing keys will be derived from modifiers or build_data
                where applicable.
            build_data ("BuildData | Any | None"): Optional build
                representation used to compute skill-specific stats
                (active skill, skill groups, config enemy values, and
                potential minion detection).

        Returns:
            stats.Stats: A Stats object populated with computed values
                (life, mana, energy shield, defenses, resistances,
                attributes, speed/crit/hit stats, DPS/DOT/average hit,
                regen/leech, EHP, unreserved resources, minion limits, and
                other derived fields).
        """
        if context is None:
            context = {}

        # Calculate attributes early so "per attribute" mods apply everywhere
        # This must be done before any other calculations that might use
        # per-attribute modifiers
        strength = self.modifiers.calculate_stat("Strength", 0.0, context)
        dexterity = self.modifiers.calculate_stat("Dexterity", 0.0, context)
        intelligence = self.modifiers.calculate_stat("Intelligence", 0.0, context)

        context["strength"] = strength
        context["dexterity"] = dexterity
        context["intelligence"] = intelligence

        # Calculate defensive stats
        defense_stats = self.defense_calc.calculate_all_defenses(context)

        # Calculate regeneration
        life_regen = self.defense_calc.calculate_life_regen(context)
        mana_regen = self.defense_calc.calculate_mana_regen(context)
        energy_shield_regen = self.defense_calc.calculate_energy_shield_regen(context)

        # Calculate leech rates
        leech_rates = self.defense_calc.calculate_leech_rates(context)

        # Calculate maximum hit taken
        from pobapi.types import DamageType

        physical_max_hit = self.defense_calc.calculate_maximum_hit_taken(
            DamageType.PHYSICAL, context
        )
        fire_max_hit = self.defense_calc.calculate_maximum_hit_taken(
            DamageType.FIRE, context
        )
        cold_max_hit = self.defense_calc.calculate_maximum_hit_taken(
            DamageType.COLD, context
        )
        lightning_max_hit = self.defense_calc.calculate_maximum_hit_taken(
            DamageType.LIGHTNING, context
        )
        chaos_max_hit = self.defense_calc.calculate_maximum_hit_taken(
            DamageType.CHAOS, context
        )

        # Calculate EHP
        total_ehp = self.defense_calc.calculate_effective_health_pool(context)

        # Calculate resource stats
        total_life = defense_stats.life
        total_mana = defense_stats.mana
        life_unreserved = self.resource_calc.calculate_unreserved_life(
            total_life, context
        )
        mana_unreserved = self.resource_calc.calculate_unreserved_mana(
            total_mana, context
        )
        life_unreserved_percent = (
            (life_unreserved / total_life * 100.0) if total_life > 0 else 0.0
        )
        mana_unreserved_percent = (
            (mana_unreserved / total_mana * 100.0) if total_mana > 0 else 0.0
        )

        # Calculate net recovery
        total_degen = self.modifiers.calculate_stat("TotalDegen", 0.0, context)
        net_life_regen = self.resource_calc.calculate_net_life_recovery(
            life_regen,
            leech_rates.get("life_leech_rate", 0.0),
            total_degen,
            context,
        )
        net_mana_regen = self.resource_calc.calculate_net_mana_recovery(
            mana_regen, leech_rates.get("mana_leech_rate", 0.0), context
        )

        # Calculate skill-specific stats
        area_of_effect_radius = None
        mana_cost = None
        mana_cost_per_second = None
        skill_cooldown = None
        if build_data:
            try:
                active_skill_group = build_data.active_skill_group
                if active_skill_group and active_skill_group.abilities:
                    active_skill = active_skill_group.abilities[
                        (active_skill_group.active or 1) - 1
                    ]
                    if active_skill:
                        skill_name = active_skill.name
                        area_of_effect_radius = (
                            self.skill_stats_calc.calculate_area_of_effect_radius(
                                skill_name, 1.0, context
                            )
                        )
                        mana_cost = self.resource_calc.calculate_mana_cost(
                            skill_name, context
                        )
                        mana_cost_per_second = (
                            self.resource_calc.calculate_mana_cost_per_second(
                                skill_name, context
                            )
                        )
                        skill_cooldown = self.skill_stats_calc.calculate_skill_cooldown(
                            skill_name, 0.0, context
                        )
            except (AttributeError, IndexError):
                pass

        # strength/dexterity/intelligence already computed and added to context above

        # Calculate speed stats
        attack_speed = self.modifiers.calculate_stat("AttackSpeed", 1.0, context)
        cast_speed = self.modifiers.calculate_stat("CastSpeed", 1.0, context)

        # Calculate crit stats
        crit_chance = self.modifiers.calculate_stat("CritChance", 0.0, context)
        crit_multiplier = self.modifiers.calculate_stat(
            "CritMultiplier", 150.0, context
        )

        # Calculate hit chance
        hit_chance = self.modifiers.calculate_stat("HitChance", 100.0, context)

        # Add enemy configuration to context
        try:
            config = build_data.config if build_data else None
            if config:
                if config.enemy_fire_resist is not None:
                    context["enemy_fire_resist"] = float(config.enemy_fire_resist)
                if config.enemy_cold_resist is not None:
                    context["enemy_cold_resist"] = float(config.enemy_cold_resist)
                if config.enemy_lightning_resist is not None:
                    context["enemy_lightning_resist"] = float(
                        config.enemy_lightning_resist
                    )
                if config.enemy_chaos_resist is not None:
                    context["enemy_chaos_resist"] = float(config.enemy_chaos_resist)
                if config.enemy_physical_damage_reduction is not None:
                    context["enemy_physical_damage_reduction"] = float(
                        config.enemy_physical_damage_reduction
                    )
        except AttributeError:
            pass

        # Calculate damage stats (for active skill)
        total_dps = None
        average_hit = None
        total_dot = None
        ignite_dps = None
        poison_dps = None
        bleed_dps = None
        if build_data:
            try:
                active_skill_group = build_data.active_skill_group
                if active_skill_group and active_skill_group.abilities:
                    active_skill = active_skill_group.abilities[
                        (active_skill_group.active or 1) - 1
                    ]
                    if active_skill:
                        skill_name = active_skill.name
                        (
                            hit_dps,
                            dot_dps,
                            total_dps,
                        ) = self.damage_calc.calculate_total_dps_with_dot(
                            skill_name, context
                        )
                        average_hit = self.damage_calc.calculate_average_hit(
                            skill_name, context
                        )
                        total_dot = dot_dps
                        ignite_dps = self.damage_calc.calculate_dot_dps(
                            skill_name, "ignite", context
                        )
                        poison_dps = self.damage_calc.calculate_dot_dps(
                            skill_name, "poison", context
                        )
                        bleed_dps = self.damage_calc.calculate_dot_dps(
                            skill_name, "bleed", context
                        )
            except (AttributeError, IndexError):
                pass

        # Calculate minion stats
        # Check if there are any minion modifiers or minion skills
        has_minions = False
        try:
            # Check for minion modifiers
            minion_damage = self.modifiers.calculate_stat("MinionDamage", 0.0, context)
            minion_life = self.modifiers.calculate_stat("MinionLife", 0.0, context)
            if minion_damage != 0.0 or minion_life != 0.0:
                has_minions = True
            # Check for minion skills
            if build_data:
                try:
                    skill_groups = build_data.skill_groups
                    for skill_group in skill_groups:
                        if skill_group.abilities:
                            for ability in skill_group.abilities:
                                skill_name = (
                                    ability.name.lower() if ability.name else ""
                                )
                                # Common minion skill names
                                minion_skills = [
                                    "raise zombie",
                                    "raise spectre",
                                    "skeleton",
                                    "golem",
                                    "animate",
                                    "dominating blow",
                                    "herald of purity",
                                    "herald of agony",
                                ]
                                if any(ms in skill_name for ms in minion_skills):
                                    has_minions = True
                                    break
                        if has_minions:
                            break
                except (AttributeError, TypeError):
                    pass
        except AttributeError:
            pass

        if has_minions:
            # Calculate minion stats with default base values
            # In a full implementation, these would come from skill gem data
            base_minion_damage = {
                "Physical": 0.0,
                "Fire": 0.0,
                "Cold": 0.0,
                "Lightning": 0.0,
                "Chaos": 0.0,
            }
            base_minion_life = 100.0  # Default base life
            base_minion_es = 0.0
            base_minion_attack_speed = 1.0
            base_minion_cast_speed = 1.0

            self.minion_calc.calculate_all_minion_stats(
                base_damage=base_minion_damage,
                base_life=base_minion_life,
                base_es=base_minion_es,
                base_attack_speed=base_minion_attack_speed,
                base_cast_speed=base_minion_cast_speed,
                context=context,
            )

        # Calculate minion limit
        minion_limit = self.modifiers.calculate_stat("MinionLimit", 0.0, context)

        # Build Stats object
        # Note: This is a simplified version - full implementation would
        # calculate all stats that Path of Building calculates
        return stats.Stats(
            life=defense_stats.life,
            mana=defense_stats.mana,
            energy_shield=defense_stats.energy_shield,
            armour=defense_stats.armour,
            evasion=defense_stats.evasion,
            block_chance=defense_stats.block_chance,
            spell_block_chance=defense_stats.spell_block_chance,
            spell_suppression_chance=defense_stats.spell_suppression_chance,
            fire_resistance=defense_stats.fire_resistance,
            cold_resistance=defense_stats.cold_resistance,
            lightning_resistance=defense_stats.lightning_resistance,
            chaos_resistance=defense_stats.chaos_resistance,
            strength=strength,
            dexterity=dexterity,
            intelligence=intelligence,
            attack_speed=attack_speed,
            cast_speed=cast_speed,
            crit_chance=crit_chance,
            crit_multiplier=crit_multiplier,
            hit_chance=int(hit_chance) if hit_chance else None,
            total_dps=total_dps,
            average_hit=average_hit,
            total_dot=total_dot,
            ignite_dps=ignite_dps,
            poison_dps=poison_dps,
            bleed_dps=bleed_dps,
            life_regen=life_regen if life_regen > 0 else None,
            mana_regen=mana_regen if mana_regen > 0 else None,
            energy_shield_regen=energy_shield_regen
            if energy_shield_regen > 0
            else None,
            life_leech_rate_per_hit=leech_rates.get("life_leech_rate")
            if leech_rates.get("life_leech_rate", 0) > 0
            else None,
            mana_leech_rate_per_hit=leech_rates.get("mana_leech_rate")
            if leech_rates.get("mana_leech_rate", 0) > 0
            else None,
            energy_shield_leech_rate_per_hit=leech_rates.get("energy_shield_leech_rate")
            if leech_rates.get("energy_shield_leech_rate", 0) > 0
            else None,
            physical_maximum_hit_taken=physical_max_hit,
            fire_maximum_hit_taken=fire_max_hit,
            cold_maximum_hit_taken=cold_max_hit,
            lightning_maximum_hit_taken=lightning_max_hit,
            chaos_maximum_hit_taken=chaos_max_hit,
            total_effective_health_pool=total_ehp,
            life_unreserved=life_unreserved if life_unreserved < total_life else None,
            life_unreserved_percent=life_unreserved_percent
            if life_unreserved_percent < 100.0
            else None,
            mana_unreserved=mana_unreserved if mana_unreserved < total_mana else None,
            mana_unreserved_percent=mana_unreserved_percent
            if mana_unreserved_percent < 100.0
            else None,
            total_degen=total_degen if total_degen > 0 else None,
            net_life_regen=net_life_regen if net_life_regen != 0.0 else None,
            net_mana_regen=net_mana_regen if net_mana_regen != 0.0 else None,
            area_of_effect_radius=area_of_effect_radius,
            mana_cost=mana_cost if mana_cost and mana_cost > 0 else None,
            mana_cost_per_second=mana_cost_per_second
            if mana_cost_per_second and mana_cost_per_second > 0
            else None,
            skill_cooldown=skill_cooldown
            if skill_cooldown and skill_cooldown > 0
            else None,
            active_minion_limit=minion_limit if minion_limit > 0 else None,
            # Additional stats would be calculated here
        )
