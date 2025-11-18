"""Texture manager for loading and caching textures."""

from typing import Dict, Optional, Tuple
from PIL import Image
from io import BytesIO

from vibecoded_mc_renderer.core.resource_manager import ResourceManager
from vibecoded_mc_renderer.utils import ResourceLocation
from vibecoded_mc_renderer.utils.colors import apply_tint, get_tint_for_block


class TextureManager:
    """Manages texture loading and caching."""

    def __init__(self, resource_manager: ResourceManager):
        """
        Initialize the texture manager.

        Args:
            resource_manager: ResourceManager instance for loading textures
        """
        self.resource_manager = resource_manager
        self.texture_cache: Dict[str, Image.Image] = {}
        self.missing_texture: Optional[Image.Image] = None

    def get_texture(
        self, texture_path: str, tint: Optional[Tuple[int, int, int]] = None
    ) -> Image.Image:
        """
        Get a texture by its resource location.

        Args:
            texture_path: Texture path like "minecraft:block/stone" or "block/stone"
            tint: Optional RGB tint color to apply

        Returns:
            PIL Image in RGBA mode
        """
        # Create cache key with tint
        cache_key = f"{texture_path}_{tint}" if tint else texture_path

        # Check cache
        if cache_key in self.texture_cache:
            return self.texture_cache[cache_key]

        # Load texture
        loc = ResourceLocation(texture_path)
        texture_file_path = loc.to_texture_path()

        data = self.resource_manager.get_resource(texture_file_path)
        if data is None:
            # Return missing texture
            texture = self._get_missing_texture()
        else:
            try:
                texture = Image.open(BytesIO(data))
                texture = texture.convert("RGBA")
            except Exception:
                texture = self._get_missing_texture()

        # Apply tint if specified
        if tint:
            texture = apply_tint(texture, tint)

        # Cache and return
        self.texture_cache[cache_key] = texture
        return texture

    def resolve_texture_variable(
        self, texture_var: str, texture_map: Dict[str, str], block_id: Optional[str] = None
    ) -> Image.Image:
        """
        Resolve a texture variable (e.g., "#all", "#side") to an actual texture.

        Args:
            texture_var: Texture variable (with or without '#')
            texture_map: Map of texture variables to texture paths
            block_id: Optional block ID for auto-tinting

        Returns:
            PIL Image in RGBA mode
        """
        # Remove '#' if present
        if texture_var.startswith("#"):
            texture_var = texture_var[1:]

        # Look up in texture map
        if texture_var not in texture_map:
            return self._get_missing_texture()

        texture_path = texture_map[texture_var]

        # If it's still a variable, it wasn't fully resolved
        if texture_path.startswith("#"):
            return self._get_missing_texture()

        # Check if block needs tinting
        tint = None
        if block_id:
            tint = get_tint_for_block(block_id)

        return self.get_texture(texture_path, tint)

    def _get_missing_texture(self) -> Image.Image:
        """
        Generate or return cached missing texture (magenta/black checkerboard).

        Returns:
            Missing texture image
        """
        if self.missing_texture is None:
            # Create 16x16 magenta/black checkerboard
            self.missing_texture = Image.new("RGBA", (16, 16), (0, 0, 0, 255))
            pixels = self.missing_texture.load()

            # Create checkerboard pattern
            magenta = (255, 0, 255, 255)
            black = (0, 0, 0, 255)

            for y in range(16):
                for x in range(16):
                    # 8x8 checkerboard squares
                    if (x // 8 + y // 8) % 2 == 0:
                        pixels[x, y] = magenta  # type: ignore
                    else:
                        pixels[x, y] = black  # type: ignore

        return self.missing_texture.copy()

    def clear_cache(self) -> None:
        """Clear the texture cache."""
        self.texture_cache.clear()

    def preload_textures(self, texture_paths: list[str]) -> None:
        """
        Preload a list of textures into the cache.

        Args:
            texture_paths: List of texture paths to preload
        """
        for path in texture_paths:
            self.get_texture(path)
