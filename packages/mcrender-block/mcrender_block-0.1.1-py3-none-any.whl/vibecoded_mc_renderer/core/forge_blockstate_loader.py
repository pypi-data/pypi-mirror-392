"""Forge blockstate loader for handling forge_marker format."""

import json
from typing import Dict, List, Optional, Any
from vibecoded_mc_renderer.models import Blockstate, ModelVariant


class ForgeBlockstateLoader:
    """Handles Forge-specific blockstate formats."""
    
    @staticmethod
    def is_forge_blockstate(data: Dict[str, Any]) -> bool:
        """
        Check if blockstate uses Forge format.
        
        Args:
            data: Parsed blockstate JSON
        
        Returns:
            True if this is a Forge blockstate
        """
        return data.get("forge_marker") == 1
    
    @staticmethod
    def parse_forge_blockstate(data: Dict[str, Any]) -> Blockstate:
        """
        Parse a Forge blockstate with property-based variants.
        
        Forge blockstates use format like:
        {
          "forge_marker": 1,
          "defaults": { "model": "...", "textures": {...} },
          "variants": {
            "property1=value1,property2=value2": {...}
          }
        }
        
        Args:
            data: Parsed blockstate JSON
        
        Returns:
            Blockstate object
        """
        blockstate = Blockstate()
        
        # Parse defaults (applied to all variants unless overridden)
        defaults = data.get("defaults", {})
        
        # Parse variants
        variants_data = data.get("variants", {})
        for state_key, variant_data in variants_data.items():
            # Handle list or single variant
            if isinstance(variant_data, list):
                variants = []
                for v in variant_data:
                    merged = ForgeBlockstateLoader._merge_with_defaults(v, defaults)
                    variants.append(ModelVariant.from_dict(merged))
                blockstate.variants[state_key] = variants
            else:
                merged = ForgeBlockstateLoader._merge_with_defaults(variant_data, defaults)
                blockstate.variants[state_key] = [ModelVariant.from_dict(merged)]
        
        return blockstate
    
    @staticmethod
    def _merge_with_defaults(variant: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge variant data with defaults.
        
        Args:
            variant: Variant-specific data
            defaults: Default values
        
        Returns:
            Merged dictionary
        """
        merged = defaults.copy()
        
        # Don't override textures if variant has its own
        if "textures" in variant and "textures" in defaults:
            # Merge texture dictionaries
            merged_textures = defaults.get("textures", {}).copy()
            merged_textures.update(variant.get("textures", {}))
            merged["textures"] = merged_textures
        
        # Override other properties
        for key, value in variant.items():
            if key != "textures":
                merged[key] = value
        
        return merged
    
    @staticmethod
    def parse_property_string(property_str: str) -> Dict[str, str]:
        """
        Parse property string like "active=true,variant=steel" into dictionary.
        
        Args:
            property_str: Comma-separated property assignments
        
        Returns:
            Dictionary of property name -> value
        """
        if not property_str or property_str in ["normal", "inventory", ""]:
            return {}
        
        properties = {}
        for part in property_str.split(","):
            if "=" in part:
                key, value = part.split("=", 1)
                properties[key.strip()] = value.strip()
        
        return properties
    
    @staticmethod
    def find_matching_variant(
        blockstate: Blockstate, 
        properties: Dict[str, str]
    ) -> Optional[ModelVariant]:
        """
        Find the variant that matches given properties.
        
        Args:
            blockstate: Blockstate to search
            properties: Properties to match (e.g., {"active": "true", "variant": "steel"})
        
        Returns:
            First matching ModelVariant or None
        """
        # Try exact match first
        property_str = ",".join(f"{k}={v}" for k, v in sorted(properties.items()))
        if property_str in blockstate.variants:
            variants = blockstate.variants[property_str]
            return variants[0] if variants else None
        
        # Try to find a partial match
        for state_key, variants in blockstate.variants.items():
            state_props = ForgeBlockstateLoader.parse_property_string(state_key)
            
            # Check if all requested properties match
            if all(state_props.get(k) == v for k, v in properties.items()):
                return variants[0] if variants else None
        
        # Fallback to first variant
        if blockstate.variants:
            first_key = next(iter(blockstate.variants))
            variants = blockstate.variants[first_key]
            return variants[0] if variants else None
        
        return None
    
    @staticmethod
    def properties_to_variant_key(properties: Dict[str, str]) -> str:
        """
        Convert properties dict to variant key string.
        
        Args:
            properties: Properties dict (e.g., {"active": "true", "tier": "lv"})
        
        Returns:
            Variant key string (e.g., "active=true,tier=lv")
        """
        return ",".join(f"{k}={v}" for k, v in sorted(properties.items()))
