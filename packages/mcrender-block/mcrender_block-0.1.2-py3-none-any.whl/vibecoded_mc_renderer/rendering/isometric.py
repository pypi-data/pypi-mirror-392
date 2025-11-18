"""Isometric rendering for Minecraft blocks using 3D OpenGL renderer."""

from typing import Tuple
from PIL import Image

# Import 3D renderer
try:
    from .renderer_3d import BlockRenderer3D
    HAS_3D_RENDERER = True
except ImportError:
    HAS_3D_RENDERER = False
    # Fallback to 2D transforms if 3D renderer not available
    import math
    import numpy as np


def create_isometric_cube(
    top_texture: Image.Image,
    left_texture: Image.Image,
    right_texture: Image.Image,
    output_size: int = 128,
    camera_height: float = 1.5,
    samples: int = 4,
) -> Image.Image:
    """
    Create an isometric cube from three face textures.

    Args:
        top_texture: Texture for the top face
        left_texture: Texture for the left face (typically north or west)
        right_texture: Texture for the right face (typically east or south)
        output_size: Size of the output image (will be square)
        camera_height: Camera Y position (1.0=acute/sharp, 1.5=standard, 2.0=wide/top-down)
        samples: MSAA samples for anti-aliasing (0=off, 2/4/8/16=quality)

    Returns:
        Isometric rendered block image
    """
    # Use 3D renderer if available
    if HAS_3D_RENDERER:
        try:
            with BlockRenderer3D(output_size=output_size, camera_height=camera_height, samples=samples) as renderer:
                return renderer.render_cube(top_texture, left_texture, right_texture)
        except Exception as e:
            # Fall back to 2D rendering if 3D fails
            print(f"3D rendering failed: {e}, falling back to 2D")
            pass
    
    # Fallback to original 2D transform approach
    return _create_isometric_cube_2d(
        top_texture, left_texture, right_texture, output_size
    )


def _create_isometric_cube_2d(
    top_texture: Image.Image,
    left_texture: Image.Image,
    right_texture: Image.Image,
    output_size: int = 128,
) -> Image.Image:
    """
    Create an isometric cube using 2D transforms (fallback method).

    Args:
        top_texture: Texture for the top face
        left_texture: Texture for the left face
        right_texture: Texture for the right face
        output_size: Size of the output image

    Returns:
        Isometric rendered block image
    """
    # Calculate dimensions for the isometric view
    # The block will be centered in the output image
    block_size = int(output_size * 0.6)  # Block takes up 60% of output

    # Create output image with transparency
    output = Image.new("RGBA", (output_size, output_size), (0, 0, 0, 0))

    # Ensure textures are in RGBA mode
    top_texture = top_texture.convert("RGBA")
    left_texture = left_texture.convert("RGBA")
    right_texture = right_texture.convert("RGBA")

    # Transform and composite faces
    top_face = _transform_top_face(top_texture, block_size)
    left_face = _transform_left_face(left_texture, block_size)
    right_face = _transform_right_face(right_texture, block_size)

    # Calculate positions for proper alignment
    center_x = output_size // 2
    center_y = output_size // 2
    
    # Position faces to align correctly
    top_pos = (center_x - top_face.width // 2, center_y - block_size)
    left_pos = (center_x - left_face.width, center_y - left_face.height // 2)
    right_pos = (center_x, center_y - right_face.height // 2)

    # Composite in correct order (back to front)
    output.paste(left_face, left_pos, left_face)
    output.paste(right_face, right_pos, right_face)
    output.paste(top_face, top_pos, top_face)

    return output


def _transform_top_face(texture: Image.Image, block_size: int) -> Image.Image:
    """
    Transform a texture to the top face of an isometric cube.

    Args:
        texture: Square texture
        block_size: Size of the isometric block

    Returns:
        Transformed texture for the top face
    """
    # Resize texture to block size
    texture = texture.resize((block_size, block_size), Image.LANCZOS)

    # Create a diamond shape by rotating 45 degrees and scaling vertically
    # First, rotate 45 degrees
    rotated = texture.rotate(45, expand=True, resample=Image.BICUBIC)

    # Calculate the new size after isometric projection
    # In isometric view, the top face is compressed vertically by about 0.5
    new_width = int(block_size * math.sqrt(2))
    new_height = int(new_width * 0.5)

    # Scale to create isometric top face
    top_face = rotated.resize((new_width, new_height), Image.LANCZOS)

    return top_face


def _transform_left_face(texture: Image.Image, block_size: int) -> Image.Image:
    """
    Transform texture for left face using proper 2:1 isometric projection.
    Uses QUAD mapping to create correct parallelogram.
    """
    s = block_size
    texture = texture.resize((s, s), Image.LANCZOS)

    # Target parallelogram dimensions (2:1 isometric)
    # Width is half the top diamond width; height is full block height
    w = int(s * math.sqrt(2) / 2)
    h = int(s)

    # QUAD transform: map source square to destination parallelogram
    # Format for data parameter: (x0,y0, x1,y1, x2,y2, x3,y3) 
    # These are the coordinates in the SOURCE that map to each corner of destination
    # We work backwards: define destination corners, map to source corners
    
    # Destination parallelogram (left face leans left):
    # Top edge is shifted left, bottom edge is at base
    dst = (
        w, 0,          # top-left of dest -> top-left of source (0,0)
        0, h // 2,     # top-right of dest -> top-right of source (s,0)
        0, h + h // 2, # bottom-right of dest -> bottom-right of source (s,s)
        w, h           # bottom-left of dest -> bottom-left of source (0,s)
    )

    face = texture.transform(
        (w, h + h // 2),  # Output canvas size
        Image.QUAD,
        dst,
        Image.BICUBIC
    )
    
    # Apply shading
    arr = np.array(face)
    if arr.shape[2] >= 3:
        arr[:,:,0:3] = (arr[:,:,0:3] * 0.8).astype(np.uint8)
    
    return Image.fromarray(arr, "RGBA")


def _transform_right_face(texture: Image.Image, block_size: int) -> Image.Image:
    """
    Transform texture for right face using proper 2:1 isometric projection.
    Uses QUAD mapping to create correct parallelogram (mirror of left).
    """
    s = block_size
    texture = texture.resize((s, s), Image.LANCZOS)

    w = int(s * math.sqrt(2) / 2)
    h = int(s)

    # Destination parallelogram (right face leans right):
    # Top edge is shifted right, bottom edge is at base
    dst = (
        0, 0,          # top-left of dest -> top-left of source (0,0)
        w, h // 2,     # top-right of dest -> top-right of source (s,0)
        w, h + h // 2, # bottom-right of dest -> bottom-right of source (s,s)
        0, h           # bottom-left of dest -> bottom-left of source (0,s)
    )

    face = texture.transform(
        (w, h + h // 2),
        Image.QUAD,
        dst,
        Image.BICUBIC
    )
    
    # Apply shading
    arr = np.array(face)
    if arr.shape[2] >= 3:
        arr[:,:,0:3] = (arr[:,:,0:3] * 0.65).astype(np.uint8)
    
    return Image.fromarray(arr, "RGBA")


def render_simple_block(
    texture: Image.Image, output_size: int = 128
) -> Image.Image:
    """
    Render a simple block (cube with same texture on all sides).

    Args:
        texture: Texture to use for all faces
        output_size: Size of the output image

    Returns:
        Isometric rendered block
    """
    return create_isometric_cube(texture, texture, texture, output_size)
