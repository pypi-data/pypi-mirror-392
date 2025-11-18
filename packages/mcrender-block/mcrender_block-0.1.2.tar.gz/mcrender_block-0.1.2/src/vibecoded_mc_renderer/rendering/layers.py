"""Multi-layer rendering system for GregTech blocks."""

from typing import Tuple, Optional
from PIL import Image
import numpy as np

from vibecoded_mc_renderer.utils.colors import apply_tint


def composite_layers(
    base_texture: Image.Image,
    overlay_texture: Optional[Image.Image] = None,
    base_tint: Optional[Tuple[int, int, int]] = None,
    overlay_tint: Optional[Tuple[int, int, int]] = None,
) -> Image.Image:
    """
    Composite base and overlay textures with optional tinting.
    
    Args:
        base_texture: Base layer texture
        overlay_texture: Optional overlay layer
        base_tint: Optional RGB color to tint base layer
        overlay_tint: Optional RGB color to tint overlay layer
    
    Returns:
        Composited RGBA image
    """
    # Ensure base is RGBA
    result = base_texture.convert("RGBA")
    
    # Apply tint to base if specified
    if base_tint:
        result = apply_tint(result, base_tint)
    
    # Composite overlay if provided
    if overlay_texture:
        overlay = overlay_texture.convert("RGBA")
        
        # Apply tint to overlay if specified
        if overlay_tint:
            overlay = apply_tint(overlay, overlay_tint)
        
        # Alpha composite overlay onto base
        result = Image.alpha_composite(result, overlay)
    
    return result


def apply_tintindex_to_faces(
    textures: dict[str, Image.Image],
    tintindex_map: dict[str, int],
    tint_color: Optional[Tuple[int, int, int]] = None,
) -> dict[str, Image.Image]:
    """
    Apply tinting to textures based on tintindex values.
    
    Args:
        textures: Dictionary of face name -> texture image
        tintindex_map: Dictionary of face name -> tintindex value
        tint_color: RGB color to apply to faces with tintindex >= 0
    
    Returns:
        Dictionary of face name -> tinted texture
    """
    if not tint_color:
        return textures
    
    result = {}
    for face_name, texture in textures.items():
        tintindex = tintindex_map.get(face_name, -1)
        
        if tintindex >= 0:
            # Apply tinting
            result[face_name] = apply_tint(texture, tint_color)
        else:
            # No tinting
            result[face_name] = texture
    
    return result


def create_emissive_layer(
    base_image: Image.Image,
    emissive_texture: Image.Image,
    emissive_strength: float = 1.0,
) -> Image.Image:
    """
    Create an emissive (glowing) layer composite.
    
    Args:
        base_image: Base rendered image
        emissive_texture: Emissive texture (will be rendered at full brightness)
        emissive_strength: Strength of emissive effect (0.0-1.0)
    
    Returns:
        Composited image with emissive layer
    """
    # Ensure both are RGBA
    base = base_image.convert("RGBA")
    emissive = emissive_texture.convert("RGBA")
    
    # Resize emissive to match base if needed
    if emissive.size != base.size:
        emissive = emissive.resize(base.size, Image.LANCZOS)
    
    # Apply emissive strength
    if emissive_strength < 1.0:
        emissive_array = np.array(emissive, dtype=np.float32)
        emissive_array[:, :, 3] *= emissive_strength  # Adjust alpha
        emissive = Image.fromarray(emissive_array.astype(np.uint8), "RGBA")
    
    # Composite using additive blending for emissive parts
    result = Image.alpha_composite(base, emissive)
    
    return result


def create_two_layer_model(
    bottom_texture: Image.Image,
    top_texture: Image.Image,
    bottom_tint: Optional[Tuple[int, int, int]] = None,
    top_tint: Optional[Tuple[int, int, int]] = None,
) -> Image.Image:
    """
    Create a two-layer texture (base + overlay) like GregTech's cube_2_layer_all.
    
    Args:
        bottom_texture: Bottom layer texture
        top_texture: Top layer overlay texture
        bottom_tint: Optional tint for bottom layer
        top_tint: Optional tint for top layer
    
    Returns:
        Composited RGBA texture
    """
    return composite_layers(bottom_texture, top_texture, bottom_tint, top_tint)


def blend_textures_additive(
    base: Image.Image,
    overlay: Image.Image,
    opacity: float = 1.0,
) -> Image.Image:
    """
    Blend two textures using additive blending (for glowing effects).
    
    Args:
        base: Base image
        overlay: Overlay image
        opacity: Opacity of overlay (0.0-1.0)
    
    Returns:
        Blended image
    """
    base_array = np.array(base.convert("RGBA"), dtype=np.float32)
    overlay_array = np.array(overlay.convert("RGBA"), dtype=np.float32)
    
    # Resize if needed
    if base_array.shape != overlay_array.shape:
        overlay = overlay.resize(base.size, Image.LANCZOS)
        overlay_array = np.array(overlay, dtype=np.float32)
    
    # Apply opacity to overlay
    overlay_alpha = overlay_array[:, :, 3:4] / 255.0 * opacity
    
    # Additive blend RGB channels
    result_rgb = np.minimum(base_array[:, :, :3] + overlay_array[:, :, :3] * overlay_alpha, 255)
    
    # Keep base alpha
    result_alpha = base_array[:, :, 3:4]
    
    # Combine
    result = np.concatenate([result_rgb, result_alpha], axis=2)
    result = np.clip(result, 0, 255).astype(np.uint8)
    
    return Image.fromarray(result, "RGBA")
