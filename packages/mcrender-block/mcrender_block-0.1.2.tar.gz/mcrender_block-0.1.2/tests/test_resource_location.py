"""Tests for the Minecraft block renderer."""

import pytest
from pathlib import Path
from vibecoded_mc_renderer.utils import ResourceLocation


class TestResourceLocation:
    """Test ResourceLocation parsing."""

    def test_parse_with_namespace(self):
        """Test parsing resource location with namespace."""
        loc = ResourceLocation("minecraft:block/stone")
        assert loc.namespace == "minecraft"
        assert loc.path == "block/stone"

    def test_parse_without_namespace(self):
        """Test parsing resource location without namespace."""
        loc = ResourceLocation("block/stone")
        assert loc.namespace == "minecraft"
        assert loc.path == "block/stone"

    def test_to_texture_path(self):
        """Test conversion to texture path."""
        loc = ResourceLocation("minecraft:block/stone")
        assert loc.to_texture_path() == "assets/minecraft/textures/block/stone.png"

    def test_to_model_path(self):
        """Test conversion to model path."""
        loc = ResourceLocation("minecraft:block/stone")
        assert loc.to_model_path() == "assets/minecraft/models/block/stone.json"

    def test_to_blockstate_path(self):
        """Test conversion to blockstate path."""
        loc = ResourceLocation("minecraft:stone")
        assert loc.to_blockstate_path() == "assets/minecraft/blockstates/stone.json"

    def test_string_representation(self):
        """Test string representation."""
        loc = ResourceLocation("minecraft:block/stone")
        assert str(loc) == "minecraft:block/stone"

    def test_custom_namespace(self):
        """Test parsing with custom namespace."""
        loc = ResourceLocation("create:block/cogwheel")
        assert loc.namespace == "create"
        assert loc.path == "block/cogwheel"
