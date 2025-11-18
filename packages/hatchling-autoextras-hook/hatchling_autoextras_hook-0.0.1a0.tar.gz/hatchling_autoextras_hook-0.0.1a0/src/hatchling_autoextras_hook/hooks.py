"""Hatchling metadata hook to automatically generate 'all' extras."""

from __future__ import annotations

from hatchling.metadata.plugin.interface import MetadataHookInterface
from hatchling.plugin import hookimpl


class AutoExtrasMetadataHook(MetadataHookInterface):
    """Metadata hook that automatically generates an 'all' extra.

    This hook collects all optional dependencies defined in the project
    and creates an 'all' extra that includes all of them.

    Example usage:

    ```pycon

    >>> from hatchling_autoextras_hook.hooks import AutoExtrasMetadataHook
    >>> metadata = {
    ...     "optional-dependencies": {
    ...         "dev": ["pytest>=7.0", "black>=22.0"],
    ...     }
    ... }
    >>> AutoExtrasMetadataHook("test", {}).update(metadata)
    >>> metadata
    {'optional-dependencies': {'dev': ['pytest>=7.0', 'black>=22.0'],
     'all': ['black>=22.0', 'pytest>=7.0']}}

    ```
    """

    PLUGIN_NAME = "autoextras"

    def update(self, metadata: dict) -> None:
        """Update the project metadata to add the 'all' extra.

        Args:
            metadata: The project metadata dictionary to update.
        """
        # Get optional dependencies
        optional_dependencies = metadata.get("optional-dependencies", {})

        if not optional_dependencies:
            return

        # Collect all dependencies from all extras (except 'all' if it already exists)
        all_deps = set()
        for extra_name, deps in optional_dependencies.items():
            if extra_name != "all":
                all_deps.update(deps)

        # Sort for consistent output
        all_deps_sorted = sorted(all_deps)

        # Add or update the 'all' extra
        optional_dependencies["all"] = all_deps_sorted
        metadata["optional-dependencies"] = optional_dependencies


@hookimpl
def hatch_register_metadata_hook() -> type[MetadataHookInterface]:
    """Register the autoextras metadata hook with hatchling."""
    return AutoExtrasMetadataHook
