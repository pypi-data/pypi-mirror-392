"""Model loader for parsing and resolving Minecraft block models."""

from typing import Dict, Optional
from vibecoded_mc_renderer.core.resource_manager import ResourceManager
from vibecoded_mc_renderer.models import BlockModel, Blockstate
from vibecoded_mc_renderer.utils import ResourceLocation
from vibecoded_mc_renderer.core.forge_blockstate_loader import ForgeBlockstateLoader


class ModelLoader:
    """Loads and resolves Minecraft block models and blockstates."""

    def __init__(self, resource_manager: ResourceManager):
        """
        Initialize the model loader.

        Args:
            resource_manager: ResourceManager instance for loading model files
        """
        self.resource_manager = resource_manager
        self.model_cache: Dict[str, BlockModel] = {}
        self.blockstate_cache: Dict[str, Blockstate] = {}
        self.forge_loader = ForgeBlockstateLoader()

    def load_blockstate(self, block_id: str) -> Optional[Blockstate]:
        """
        Load a blockstate definition for a block.

        Args:
            block_id: Block identifier (e.g., "minecraft:stone")

        Returns:
            Blockstate object or None if not found
        """
        if block_id in self.blockstate_cache:
            return self.blockstate_cache[block_id]

        loc = ResourceLocation(block_id)
        blockstate_path = loc.to_blockstate_path()

        data = self.resource_manager.get_json(blockstate_path)
        if data is None:
            return None

        # Check if this is a Forge blockstate (forge_marker: 1)
        if self.forge_loader.is_forge_blockstate(data):
            blockstate = self.forge_loader.parse_forge_blockstate(data)
        else:
            blockstate = Blockstate.from_dict(data)
        
        self.blockstate_cache[block_id] = blockstate
        return blockstate

    def load_model(self, model_path: str) -> Optional[BlockModel]:
        """
        Load a block model and resolve its parent chain.

        Args:
            model_path: Model path (e.g., "minecraft:block/stone" or "block/stone")

        Returns:
            Fully resolved BlockModel or None if not found
        """
        if model_path in self.model_cache:
            return self.model_cache[model_path]

        loc = ResourceLocation(model_path)
        json_path = loc.to_model_path()

        data = self.resource_manager.get_json(json_path)
        if data is None:
            return None

        model = BlockModel.from_dict(data)

        # Resolve parent chain
        if model.parent:
            parent_model = self.load_model(model.parent)
            if parent_model:
                # Merge with parent
                model = self._merge_with_parent(model, parent_model)

        self.model_cache[model_path] = model
        return model

    def _merge_with_parent(self, model: BlockModel, parent: BlockModel) -> BlockModel:
        """
        Merge a model with its parent model.

        Args:
            model: Child model
            parent: Parent model

        Returns:
            Merged BlockModel
        """
        # Start with parent's elements if child has none
        elements = model.elements if model.elements else parent.elements

        # Merge textures (child overrides parent)
        merged_textures = parent.textures.copy()
        merged_textures.update(model.textures)

        # Merge display settings
        merged_display = parent.display.copy()
        merged_display.update(model.display)

        return BlockModel(
            parent=None,  # Clear parent since we've merged
            textures=merged_textures,
            elements=elements,
            ambientocclusion=model.ambientocclusion,
            display=merged_display,
        )

    def get_model_for_block(
        self, 
        block_id: str,
        properties: Optional[Dict[str, str]] = None
    ) -> Optional[BlockModel]:
        """
        Get the block model for a given block ID.

        This loads the blockstate and returns the model for the default variant,
        or a specific variant if properties are provided.

        Args:
            block_id: Block identifier (e.g., "minecraft:stone")
            properties: Optional block properties for Forge blockstates
                       (e.g., {"active": "true", "tier": "lv"})

        Returns:
            BlockModel or None if not found
        """
        blockstate = self.load_blockstate(block_id)
        if blockstate is None:
            return None

        # If properties provided, try to find matching variant
        if properties and blockstate.variants:
            variant_key = self.forge_loader.properties_to_variant_key(properties)
            if variant_key in blockstate.variants:
                model_path = blockstate.variants[variant_key][0].model
            else:
                # Fall back to default
                model_path = blockstate.get_default_model()
        else:
            model_path = blockstate.get_default_model()
        
        if model_path is None:
            return None

        # In Minecraft 1.12.2 and earlier, model paths in blockstates
        # are often just the model name without "block/" prefix
        # Try to load as-is first, then with block/ prefix if needed
        model = self.load_model(model_path)
        if model is None and ":" not in model_path and "/" not in model_path:
            # Try with block/ prefix (e.g., "stone" -> "minecraft:block/stone")
            loc = ResourceLocation(block_id)
            prefixed_path = f"{loc.namespace}:block/{model_path}"
            model = self.load_model(prefixed_path)
        
        return model

    def clear_cache(self) -> None:
        """Clear model and blockstate caches."""
        self.model_cache.clear()
        self.blockstate_cache.clear()
