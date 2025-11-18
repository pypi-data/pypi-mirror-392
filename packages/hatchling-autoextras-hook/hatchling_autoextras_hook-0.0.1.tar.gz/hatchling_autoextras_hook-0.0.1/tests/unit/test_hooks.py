from __future__ import annotations

from hatchling_autoextras_hook.hooks import AutoExtrasMetadataHook


def test_plugin_name() -> None:
    """Test that the plugin name is correct."""
    assert AutoExtrasMetadataHook.PLUGIN_NAME == "autoextras"


def test_update_with_no_optional_dependencies() -> None:
    """Test that update does nothing when there are no optional
    dependencies."""
    metadata = {}
    AutoExtrasMetadataHook("test", {}).update(metadata)
    assert metadata == {}


def test_update_with_empty_optional_dependencies() -> None:
    """Test that update does nothing when optional dependencies is
    empty."""
    metadata = {"optional-dependencies": {}}
    AutoExtrasMetadataHook("test", {}).update(metadata)
    assert metadata == {"optional-dependencies": {}}


def test_update_with_single_extra() -> None:
    """Test that update creates 'all' extra with dependencies from one
    extra."""
    metadata = {
        "optional-dependencies": {
            "dev": ["pytest>=7.0", "black>=22.0"],
        }
    }
    AutoExtrasMetadataHook("test", {}).update(metadata)
    assert "all" in metadata["optional-dependencies"]
    assert set(metadata["optional-dependencies"]["all"]) == {
        "pytest>=7.0",
        "black>=22.0",
    }


def test_update_with_multiple_extras() -> None:
    """Test that update creates 'all' extra combining all extras."""
    metadata = {
        "optional-dependencies": {
            "dev": ["pytest>=7.0", "black>=22.0"],
            "docs": ["sphinx>=5.0", "sphinx-rtd-theme>=1.0"],
            "typing": ["mypy>=1.0"],
        }
    }
    AutoExtrasMetadataHook("test", {}).update(metadata)
    assert "all" in metadata["optional-dependencies"]
    expected = {
        "pytest>=7.0",
        "black>=22.0",
        "sphinx>=5.0",
        "sphinx-rtd-theme>=1.0",
        "mypy>=1.0",
    }
    assert set(metadata["optional-dependencies"]["all"]) == expected


def test_update_with_duplicate_dependencies() -> None:
    """Test that update handles duplicate dependencies across extras."""
    metadata = {
        "optional-dependencies": {
            "dev": ["pytest>=7.0", "black>=22.0"],
            "test": ["pytest>=7.0", "coverage>=6.0"],
        }
    }
    AutoExtrasMetadataHook("test", {}).update(metadata)
    assert "all" in metadata["optional-dependencies"]
    # pytest should only appear once
    assert metadata["optional-dependencies"]["all"].count("pytest>=7.0") == 1
    expected = {"pytest>=7.0", "black>=22.0", "coverage>=6.0"}
    assert set(metadata["optional-dependencies"]["all"]) == expected


def test_update_preserves_existing_all_extra() -> None:
    """Test that update replaces existing 'all' extra."""
    metadata = {
        "optional-dependencies": {
            "all": ["old-dependency"],
            "dev": ["pytest>=7.0", "black>=22.0"],
        }
    }
    AutoExtrasMetadataHook("test", {}).update(metadata)
    assert "all" in metadata["optional-dependencies"]
    # 'all' should be regenerated from 'dev', not include old-dependency
    assert "old-dependency" not in metadata["optional-dependencies"]["all"]
    assert set(metadata["optional-dependencies"]["all"]) == {
        "pytest>=7.0",
        "black>=22.0",
    }


def test_update_sorts_dependencies() -> None:
    """Test that dependencies in 'all' extra are sorted."""
    metadata = {
        "optional-dependencies": {
            "dev": ["zzz-package", "aaa-package", "mmm-package"],
        }
    }
    AutoExtrasMetadataHook("test", {}).update(metadata)
    assert metadata["optional-dependencies"]["all"] == [
        "aaa-package",
        "mmm-package",
        "zzz-package",
    ]
