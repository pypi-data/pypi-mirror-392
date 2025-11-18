"""Utility functions for resource locations."""

from typing import Tuple


class ResourceLocation:
    """Represents a Minecraft resource location (namespace:path)."""

    def __init__(self, resource_string: str, default_namespace: str = "minecraft"):
        """
        Parse a resource location string.

        Args:
            resource_string: String like "minecraft:block/stone" or "block/stone"
            default_namespace: Default namespace if not specified (default: "minecraft")
        """
        if ":" in resource_string:
            self.namespace, self.path = resource_string.split(":", 1)
        else:
            self.namespace = default_namespace
            self.path = resource_string

    def __str__(self) -> str:
        """Return the full resource location string."""
        return f"{self.namespace}:{self.path}"

    def __repr__(self) -> str:
        """Return the representation of the resource location."""
        return f"ResourceLocation('{self.namespace}:{self.path}')"

    def to_texture_path(self) -> str:
        """
        Convert to a texture file path within a jar.

        Example:
            "minecraft:block/stone" -> "assets/minecraft/textures/block/stone.png"
        """
        return f"assets/{self.namespace}/textures/{self.path}.png"

    def to_model_path(self) -> str:
        """
        Convert to a model file path within a jar.

        Example:
            "minecraft:block/stone" -> "assets/minecraft/models/block/stone.json"
        """
        return f"assets/{self.namespace}/models/{self.path}.json"

    def to_blockstate_path(self) -> str:
        """
        Convert to a blockstate file path within a jar.

        Example:
            "minecraft:stone" -> "assets/minecraft/blockstates/stone.json"
        """
        # For blockstates, the path is just the block name
        block_name = self.path.split("/")[-1]
        return f"assets/{self.namespace}/blockstates/{block_name}.json"


def parse_resource_location(resource_string: str) -> Tuple[str, str]:
    """
    Parse a resource location string into namespace and path.

    Args:
        resource_string: String like "minecraft:block/stone" or "block/stone"

    Returns:
        Tuple of (namespace, path)
    """
    loc = ResourceLocation(resource_string)
    return loc.namespace, loc.path
