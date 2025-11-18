"""Core renderer for Minecraft blocks."""

from typing import Optional
from PIL import Image

from vibecoded_mc_renderer.models import BlockModel
from vibecoded_mc_renderer.core.texture_manager import TextureManager
from vibecoded_mc_renderer.rendering.isometric import create_isometric_cube, render_simple_block


class BlockRenderer:
    """Renders Minecraft blocks to images."""

    def __init__(self, texture_manager: TextureManager):
        """
        Initialize the block renderer.

        Args:
            texture_manager: TextureManager for loading textures
        """
        self.texture_manager = texture_manager

    def render_block(
        self, model: BlockModel, block_id: Optional[str] = None, output_size: int = 128
    ) -> Image.Image:
        """
        Render a block model to an isometric image.

        Args:
            model: BlockModel to render
            block_id: Optional block ID for context (used for tinting)
            output_size: Size of the output image (square)

        Returns:
            Rendered block image
        """
        # Resolve all texture variables
        texture_map = model.resolve_textures()

        # For now, handle simple cube blocks
        # Later we can expand to handle complex elements
        if not model.elements:
            # No elements means this is a parent model or invalid
            # Try to render with textures if available
            return self._render_simple_cube(texture_map, block_id, output_size)

        # Check if this is a simple cube (6 faces covering full block)
        if self._is_simple_cube(model):
            return self._render_simple_cube(texture_map, block_id, output_size)

        # For complex models, use simplified rendering
        # TODO: Implement full element-based rendering
        return self._render_simple_cube(texture_map, block_id, output_size)

    def _is_simple_cube(self, model: BlockModel) -> bool:
        """
        Check if the model is a simple full cube.

        Args:
            model: BlockModel to check

        Returns:
            True if the model is a simple cube
        """
        if len(model.elements) != 1:
            return False

        element = model.elements[0]

        # Check if element covers the full block (0,0,0 to 16,16,16)
        return (
            element.from_pos == [0, 0, 0]
            and element.to_pos == [16, 16, 16]
            and len(element.faces) >= 3
        )

    def _render_simple_cube(
        self, texture_map: dict, block_id: Optional[str], output_size: int
    ) -> Image.Image:
        """
        Render a simple cube with textures.

        Args:
            texture_map: Map of texture variables to paths
            block_id: Optional block ID for tinting
            output_size: Output image size

        Returns:
            Rendered block image
        """
        # Try to get textures for visible faces in isometric view
        # Priority: up (top), north/west (left), east/south (right)

        # Get top face texture
        top_texture = self._get_face_texture(texture_map, ["up", "top", "all"], block_id)

        # Get left face texture (typically north or west)
        left_texture = self._get_face_texture(
            texture_map, ["north", "west", "side", "all"], block_id
        )

        # Get right face texture (typically east or south)
        right_texture = self._get_face_texture(
            texture_map, ["east", "south", "side", "all"], block_id
        )

        # If all faces use the same texture, use simple rendering
        if top_texture == left_texture == right_texture:
            return render_simple_block(top_texture, output_size)

        return create_isometric_cube(top_texture, left_texture, right_texture, output_size)

    def _get_face_texture(
        self, texture_map: dict, face_names: list, block_id: Optional[str]
    ) -> Image.Image:
        """
        Get texture for a face, trying multiple possible names.

        Args:
            texture_map: Texture map from model
            face_names: List of possible face names to try (in priority order)
            block_id: Optional block ID for tinting

        Returns:
            Texture image
        """
        for face_name in face_names:
            if face_name in texture_map:
                texture_path = texture_map[face_name]
                if not texture_path.startswith("#"):
                    return self.texture_manager.resolve_texture_variable(
                        face_name, texture_map, block_id
                    )

        # Fallback to missing texture
        return self.texture_manager._get_missing_texture()
