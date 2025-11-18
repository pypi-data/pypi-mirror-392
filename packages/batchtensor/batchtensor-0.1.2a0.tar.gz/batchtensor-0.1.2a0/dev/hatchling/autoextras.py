# noqa: INP001
r"""Metadata hook to generate the "all" optional dependencies from the
optional dependencies."""

from __future__ import annotations

from hatchling.metadata.plugin.interface import MetadataHookInterface


class AutoExtrasMetadataHook(MetadataHookInterface):
    r"""Metadata hook to generate the "all" optional dependencies from
    the optional dependencies."""

    def update(self, metadata: dict) -> None:
        """Update the metadata.

        Args:
            metadata: The metadata dictionary.
        """
        extras = metadata.get("optional-dependencies", {})

        all_deps = []
        for name, deps in extras.items():
            if name != "all":
                all_deps.extend(deps)

        # remove duplicates
        unique = sorted(set(all_deps))

        extras["all"] = unique
        metadata["optional-dependencies"] = extras
