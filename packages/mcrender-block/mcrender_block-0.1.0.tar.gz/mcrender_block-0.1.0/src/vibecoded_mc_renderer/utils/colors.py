"""Color utilities for texture tinting."""

from typing import Tuple
import numpy as np
from PIL import Image


# Default biome colors for tinting
GRASS_COLOR = (124, 189, 107)  # Plains biome grass color
FOLIAGE_COLOR = (119, 171, 47)  # Plains biome foliage color
WATER_COLOR = (63, 118, 228)  # Default water color


def apply_tint(texture: Image.Image, tint_color: Tuple[int, int, int]) -> Image.Image:
    """
    Apply a color tint to a texture.

    This multiplies the RGB channels by the tint color while preserving alpha.
    Used for grass, leaves, water, and other biome-tinted blocks.

    Args:
        texture: Input texture (RGBA image)
        tint_color: RGB tuple (0-255 for each channel)

    Returns:
        Tinted texture as RGBA image
    """
    if texture.mode != "RGBA":
        texture = texture.convert("RGBA")

    data = np.array(texture, dtype=np.float32)

    # Multiply RGB channels by tint color, normalize by 255
    tint_array = np.array(tint_color, dtype=np.float32) / 255.0
    data[:, :, 0:3] = data[:, :, 0:3] * tint_array

    # Clamp values to valid range
    data = np.clip(data, 0, 255).astype(np.uint8)

    return Image.fromarray(data, "RGBA")


def blend_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], alpha: float) -> Tuple[int, int, int]:
    """
    Blend two RGB colors together.

    Args:
        color1: First RGB color
        color2: Second RGB color
        alpha: Blend factor (0.0 = all color1, 1.0 = all color2)

    Returns:
        Blended RGB color
    """
    r = int(color1[0] * (1 - alpha) + color2[0] * alpha)
    g = int(color1[1] * (1 - alpha) + color2[1] * alpha)
    b = int(color1[2] * (1 - alpha) + color2[2] * alpha)
    return (r, g, b)


def get_tint_for_block(block_id: str) -> Tuple[int, int, int] | None:
    """
    Get the default tint color for a block if it requires tinting.

    Args:
        block_id: Block identifier (e.g., "minecraft:grass_block")

    Returns:
        RGB tint color tuple, or None if block doesn't need tinting
    """
    # Normalize block_id
    if ":" not in block_id:
        block_id = f"minecraft:{block_id}"

    # Grass blocks and related
    if "grass_block" in block_id or "grass_path" in block_id:
        return GRASS_COLOR

    # Leaves and foliage
    if any(x in block_id for x in ["leaves", "vine", "lily_pad"]):
        return FOLIAGE_COLOR

    # Water
    if "water" in block_id:
        return WATER_COLOR

    return None
