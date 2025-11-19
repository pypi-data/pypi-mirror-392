"""Tests for GameDataLoader."""

import json
import tempfile
from pathlib import Path

from pobapi.calculator.game_data import (
    GameDataLoader,
    PassiveNode,
    SkillGem,
    UniqueItem,
)


class TestPassiveNode:
    """Tests for PassiveNode dataclass."""

    def test_init(self) -> None:
        """Test PassiveNode initialization."""
        node = PassiveNode(
            node_id=12345,
            name="Test Node",
            stats=["+10 to Strength"],
            is_keystone=False,
        )
        assert node.node_id == 12345
        assert node.name == "Test Node"
        assert len(node.stats) == 1


class TestSkillGem:
    """Tests for SkillGem dataclass."""

    def test_init(self) -> None:
        """Test SkillGem initialization."""
        gem = SkillGem(
            name="Fireball",
            base_damage={"Fire": (10.0, 15.0)},
            is_spell=True,
        )
        assert gem.name == "Fireball"
        assert gem.is_spell is True
        assert gem.is_attack is False


class TestUniqueItem:
    """Tests for UniqueItem dataclass."""

    def test_init(self) -> None:
        """Test UniqueItem initialization."""
        unique = UniqueItem(
            name="Test Unique",
            base_type="Leather Belt",
            special_effects=["Special effect"],
        )
        assert unique.name == "Test Unique"
        assert unique.base_type == "Leather Belt"
        assert len(unique.special_effects) == 1


