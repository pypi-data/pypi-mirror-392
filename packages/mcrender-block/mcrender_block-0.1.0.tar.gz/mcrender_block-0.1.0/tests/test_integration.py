"""Integration tests for the Minecraft block renderer."""

import pytest
from pathlib import Path
from PIL import Image

from vibecoded_mc_renderer.core.resource_manager import ResourceManager
from vibecoded_mc_renderer.core.model_loader import ModelLoader
from vibecoded_mc_renderer.core.texture_manager import TextureManager
from vibecoded_mc_renderer.core.renderer import BlockRenderer


class TestResourceManager:
    """Test ResourceManager functionality."""

    def test_list_blockstates(self, resource_manager: ResourceManager):
        """Test listing blockstates from the jar."""
        blockstates = resource_manager.list_blockstates()
        
        assert len(blockstates) > 0
        assert "minecraft:stone" in blockstates
        assert "minecraft:dirt" in blockstates
        assert "minecraft:grass" in blockstates

    def test_list_namespaces(self, resource_manager: ResourceManager):
        """Test listing namespaces."""
        namespaces = resource_manager.list_namespaces()
        
        assert "minecraft" in namespaces

    def test_get_resource(self, resource_manager: ResourceManager):
        """Test getting a resource."""
        # Try to get stone blockstate
        data = resource_manager.get_resource("assets/minecraft/blockstates/stone.json")
        
        assert data is not None
        assert len(data) > 0

    def test_get_json(self, resource_manager: ResourceManager):
        """Test getting and parsing JSON."""
        blockstate = resource_manager.get_json("assets/minecraft/blockstates/stone.json")
        
        assert blockstate is not None
        assert "variants" in blockstate


class TestModelLoader:
    """Test ModelLoader functionality."""

    def test_load_blockstate(self, model_loader: ModelLoader):
        """Test loading a blockstate."""
        blockstate = model_loader.load_blockstate("minecraft:stone")
        
        assert blockstate is not None
        assert len(blockstate.variants) > 0

    def test_load_model(self, model_loader: ModelLoader):
        """Test loading a block model."""
        model = model_loader.load_model("minecraft:block/stone")
        
        assert model is not None
        assert len(model.textures) > 0 or model.parent is not None

    def test_get_model_for_block(self, model_loader: ModelLoader):
        """Test getting a complete model for a block."""
        model = model_loader.get_model_for_block("minecraft:stone")
        
        assert model is not None
        # After resolving parents, should have textures or elements
        assert len(model.textures) > 0 or len(model.elements) > 0

    def test_parent_resolution(self, model_loader: ModelLoader):
        """Test that parent models are resolved correctly."""
        # Stone block should have a parent chain
        model = model_loader.get_model_for_block("minecraft:stone")
        
        assert model is not None
        # After merging with parent, should not have parent reference
        assert model.parent is None
        # Should have resolved textures
        texture_map = model.resolve_textures()
        assert len(texture_map) > 0


class TestTextureManager:
    """Test TextureManager functionality."""

    def test_get_texture(self, texture_manager: TextureManager):
        """Test loading a texture."""
        texture = texture_manager.get_texture("minecraft:block/stone")
        
        assert texture is not None
        assert isinstance(texture, Image.Image)
        assert texture.mode == "RGBA"
        assert texture.width > 0
        assert texture.height > 0

    def test_missing_texture(self, texture_manager: TextureManager):
        """Test missing texture fallback."""
        texture = texture_manager.get_texture("minecraft:block/nonexistent_texture")
        
        assert texture is not None
        assert isinstance(texture, Image.Image)
        # Should return the magenta/black checkerboard
        assert texture.width == 16
        assert texture.height == 16

    def test_texture_caching(self, texture_manager: TextureManager):
        """Test that textures are cached."""
        texture1 = texture_manager.get_texture("minecraft:block/stone")
        texture2 = texture_manager.get_texture("minecraft:block/stone")
        
        # Should return the same cached instance
        assert texture1 is texture2


class TestBlockRenderer:
    """Test BlockRenderer functionality."""

    def test_render_stone_block(self, model_loader: ModelLoader, renderer: BlockRenderer):
        """Test rendering a simple stone block."""
        model = model_loader.get_model_for_block("minecraft:stone")
        assert model is not None
        
        image = renderer.render_block(model, "minecraft:stone", output_size=128)
        
        assert image is not None
        assert isinstance(image, Image.Image)
        assert image.mode == "RGBA"
        assert image.width == 128
        assert image.height == 128

    def test_render_dirt_block(self, model_loader: ModelLoader, renderer: BlockRenderer):
        """Test rendering a dirt block."""
        model = model_loader.get_model_for_block("minecraft:dirt")
        assert model is not None
        
        image = renderer.render_block(model, "minecraft:dirt", output_size=256)
        
        assert image is not None
        assert image.width == 256
        assert image.height == 256

    def test_render_grass_block(self, model_loader: ModelLoader, renderer: BlockRenderer):
        """Test rendering a grass block (with tinting)."""
        model = model_loader.get_model_for_block("minecraft:grass")
        assert model is not None
        
        image = renderer.render_block(model, "minecraft:grass", output_size=128)
        
        assert image is not None
        assert isinstance(image, Image.Image)

    def test_render_different_sizes(self, model_loader: ModelLoader, renderer: BlockRenderer):
        """Test rendering at different output sizes."""
        model = model_loader.get_model_for_block("minecraft:stone")
        assert model is not None
        
        for size in [64, 128, 256, 512]:
            image = renderer.render_block(model, "minecraft:stone", output_size=size)
            assert image.width == size
            assert image.height == size


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_full_rendering_pipeline(self, minecraft_jar: Path, tmp_path: Path):
        """Test the complete rendering pipeline from jar to image file."""
        output_file = tmp_path / "test_stone.png"
        
        # Create all components
        with ResourceManager([minecraft_jar]) as resource_manager:
            model_loader = ModelLoader(resource_manager)
            texture_manager = TextureManager(resource_manager)
            renderer = BlockRenderer(texture_manager)
            
            # Load and render
            model = model_loader.get_model_for_block("minecraft:stone")
            assert model is not None
            
            image = renderer.render_block(model, "minecraft:stone", output_size=128)
            image.save(output_file)
            
            # Verify file was created
            assert output_file.exists()
            assert output_file.stat().st_size > 0
            
            # Verify it can be loaded back
            loaded_image = Image.open(output_file)
            assert loaded_image.width == 128
            assert loaded_image.height == 128

    def test_batch_rendering(self, minecraft_jar: Path, tmp_path: Path):
        """Test rendering multiple blocks."""
        blocks = ["minecraft:stone", "minecraft:dirt", "minecraft:cobblestone"]
        
        with ResourceManager([minecraft_jar]) as resource_manager:
            model_loader = ModelLoader(resource_manager)
            texture_manager = TextureManager(resource_manager)
            renderer = BlockRenderer(texture_manager)
            
            for block_id in blocks:
                model = model_loader.get_model_for_block(block_id)
                assert model is not None
                
                image = renderer.render_block(model, block_id, output_size=64)
                assert image is not None
                
                # Save to verify
                output_file = tmp_path / f"{block_id.replace(':', '_')}.png"
                image.save(output_file)
                assert output_file.exists()
