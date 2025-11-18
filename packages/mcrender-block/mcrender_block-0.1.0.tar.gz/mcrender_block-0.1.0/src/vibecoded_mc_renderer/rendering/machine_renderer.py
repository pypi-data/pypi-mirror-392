"""Machine renderer for GregTech-style machines with overlays."""

from typing import Optional, Tuple
from pathlib import Path
from PIL import Image

from vibecoded_mc_renderer.core.texture_manager import TextureManager
from vibecoded_mc_renderer.core.resource_manager import ResourceManager
from vibecoded_mc_renderer.rendering.layers import composite_layers, create_emissive_layer
from vibecoded_mc_renderer.rendering.isometric import create_isometric_cube
from vibecoded_mc_renderer.utils.materials import get_tier_color, get_material_color


class MachineRenderer:
    """Renders GregTech-style machines with voltage tiers and overlays."""
    
    def __init__(
        self, 
        texture_manager: TextureManager,
        resource_manager: ResourceManager
    ):
        """
        Initialize machine renderer.
        
        Args:
            texture_manager: TextureManager for loading textures
            resource_manager: ResourceManager for checking resources
        """
        self.texture_manager = texture_manager
        self.resource_manager = resource_manager
    
    def render_machine(
        self,
        machine_name: str,
        tier: str = "lv",
        active: bool = False,
        material: Optional[str] = None,
        output_size: int = 128,
        emissive_strength: float = 1.0,
        camera_height: float = 1.5,
    ) -> Image.Image:
        """
        Render a GregTech machine with casing, overlays, and emissive layers.
        
        Args:
            machine_name: Machine identifier (e.g., "electric_furnace")
            tier: Voltage tier (lv, mv, hv, ev, iv, luv, zpm, uv, etc.)
            active: Whether machine is active (affects overlay)
            material: Optional material override for casing color
            output_size: Size of output image
            emissive_strength: Strength of emissive glow (0.0-1.0)
            camera_height: Camera Y position (1.0=acute/sharp, 1.5=standard, 2.0=wide/top-down)
        
        Returns:
            Rendered machine image
        """
        tier = tier.lower()
        
        # Load casing textures (voltage tier) - no tinting, textures have correct colors
        casing_bottom = self._load_casing_texture(tier, "bottom")
        casing_top = self._load_casing_texture(tier, "top")
        casing_side = self._load_casing_texture(tier, "side")
        
        # Debug: save casing textures
        import os
        if os.environ.get('DEBUG_RENDER'):
            casing_top.save(f'debug_casing_top_{tier}.png')
            casing_side.save(f'debug_casing_side_{tier}.png')
        
        # Load machine overlays
        overlay_front = self._load_machine_overlay(machine_name, "front", active)
        overlay_top = self._load_machine_overlay(machine_name, "top", active)
        
        # Debug: save overlays
        if os.environ.get('DEBUG_RENDER'):
            if overlay_front:
                overlay_front.save(f'debug_overlay_front_{machine_name}.png')
            if overlay_top:
                overlay_top.save(f'debug_overlay_top_{machine_name}.png')
        
        # Composite top face (top casing + top overlay)
        if overlay_top:
            top_face = composite_layers(casing_top, overlay_top)
        else:
            top_face = casing_top
        
        # Left face is plain casing (left side in isometric view)
        left_face = casing_side
        
        # Right face is front with overlay (right side = front in isometric view)
        if overlay_front:
            right_face = composite_layers(casing_side, overlay_front)
        else:
            right_face = casing_side
        
        # Debug: save composited faces
        if os.environ.get('DEBUG_RENDER'):
            top_face.save(f'debug_top_face_{machine_name}.png')
            left_face.save(f'debug_left_face_{machine_name}.png')
            right_face.save(f'debug_right_face_{machine_name}.png')
        
        # Create isometric cube with correct face assignment
        result = create_isometric_cube(top_face, left_face, right_face, output_size, camera_height)
        
        # Add emissive layer if active and emissive textures exist
        if active and emissive_strength > 0:
            emissive_front = self._load_machine_overlay(
                machine_name, "front", active, emissive=True
            )
            if emissive_front:
                # Composite emissive on right face (front in isometric view)
                emissive_right_face = composite_layers(
                    Image.new("RGBA", casing_side.size, (0, 0, 0, 0)),
                    emissive_front
                )
                emissive_cube = create_isometric_cube(
                    Image.new("RGBA", casing_top.size, (0, 0, 0, 0)),
                    Image.new("RGBA", casing_side.size, (0, 0, 0, 0)),
                    emissive_right_face,
                    output_size,
                    camera_height
                )
                result = create_emissive_layer(result, emissive_cube, emissive_strength)
        
        return result
    
    def _load_casing_texture(
        self, 
        tier: str, 
        face: str,
        tint: Optional[Tuple[int, int, int]] = None
    ) -> Image.Image:
        """
        Load voltage tier casing texture.
        
        Args:
            tier: Voltage tier (lv, mv, hv, etc.)
            face: Face name (bottom, top, side)
            tint: Optional RGB tint color
        
        Returns:
            Texture image
        """
        # Try GregTech casing path
        texture_path = f"gregtech:blocks/casings/voltage/{tier}/{face}"
        texture = self.texture_manager.get_texture(texture_path, tint)
        
        # If not found, might return missing texture
        return texture
    
    def _load_machine_overlay(
        self,
        machine_name: str,
        face: str,
        active: bool,
        emissive: bool = False
    ) -> Optional[Image.Image]:
        """
        Load machine overlay texture.
        
        Args:
            machine_name: Machine identifier
            face: Face name (front, top, etc.)
            active: Whether to load active variant
            emissive: Whether to load emissive variant
        
        Returns:
            Overlay texture or None if not found
        """
        # Build texture path
        state_suffix = "_active" if active else ""
        emissive_suffix = "_emissive" if emissive else ""
        
        texture_path = (
            f"gregtech:blocks/machines/{machine_name}/"
            f"overlay_{face}{state_suffix}{emissive_suffix}"
        )
        
        # Check if texture exists
        resource_path = f"assets/gregtech/textures/blocks/machines/{machine_name}/overlay_{face}{state_suffix}{emissive_suffix}.png"
        
        if not self.resource_manager.resource_exists(resource_path):
            return None
        
        return self.texture_manager.get_texture(texture_path)
    
    def render_material_block(
        self,
        material: str,
        material_set: str = "dull",
        output_size: int = 128,
    ) -> Image.Image:
        """
        Render a material block (compressed block like Copper Block, Steel Block).
        
        Args:
            material: Material name (copper, steel, aluminum, etc.)
            material_set: Material set texture style (dull, shiny, metallic, etc.)
            output_size: Size of output image
        
        Returns:
            Rendered block image
        """
        # Get material color
        material_color = get_material_color(material)
        
        # Load material set texture
        texture_path = f"gregtech:blocks/material_sets/{material_set}/block"
        texture = self.texture_manager.get_texture(texture_path, material_color)
        
        # Create isometric cube with same texture on all faces
        from vibecoded_mc_renderer.rendering.isometric import render_simple_block
        return render_simple_block(texture, output_size)
    
    def render_cable(
        self,
        material: str,
        size: str = "single",
        insulated: bool = True,
        output_size: int = 128,
    ) -> Image.Image:
        """
        Render a cable/wire.
        
        Args:
            material: Material name (copper, gold, aluminum, etc.)
            size: Cable size (single, double, quadruple, octal, hex)
            insulated: Whether cable is insulated
            output_size: Size of output image
        
        Returns:
            Rendered cable image
        """
        # Get material color
        material_color = get_material_color(material)
        
        # Load wire texture
        wire_texture = self.texture_manager.get_texture(
            "gregtech:blocks/cable/wire", material_color
        )
        
        if insulated:
            # Load insulation overlay (size determines which insulation texture)
            insulation_map = {
                "single": 0,
                "double": 1,
                "quadruple": 2,
                "octal": 3,
                "hex": 4,
            }
            insulation_index = insulation_map.get(size, 0)
            insulation_texture = self.texture_manager.get_texture(
                f"gregtech:blocks/cable/insulation_{insulation_index}"
            )
            
            # Composite wire + insulation
            result_texture = composite_layers(wire_texture, insulation_texture)
        else:
            result_texture = wire_texture
        
        # Render as simple block
        from vibecoded_mc_renderer.rendering.isometric import render_simple_block
        return render_simple_block(result_texture, output_size)