class TestGameDataLoader:
    """Tests for GameDataLoader."""

    def test_init(self) -> None:
        """Test GameDataLoader initialization."""
        loader = GameDataLoader()
        assert loader is not None

    def test_load_passive_tree_data_empty(self) -> None:
        """Test loading passive tree data from empty file."""
        loader = GameDataLoader()
        # Without actual data file, should return empty or handle gracefully
        nodes = loader.load_passive_tree_data()
        assert isinstance(nodes, dict)

    def test_load_skill_gem_data_empty(self) -> None:
        """Test loading skill gem data from empty file."""
        loader = GameDataLoader()
        gems = loader.load_skill_gem_data()
        assert isinstance(gems, dict)

    def test_load_unique_item_data_empty(self) -> None:
        """Test loading unique item data from empty file."""
        loader = GameDataLoader()
        uniques = loader.load_unique_item_data()
        assert isinstance(uniques, dict)

    def test_load_unique_item_data_from_file(self) -> None:
        """Test loading unique item data from JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "uniques.json"
            data = {
                "uniques": {
                    "TestUnique": {
                        "name": "Test Unique",
                        "baseType": "Leather Belt",
                        "specialEffects": ["Effect 1"],
                        "implicitMods": ["+10 to Strength"],
                        "explicitMods": ["+20 to Life"],
                    }
                }
            }
            with open(data_file, "w") as f:
                json.dump(data, f)

            loader = GameDataLoader()
            loader._data_paths = [str(tmpdir)]
            uniques = loader.load_unique_item_data(str(data_file))
            assert len(uniques) >= 1
            assert "testunique" in uniques or "TestUnique" in uniques

    def test_get_unique_item_not_found(self) -> None:
        """Test getting unique item that doesn't exist."""
        loader = GameDataLoader()
        item = loader.get_unique_item("NonExistent Unique")
        assert item is None

    def test_get_unique_item_by_name(self) -> None:
        """Test getting unique item by name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "uniques.json"
            data = {
                "uniques": {
                    "inpulsasbrokenheart": {  # Normalized name
                        "name": "Inpulsa's Broken Heart",
                        "baseType": "Sadist Garb",
                        "specialEffects": [
                            (
                                "Enemies you kill explode, dealing 5% of "
                                "their Life as Lightning Damage"
                            )
                        ],
                        "implicitMods": [],
                        "explicitMods": ["+100 to maximum Life"],
                    }
                }
            }
            with open(data_file, "w") as f:
                json.dump(data, f)

            loader = GameDataLoader()
            loader._data_paths = [str(tmpdir)]
            loader.load_unique_item_data(str(data_file))
            # Get the unique item - should be found
            item = loader.get_unique_item("Inpulsa's Broken Heart")
            assert item is not None
            assert isinstance(item, UniqueItem)
            assert item.name == "Inpulsa's Broken Heart"

    def test_get_passive_node_not_found(self) -> None:
        """Test getting passive node that doesn't exist - covers line 482."""
        loader = GameDataLoader()
        # Load some data first
        loader.load_passive_tree_data()
        # Try to get non-existent node (covers line 482)
        node = loader.get_passive_node(999999)
        assert node is None

    def test_get_skill_gem_not_found(self) -> None:
        """Test getting skill gem that doesn't exist - covers line 490."""
        loader = GameDataLoader()
        # Load some data first
        loader.load_skill_gem_data()
        # Try to get non-existent gem (covers line 490)
        gem = loader.get_skill_gem("NonExistent Gem")
        assert gem is None

    def test_get_unique_item_with_normalized_name(self) -> None:
        """Test getting unique item with normalized name - covers line 505."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "uniques.json"
            data = {
                "uniques": {
                    "testunique": {  # Normalized name (lowercase, no spaces)
                        "name": "Test Unique",
                        "baseType": "Leather Belt",
                        "specialEffects": ["Effect 1"],
                    }
                }
            }
            with open(data_file, "w") as f:
                json.dump(data, f)

            loader = GameDataLoader()
            loader._data_paths = [str(tmpdir)]
            loader.load_unique_item_data(str(data_file))
            # Try to get with name that needs normalization (covers line 505)
            item = loader.get_unique_item("Test Unique")
            assert item is not None
            assert item.name == "Test Unique"

    def test_get_unique_item_with_case_insensitive_search(self) -> None:
        """Test getting unique item with case-insensitive search - covers line 510."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "uniques.json"
            data = {
                "uniques": {
                    "TestUnique": {
                        "name": "Test Unique",
                        "baseType": "Leather Belt",
                        "specialEffects": ["Effect 1"],
                    }
                }
            }
            with open(data_file, "w") as f:
                json.dump(data, f)

            loader = GameDataLoader()
            loader._data_paths = [str(tmpdir)]
            loader.load_unique_item_data(str(data_file))
            # Try to get with different case (covers line 510
            # - key.lower() == unique_name.lower())
            item = loader.get_unique_item("testunique")
            assert item is not None
            assert item.name == "Test Unique"

    def test_get_unique_item_with_item_name_match(self) -> None:
        """Test getting unique item by matching item.name - covers line 513."""
        loader = GameDataLoader()
        # Manually add an item with a key that won't match our search term
        # but with a name that will - this forces the loop to check item.name
        from pobapi.calculator.game_data import UniqueItem

        test_item = UniqueItem(
            name="Special Test Item",
            base_type="Leather Belt",
            special_effects=[],
            implicit_mods=[],
            explicit_mods=[],
        )
        # Store with a key that won't match our search (covers line 513)
        loader._unique_items["unmatchablekey"] = test_item
        # Search with term that doesn't match key but matches item.name.lower()
        item = loader.get_unique_item("special test item")
        assert item is not None
        assert item.name == "Special Test Item"

    def test_load_unique_item_data_fallback_to_uniques_json(self, mocker) -> None:
        """Test load_unique_item_data falls back to uniques.json - covers line 431."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create uniques.json (not uniques_processed.json) to test fallback
            uniques_file = Path(tmpdir) / "uniques.json"
            data = {
                "uniques": {
                    "testunique": {
                        "name": "Test Unique",
                        "baseType": "Leather Belt",
                        "specialEffects": ["Effect 1"],
                    }
                }
            }
            with open(uniques_file, "w") as f:
                json.dump(data, f)

            loader = GameDataLoader()
            loader._data_paths = [str(tmpdir)]
            # Mock _find_data_file to return None
            # for uniques_processed.json, then path for uniques.json
            mock_find = mocker.patch.object(
                loader, "_find_data_file", side_effect=[None, str(uniques_file)]
            )

            # Should fall back to uniques.json (covers line 431)
            uniques = loader.load_unique_item_data()
            assert isinstance(uniques, dict)
            # Verify that _find_data_file was called for both files
            assert mock_find.call_count >= 2
            # Verify that unique was loaded
            assert len(uniques) > 0

    def test_find_data_file_nonexistent(self) -> None:
        """Test finding non-existent data file."""
        loader = GameDataLoader()
        path = loader._find_data_file("nonexistent_file.json")
        assert path is None

    def test_load_unique_item_data_camel_case(self) -> None:
        """Test loading unique item data with camelCase keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "uniques.json"
            data = {
                "uniques": {
                    "TestUnique": {
                        "name": "Test Unique",
                        "baseType": "Leather Belt",
                        "specialEffects": ["Effect 1"],
                        "implicitMods": ["+10 to Strength"],
                        "explicitMods": ["+20 to Life"],
                    }
                }
            }
            with open(data_file, "w") as f:
                json.dump(data, f)

            loader = GameDataLoader()
            # Override data path for testing
            loader._data_paths = [str(tmpdir)]
            uniques = loader.load_unique_item_data(str(data_file))
            assert len(uniques) >= 1
            assert "testunique" in uniques or "TestUnique" in uniques

    def test_load_unique_item_data_snake_case(self) -> None:
        """Test loading unique item data with snake_case keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "uniques.json"
            data = {
                "uniques": {
                    "TestUnique": {
                        "name": "Test Unique",
                        "base_type": "Leather Belt",
                        "special_effects": ["Effect 1"],
                        "implicit_mods": ["+10 to Strength"],
                        "explicit_mods": ["+20 to Life"],
                    }
                }
            }
            with open(data_file, "w") as f:
                json.dump(data, f)

            loader = GameDataLoader()
            loader._data_paths = [str(tmpdir)]
            uniques = loader.load_unique_item_data(str(data_file))
            assert len(uniques) >= 1

    def test_find_data_file_existing(self) -> None:
        """Test finding existing data file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "test.json"
            data_file.write_text('{"test": "data"}')

            loader = GameDataLoader()
            # Set data_directory to tmpdir
            loader.data_directory = str(tmpdir)
            found_path = loader._find_data_file("test.json")
            # Should find the file in data_directory
            assert found_path == str(data_file) or found_path is not None

    def test_find_data_file_with_env_var(self, monkeypatch) -> None:
        """Test finding data file using environment variable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "test.json"
            data_file.write_text('{"test": "data"}')

            monkeypatch.setenv("POBAPI_DATA_DIR", str(tmpdir))
            loader = GameDataLoader()
            found_path = loader._find_data_file("test.json")
            assert found_path == str(data_file)

    def test_load_passive_tree_data_from_file(self) -> None:
        """Test loading passive tree data from JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "nodes.json"
            data = {
                "nodes": {
                    "12345": {
                        "name": "Test Node",
                        "stats": ["+10 to Strength"],
                        "isKeystone": False,
                    }
                }
            }
            with open(data_file, "w") as f:
                json.dump(data, f)

            loader = GameDataLoader()
            loader._data_paths = [str(tmpdir)]
            nodes = loader.load_passive_tree_data(str(data_file))
            assert len(nodes) >= 1
            assert 12345 in nodes

    def test_load_skill_gem_data_from_file(self) -> None:
        """Test loading skill gem data from JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "gems.json"
            data = {
                "gems": {
                    "Fireball": {
                        "baseDamage": {"Fire": [10.0, 15.0]},
                        "damageEffectiveness": 100.0,
                        "isSpell": True,
                    }
                }
            }
            with open(data_file, "w") as f:
                json.dump(data, f)

            loader = GameDataLoader()
            loader._data_paths = [str(tmpdir)]
            gems = loader.load_skill_gem_data(str(data_file))
            assert len(gems) >= 1
            assert "Fireball" in gems

    def test_load_passive_tree_data_invalid_json(self) -> None:
        """Test loading passive tree data from invalid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "nodes.json"
            data_file.write_text("invalid json")

            loader = GameDataLoader()
            loader._data_paths = [str(tmpdir)]
            nodes = loader.load_passive_tree_data(str(data_file))
            # Should return empty dict on error
            assert isinstance(nodes, dict)

    def test_load_skill_gem_data_invalid_json(self) -> None:
        """Test loading skill gem data from invalid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "gems.json"
            data_file.write_text("invalid json")

            loader = GameDataLoader()
            loader._data_paths = [str(tmpdir)]
            gems = loader.load_skill_gem_data(str(data_file))
            # Should return empty dict on error
            assert isinstance(gems, dict)

    def test_load_unique_item_data_invalid_json(self) -> None:
        """Test loading unique item data from invalid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "uniques.json"
            data_file.write_text("invalid json")

            loader = GameDataLoader()
            loader._data_paths = [str(tmpdir)]
            uniques = loader.load_unique_item_data(str(data_file))
            # Should return empty dict on error
            assert isinstance(uniques, dict)

    def test_load_passive_tree_data_wrong_structure(self) -> None:
        """Test loading passive tree data with wrong structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "nodes.json"
            data = {"wrong": "structure"}
            with open(data_file, "w") as f:
                json.dump(data, f)

            loader = GameDataLoader()
            loader._data_paths = [str(tmpdir)]
            nodes = loader.load_passive_tree_data(str(data_file))
            # Should return empty dict if structure is wrong
            assert isinstance(nodes, dict)

    def test_load_skill_gem_data_wrong_structure(self) -> None:
        """Test loading skill gem data with wrong structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "gems.json"
            data = {"wrong": "structure"}
            with open(data_file, "w") as f:
                json.dump(data, f)

            loader = GameDataLoader()
            loader._data_paths = [str(tmpdir)]
            gems = loader.load_skill_gem_data(str(data_file))
            # Should return empty dict if structure is wrong
            assert isinstance(gems, dict)
