"""Test 3D isometric rendering quality."""

import pytest
from PIL import Image
from vibecoded_mc_renderer.rendering.renderer_3d import BlockRenderer3D
from vibecoded_mc_renderer.rendering.isometric import create_isometric_cube


class TestRenderer3D:
    """Tests for the 3D OpenGL-based renderer."""
    
    def test_renderer_initialization(self):
        """Test that the 3D renderer can be initialized."""
        renderer = BlockRenderer3D(output_size=128)
        assert renderer.output_size == 128
        assert renderer.ctx is not None
        assert renderer.program is not None
        renderer.cleanup()
    
    def test_renderer_context_manager(self):
        """Test that the renderer works as a context manager."""
        with BlockRenderer3D(output_size=128) as renderer:
            assert renderer.ctx is not None
    
    def test_render_simple_cube(self):
        """Test rendering a simple cube with solid colors."""
        # Create colored textures
        top = Image.new('RGB', (16, 16), (255, 0, 0))  # Red
        left = Image.new('RGB', (16, 16), (0, 255, 0))  # Green
        right = Image.new('RGB', (16, 16), (0, 0, 255))  # Blue
        
        with BlockRenderer3D(output_size=128) as renderer:
            result = renderer.render_cube(top, left, right)
        
        # Verify output
        assert result.size == (128, 128)
        assert result.mode == 'RGBA'
        
        # Check that the image has non-transparent pixels
        pixels = list(result.getdata())
        non_transparent = [p for p in pixels if p[3] > 0]
        assert len(non_transparent) > 0, "Image should have visible pixels"
    
    def test_render_with_textures(self):
        """Test rendering with actual textured images."""
        # Create a checkerboard pattern
        size = 16
        texture = Image.new('RGB', (size, size))
        pixels = []
        for y in range(size):
            for x in range(size):
                if (x // 4 + y // 4) % 2 == 0:
                    pixels.append((255, 255, 255))
                else:
                    pixels.append((0, 0, 0))
        texture.putdata(pixels)
        
        with BlockRenderer3D(output_size=256) as renderer:
            result = renderer.render_cube(texture, texture, texture)
        
        assert result.size == (256, 256)
        assert result.mode == 'RGBA'
    
    def test_isometric_cube_integration(self):
        """Test that create_isometric_cube uses the 3D renderer."""
        # Create simple textures
        top = Image.new('RGB', (16, 16), (255, 0, 0))
        left = Image.new('RGB', (16, 16), (0, 255, 0))
        right = Image.new('RGB', (16, 16), (0, 0, 255))
        
        # This should use the 3D renderer if available
        result = create_isometric_cube(top, left, right, output_size=128)
        
        assert result.size == (128, 128)
        assert result.mode == 'RGBA'
    
    def test_different_output_sizes(self):
        """Test rendering with different output sizes."""
        texture = Image.new('RGB', (16, 16), (128, 128, 128))
        
        for size in [64, 128, 256, 512]:
            with BlockRenderer3D(output_size=size) as renderer:
                result = renderer.render_cube(texture, texture, texture)
            
            assert result.size == (size, size)
    
    def test_transparency_handling(self):
        """Test that transparent textures are handled correctly."""
        # Create texture with transparency
        texture = Image.new('RGBA', (16, 16), (255, 0, 0, 128))  # Semi-transparent red
        
        with BlockRenderer3D(output_size=128) as renderer:
            result = renderer.render_cube(texture, texture, texture)
        
        assert result.mode == 'RGBA'
        
        # Check that there are pixels with varying alpha values
        pixels = list(result.getdata())
        alphas = [p[3] for p in pixels]
        assert min(alphas) < 255, "Should have some transparency"
